#interrogator with classes:

def interro(corpus, 
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
            **kwargs):
    
    # store kwargs
    locs = locals()

    from corpkit.interrogation import Interrogation
    from corpkit.process import tregex_engine
    from pandas import DataFrame, Series
    from collections import Counter
    from corpkit.other import as_regex
    from corpkit.process import get_deps

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')

    # convert path to corpus object
    if type(corpus) == str:
        from corpkit.Corpus import Corpus
        corpus = Corpus(corpus)

    # determine if data is parsed/single file
    from corpkit.process import determine_datatype
    datatype, singlefile = determine_datatype(corpus.path)

    # figure out how the user has entered the query and normalise
    from corpkit.process import searchfixer
    search, search_iterable = searchfixer(search, query, datatype)

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
        import bs4
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

    # do multiprocessing if need be
    im, corpus, search, query, just_speakers = is_multiquery(corpus, search, query, just_speakers)
    if im:
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)

    # check if just counting
    countmode = 'c' in search.keys()

    # store all results in here
    results = {}

    ############################################
    # Determine the search function to be used #
    ############################################
    
    # simple tregex is tregex over whole dirs
    simple_tregex_mode = False
    if not just_speakers and 't' in search.keys():
        searcher = tregex_engine
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
                    searcher = plaintext_regex
                else:
                    searcher = plaintext_simple
                optiontext = 'Searching plaintext'

        elif corpus.datatype == 'tokens':
            if search.get('n'):
                searcher = tokens_ngram
                optiontext = 'n-grams via tokens'
            elif search.get('w'):
                if kwargs.get('regex', True):
                    searcher = tokens_regex
                else:
                    searcher = tokens_simple
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
        optiontext = 'Searching parse trees'
        if 'p' in show:
            translated_option = 'u'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 't' in show:
            translated_option = 'o'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 'w' in show:
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'c' in show:
            count_results = {}
            only_count = True
            translated_option = 'C'
            if type(query) == list:
                query = r'/%s/ !< __'  % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'l' in show:
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'

    ############################################
    # Make iterable for corpus/subcorpus/file  #
    ############################################

    if corpus.singlefile:
        to_iterate_over = {(corpus.name, corpus.path): [corpus.path]}
    elif not corpus.subcorpora:
        to_iterate_over = {(corpus.name, corpus.path): corpus.files}
    else:
        to_iterate_over = {}
        for k, v in corpus.structure.items():
            to_iterate_over[(k.name, k.path)] = v

    ############################################
    # Iterate over data, doing interrogations  #
    ############################################

    for (subcorpus_name, subcorpus_path), files in sorted(to_iterate_over.items()):
        results[subcorpus_name] = []
        
        # tregex over subcorpus
        if simple_tregex_mode:
            op = ['-o', '-' + translated_option]
            result = tregex_engine(query = search['t'], options = op, 
                                   corpus = subcorpus_path, root = root, preserve_case = True)
        # dependencies, plaintext, tokens or slow_tregex
        else:
            for f in files:
                if corpus.datatype == 'parse':
                    if singlefile:
                        pat = f
                    else:
                        pat = f.path
                    with open(pat, 'r') as data:
                        data = data.read()
                        from corenlp_xml.document import Document
                        try:
                            corenlp_xml = Document(data)
                        except:
                            print 'Could not read file: %s' % f.path
                            continue
                        #corenlp_xml = Beautifulcorenlp_xml(data, parse_only=justsents)  
                        if just_speakers:  
                            sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                            if not sents:
                                continue
                            #sents = [s for s in corenlp_xml.find_all('sentence') \
                            #if s.speakername.text.strip() in just_speakers]
                        else:
                            sents = corenlp_xml.sentences

                        result = searcher(sents, search = search, show = show,
                            dep_type = dep_type,
                            exclude = exclude,
                            excludemode = excludemode,
                            searchmode = searchmode,
                            lemmatise = False,
                            case_sensitive = case_sensitive)
                elif corpus.datatype == 'tokens':
                    pass

                elif corpus.datatype == 'plaintext':
                    pass
        if result:
            for r in result:
                if not preserve_case:
                    r = r.lower()
                results[subcorpus_name].append(r)
        elif 'v' in search.keys():
            results[subcorpus_name] = statsmode_results

        # turn data into counter object
        if not countmode:
            results[subcorpus_name] = Counter(results[subcorpus_name])

    ############################################
    #   Tally everything into big DataFrame    #
    ############################################

    if countmode:
        df = pd.Series([d[0] for d in results.values()], results.keys())
        tot = df.sum()
    else:
        the_big_dict = {}
        unique_results = set([item for sublist in results.values() for item in sublist])
        for word in unique_results:
            the_big_dict[word] = [subcorp_result[word] for subcorp_result in results.values()]
        # turn master dict into dataframe, sorted
        df = DataFrame(the_big_dict, index = sorted(results.keys()))

    ############################################
    # Format, output as Interrogation object   #
    ############################################

    if not countmode:
        tot = df.sum(axis = 1)
        if not corpus.subcorpora or singlefile:
            if not kwargs.get('df1_always_df'):
                df = Series(df.ix[0])
                df.sort(ascending = False)
                tot = df.sum()
            else:
                tot = df.sum().sum()

    return Interrogation(results = df, totals = tot, query = locs)