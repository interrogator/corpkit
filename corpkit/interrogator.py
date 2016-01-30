#!/usr/bin/python

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
            multiprocess = False,
            spelling = False,
            regex_nonword_filter = r'[A-Za-z0-9:_]',
            gramsize = 2,
            split_contractions = False,
            **kwargs):
    """interrogate corpus, corpora, subcorpus and file objects

    see corpkit.interrogation.interrogate() for docstring"""
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
    from corpkit.dictionaries.word_transforms import wordlist, taglemma

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')

    # convert path to corpus object
    if type(corpus) == str:
        from corpkit.corpus import Corpus
        corpus = Corpus(corpus)

    # figure out how the user has entered the query and normalise
    from corpkit.process import searchfixer
    search, search_iterable = searchfixer(search, query)
    
    # for better printing of query, esp during multiprocess
    # can remove if multiprocess printing improved
    if len(search.keys()) == 1:
        query = search.values()[0]

    if 'l' in show and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    if type(show) == str:
        show = [show]

    def is_multiquery(corpus, search, query, just_speakers):
        """determine if multiprocessing is needed
        do some retyping if need be as well"""
        im = False
        from collections import OrderedDict
        if hasattr(corpus, '__iter__'):
            im = True
        # so we can do search = 't', query = ['NP', 'VP']:
        if type(query) == list:
            if query != search.values()[0] or len(search.keys()) > 1:
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
        to_write = '\n'.join([sent._parse_string.strip() for sent in sents \
                              if sent.parse_string is not None])
        to_write.encode('utf-8', errors = 'ignore')
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
        if countmode:
            return(len(res))
        else:
            return res

    def get_stats(sents, **dummy_args):
        """get a bunch of frequencies on interpersonal phenomena"""
        import os
        import re
        from collections import Counter
        statsmode_results = Counter()  
        # first, put the relevant trees into temp file
        if kwargs.get('outname'):
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        with open(to_open, "w") as fo:
            for sent in sents:
                statsmode_results['Sentences'] += 1
                sts = sent.parse_string.rstrip()
                encd = sts.encode('utf-8', errors = 'ignore') + '\n'
                fo.write(encd)
                deps = get_deps(sent, dep_type)
                numpass = len([x for x in deps.links if x.type.endswith('pass')])
                statsmode_results['Passives'] += numpass
                statsmode_results['Tokens'] += len(sent.tokens)
                words = [w.word for w in sent.tokens if w.word.isalnum()]
                statsmode_results['Words'] += len(words)
                statsmode_results['Characters'] += len(''.join(words))

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
            else:
                tot_string = str(numdone + 1) + '/' + str(total_files)
                if kwargs.get('outname'):
                    tot_string = '%s: %s' % (kwargs['outname'], tot_string)
                animator(p, numdone, tot_string, **par_args)
            if kwargs.get('note', False):
                kwargs['note'].progvar.set((numdone * 100.0 / total_files / denom) + startnum)
        os.remove(to_open)
        return statsmode_results

    def make_conc_lines_from_whole_mid(wholes, middle_column_result, 
                                       speakr = False):
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
            qr = query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', '')
            treebank_tag = re.findall(tagfinder, qr)
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

    def tok_by_list(pattern, list_of_toks, concordancing = False, **kwargs):
        """search for regex in plaintext corpora"""
        import re
        if type(pattern) == str:
            pattern = [pattern]
        if not case_sensitive:
            pattern = [p.lower() for p in pattern]
        if not concordancing:
            if case_sensitive:
                matches = [m for m in list_of_toks if m in pattern]
            else:
                matches = [m for m in list_of_toks if m.lower() in pattern]
        else:
            matches = []
            for index, token in enumerate(list_of_toks):
                if token in pattern:
                    match = [' '.join([t for t in unsplitter(list_of_toks[:index])])[-140:]]
                    match.append(token)
                    match.append(' '.join([t for t in unsplitter(list_of_toks[index + 1:])])[:140])
                    matches.append(match)
        if countmode:
            return(len(matches))
        else:
            return matches

    def unsplitter(lst):
        """unsplit contractions and apostophes from tokenised text"""
        if split_contractions:
            return lst
        unsplit = []
        for index, t in enumerate(lst):
            if index == 0 or index == len(lst) - 1:
                unsplit.append(t)
                continue
            if "'" in t and not t.endswith("'"):
                rejoined = ''.join([lst[index - 1], t])
                unsplit.append(rejoined)
            else:
                if not "'" in lst[index + 1]:
                    unsplit.append(t)
        return unsplit

    def tok_ngrams(pattern, list_of_toks, concordancing = False, split_contractions = True):
        from collections import Counter
        import re
        ngrams = Counter()
        result = []
        # if it's not a compiled regex
        list_of_toks = [x for x in list_of_toks if re.search(regex_nonword_filter, x)]
        if pattern.lower() == 'any':
            pattern = r'.*'

        if not split_contractions:
            list_of_toks = unsplitter(list_of_toks)
            
            #list_of_toks = [x for x in list_of_toks if "'" not in x]
        for index, w in enumerate(list_of_toks):
            try:
                the_gram = [list_of_toks[index+x] for x in range(gramsize)]
                if not any(re.search(pattern, x) for x in the_gram):
                    continue
                ngrams[' '.join(the_gram)] += 1
            except IndexError:
                pass

        # turn counter into list of results
        for k, v in ngrams.items():
            if v > 1:
                for i in range(v):
                    result.append(k)
        if countmode:
            return(len(result))
        else:
            return result

    def compiler(pattern):
        """compile regex or fail gracefully"""
        import re
        try:
            if case_sensitive:
                comped = re.compile(pattern)
            else:
                comped = re.compile(pattern, re.IGNORECASE)
            return comped
        except:
            import traceback
            import sys
            from time import localtime, strftime
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            if root:
                return 'Bad query'
            else:
                raise ValueError('%s: Query %s' % (thetime, error_message))

    def tok_by_reg(pattern, list_of_toks, concordancing = False, **kwargs):
        """search for regex in plaintext corpora"""
        import re
        comped = compiler(pattern)
        if comped == 'Bad query':
            return 'Bad query'
        if not concordancing:
            matches = [m for m in list_of_toks if re.search(comped, m)]
        else:
            matches = []
            for index, token in enumerate(list_of_toks):
                if re.search(comped, token):
                    match = [' '.join([t for t in unsplitter(list_of_toks[:index])])[-140:]]
                    match.append(re.search(comped, token).group(0))
                    match.append(' '.join([t for t in unsplitter(list_of_toks[index + 1:])])[:140])
                    matches.append(match)
        if countmode:
            return(len(matches))
        else:
            return matches

    def plaintext_regex_search(pattern, plaintext_data, concordancing = False, **kwargs):
        """search for regex in plaintext corpora

        it searches over lines, so the user needs to be careful.
        """
        import re
        if concordancing:
            pattern = r'(.{,140})\b(' + pattern + r')\b(.{,140})'
        compiled_pattern = compiler(pattern)
        if compiled_pattern == 'Bad query':
            return 'Bad query'
        matches = re.findall(compiled_pattern, plaintext_data)
        if concordancing:
            matches = [list(m) for m in matches]
        if not concordancing:
            for index, i in enumerate(matches):
                if type(i) == tuple:
                    matches[index] = i[0]
        if countmode:
            return(len(matches))
        else:
            return matches

    def correct_spelling(a_string):
        if not spelling:
            return a_string
        from dictionaries.word_transforms import usa_convert
        if spelling.lower() == 'uk':
            usa_convert = {v: k for k, v in usa_convert.items()}
        spell_out = []
        bits = a_string.split('/')
        for index, i in enumerate(bits):
            converted = usa_convert.get(i.lower(), i)
            if i.islower() or preserve_case is False:
                converted = converted.lower()
            elif i.isupper() and preserve_case:
                converted = converted.upper()
            elif i.istitle() and preserve_case:
                converted = converted.title()
            bits[index] = converted
        r = '/'.join(bits)
        return r

    def plaintext_simple_search(pattern, plaintext_data, concordancing = False, **kwargs):
        """search for tokens in plaintext corpora"""
        import re
        result = []
        if type(pattern) == str:
            pattern = [pattern]
        for p in pattern:
            if concordancing:
                pat = r'(.{0,140})\b(' + re.escape(p) + r')\b(.{0,140})'
            pat = compiler(pat)
            if pat == 'Bad query':
                return 'Bad query'
            matches = re.findall(pat, plaintext_data)
            if concordancing:
                matches = [list(m) for m in matches]
                for i in matches:
                    result.append(i)
            else:   
                for m in range(len(matches)):
                    result.append(p)
        return result

    # do multiprocessing if need be
    im, corpus, search, query, just_speakers = is_multiquery(corpus, search, query, just_speakers)
    
    locs['search'] = search
    locs['query'] = query
    locs['just_speakers'] = just_speakers
    locs['corpus'] = corpus
    locs['multiprocess'] = multiprocess

    if im:
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)

    datatype = corpus.datatype
    singlefile = corpus.singlefile

    # store all results in here
    results = {}
    # check if just counting
    countmode = 'c' in show
    # where we are at in interrogation
    current_iter = 0

    # multiprocessing progress bar
    denom = kwargs.get('denominator', 1)
    startnum = kwargs.get('startnum', 0)

    ############################################
    # Determine the search function to be used #
    ############################################
    
    # simple tregex is tregex over whole dirs
    simple_tregex_mode = False
    statsmode = False
    if not just_speakers and 't' in search.keys():
        simple_tregex_mode = True
    else:
        if corpus.datatype == 'plaintext':
            if search.get('n'):
                raise NotImplementedError('Use a tokenised corpus for n-gramming.')
                #searcher = plaintext_ngram
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
                if type(search.get('w')) == list:
                    searcher = tok_by_list
                optiontext = 'Searching tokens'
        only_parse = ['r', 'd', 'g', 'dl', 'gl', 'df', 'gf', 'dp', 'gp', 'f']
        if corpus.datatype != 'parse' and any(i in only_parse for i in search.keys()):
            raise ValueError('Need parsed corpus to search with "%s" option(s).' % ', '.join([i for i in search.keys() if i in only_parse]))

        elif corpus.datatype == 'parse':
            if search.get('t'):
                searcher = slow_tregex
            elif search.get('s'):
                searcher = get_stats
                statsmode = True
                optiontext = 'General statistics'
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
        query = search.get('t')

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
            if type(search['t']) == list:
                search['t'] = r'__ < (/%s/ !< __)' % as_regex(search['t'], boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if search['t'] == 'any':
                search['t'] = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 't' in show:
            translated_option = 'o'
            if type(search['t']) == list:
                search['t'] = r'__ < (/%s/ !< __)' % as_regex(search['t'], boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if search['t'] == 'any':
                search['t'] = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 'w' in show:
            translated_option = 't'
            if type(search['t']) == list:
                search['t'] = r'/%s/ !< __' % as_regex(search['t'], boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if search['t'] == 'any':
                search['t'] = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'c' in show:
            count_results = {}
            only_count = True
            translated_option = 'C'
            if type(search['t']) == list:
                search['t'] = r'/%s/ !< __'  % as_regex(search['t'], boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if search['t'] == 'any':
                search['t'] = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'l' in show:
            translated_option = 't'
            if type(search['t']) == list:
                search['t'] = r'/%s/ !< __' % as_regex(search['t'], boundaries = 'line', 
                                            case_sensitive = case_sensitive)
            if search['t'] == 'any':
                search['t'] = r'/.?[A-Za-z0-9].?/ !< __'

        query = search['t']

    ############################################
    # Make iterable for corpus/subcorpus/file  #
    ############################################

    if corpus.singlefile:
        to_iterate_over = {(corpus.name, corpus.path): [corpus]}
    elif not corpus.subcorpora:
        to_iterate_over = {(corpus.name, corpus.path): corpus.files}
    else:
        to_iterate_over = {}
        for k, v in sorted(corpus.structure.items()):
            to_iterate_over[(k.name, k.path)] = v
    if files_as_subcorpora:
        to_iterate_over = {}
        for f in corpus.files:
            to_iterate_over[(f.name, f.path)] = [f]

    ############################################
    #           Print welcome message          #
    ############################################

    if conc:
        message = 'Concordancing'
    else:
        message = 'Interrogating'
    if kwargs.get('printstatus', True):
        thetime = strftime("%H:%M:%S", localtime())

        sformat = '\n                 '.join(['%s: %s' % (k.rjust(3), v) for k, v in search.items()])
        if search == {'s': r'.*'}:
            sformat = 'features'
        welcome = '\n%s: %s %s ...\n          %s\n          Query: %s\n' % \
                  (thetime, message, corpus.name, optiontext, sformat)
        print welcome

    ############################################
    #           Make progress bar              #
    ############################################

    if simple_tregex_mode:
        total_files = len(to_iterate_over.keys())
    else:
        if search.get('s'):
            total_files = sum([len(x) for x in to_iterate_over.values()]) * 12
        else:
            total_files = sum([len(x) for x in to_iterate_over.values()])

    par_args = {'printstatus': kwargs.get('printstatus', True),
                'root': root, 
                'note': note,
                'length': total_files}

    term = None
    if kwargs.get('paralleling', None) is not None:
        from blessings import Terminal
        term = Terminal()
        par_args['terminal'] = term
        par_args['linenum'] = kwargs.get('paralleling')

    outn = kwargs.get('outname', '')
    if outn:
        outn = outn + ': '
    tstr = '%s%d/%d' % (outn, current_iter, total_files)
    p = animator(None, None, init = True, tot_string = tstr, **par_args)
    tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
    animator(p, current_iter, tstr, **par_args)

    ############################################
    # Iterate over data, doing interrogations  #
    ############################################

    for (subcorpus_name, subcorpus_path), files in sorted(to_iterate_over.items()):

        if countmode or conc:
            results[subcorpus_name] = []
        else:
            results[subcorpus_name] = Counter()
        
        # tregex over subcorpora, not files
        if simple_tregex_mode:

            op = ['-o', '-' + translated_option]                
            result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = preserve_case)
            
            if countmode:
                results[subcorpus_name].append(result)
                continue

            result = Counter(format_tregex(result))

            if conc:
                op.append('-w')
                whole_result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = preserve_case)
                
                if not only_format_match:
                    whole_result = format_tregex(whole_result)

                result = make_conc_lines_from_whole_mid(whole_result, result, speakr = False)

                if spelling:
                    for index, line in enumerate(result):
                        result[index] = [correct_spelling(b) for b in line]
            
            results[subcorpus_name] += result

            current_iter += 1
            if kwargs.get('paralleling', None) is not None:
                tstr = '%s%d/%d' % (outn, current_iter + 2, total_files)
            else:
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
            animator(p, current_iter, tstr, **par_args)

        # dependencies, plaintext, tokens or slow_tregex
        else:
            for f in files:

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
                        
                        if res == 'Bad query':
                            return 'Bad query'

                        if searcher == slow_tregex and not countmode:
                            res = format_tregex(res)

                elif corpus.datatype == 'tokens':
                    import pickle
                    with open(f.path, "rb") as fo:
                        data = pickle.load(fo)
                    res = searcher(search.values()[0], data, split_contractions = split_contractions, 
                        concordancing = conc)
                    if conc:
                        for index, line in enumerate(res):
                            line.insert(0, '')

                elif corpus.datatype == 'plaintext':
                    with open(f.path, 'rb') as data:
                        data = data.read()
                        data = unicode(data, errors = 'ignore')
                        res = searcher(search.values()[0], data, 
                            concordancing = conc)
                        if conc:
                            for index, line in enumerate(res):
                                line.insert(0, '')

                if countmode:
                    results[subcorpus_name] += res
                    continue
            
                # add filename and do lowercasing for conc
                if conc:
                    for index, line in enumerate(res):
                        line.insert(0, f.name)
                        if not preserve_case:
                            line = [b.lower() for b in line]
                        if spelling:
                            line = [correct_spelling(b) for b in line]
                        results[subcorpus_name] += [line]

                # do lowercasing and spelling
                else:
                    if not preserve_case:
                        res = [r.lower() for r in res]
                    if spelling:
                        res = [correct_spelling(r) for r in res]
                    results[subcorpus_name] += Counter(res)

                if not statsmode:
                    current_iter += 1
                    if kwargs.get('paralleling', None) is not None:
                        tstr = '%s%d/%d' % (outn, current_iter + 2, total_files)
                    else:
                        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)

    # delete temp file if there
    import os
    if os.path.isfile('tmp.txt'):
        os.remove('tmp.txt')

    ############################################
    #     Get concordances into DataFrame      #
    ############################################

    if conc:
        all_conc_lines = []
        for sc_name, resu in sorted(results.items()):

            if only_unique:
                unique_results = uniquify(resu)
            else:
                unique_results = resu
            #make into series
            pindex = 'c f s l m r'.encode('utf-8').split()
            for fname, spkr, start, word, end in unique_results:
                spkr = unicode(spkr, errors = 'ignore')
                fname = os.path.basename(fname)

                # the use of ascii here makes sure the string formats ok, but will also screw over
                # anyone doing non-english work. so, change to utf-8, then fix errors as they come
                # in the corpkit-gui "add_conc_lines_to_window" function
                all_conc_lines.append(Series([sc_name.encode('ascii', errors = 'ignore'),
                                     fname.encode('ascii', errors = 'ignore'), \
                                     spkr.encode('ascii', errors = 'ignore'), \
                                     start.encode('ascii', errors = 'ignore'), \
                                     word.encode('ascii', errors = 'ignore'), \
                                     end.encode('ascii', errors = 'ignore')], \
                                     index = pindex))

        # randomise results...
        if random:
            from random import shuffle
            shuffle(all_conc_lines)

        df = pd.concat(all_conc_lines, axis = 1).T

        # not doing anything yet --- this is for multimodal concordancing
        add_links = False
        if not add_links:
            df.columns = ['c', 'f', 's', 'l', 'm', 'r']
        else:
            df.columns = ['c', 'f', 's', 'l', 'm', 'r', 'link']

        if all(x == '' for x in list(df['s'].values)):
            df.drop('s', axis = 1, inplace = True)

        if kwargs.get('note'):
            kwargs['note'].progvar.set(100)

        if kwargs.get('printstatus', True):
            thetime = strftime("%H:%M:%S", localtime())
            finalstring = '\n\n%s: Concordancing finished! %d matches.\n' % (thetime, len(df.index))
            print finalstring

        from corpkit.interrogation import Concordance
        output = Concordance(df)
        output.query = locs
        if quicksave:
            interro.save()
        return output 

    ############################################
    #     Get interrogation into DataFrame     #
    ############################################

    else:
        if countmode:
            df = Series({k: sum(v) for k, v in sorted(results.items())})
            tot = df.sum()
        else:
            the_big_dict = {}
            unique_results = set([item for sublist in results.values() for item in sublist])
            for word in unique_results:
                the_big_dict[word] = [subcorp_result[word] for subcorp_result in sorted(results.values())]
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


        # sort by total
        if type(df) == pd.core.frame.DataFrame:
            if not df.empty:   
                df.ix['Total-tmp'] = df.sum()
                the_tot = df.ix['Total-tmp']
                df = df[the_tot.argsort()[::-1]]
                df = df.drop('Total-tmp', axis = 0)

        # format final string
        if kwargs.get('printstatus', True):
            thetime = strftime("%H:%M:%S", localtime())
            finalstring = '\n\n%s: Interrogation finished!' % thetime
            if countmode:
                finalstring += ' %d matches.' % tot
            else:
                finalstring += ' %d unique results, %d total occurrences.' % (numentries, total_total)
            print finalstring

        interro = Interrogation(results = df, totals = tot, query = locs)
        
        if quicksave:
            interro.save()
        
        return interro