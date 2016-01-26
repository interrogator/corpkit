#interrogator with classes:

def interrogator(corpus, 
            search, 
            query = 'any', 
            show = 'w',
            exclude = False,
            excludemode = 'any',
            searchmode = 'all',
            dep_type = 'collapsed-ccprocessed-dependencies',
            case_sensitive = False,
            quicksave = False,
            just_speakers = False,
            preserve_case = False,
            lemmatag = False,
            files_as_subcorpora = False,
            conc = False,
            only_unique = False,
            random = False,
            only_format_match = False,
            num_proc = 'default',
            **kwargs):
    
    # store kwargs
    locs = locals()

    from corpkit.interrogation import Interrogation
    from corpkit.process import tregex_engine
    import pandas as pd
    from pandas import DataFrame, Series
    from collections import Counter
    from corpkit.other import as_regex
    from corpkit.process import get_deps
    from time import localtime, strftime
    thetime = strftime("%H:%M:%S", localtime())
    from corpkit.textprogressbar import TextProgressBar
    from corpkit.process import animator
    from corpkit.dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')

    # convert path to corpus object
    if type(corpus) == str:
        from corpkit.Corpus import Corpus
        corpus = Corpus(corpus)

    # figure out how the user has entered the query and normalise
    from corpkit.process import searchfixer
    search, search_iterable = searchfixer(search, query)

    if 'l' in show and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    if type(show) == str:
        show = [show]

    # check if just counting
    countmode = 'c' in show

    def is_multiquery(corpus, search, query, just_speakers):
        """determine if multiprocessing is needed
        do some retyping if need be as well"""
        im = False
        from collections import OrderedDict
        if hasattr(corpus, '__iter__'):
            im = True
        if type(query) == list:
            query = {c.title(): c for c in query}
        if type(query) == dict or type(query) == OrderedDict:
            im = True
        if just_speakers:
            if just_speakers == 'each':
                im = True
                just_speakers = ['each']
            if just_speakers == ['each']:
                im = True
            if type(just_speakers) == str:
                im = False
                just_speakers = [just_speakers]
            if type(just_speakers) == list:
                if len(just_speakers) > 1:
                    im = True
        if type(search) == dict:
            if all(type(i) == dict for i in search.values()):
                im = True
        return im, corpus, search, query, just_speakers

    def slow_tregex(sents, **dummy_args):
        """do the speaker-specific version of tregex queries"""
        import os
        from corpkit.process import tregex_engine
        # first, put the relevant trees into temp file
        if kwargs.get('outname'):
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        to_write = '\n'.join([sent._parse_string.strip() for sent in sents if sent.parse_string is not None]).encode('utf-8', errors = 'ignore')
        with open(to_open, "w") as fo:
            fo.write(to_write)
        q = search.values()[0]
        res = tregex_engine(query = q, 
                            options = ['-o', '-%s' % translated_option], 
                            corpus = to_open,
                            root = root,
                            preserve_case = True)
        if root:
            root.update()
        os.remove(to_open)
        return res

    def get_stats(sents, **dummy_args):
        """get a bunch of frequencies on interpersonal phenomena"""
        import os
        import re  
        # first, put the relevant trees into temp file
        if kwargs.get('outname'):
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        with open(to_open, "w") as fo:
            for sent in sents:
                statsmode_results['Sentences'] += 1
                fo.write(sent.parse_string.rstrip().encode('utf-8', errors = 'ignore') + '\n')
                deps = get_deps(sent, dep_type)
                numpass = len([x for x in deps.links if x.type.endswith('pass')])
                statsmode_results['Passives'] += numpass
                statsmode_results['Tokens'] += len(sent.tokens)
                words = [w.word for w in sent.tokens if w.word.isalnum()]
                statsmode_results['Words'] += len(words)
                statsmode_results['Characters'] += len(''.join(words))
                #statsmode_results['Unique words'] += len(set([w.word.lower() for w in sent.tokens if w.word.isalnum()]))
                #statsmode_results['Unique lemmata'] += len(set([w.lemma.lower() for w in sent.tokens if w.word.isalnum()]))

        # count moods via trees          (/\?/ !< __)
        from dictionaries.process_types import processes
        from corpkit.other import as_regex
        tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                     'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                     'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Open class words': r'/^(NN|JJ|VB|RB)/ < __',
                     'Closed class words': r'__ !< __ !> /^(NN|JJ|VB|RB)/',
                     'Clauses': r'/^S/ < __',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Mental processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.mental, boundaries = 'w'),
                     'Verbal processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.verbal, boundaries = 'w'),
                     'Relational processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.relational, boundaries = 'w')
                     }

        for name, q in sorted(tregex_qs.items()):
            res = tregex_engine(query = q, 
                  options = ['-o', '-C'], 
                  corpus = to_open,  
                  root = root)
            statsmode_results[name] += int(res)
            global numdone
            numdone += 1
            if root:
                root.update()
            #if not root:
            #    tot_string = str(numdone + 1) + '/' + str(total_files * len(tregex_qs.keys()))
            #    if kwargs.get('outname'):
            #        tot_string = '%s: %s' % (kwargs['outname'], tot_string)
            #    animator(p, numdone, tot_string, **par_args)
            if kwargs.get('note', False):
                kwargs['note'].progvar.set((numdone * 100.0 / (total_files * len(tregex_qs.keys())) / denom) + startnum)
        os.remove(to_open)

    def make_conc_lines_from_whole_mid(wholes, middle_column_result, speakr = False):
        if speakr is False:
            speakr = ''
        conc_lines = []
        # remove duplicates from results
        unique_wholes = []
        unique_middle_column_result = []
        duplicates = []
        for index, ((f, whole), mid) in enumerate(zip(wholes, middle_column_result)):
            if '-join-'.join([f, whole, mid]) not in duplicates:
                duplicates.append('-join-'.join([f, whole, mid]))
                unique_wholes.append([f, whole])
                unique_middle_column_result.append(mid)

        # split into start, middle and end, dealing with multiple occurrences
        for index, ((f, whole), mid) in enumerate(zip(unique_wholes, unique_middle_column_result)):
            reg = re.compile(r'([^a-zA-Z0-9-]|^)(' + re.escape(mid) + r')([^a-zA-Z0-9-]|$)', re.IGNORECASE | re.UNICODE)
            offsets = [(m.start(), m.end()) for m in re.finditer(reg,whole)]
            for offstart, offend in offsets:              
                start, middle, end = whole[0:offstart].strip(), whole[offstart:offend].strip(), whole[offend:].strip()
                conc_lines.append([os.path.basename(f), speakr, start, middle, end])
        return conc_lines

    def uniquify(conc_lines):
        from collections import OrderedDict
        od = OrderedDict()
        unique_lines = []
        checking = []
        for index, (f, speakr, start, middle, end) in enumerate(conc_lines):
            joined = ' '.join([speakr, start, 'MIDDLEHERE:', middle, ':MIDDLEHERE', end])
            if joined not in checking:
                unique_lines.append(conc_lines[index])
            checking.append(joined)
        return unique_lines

    def lemmatiser(list_of_words, tag):
        """take a list of unicode words and a tag and return a lemmatised list."""
        
        output = []
        for word in list_of_words:
            if translated_option.startswith('u'):
                if word.lower() in taglemma.keys():
                    word = taglemma[word.lower()]
                else:
                    if word == 'x':
                        word = 'Other'
            # only use wordnet lemmatiser when appropriate
            else:
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            output.append(word)
        return output

    def gettag(query, lemmatag = False):
        """
        Find tag for WordNet lemmatisation
        """
        import re

        tagdict = {'N': 'n',
                   'A': 'a',
                   'V': 'v',
                   'A': 'r',
                   'None': False,
                   '': False,
                   'Off': False}

        if lemmatag is False:
            tag = 'n' # same default as wordnet
            # attempt to find tag from tregex query
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)')
            tagchecker = re.compile(r'^[A-Z]{1,4}$')
            treebank_tag = re.findall(tagfinder, query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', ''))
            if re.match(tagchecker, treebank_tag[0]):
                tag = tagdict.get(treebank_tag[0], 'n')
        elif lemmatag:
            tag = lemmatag
        return tag

    def format_tregex(results):
        """format tregex by show list"""
        if countmode:
            return results
        import re
        done = []
        if 'l' in show or 'pl' in show:
            lemmata = lemmatiser(results, gettag(search.get('t'), lemmatag))
        else:
            lemmata = [None for i in results]

        for word, lemma in zip(results, lemmata):
            bits = []
            if exclude and exclude.get('w'):
                if len(exclude.keys()) == 1 or excludemode == 'any':
                    if re.search(exclude.get('w'), word):
                        continue
                if len(exclude.keys()) == 1 or excludemode == 'any':
                    if re.search(exclude.get('l'), lemma):
                        continue
                if len(exclude.keys()) == 1 or excludemode == 'any':
                    if re.search(exclude.get('p'), word):
                        continue
                if len(exclude.keys()) == 1 or excludemode == 'any':
                    if re.search(exclude.get('pl'), lemma):
                        continue
            if exclude and excludemode == 'all':
                num_to_cause_exclude = len(exclude.keys())
                current_num = 0
                if exclude.get('w'):
                    if re.search(exclude.get('w'), word):
                        current_num += 1
                if exclude.get('l'):
                    if re.search(exclude.get('l'), lemma):
                        current_num += 1
                if exclude.get('p'):
                    if re.search(exclude.get('p'), word):
                        current_num += 1
                if exclude.get('pl'):
                    if re.search(exclude.get('pl'), lemma):
                        current_num += 1   
                if current_num == num_to_cause_exclude:
                    continue                 

            for i in show:
                if i == 't':
                    bits.append(word)
                if i == 'l':
                    bits.append(lemma)
                elif i == 'w':
                    bits.append(word)
                elif i == 'p':
                    bits.append(word)
                elif i == 'pl':
                    bits.append(lemma)
            joined = '/'.join(bits)
            done.append(joined)
        return done


    def tok_by_list(pattern, list_of_toks, **kwargs):
        """search for regex in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        matches = [m for m in list_of_toks if m in pattern]
        for m in matches:
            result.append(m)
        return result

    def tok_ngrams(pattern, list_of_toks, split_contractions = True):
        from collections import Counter
        global gramsize
        import re
        ngrams = Counter()
        result = []
        # if it's not a compiled regex
        list_of_toks = [x for x in list_of_toks if re.search(regex_nonword_filter, x)]

        if not split_contractions:
            list_of_toks = unsplitter(list_of_toks)
            
            #list_of_toks = [x for x in list_of_toks if "'" not in x]
        for index, w in enumerate(list_of_toks):
            try:
                the_gram = [list_of_toks[index+x] for x in range(gramsize)]
                if not any(re.search(query, x) for x in the_gram):
                    continue
                #if query != 'any':
                #    if not any(re.search(query, w) is True for w in the_gram):
                #        continue
                ngrams[' '.join(the_gram)] += 1
            except IndexError:
                pass
        # turn counter into list of results
        for k, v in ngrams.items():
            if v > 1:
                for i in range(v):
                    result.append(k)
        return result

    def tok_by_reg(pattern, list_of_toks):
        """search for regex in plaintext corpora"""
        try:
            comped = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'

        matches = [m for m in list_of_toks if re.search(comped, m)]

        return matches

    def plaintext_regex_search(pattern, plaintext_data):
        """search for regex in plaintext corpora"""
        result = []
        #if not pattern.startswith(r'\b') and not pattern.endswith(r'\b'):
            #pattern = r'\b' + pattern + '\b'
        try:
            compiled_pattern = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'
        matches = re.findall(compiled_pattern, plaintext_data)
        for index, i in enumerate(matches):
            if type(i) == tuple:
                matches[index] = i[0]
        return matches

    def plaintext_simple_search(pattern, plaintext_data):
        """search for tokens in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        try:
            tmp = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'

        for p in pattern:
            if case_sensitive:
                pat = re.compile(r'\b' + re.escape(p) + r'\b')
            else:
                pat = re.compile(r'\b' + re.escape(p) + r'\b', re.IGNORECASE)
            matches = re.findall(pat, plaintext_data)
            for m in range(len(matches)):
                result.append(p)
        return result


    # do multiprocessing if need be
    im, corpus, search, query, just_speakers = is_multiquery(corpus, search, query, just_speakers)
    if im:
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)

    # determine if data is parsed/single file
    from corpkit.process import determine_datatype
    datatype, singlefile = determine_datatype(corpus.path)



    # store all results in here
    results = {}

    ############################################
    # Determine the search function to be used #
    ############################################
    
    # simple tregex is tregex over whole dirs
    simple_tregex_mode = False
    if not just_speakers and 't' in search.keys():
        simple_tregex_mode = True
        if datatype != 'parse':
            raise ValueError('Need parsed corpus to search trees.')
    else:
        if corpus.datatype == 'plaintext':
            if search.get('n'):
                searcher = plaintext_ngram
                optiontext = 'n-grams via plaintext'
            if search.get('w'):
                if kwargs.get('regex', True):
                    searcher = plaintext_regex_search
                else:
                    searcher = plaintext_simple_search
                optiontext = 'Searching plaintext'

        elif corpus.datatype == 'tokens':
            if search.get('n'):
                searcher = tok_ngrams
                optiontext = 'n-grams via tokens'
            elif search.get('w'):
                if kwargs.get('regex', True):
                    searcher = tok_by_reg
                else:
                    searcher = tok_by_list
                optiontext = 'Searching tokens'

        elif corpus.datatype == 'parse':
            if search.get('t'):
                searcher = slow_tregex
            elif search.get('v'):
                searcher = get_stats
                optiontext = 'General statistics'
                from collections import Counter
                statsmode_results = Counter()
                global numdone
                numdone = 0
            else:
                from corpkit.depsearch import dep_searcher
                searcher = dep_searcher
                optiontext = 'Dependency querying'

    ############################################
    #      Set some Tregex-related values      #
    ############################################

    if search.get('t'):

        # check the query
        q = tregex_engine(corpus = False, query = search.get('t'), 
                          options = ['-t'], check_query = True, root = root)
        if query is False:
            if root:
                return 'Bad query'
            else:
                return

        optiontext = 'Searching parse trees'
        if 'p' in show or 'pl' in show:
            translated_option = 'u'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 't' in show:
            translated_option = 'o'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 'w' in show:
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'c' in show:
            count_results = {}
            only_count = True
            translated_option = 'C'
            if type(query) == list:
                query = r'/%s/ !< __'  % as_regex(query, boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'l' in show:
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'

    ############################################
    # Make iterable for corpus/subcorpus/file  #
    ############################################

    if corpus.singlefile:
        to_iterate_over = {(corpus.name, corpus.path): [corpus]}
    elif not corpus.subcorpora:
        to_iterate_over = {(corpus.name, corpus.path): corpus.files}
    else:
        to_iterate_over = {}
        for k, v in corpus.structure.items():
            to_iterate_over[(k.name, k.path)] = v
    if files_as_subcorpora:
        to_iterate_over = {}
        for f in corpus.files:
            to_iterate_over[(f.name, f.path)] = [f]

    ############################################
    # Print welcome message #
    ############################################

    if conc:
        message = 'Concordancing'
    else:
        message = 'Interrogating'
    if kwargs.get('printstatus', True):
        thetime = strftime("%H:%M:%S", localtime())

        sformat = '\n          '.join(['%s: %s' %(k, v) for k, v in search.items()])
        welcome = '\n%s: %s %s ...\n          %s\n          %s\n' % (thetime, message, corpus.name, optiontext, sformat)
        print welcome

    current_file = 0
    
    par_args = {'printstatus': kwargs.get('printstatus', True), 'root': root}
    if kwargs.get('paralleling'):
        from blessings import Terminal
        term = Terminal()
        par_args['terminal'] = term
        par_args['linenum'] = kwargs.get('paralleling')

    ############################################
    # Make progress bar  #
    ############################################

    if simple_tregex_mode:
        total_files = len(to_iterate_over.keys())
    else:
        if search.get('v'):
            total_files = sum([len(x) for x in to_iterate_over.values()]) * 12
        else:
            total_files = sum([len(x) for x in to_iterate_over.values()])

    outn = kwargs.get('outname', '')
    if outn:
        outn = outn + ': '
    tstr = '%s%d/%d' % (outn, current_file + 1, total_files)
    p = animator(None, None, init = True, tot_string = tstr, length = total_files, **par_args)

    ############################################
    # Iterate over data, doing interrogations  #
    ############################################

    for (subcorpus_name, subcorpus_path), files in sorted(to_iterate_over.items()):
        results[subcorpus_name] = []
        
        # tregex over subcorpus
        if simple_tregex_mode:

            current_file += 1
            tstr = '%s%d/%d' % (outn, current_file + 1, total_files)
            animator(p, current_file, tstr, **par_args)

            op = ['-o', '-' + translated_option]                
            result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = True)
            
            if countmode:
                results[subcorpus_name].append(result)
                continue

            result = format_tregex(result)
            if conc:
                op.append('-w')
                whole_result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = True)

                result = make_conc_lines_from_whole_mid(whole_result, result, speakr = False)

        # dependencies, plaintext, tokens or slow_tregex
        else:
            result = []
            for f in files:
                current_file += 1
                tstr = '%s%d/%d' % (outn, current_file + 1, total_files)
                animator(p, current_file, tstr, **par_args)
                if corpus.datatype == 'parse':
                    with open(f.path, 'r') as data:
                        data = data.read()
                        from corenlp_xml.document import Document
                        try:
                            corenlp_xml = Document(data)
                        except:
                            print 'Could not read file: %s' % f.path
                            continue
                        if just_speakers:  
                            sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                            if not sents:
                                continue
                        else:
                            sents = corenlp_xml.sentences

                        res = searcher(sents, search = search, show = show,
                            dep_type = dep_type,
                            exclude = exclude,
                            excludemode = excludemode,
                            searchmode = searchmode,
                            lemmatise = False,
                            case_sensitive = case_sensitive,
                            concordancing = conc,
                            only_format_match = only_format_match)

                        if countmode:
                            results[subcorpus_name].append(res)
                            continue
                        
                        if searcher == slow_tregex:
                            res = format_tregex(res)
                    
                        # add filename for conc
                        if conc:
                            for line in res:
                                line.insert(0, f.name)

                elif corpus.datatype == 'tokens':
                    import pickle
                    data = pickle.load(open(filepath, "rb"))
                    res = searcher(search.values[0], data)

                elif corpus.datatype == 'plaintext':
                    with open(f.path, 'rb') as data:
                        data = data.read()
                        res = searcher(search.values[0], data)

                if res:
                    for i in res:
                        result.append(i)

        if not countmode:
            for r in result:
                if not preserve_case:
                    if conc:
                        r = [b.lower() for b in r]
                    else:
                        r = r.lower()
                results[subcorpus_name].append(r)
        
        # turn data into counter object
        if not countmode and not conc:
            results[subcorpus_name] = Counter(results[subcorpus_name])

        elif 'v' in search.keys():
            results[subcorpus_name] = statsmode_results

    # delete temp file if there
    import os
    if os.path.isfile('tmp.txt'):
        os.remove('tmp.txt')

    ############################################
    #   Tally everything into big DataFrame    #
    ############################################

    if conc:
        all_conc_lines = []
        for sc_name, results in results.items():

            if only_unique:
                unique_results = uniquify(results)
            else:
                unique_results = results

            print unique_results

            #make into series
            pindex = 'c f s l m r'.encode('utf-8').split()

            for fname, spkr, start, word, end in unique_results:
                spkr = unicode(spkr, errors = 'ignore')
                fname = os.path.basename(fname)
                #start = start.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
                #word = word.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
                #end = end.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
                #spaces = ' ' * (maximum / 2 - (len(word) / 2))
                #new_word = spaces + word + spaces

                # the use of ascii here makes sure the string formats ok, but will also screw over
                # anyone doing non-english work. so, change to utf-8, then fix errors as they come
                # in the corpkit-gui "add_conc_lines_to_window" function
                all_conc_lines.append(Series([sc_name.encode('ascii', errors = 'ignore'),
                                         fname.encode('ascii', errors = 'ignore'), \
                                         spkr.encode('ascii', errors = 'ignore'), \
                                         start.encode('ascii', errors = 'ignore'), \
                                         word.encode('ascii', errors = 'ignore'), \
                                         end.encode('ascii', errors = 'ignore')], index = pindex))

        # randomise results...
        if random:
            from random import shuffle
            shuffle(all_conc_lines)

        df = pd.concat(all_conc_lines, axis = 1).T

        add_links = False

        if not add_links:
            df.columns = ['c', 'f', 's', 'l', 'm', 'r']
        else:
            df.columns = ['c', 'f', 's', 'l', 'm', 'r', 'link']

        if all(x == '' for x in list(df['s'].values)):
            df.drop('s', axis = 1, inplace = True)

        if 'note' in kwargs.keys():
            kwargs['note'].progvar.set(100)

        #if print_output:
        #    formatl = lambda x: "{0}".format(x[-window:])
        #    formatf = lambda x: "{0}".format(x[-20:])
        #    #formatr = lambda x: 
        #    formatr = lambda x: "{{:<{}s}}".format(df['r'].str.len().max()).format(x[:window])
        #    st = df.head(n).to_string(header = False, formatters={'l': formatl,
        #                                                          'r': formatr,
        #                                                          'f': formatf}).splitlines()
        #    
        #    # hack because i can't figure out formatter:
        #    rem = '\n'.join([re.sub('\s*\.\.\.\s*$', '', s) for s in st])
        #    print rem

        from corpkit.interrogation import Concordance
        output = Concordance(df)
        #output = df
        try:
            del locs['corpus']
        except:
            pass
        output.query = locs
        return output 

    # if interrogate, make into Interrogation
    else:
        if countmode:
            df = Series({k: sum(v) for k, v in sorted(results.items())})
            tot = df.sum()
        else:
            the_big_dict = {}
            unique_results = set([item for sublist in results.values() for item in sublist])
            for word in unique_results:
                the_big_dict[word] = [subcorp_result[word] for subcorp_result in results.values()]
            # turn master dict into dataframe, sorted
            df = DataFrame(the_big_dict, index = sorted(results.keys()))
            numentries = len(df.columns)
            tot = df.sum(axis = 1)
            total_total = df.sum().sum()

        ############################################
        # Format, output as Interrogation object   #
        ############################################

        if not countmode:
            if not corpus.subcorpora or singlefile:
                if not files_as_subcorpora:
                    if not kwargs.get('df1_always_df'):
                        df = Series(df.ix[0])
                        df.sort(ascending = False)
                        tot = df.sum()
                        numentries = len(df.index)
                        total_total = tot

        # format final string
        if kwargs.get('printstatus', True):
            thetime = strftime("%H:%M:%S", localtime())
            finalstring = '\n\n%s: Interrogation finished!' % thetime
            if countmode:
                finalstring += ' %d matches.' % tot
            else:
                finalstring += ' %d unique results, %d total occurrences' % (numentries, total_total)
            print finalstring

        return Interrogation(results = df, totals = tot, query = locs)