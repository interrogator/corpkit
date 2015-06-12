
def interrogator(path, options, query, 
                lemmatise = False, 
                dictionary = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                function_filter = False,
                table_size = 50,
                plaintext = False,
                quicksave = False,
                add_to = False,
                **kwargs):
    
    """
    Interrogate a parsed corpus using Tregex queries, dependencies, or for
    keywords/ngrams

    Output: a named tuple, with 'branches':
        variable_name.query = a record of what query generated the results
        variable_name.results = a table of results, sorted by total freq
        variable_name.totals = a list of totals for each subcorpus (except when keywording)
        variable_name.table = a DataFrame showing top results in each subcorpus
        of top <table_size> results

    Parameters
    ----------

    path : str
        path to a corpus. If it contains subfolders, these will be treated
        as subcorpora. If not, the corpus will be treated as unstructured.
    
    options : (can type letter or word): 
        - Tregex output options:
            c/count: only *count*
            w/words: only *words*
            p/pos: only *pos* tag
            b/both: *both* words and tags
        - dependency options:
            n/number: get the index *number* of the governor
            f/funct: get the semantic *function*
            g/gov: get *governor* role and governor:
                /good/ might return amod:day
            d/dep: get dependent and its role:
                /day/ might return amod:sunny
        - plaintext:
            r/regex: search plain text with query as regex
        for keywords/ngrams, use 'words'
   
    query : str
        - a Tregex query (if using a Tregex option)
        - 'keywords' (use keywords() on each subcorpus)
        - 'ngrams' (use keywords() on each subcorpus)
        - A regex to match a token/tokens (if using a dependencies option)

    lemmatise : Boolean
        Do lemmatisation on results?
    lemmatag : False/'n'/'v'/'a'/'r'
        explicitly pass a pos to lemmatiser
    titlefilter : Boolean
        strip 'mr, 'the', 'dr.' etc. from results (turns 'phrases' on)
    spelling : False/'US'/UK
        convert all to U.S. English
    phrases : Boolean
        Use if your expected results are multiword and thus need tokenising
    dictionary : string
        The name of a dictionary made with dictmaker() for keywording.
        BNC included as default.
    dep_type : str
        the kind of Stanford CoreNLP dependency parses you want to use:
        - 'basic-dependencies'
        - 'collapsed-dependencies'
        - 'collapsed-ccprocessed-dependencies'
    function_filter : Bool/regex
        If you set this to a regex, for the 'g' and 'd' options, only words 
        whose function matches the regex will be kept, and the tag will not be printed

    Example 1: Tree querying
    --------
    from corpkit import interrogator, tally, plotter
    corpus = 'path/to/corpus'
    ion_nouns = interrogator(corpus, 'w', r'/NN.?/ < /(?i)ion\b'/)
    tally(ion_nouns.results, [0, 1, 2, 3, 4])
    plotter('Common -ion words', ion_nouns.results, fract_of = ion_nouns.totals)

    Output:

    ['0: election: 22 total occurrences.',
     '1: decision: 14 total occurrences.',
     '2: question: 10 total occurrences.',
     '3: nomination: 8 total occurrences.',
     '4: recession: 8 total occurrences.']

    <matplotlib figure>

    Example 2: Dependencies querying
    -----------------------
    risk_functions = interrogator(corpus, 'f', r'(?i)\brisk')
    print risk_functions.results[0]
    plotter('Functions of risk words', risk_functions.results, num_to_plot = 15)

    Output:

    ['pobj', [1989, 1], [2005, 52], [2006, 52], [u'Total', 105]]

    <matplotlib figure>

    """
    
    import os
    import re
    import signal
    import numpy
    import collections
    import warnings
    from collections import Counter
    from time import localtime, strftime
    try:
        import pandas as pd
        from pandas import read_csv, DataFrame, Series
        from StringIO import StringIO
        have_pandas = True
    except:
        have_pandas = False

    import nltk
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.tests import check_dit, check_pytex
    from corpkit.progressbar import ProgressBar
    from corpkit.other import tregex_engine
    import dictionaries
    from dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

    the_time_started = strftime("%Y-%m=%d %H:%M:%S")

    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()
    
    # check if we are in ipython
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
           
    have_python_tex = check_pytex()
    on_cloud = check_dit()

    regex_nonword_filter = re.compile("[A-Za-z0-9-\']")

    def signal_handler(signal, frame):
        """exit on ctrl+c, rather than just stop loop"""
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    def gettag(query):
        import re
        if lemmatag is False:
            tag = 'n' # same default as wordnet
            # attempt to find tag from tregex query
            # currently this will fail with a query like r'/\bthis/'
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)')
            tagchecker = re.compile(r'^[A-Z]{2,4}$')
            treebank_tag = re.findall(tagfinder, query)
            if re.match(tagchecker, treebank_tag[0]):
                if treebank_tag[0].startswith('J'):
                    tag = 'a'
                elif treebank_tag[0].startswith('V') or treebank_tag[0].startswith('M'):
                    tag = 'v'
                elif treebank_tag[0].startswith('N'):
                    tag = 'n'
                elif treebank_tag[0].startswith('R'):
                    tag = 'r'
        elif lemmatag:
            tag = lemmatag
            tagchecker = re.compile(r'^[avrn]$')
            if not re.match(tagchecker, lemmatag):
                raise ValueError("WordNet POS tag not recognised. Must be 'a', 'v', 'r' or 'n'.")
        return tag
    
    def processwords(list_of_matches):
        """edit matches from interrogations"""

        # make everything unicode, lowercase and sorted
        # dependency is already unicode because of bs4
        if not dependency:
            list_of_matches = [unicode(w, 'utf-8', errors = 'ignore') for w in list_of_matches]
        
        # remove commas for pandas csv tokeniser, which i should probably remove soon.
        list_of_matches = [w.lower().replace(',', '') for w in list_of_matches]
        
        # remove punct etc.
        if translated_options != 'o' and translated_options != 'u':
            list_of_matches = [w for w in list_of_matches if re.search(regex_nonword_filter, w)]
        
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases:
            list_of_matches = [nltk.word_tokenize(i) for i in list_of_matches]
        if lemmatise:
            tag = gettag(query)
            list_of_matches = lemmatiser(list_of_matches, tag)
        if titlefilter:
            list_of_matches = titlefilterer(list_of_matches)
        if spelling:
            list_of_matches = convert_spelling(list_of_matches)
        
        # turn every result into a single string again if need be:
        if phrases:
            output = []
            for res in list_of_matches:
                joined = ' '.join(res)
                output.append(joined)
            return output
        else:
            return list_of_matches

    def lemmatiser(list_of_words, tag):
        """take a list of unicode words and a tag and return a lemmatised list."""
        output = []
        for entry in list_of_words:
            if phrases:
                # just get the rightmost word
                word = entry[-1]
                entry.pop()
            else:
                word = entry
            if translated_options.startswith('u'):
                if word in taglemma:
                    word = taglemma[word]
            # only use wordnet lemmatiser when appropriate
            if translated_options.startswith('t') or translated_options.startswith('w') or 'keyword' in query or 'ngram' in query:
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            # do the manual_lemmatisation
            if dependency:
                if word in wordlist:
                    word = wordlist[word]
            if phrases:
                entry.append(word)
                output.append(entry)
            else:
                output.append(word)
        return output

    def titlefilterer(list_of_matches):
        from dictionaries.titlewords import titlewords, determiners
        output = []
        for result in list_of_matches:
            head = result[-1]
            non_head = len(result) - 1 # ???
            title_stripped = [token for token in result[:non_head] if token.rstrip('.') not in titlewords and token.rstrip('.') not in determiners]
            title_stripped.append(head)
            output.append(title_stripped)
        return output

    def convert_spelling(list_of_matches):
        from dictionaries.word_transforms import usa_convert
        if spelling == 'UK':
            usa_convert = {v: k for k, v in usa_convert.items()}
        output = []
        # if we have funct:word, spellfix the word only
        if dependency and not function_filter:
            for result in list_of_matches:
                funct, word = result.split(':', 1)
                try:
                    word = usa_convert[word]
                    result = u'%s:%s' % (funct, word)
                except KeyError:
                    pass
                output.append(result)
            return output            
        # in any other case, do it normally
        else:
            for result in list_of_matches:
                if phrases:
                    for w in result:
                        try:
                            w = usa_convert[w]
                        except KeyError:
                            pass
                    output.append(result)
                else:
                    try:
                        result = usa_convert[result]
                    except KeyError:
                        pass
                    output.append(result)
            return output

    def govrole(xmldata):
        """print funct:gov, using good lemmatisation"""
        # for each sentence
        result = []
        if lemmatise:
            # if lemmatise, we have to do something tricky.
            just_good_deps = SoupStrainer('sentences')
            soup = BeautifulSoup(xmldata, parse_only=just_good_deps)    
            #print soup
            for s in soup.find_all('sentence'):
                right_dependency_grammar = s.find_all('dependencies', type=dep_type, limit = 1)
                for dep in right_dependency_grammar[0].find_all('dep'):                    
                    for dependent in dep.find_all('dependent', limit = 1):
                        word = dependent.get_text()
                        if re.match(regex, word):
                            role = dep.attrs.get('type')
                            gov = dep.find_all('governor', limit = 1)
                            result_word = gov[0].get_text()
                            result_word_id = gov[0].attrs.get('idx')
                            if role != u'root':
                                token_info = s.find_all('token', id=result_word_id, limit = 1)
                                result_word = token_info[0].find_all('lemma', limit = 1)[0].text
                                # could just correct spelling here ...
                                if function_filter:
                                    if re.search(funfil_regex, role):
                                        result.append(result_word)
                                else:
                                    colsep = role + u':' + result_word
                                    result.append(colsep)
                            else:
                                result.append(u'root:root')

        else:
            just_good_deps = SoupStrainer('dependencies', type=dep_type)
            soup = BeautifulSoup(xmldata, parse_only=just_good_deps)
            for dep in soup.find_all('dep'):
                for dependent in dep.find_all('dependent', limit = 1):
                    word = dependent.get_text()
                    if re.match(regex, word):
                        role = dep.attrs.get('type')
                        gov = dep.find_all('governor', limit = 1)
                        result_word = gov[0].get_text()
                        if function_filter:
                            if re.search(funfil_regex, role):
                                result.append(result_word)
                            else:
                                colsep = role + u':' + result_word
                                result.append(colsep)

        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

    def deprole(xmldata):
        """print funct:dep, using good lemmatisation"""
        # for each sentence
        result = []
        if lemmatise:
            # if lemmatise, we have to do something tricky.
            just_good_deps = SoupStrainer('sentences')
            soup = BeautifulSoup(xmldata, parse_only=just_good_deps)    
            #print soup
            for s in soup.find_all('sentence'):
                right_dependency_grammar = s.find_all('dependencies', type=dep_type, limit = 1)
                for dep in right_dependency_grammar[0].find_all('dep'):
                    for governor in dep.find_all('governor', limit = 1):
                        word = governor.get_text()
                        if re.match(regex, word) or word == u'ROOT':
                            role = dep.attrs.get('type')
                            deppy = dep.find_all('dependent', limit = 1)
                            result_word = deppy[0].get_text()
                            result_word_id = deppy[0].attrs.get('idx')
                            # find this idea
                            token_info = s.find_all('token', id=result_word_id, limit = 1)
                            result_word = token_info[0].find_all('lemma', limit = 1)[0].text
                            if function_filter:
                                if re.search(funfil_regex, role):
                                    result.append(result_word)
                            else:
                                colsep = role + u':' + result_word
                                result.append(colsep)
        else:
            just_good_deps = SoupStrainer('dependencies', type=dep_type)
            soup = BeautifulSoup(xmldata, parse_only=just_good_deps)
            for dep in soup.find_all('dep'):
                for governor in dep.find_all('governor', limit = 1):
                    word = governor.get_text()
                    if re.match(regex, word):
                        role = dep.attrs.get('type')
                        deppy = dep.find_all('dependent', limit = 1)
                        result_word = deppy[0].get_text()
                        if function_filter:
                            if re.search(funfil_regex, role):
                                result.append(result_word)
                        else:
                            colsep = role + u':' + result_word
                            result.append(colsep)
        
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

    def funct(xmldata):
        """"print functional role"""
        just_good_deps = SoupStrainer('dependencies', type=dep_type)
        soup = BeautifulSoup(xmldata, parse_only=just_good_deps)
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent', limit = 1):
                word = dependent.get_text()
                if re.match(regex, word):
                    role = dep.attrs.get('type')
                    # can do automatic categorisation of functions here, 
                    # i.e. convert to more basic type
                    #if lemmatise:
                    result.append(role)
        
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

    def plaintexter(plaintext_regex, plaintext_data):
        try:
            result = re.findall(plaintext_regex, plaintext_data)
            return result
        except:
            return

    def depnummer(xmldata):
        """print dependency number"""
        soup = BeautifulSoup(xmldata)
        result = []
        for sent in soup.find_all('sentence'):
            right_deps = sent.find("dependencies", {"type":dep_type})
            for index, dep in enumerate(right_deps.find_all('dep')):
                for dependent in dep.find_all('dependent', limit = 1):
                    word = dependent.get_text()
                    if re.match(regex, word):
                        result.append(index)

                    # get just the number
                    #result.append(int(dependent.attrs.get('idx')))
        
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

    def depnum_reorder(results_list, output = 'results'):
        """reorder depnum results and/or generate totals list"""
        return results_list

    def tabler(subcorpus_names, list_of_dicts, num_rows):
        csvdata = [','.join(subcorpus_names)]
        # for number of rows of data in table
        for i in range(num_rows):
            line = []
            for dictionary in list_of_dicts:
                # check there are sufficient entries in the dictionary
                if not len(dictionary) <= i:
                    the_key = dictionary.most_common(i + 1)[-1][0]
                else:
                    the_key = ' '
                line.append(the_key)
            csvdata.append(','.join(line))
        csv = '\n'.join(csvdata)
        df = read_csv(StringIO(csv))
        return df

    # a few things are off by default:
    only_count = False
    keywording = False
    n_gramming = False
    dependency = False
    depnum = False
    dicts = []

    # check if pythontex is being used:
    # have_python_tex = check_pythontex()

    # parse options
    # handle hyphen at start
    if options.startswith('-'):
        translated_options = options[1:]
    
    # Tregex options:
    if options.startswith('p') or options.startswith('P') or options.startswith('u') or options.startswith('U'):
        optiontext = 'Part-of-speech tags only.'
        translated_options = 'u'
    elif options.startswith('b') or options.startswith('B') or options.startswith('o') or options.startswith('O'):
        optiontext = 'Tags and words.'
        translated_options = 'o'
    elif options.startswith('t') or options.startswith('T') or options.startswith('w') or options.startswith('W'):
        optiontext = 'Words only.'
        translated_options = 't'
    elif options.startswith('c') or options.startswith('C'):
        only_count = True
        translated_options = 'C'
        optiontext = 'Counts only.'
    elif options.startswith('r'):
        plaintext = True
        optiontext = 'Regular expression matches only.'
        translated_options = 'regex'
    
    # dependency options:
    elif options.startswith('n') or options.startswith('N'):
        translated_options = 'n'
        depnum = True
        dependency = True
        optiontext = 'Dependency index number only.'
    elif options.startswith('f') or options.startswith('F'):
        translated_options = 'f'
        dependency = True
        optiontext = 'Functional role only.'
    elif options.startswith('g') or options.startswith('G'):
        translated_options = 'g'
        dependency = True
        optiontext = 'Role and governor.'
    elif options.startswith('d') or options.startswith('D'):
        translated_options = 'd'
        dependency = True
        optiontext = 'Dependent and its role.'
    else:
        raise ValueError("'%s' option not recognised. See docstring for possible options." % options)
    
    # if query is a special query, convert it:
    if query == 'any':
        if translated_options == 't' or translated_options == 'C':
            query = r'/.?[A-Za-z0-9].?/ !< __'
        if translated_options == 'u' or translated_options == 'o':
            query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
    if query == 'subjects':
        query = r'__ >># @NP'
    if query == 'processes':
        query = r'/VB.?/ >># ( VP >+(VP) (VP !> VP $ NP))'
    if query == 'modals':
        query = r'MD < __'
    if query == 'participants':
        query = r'/(NN|PRP|JJ).?/ >># (/(NP|ADJP)/ $ VP | > VP)'
    if query == 'entities':
        query = r'NP <# NNP'
        titlefilter = True

    # check that there's nothing in the quicksave path
    if quicksave:
        savedir = 'data/saved_interrogations'
        if not quicksave.endswith('.p'):
            quicksave = quicksave + '.p'
        fullpath = os.path.join(savedir, quicksave)
        if os.path.isfile(fullpath):
            # if the file exists, check if the query is pretty much the same
            from corpkit import load_result
            loaded = load_result(quicksave)
            if loaded.query['query'] == query and \
            loaded.query['path'] == path and \
            loaded.query['translated_options'] == translated_options and \
            loaded.query['lemmatise'] == lemmatise and \
            loaded.query['titlefilter'] == titlefilter and \
            loaded.query['spelling'] == spelling and \
            loaded.query['dep_type'] == dep_type and \
            loaded.query['function'] == 'interrogator' and \
            loaded.query['function_filter'] == function_filter:
                time = strftime("%H:%M:%S", localtime())
                print ('%s: Duplicate interrogation found in %s.\n' \
                       '          Returning %s instead.\n' \
                       '          Use a new quicksave name if you want to run this query.'% (time, savedir, fullpath))
                return loaded
            else:
                raise ValueError("Save error: non-identifical %s already exists in %s. Pick a new name." % (quicksave, savedir))

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    # dependencies can't be phrases
    if dependency:
        import gc
        from bs4 import BeautifulSoup, SoupStrainer
        regex = re.compile(query)
        phrases = False
        if function_filter:
            funfil_regex = re.compile(function_filter)

    # make sure dep_type is valid:
    if dependency:
        allowed_dep_types = ['basic-dependencies', 'collapsed-dependencies', 'collapsed-ccprocessed-dependencies']
        if dep_type not in allowed_dep_types:
            raise ValueError('dep_type %s not recognised. Must be one of: %s' % (dep_type, ', '.join(allowed_dep_types)))

    # find out if doing keywords or ngrams
    if query.startswith('key'):
        query = 'keywords'
        keywording = True
        optiontext = 'Words only.'
    elif 'ngram' in query:
        query = 'ngrams'
        n_gramming = True
        phrases = True
        optiontext = 'Words only.'

    # if keywording and self is the dictionary, make the dict if need be:
    if keywording:
        if dictionary.startswith('self') or dictionary == os.path.basename(path):
            dictionary = os.path.basename(path) + '.p'
            dictpath = 'data/dictionaries'
            import pickle
            try:
                dic = pickle.load( open( os.path.join(dictpath, dictionary), "rb" ) )
            except:
                from corpkit.build import dictmaker
                time = strftime("%H:%M:%S", localtime())
                print '\n%s: Making reference corpus ...' % time
                dictmaker(path, dictionary)

    # begin interrogation
    time = strftime("%H:%M:%S", localtime())
    print ("\n%s: Beginning corpus interrogation: %s" \
           "\n          Query: '%s'\n          %s" \
           "\n          Interrogating corpus ... \n" % (time, path, query, optiontext) )
    
    # get list of subcorpora and sort them
    sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    sorted_dirs.sort(key=int)
    num_zeroes = len(str(sorted_dirs[-1]))
    
    # treat as one large corpus if no subdirs found
    if len(sorted_dirs) == 0:
        warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        sorted_dirs = [os.path.basename(path)]
    
    # some empty lists we'll need
    allwords_list = []
    main_totals = []

    # check first subcorpus to see if we're using plaintext
    if len(sorted_dirs) == 1:
        subcorpus = path
    else:
        # set to last subcorpus, just to make 'guess' quicker in my case
        subcorpus = os.path.join(path,sorted_dirs[-1])
    if plaintext == 'guess':
        if not tregex_engine(corpus = subcorpus, check_for_trees = True):
            plaintext = True
        else:
            plaintext = False

    # if doing dependencies, make list of all files, and a progress bar
    if dependency or plaintext:
        all_files = []
        for d in sorted_dirs:
            subcorpus = os.path.join(path, d)
            files = [f for f in os.listdir(subcorpus) if f.endswith('.xml')]
            all_files.append([d, files])
        total_files = len([item for sublist in all_files for item in sublist[1]])
        sorted_dirs = all_files
        c = 0
        p = ProgressBar(total_files)
    
    # if tregex, make progress bar for each dir
    else:
        p = ProgressBar(len(sorted_dirs))

    # loop through each subcorpus
    subcorpus_names = []

    # check for valid query. so ugly.
    if not dependency and not keywording and not n_gramming and not plaintext:
        good_tregex_query = tregex_engine(query = query, 
        check_query = True, on_cloud = on_cloud)
    else:
        try:
            plaintext_regex = re.compile(r'\b' + query + r'\b')
        except re.error:
            raise ValueError("Regular expression '%s' contains an error." % query)                
    if dependency:
        re.compile(query)
    for index, d in enumerate(sorted_dirs):
        if not dependency and not plaintext:
            subcorpus_name = d
            subcorpus_names.append(subcorpus_name)
            p.animate(index)
    
            # get path to corpus/subcorpus
            if len(sorted_dirs) == 1:
                subcorpus = path
            else:
                subcorpus = os.path.join(path,subcorpus_name)
    
            # get keywords and ngrams, rather than tregex:
            if keywording or n_gramming:
                from corpkit import keywords
                keys, ngrams = keywords(subcorpus, dictionary = dictionary, 
                                        printstatus = False, clear = False)
                
                unicode_keys = []
                if keywording:
                    for index, w, score in keys:
                        word = unicode(w, 'utf-8', errors = 'ignore')
                        unicode_keys.append([index, word, score])
                    result = unicode_keys
                elif n_gramming:
                    result = []
                    for index, ngram, score in ngrams:
                        for _ in range(int(score)):
                            result.append(ngram)
    
            #if tregex, search
            else:
                op = ['-o', '-' + translated_options]
                result = tregex_engine(query = query, 
                                       options = op, 
                                       corpus = subcorpus,
                                       on_cloud = on_cloud)
                # if just counting matches, just 
                # add subcorpus name and count...
                if only_count:
                    tup = [d, int(result)]
                    main_totals.append(tup)
                    continue

        # for dependencies, d[0] is the subcorpus name 
        # and d[1] is its file list ... 
        if dependency or plaintext:
            subcorpus_name = d[0]
            subcorpus_names.append(subcorpus_name)
            fileset = d[1]
            #for f in read_files:
            result = []
            for f in fileset:
                # pass the x/y argument for more updates
                p.animate(c, str(c) + '/' + str(total_files))
                c += 1
                with open(os.path.join(path, subcorpus_name, f), "rb") as text:
                    data = text.read()
                    if translated_options == 'g':
                        result_from_file = govrole(data)
                    if translated_options == 'd':
                        result_from_file = deprole(data)
                    if translated_options == 'f':
                        result_from_file = funct(data)
                    if translated_options == 'n':
                        result_from_file = depnummer(data)
                    if plaintext:
                        result_from_file = plaintexter(plaintext_regex, data)
                if result_from_file is not None:
                    for entry in result_from_file:
                        result.append(entry)

        if not keywording:
            result.sort()

        # add subcorpus name and total count to totals
        # prefer int subcorpus names...
        # could remove this silliness really
        main_totals.append([subcorpus_name, len(result)])

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        if not keywording and not depnum:
            processed_result = processwords(result)
        if depnum:
            processed_result = result
            allwords_list.append(processed_result)
        if keywording:
            allwords_list.append([w for index, w, score in result])

            # add results master list and to results list
        
        if keywording:
            little_dict = {}
            for index, word, score in result:
                little_dict[word] = score
            dicts.append(Counter(little_dict))
        else:
            dicts.append(Counter(processed_result))

    # 100%
    p.animate(len(sorted_dirs))
    
    if not have_ipython:
        print '\n'
    
    # if only counting, get total total and finish up:
    if only_count:
        stotals = pd.Series([c for name, c in main_totals], index = [str(name) for name, c in main_totals])
        stotals.name = 'Total' 
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        the_time_ended = strftime("%Y-%m=%d %H:%M:%S")
        # add options to named tuple
        the_options = {}
        the_options['path'] = path
        the_options['options'] = options
        the_options['datatype'] = stotals.dtype
        the_options['translated_options'] = translated_options
        the_options['query'] = query 
        the_options['lemmatise'] = lemmatise
        the_options['dictionary'] = dictionary
        the_options['titlefilter'] = titlefilter 
        the_options['lemmatag'] = lemmatag
        the_options['spelling'] = spelling
        the_options['phrases'] = phrases
        the_options['dep_type'] = dep_type
        the_options['function_filter'] = function_filter
        the_options['table_size'] = table_size
        the_options['plaintext'] = plaintext
        the_options['quicksave'] = quicksave
        the_options['time_started'] = the_time_started
        the_options['time_ended'] = the_time_ended

        output = outputnames(the_options, stotals)
        if have_ipython:
            clear_output()
        if quicksave:
            from corpkit.other import save_result
            save_result(output, quicksave)

        if add_to:
            d = add_to[0]
            d[add_to[1]] = output
            return output, d
        else:
            return output

    # flatten and sort master list, in order to make a list of unique words
    allwords = [item for sublist in allwords_list for item in sublist]
    allwords.sort()
    unique_words = set(allwords)

    #make master dictionary
    the_big_dict = {}

    #calculate results
    for word in unique_words:
        the_big_dict[word] = [each_dict[word] for each_dict in dicts]
    # turn master dict into dataframe, sorted
    pandas_frame = DataFrame(the_big_dict, index = subcorpus_names)
    pandas_frame = pandas_frame.T
    pandas_frame['Total'] = pandas_frame.sum(axis=1)
    pandas_frame = pandas_frame.T
    tot = pandas_frame.ix['Total']
    if not depnum:
        pandas_frame = pandas_frame[tot.argsort()[::-1]]
    pandas_frame = pandas_frame.drop('Total', axis = 0)

    # totals --- could just use the frame above ...
    stotals = pd.Series([c for name, c in main_totals], index = [str(name) for name, c in main_totals])
    stotals.name = 'Total'

    # return pandas/csv table of most common results in each subcorpus
    if not depnum:
        if table_size > max([len(d) for d in dicts]):
            table_size = max([len(d) for d in dicts])
        df = tabler(subcorpus_names, dicts, table_size)
    
    # depnum is a little different, though
    # still needs to be done
    if depnum:
        pandas_frame = pandas_frame.T
        
    #make results into named tuple
    # add options to named tuple
    the_time_ended = strftime("%Y-%m=%d %H:%M:%S")
    the_options = {}
    the_options['function'] = 'interrogator'
    the_options['path'] = path
    the_options['options'] = options
    the_options['datatype'] = pandas_frame.iloc[0].dtype
    the_options['translated_options'] = translated_options
    the_options['query'] = query 
    the_options['lemmatise'] = lemmatise
    the_options['dictionary'] = dictionary
    the_options['titlefilter'] = titlefilter 
    the_options['lemmatag'] = lemmatag
    the_options['spelling'] = spelling
    the_options['phrases'] = phrases
    the_options['dep_type'] = dep_type
    the_options['function_filter'] = function_filter
    the_options['table_size'] = table_size
    the_options['plaintext'] = plaintext
    the_options['quicksave'] = quicksave
    the_options['time_started'] = the_time_started
    the_options['time_ended'] = the_time_ended

    if not keywording and not depnum:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals', 'table'])
        output = outputnames(the_options, pandas_frame, stotals, df)
    if keywording:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'table'])
        output = outputnames(the_options, pandas_frame, df)
    if depnum:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
        output = outputnames(the_options, pandas_frame, stotals)        

    if have_ipython:
        clear_output()
    
    # warnings if nothing generated...
    time = strftime("%H:%M:%S", localtime())
    if not only_count:
        if not keywording:
            print '%s: Finished! %d unique results, %d total.' % (time, len(pandas_frame.columns), stotals.sum())
        else:
            print '%s: Finished! %d unique results.' % (time, len(pandas_frame.columns))
        if len(pandas_frame.columns) == 0:
            warnings.warn('No results produced. Maybe your query needs work.')
    else:
        print '%s: Finished! %d total.' % (time, stotals.sum())
    if len(main_totals) == 0:
        warnings.warn('No totals produced. Maybe your query needs work.')
    if stotals.sum() == 0:
        warnings.warn('Total total of zero. Maybe your query needs work.')
    if quicksave:
        from corpkit.other import save_result
        save_result(output, quicksave)

    if add_to:
        d = add_to[0]
        d[add_to[1]] = output
        return output, d
    else:
        return output
    