#!/usr/bin/python

from __future__ import print_function

def interrogator(corpus, 
            search, 
            query = 'any', 
            show = 'w',
            exclude = False,
            excludemode = 'any',
            searchmode = 'all',
            dep_type = 'collapsed-ccprocessed-dependencies',
            case_sensitive = False,
            save = False,
            just_speakers = False,
            preserve_case = False,
            lemmatag = False,
            files_as_subcorpora = False,
            only_unique = False,
            random = False,
            only_format_match = False,
            multiprocess = False,
            spelling = False,
            regex_nonword_filter = r'[A-Za-z0-9:_]',
            gramsize = 2,
            split_contractions = False,
            do_concordancing = False,
            maxconc = 9999,
            **kwargs):
    """interrogate corpus, corpora, subcorpus and file objects

    see corpkit.interrogation.interrogate() for docstring"""

    only_conc = False
    no_conc = False
    if do_concordancing is False:
        no_conc = True
    if type(do_concordancing) == str and do_concordancing.lower() == 'only':
        only_conc = True
        no_conc = False

    # iteratively count conc lines
    numconc = 0

    # store kwargs
    locs = locals()
    
    if kwargs:
        for k, v in kwargs.items():
            locs[k] = v
        locs.pop('kwargs', None)

    import codecs
    import signal
    from time import localtime, strftime
    from collections import Counter

    import corenlp_xml
    import pandas as pd
    from pandas import DataFrame, Series

    import corpkit
    from interrogation import Interrogation, Interrodict
    from corpus import Datalist, Corpora, Corpus, File, Subcorpus
    from process import tregex_engine, get_deps
    from other import as_regex
    from textprogressbar import TextProgressBar
    from process import animator
    from dictionaries.word_transforms import wordlist, taglemma

    original_sigint = signal.getsignal(signal.SIGINT)

    if kwargs.get('paralleling', None) is None:
        original_sigint = signal.getsignal(signal.SIGINT)
        
        def signal_handler(signal, frame):
            """pause on ctrl+c, rather than just stop loop"""   
            import signal
            import sys
            from time import localtime, strftime
            signal.signal(signal.SIGINT, original_sigint)
            thetime = strftime("%H:%M:%S", localtime())
            try:
                sel = raw_input('\n\n%s: Paused. Press any key to resume, or ctrl+c to quit.\n' % thetime)
            except NameError:
                sel = input('\n\n%s: Paused. Press any key to resume, or ctrl+c to quit.\n' % thetime)
            time = strftime("%H:%M:%S", localtime())
            print('%s: Interrogation resumed.\n' % time)
            signal.signal(signal.SIGINT, signal_handler)

        signal.signal(signal.SIGINT, signal_handler)

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')

    # wipe non essential class attributes to not bloat query attrib
    if corpus.__class__ == Corpus:
        import copy
        corpus = copy.copy(corpus)
        for k, v in corpus.__dict__.items():
            if type(v) in [Interrogation, Interrodict]:
                corpus.__dict__.pop(k, None)

    # convert path to corpus object
    if corpus.__class__ not in [Corpus, Corpora, Subcorpus, File, Datalist]:
        if not multiprocess and not kwargs.get('outname'):
            corpus = Corpus(corpus, print_info = False)

    # figure out how the user has entered the query and normalise
    from process import searchfixer
    search = searchfixer(search, query)

    # lowercase anything in show
    if type(show) == list:
        show = [i.lower() for i in show]
    elif type(show) == str:
        show = show.lower()
        show = [show]
    
    # instantiate lemmatiser if need be
    if 'l' in show and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    def is_multiquery(corpus, search, query, just_speakers):
        """determine if multiprocessing is needed
        do some retyping if need be as well"""
        im = False
        from collections import OrderedDict
        #if hasattr(corpus, '__iter__'):
        #    im = True
        # so we can do search = 't', query = ['NP', 'VP']:
        if type(query) == list:
            if query != list(search.values())[0] or len(list(search.keys())) > 1:
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
            if all(type(i) == dict for i in list(search.values())):
                im = True
        return im, corpus, search, query, just_speakers

    def slow_tregex(sents, **dummy_args):
        """do the speaker-specific version of tregex queries"""
        speakr = dummy_args.get('speaker', False)
        import os
        from process import tregex_engine
        # first, put the relevant trees into temp file
        if kwargs.get('outname'):
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        to_write = '\n'.join([sent._parse_string.strip() for sent in sents \
                              if sent.parse_string is not None])
        to_write.encode('utf-8', errors = 'ignore')
        with open(to_open, "w") as fo:
            encd = to_write.encode('utf-8', errors = 'ignore') + '\n'
            fo.write(encd)
        q = list(search.values())[0]
        ops = ['-o', '-%s' % translated_option]
        concs = []
        res = tregex_engine(query = q, 
                            options = ops, 
                            corpus = to_open,
                            root = root,
                            preserve_case = True)
        if not no_conc:
            ops += ['-w', '-f']
            whole_res = tregex_engine(query = q, 
                            options = ops, 
                            corpus = to_open,
                            root = root,
                            preserve_case = True) 

            res = format_tregex(res)
            whole_res = format_tregex(whole_res, whole = True)
            concs = make_conc_lines_from_whole_mid(whole_res, res, speakr)

        if root:
            root.update()
        try:
            os.remove(to_open)
        except OSError:
            pass
        if countmode:
            return(len(res))
        else:
            return res, concs

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
        from other import as_regex
        tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                     'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                     'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Open class': r'/^(NN|JJ|VB|RB)/ < __',
                     'Closed class': r'__ !< __ !> /^(NN|JJ|VB|RB)/',
                     'Clauses': r'/^S/ < __',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Mental processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.mental, boundaries = 'w'),
                     'Verbal processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.verbal, boundaries = 'w'),
                     'Relational processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.relational, boundaries = 'w'),
                     'Verbless clause': r'/^S/ !<< /^VB.?/'}

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
        try:
            os.remove(to_open)
        except OSError:
            pass
        return statsmode_results, []

    def make_conc_lines_from_whole_mid(wholes, middle_column_result, 
                                       speakr = False):
        import re, os
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
                word = taglemma.get(word.lower(), 'Other')
            else:
                if word in wordlist:
                    word = wordlist[word]
                else:
                    word = lmtzr.lemmatize(word, tag)
            output.append(word)
        return output

    def gettag(query, lemmatag = False):
        """
        Find tag for WordNet lemmatisation
        """
        if lemmatag:
            return lemmatag

        tagdict = {'N': 'n',
                   'A': 'a',
                   'V': 'v',
                   'A': 'r',
                   'None': False,
                   '': False,
                   'Off': False}

        qr = query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', '')
        firstletter = next(c for c in query if c.isalpha())
        return tagdict.get(firstletter.upper(), 'n')

    def format_tregex(results, whole = False):
        """format tregex by show list"""
        if countmode:
            return results
        import re
        done = []
        
        if whole:
            fnames = [x for x, y in results]
            results = [y for x, y in results]

        if 'l' in show or 'pl' in show:
            lemmata = lemmatiser(results, gettag(search.get('t'), lemmatag))
        else:
            lemmata = [None for i in results]
        for word, lemma in zip(results, lemmata):
            bits = []
            if exclude and exclude.get('w'):
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('w'), word):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('l'), lemma):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('p'), word):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('pl'), lemma):
                        continue
            if exclude and excludemode == 'all':
                num_to_cause_exclude = len(list(exclude.keys()))
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

        if whole:
            done = zip(fnames, done)

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
        for k, v in list(ngrams.items()):
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
            print('%s: Query %s' % (thetime, error_message))
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
            usa_convert = {v: k for k, v in list(usa_convert.items())}
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

    if hasattr(corpus, '__iter__') and im:
        corpus = Corpus(corpus)
    if hasattr(corpus, '__iter__') and not im:
        im = True
    if corpus.__class__ == Corpora:
        im = True

    if not im and multiprocess:
        im = True
        corpus = corpus[:]
    # if it's already been through pmultiquery, don't do it again
    
    locs['search'] = search
    locs['query'] = query
    locs['just_speakers'] = just_speakers
    locs['corpus'] = corpus
    locs['multiprocess'] = multiprocess
    locs['print_info'] = kwargs.get('printstatus', True)

    if im:
        signal.signal(signal.SIGINT, original_sigint)
        from multiprocess import pmultiquery
        return pmultiquery(**locs)

    cname = corpus.name
    subcorpora = corpus.subcorpora
    
    try:
        datatype = corpus.datatype
        singlefile = corpus.singlefile
    except AttributeError:
        datatype = 'parse'
        singlefile = False
        
    # store all results in here
    results = {}
    count_results = {}
    conc_results = {}
    # check if just counting
    countmode = 'c' in show
    if countmode:
        no_conc = True
        only_conc = False
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
    if not just_speakers and 't' in list(search.keys()):
        simple_tregex_mode = True
    else:
        if datatype == 'plaintext':
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

        elif datatype == 'tokens':
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
        only_parse = ['r', 'd', 'g', 'dl', 'gl', 'df', 'gf', 'dp', 'gp', 'f', 'd2', 'd2f', 'd2p', 'd2l']
        if datatype != 'parse' and any(i in only_parse for i in list(search.keys())):
            raise ValueError('Need parsed corpus to search with "%s" option(s).' % ', '.join([i for i in list(search.keys()) if i in only_parse]))

        elif datatype == 'parse':
            if search.get('t'):
                searcher = slow_tregex
            elif search.get('s'):
                searcher = get_stats
                statsmode = True
                optiontext = 'General statistics'
                global numdone
                numdone = 0
                no_conc = True
                only_conc = False
                do_concordancing = False
            else:
                from depsearch import dep_searcher
                searcher = dep_searcher
                optiontext = 'Dependency querying'

    ############################################
    #      Set some Tregex-related values      #
    ############################################

    if search.get('t'):
        translated_option = 't'
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

    if corpus.__class__ == Datalist:
        to_iterate_over = {}
        # it could be files or subcorpus objects
        if corpus[0].level == 's':
            for subcorpus in corpus:
                to_iterate_over[(subcorpus.name, subcorpus.path)] = subcorpus.files
        elif corpus[0].level == 'f':
            for fl in corpus:
                to_iterate_over[(fl.name, fl.path)] = [fl]
    elif singlefile:
        to_iterate_over = {(corpus.name, corpus.path): [corpus]}
    elif not subcorpora:
        if files_as_subcorpora:
            to_iterate_over = {}
            for fl in corpus.files:
                to_iterate_over[(fl.name, fl.path)] = [fl]
        else:
            to_iterate_over = {(corpus.name, corpus.path): corpus.files}
    else:
        to_iterate_over = {}
        if files_as_subcorpora:
            for f in corpus.files:
                to_iterate_over[(f.name, f.path)] = [f]
        else:
            if corpus[0].level == 's':
                for subcorpus in corpus:
                    to_iterate_over[(subcorpus.name, subcorpus.path)] = subcorpus.files
            elif corpus[0].level == 'f':
                for fl in corpus:
                    to_iterate_over[(fl.name, fl.path)] = [fl]
            else:
                for subcorpus in subcorpora:
                    to_iterate_over[(subcorpus.name, subcorpus.path)] = subcorpus.files
        #for k, v in sorted(corpus.structure.items(), key=lambda obj: obj[0].name):
        #    to_iterate_over[(k.name, k.path)] = v


    ############################################
    #           Print welcome message          #
    ############################################

    if no_conc:
        message = 'Interrogating'
    else:
        message = 'Interrogating and concordancing'
    if kwargs.get('printstatus', True):
        thetime = strftime("%H:%M:%S", localtime())

        sformat = '\n                 '.join(['%s: %s' % (k.rjust(3), v) for k, v in list(search.items())])
        if search == {'s': r'.*'}:
            sformat = 'features'
        welcome = '\n%s: %s %s ...\n          %s\n          Query: %s\n          %s corpus ... \n' % \
                  (thetime, message, cname, optiontext, sformat, message)
        print(welcome)

    ############################################
    #           Make progress bar              #
    ############################################

    if simple_tregex_mode:
        total_files = len(list(to_iterate_over.keys()))
    else:
        if search.get('s'):
            total_files = sum([len(x) for x in list(to_iterate_over.values())]) * 13
        else:
            total_files = sum([len(x) for x in list(to_iterate_over.values())])

    par_args = {'printstatus': kwargs.get('printstatus', True),
                'root': root, 
                'note': note,
                'length': total_files,
                'startnum': kwargs.get('startnum'),
                'denom': kwargs.get('denominator', 1)}

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

        conc_results[subcorpus_name] = []
        count_results[subcorpus_name] = []
        results[subcorpus_name] = Counter()
        
        # tregex over subcorpora, not files
        if simple_tregex_mode:

            op = ['-o', '-' + translated_option]                
            result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = preserve_case)

            if not countmode:
                result = format_tregex(result)

            if not no_conc:
                op += ['-w', '-f']
                whole_result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = preserve_case)
                
                if not only_format_match:
                    whole_result = format_tregex(whole_result, whole = True)

                conc_result = make_conc_lines_from_whole_mid(whole_result, result, speakr = False)

            if countmode:
                count_results[subcorpus_name] += [result]            
            else:
                result = Counter(result)
                results[subcorpus_name] += result
                if not no_conc:
                    for lin in conc_result:
                        if numconc < maxconc or not maxconc:
                            conc_results[subcorpus_name].append(lin)
                        numconc += 1

            current_iter += 1
            if kwargs.get('paralleling', None) is not None:
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
            else:
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)

            animator(p, current_iter, tstr, **par_args)

        # dependencies, plaintext, tokens or slow_tregex
        else:
            for f in files:
                slow_treg_speaker_guess = kwargs.get('outname', False)
                if datatype == 'parse':
                    with open(f.path, 'r') as data:
                        data = data.read()
                        from corenlp_xml.document import Document
                        try:
                            corenlp_xml = Document(data)
                        except:
                            print('Could not read file: %s' % f.path)
                            continue
                        if just_speakers:  
                            sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                            if len(just_speakers) == 1:
                                slow_treg_speaker_guess = just_speakers[0]
                            if not sents:
                                continue
                        else:
                            sents = corenlp_xml.sentences

                        res, conc_res = searcher(sents, search = search, show = show,
                            dep_type = dep_type,
                            exclude = exclude,
                            excludemode = excludemode,
                            searchmode = searchmode,
                            lemmatise = False,
                            case_sensitive = case_sensitive,
                            do_concordancing = do_concordancing,
                            only_format_match = only_format_match,
                            speaker = slow_treg_speaker_guess)
                        
                        if res == 'Bad query':
                            return 'Bad query'

                elif datatype == 'tokens':
                    import pickle
                    with codecs.open(f.path, "rb") as fo:
                        data = pickle.load(fo)
                    if not only_conc:
                        res = searcher(list(search.values())[0], data, split_contractions = split_contractions, 
                        concordancing = False)
                    if not no_conc:
                        conc_res = searcher(list(search.values())[0], data, split_contractions = split_contractions, 
                        concordancing = True)
                    if not no_conc:
                        for index, line in enumerate(conc_res):
                            line.insert(0, '')

                elif datatype == 'plaintext':
                    with codecs.open(f.path, 'rb', encoding = 'utf-8') as data:
                        data = data.read()
                        if not only_conc:
                            res = searcher(list(search.values())[0], data, 
                            concordancing = False)
                        if not no_conc:
                            conc_res = searcher(list(search.values())[0], data, 
                            concordancing = True)
                        if not no_conc:
                            for index, line in enumerate(conc_res):
                                line.insert(0, '')

                if countmode:
                    count_results[subcorpus_name] += [res]
                else:
                    # add filename and do lowercasing for conc
                    if not no_conc:
                        for index, line in enumerate(conc_res):
                            if searcher != slow_tregex:
                                line.insert(0, f.name)
                            else:
                                line[0] = f.name
                            if not preserve_case:
                                line[3:] = [x.lower() for x in line[3:]]
                            if spelling:
                                line = [correct_spelling(b) for b in line]
                            if numconc < maxconc or not maxconc:
                                conc_results[subcorpus_name].append(line)
                                numconc += 1

                    # do lowercasing and spelling
                    if not only_conc:
                        if not preserve_case:
                            if not statsmode:
                                res = [i.lower() for i in res]
                        if spelling:
                            if not statsmode:
                                res = [correct_spelling(r) for r in res]
                        #if not statsmode:
                        results[subcorpus_name] += Counter(res)
                        #else:
                        #results[subcorpus_name] += res

                if not statsmode:
                    current_iter += 1
                    if kwargs.get('paralleling', None) is not None:
                        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
                    else:
                        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
                    animator(p, current_iter, tstr, **par_args)

    # delete temp file if there
    import os
    if os.path.isfile('tmp.txt'):
        os.remove('tmp.txt')

    ############################################
    #     Get concordances into DataFrame      #
    ############################################

    if not no_conc:
        all_conc_lines = []
        for sc_name, resu in sorted(conc_results.items()):
            if only_unique:
                unique_results = uniquify(resu)
            else:
                unique_results = resu
            #make into series
            pindex = 'c f s l m r'.encode('utf-8').split()
            for fname, spkr, start, word, end in unique_results:
                #spkr = str(spkr, errors = 'ignore')
                fname = os.path.basename(fname)
                all_conc_lines.append(Series([sc_name,
                                     fname, \
                                     spkr, \
                                     start, \
                                     word, \
                                     end], \
                                     index = pindex))

        # randomise results...
        if random:
            from random import shuffle
            shuffle(all_conc_lines)

        conc_df = pd.concat(all_conc_lines, axis = 1).T

        # not doing anything yet --- this is for multimodal concordancing
        add_links = False
        if not add_links:
            conc_df.columns = ['c', 'f', 's', 'l', 'm', 'r']
        else:
            conc_df.columns = ['c', 'f', 's', 'l', 'm', 'r', 'link']

        if all(x == '' for x in list(conc_df['s'].values)):
            conc_df.drop('s', axis = 1, inplace = True)

        #if kwargs.get('note'):
        #    kwargs['note'].progvar.set(100)

        #if kwargs.get('printstatus', True):
        #    thetime = strftime("%H:%M:%S", localtime())
        #    finalstring = '\n\n%s: Concordancing finished! %d matches.\n' % (thetime, len(conc_df.index))
        #    print(finalstring)

        from interrogation import Concordance
        output = Concordance(conc_df)
        if only_conc:
            output.query = locs
            if save and not kwargs.get('outname'):
                output.save(save)

            if kwargs.get('printstatus', True):
                thetime = strftime("%H:%M:%S", localtime())
                finalstring = '\n\n%s: Concordancing finished! %d results.' % (thetime, len(conc_df))
                print(finalstring)
            signal.signal(signal.SIGINT, original_sigint)
            return output

        #output.query = locs

        #return output 

    ############################################
    #     Get interrogation into DataFrame     #
    ############################################

    if not only_conc:
        if countmode:
            df = Series({k: sum(v) for k, v in sorted(count_results.items())})
            tot = df.sum()
        else:
            the_big_dict = {}
            unique_results = set([item for sublist in list(results.values()) for item in sublist])
            for word in unique_results:
                the_big_dict[word] = [subcorp_result[word] for name, subcorp_result in sorted(results.items(), key=lambda x: x[0])]
            # turn master dict into dataframe, sorted
            df = DataFrame(the_big_dict, index = sorted(results.keys()))

            numentries = len(df.columns)
            tot = df.sum(axis = 1)
            total_total = df.sum().sum()

        ############################################
        # Format, output as Interrogation object   #
        ############################################

        if not countmode:
            if not subcorpora or singlefile:
                if not files_as_subcorpora:
                    if not kwargs.get('df1_always_df'):
                        df = Series(df.ix[0])
                        df.sort_values(ascending = False, inplace = True)
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
            print(finalstring)

        if not no_conc:
            interro = Interrogation(results = df, totals = tot, query = locs, concordance = output)
        else:
            interro = Interrogation(results = df, totals = tot, query = locs)

        if save and not kwargs.get('outname'):
            interro.save(save)
        signal.signal(signal.SIGINT, original_sigint)
        return interro
