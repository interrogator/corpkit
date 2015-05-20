#!/usr/local/bin/ipython

#   Interrogating parsed corpora and plotting the results: interrogator
#   Author: Daniel McDonald
#   MIT LICENSE

def old_interrogator(path, options, query, 
                lemmatise = False, 
                dictionary = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                function_filter = False,
                table_size = 50):
    
    """
    Interrogate a parsed corpus using Tregex queries, dependencies, or for
    keywords/ngrams

    Output: a named tuple, with 'branches':
        variable_name.query = a record of what query generated th
        variable_name.results = a list of all results
        variable_name.totals = a list of just totals
        variable_name.table = a Pandas (or CSV if Pandas not found) table
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
        for keywords/ngrams, use 't'
   
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

    from corpkit.tests import query_test, check_dit, check_pytex
    from corpkit.progressbar import ProgressBar
    import dictionaries
    from dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

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

    regex_nonword_filter = re.compile("^[A-Za-z0-9-\']+$")

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
        if not depnum:
            list_of_matches = [w.lower() for w in list_of_matches]
        # remove punct etc.
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
            if options.startswith('u'):
                if word in taglemma:
                    word = taglemma[word]
            # only use wordnet lemmatiser when appropriate
            if options.startswith('t') or options.startswith('w') or 'keyword' in query or 'ngram' in query:
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

    def depnummer(xmldata):
        """print dependency number"""
        just_good_deps = SoupStrainer('dependencies', type=dep_type)
        soup = BeautifulSoup(xmldata, parse_only=just_good_deps)
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent', limit = 1):
                word = dependent.get_text()
                if re.match(regex, word):
                    # get just the number
                    result.append(int(dependent.attrs.get('idx')))
        
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

    def depnum_reorder(results_list, output = 'results'):
        """reorder depnum results and/or generate totals list"""
        yearlist = [[unicode(i[0])] for i in results_list[0][1:]]
        #print yearlist
        totallist = [u'Total']
        counts = []
        for entry in results_list: # for each depnum:
            depnum = entry[0]
            #print depnum
            count = sum(d[1] for d in entry[1:])
            #print count
            totallist.append([depnum, count])
        for year in yearlist:
            for entry in results_list:
                word = entry[0]
                data = entry[1:]
                #depnum_and_count = [word, sum([d[1] for d in data])] # sum for each depnum
                #totallist.append(depnum_and_count)
                for theyear, count in data:
                    if theyear == int(year[0]):
                        fixed_datum = [word, count]
                        year.append(fixed_datum)
        # this could be done more efficiently earlier:
        for year in yearlist:
            for entry in year[1:]:
                if entry[0] > 50:
                    year.remove(entry)
        for entry in totallist[1:]:
            if entry[0] > 50:
                    totallist.remove(entry)
        if output == 'results':
            return yearlist
        if output == 'totals':
            return totallist

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
        if not have_pandas:
            df = csv
        else:
            df = read_csv(StringIO(csv))
            pd.set_option('display.max_columns', len(subcorpus_names))
            pd.set_option('display.max_rows', num_rows + 1)
        return df

    # a few things are off by default:
    only_count = False
    keywording = False
    n_gramming = False
    dependency = False
    depnum = False

    # check if pythontex is being used:
    # have_python_tex = check_pythontex()

    # if query is a special query, convert it:
    if 'any_word' in query:
        query = r'/.?[A-Za-z0-9].?/ !< __'
    if 'subjects' in query:
        query = r'__ >># @NP'
    if 'processes' in query:
        query = r'/VB.?/ >># ( VP >+(VP) (VP !> VP $ NP))'
    if 'modals' in query:
        query = r'MD'
    if 'participants' in query:
        query = r'/(NN|PRP|JJ).?/ >># (/(NP|ADJP) $ VP | > VP)'
    if 'entities' in query:
        query = r'NP <# NNP'
        titlefilter = True

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    # parse options
    # handle hyphen at start
    if options.startswith('-'):
        options = options[1:]
    
    # Tregex options:
    if options.startswith('p') or options.startswith('P') or options.startswith('u') or options.startswith('U'):
        optiontext = 'Part-of-speech tags only.'
        options = 'u'
    elif options.startswith('b') or options.startswith('B') or options.startswith('o') or options.startswith('O'):
        optiontext = 'Tags and words.'
        options = 'o'
    elif options.startswith('t') or options.startswith('T') or options.startswith('w') or options.startswith('W'):
        optiontext = 'Words only.'
        options = 't'
    elif options.startswith('c') or options.startswith('C'):
        only_count = True
        options = 'C'
        optiontext = 'Counts only.'
    
    # dependency options:
    elif options.startswith('n') or options.startswith('N'):
        depnum = True
        dependency = True
        optiontext = 'Dependency index number only.'
    elif options.startswith('f') or options.startswith('F'):
        dependency = True
        optiontext = 'Functional role only.'
    elif options.startswith('g') or options.startswith('G'):
        dependency = True
        optiontext = 'Role and governor.'
    elif options.startswith('d') or options.startswith('D'):
        dependency = True
        optiontext = 'Dependent and its role.'
    else:
        raise ValueError("'%s' option not recognised. See docstring for possible options." % options)
    
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

    # parse query
    if query.startswith('key'):
        keywording = True
        optiontext = 'Words only.'
    elif 'ngram' in query:
        n_gramming = True
        phrases = True
        optiontext = 'Words only.'
    else:
        if not dependency:
            # it's tregex. check if ok
            query_test(query, have_ipython = have_ipython, on_cloud = on_cloud)
        else:
            try:
                re.compile(query)
            except re.error:
                raise ValueError("Regular expression '%s' contains an error." % query)

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
    results_list = []
    main_totals = [u'Total']

    # if doing dependencies, make list of all files, and a progress bar
    if dependency:
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
    for index, d in enumerate(sorted_dirs):
        if not dependency:
            subcorpus_name = d
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
                result = []
    
                # this remains a total hack, and sacrifices a little 
                # bit of accuracy when doing the division. rewrite, one day.
                if keywording:
                    for index, word, score in keys:
                        divided_score = score / 10.0
                        for _ in range(int(divided_score)):
                            result.append(word)
                elif n_gramming:
                    for index, ngram, score in ngrams:
                        for _ in range(int(score)):
                            result.append(ngram)
    
            #if tregex, determine ipython or not and search
            else:
                if have_ipython:
                    if on_cloud:
                        tregex_command = 'sh tregex.sh -o -%s \'%s\' %s 2>/dev/null' %(options, query, subcorpus)
                    else:
                        tregex_command = 'tregex.sh -o -%s \'%s\' %s 2>/dev/null' %(options, query, subcorpus)
                    result_with_blanklines = get_ipython().getoutput(tregex_command)
                    result = [line for line in result_with_blanklines if line]
                else:
                    if on_cloud:
                        tregex_command = ["sh", "tregex.sh", "-o", "-%s" % options, '%s' % query, "%s" % subcorpus]
                    else:
                        tregex_command = ["tregex.sh", "-o", "-%s" % options, '%s' % query, "%s" % subcorpus]
                    FNULL = open(os.devnull, 'w')
                    result = subprocess.check_output(tregex_command, stderr=FNULL)
                    result = os.linesep.join([s for s in result.splitlines() if s]).split('\n')
            
                # if just counting matches, just 
                # add subcorpus name and count...
                if only_count:
                    try:
                        tup = [int(d), int(result[0])]
                    except ValueError:
                        tup = [d, int(result[0])]
                    main_totals.append(tup)
                    continue

        # for dependencies, d[0] is the subcorpus name 
        # and d[1] is its file list ... 
        if dependency:
            subcorpus_name = d[0]
            fileset = d[1]
            #for f in read_files:
            result = []
            for f in fileset:
                # pass the x/y argument for more updates
                p.animate(c, str(c) + '/' + str(total_files))
                c += 1
                with open(os.path.join(path, subcorpus_name, f), "rb") as text:
                    data = text.read()

                    if options.startswith('g') or options.startswith('G'):
                        result_from_file = govrole(data)
                    if options.startswith('d') or options.startswith('D'):
                        result_from_file = deprole(data)
                    if options.startswith('f') or options.startswith('F'):
                        result_from_file = funct(data)
                    if options.startswith('n') or options.startswith('N'):
                        result_from_file = depnummer(data)
                if result_from_file is not None:
                    for entry in result_from_file:
                        result.append(entry)

        result.sort()

        # add subcorpus name and total count to totals
        # prefer int subcorpus names...
        try:
            main_totals.append([int(subcorpus_name), len(result)])
        except ValueError:
            main_totals.append([subcorpus_name, len(result)])

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        processed_result = processwords(result)


        # add results master list and to results list
        allwords_list.append(processed_result)
        results_list.append([subcorpus_name, processed_result])

        # could probably make dictionaries here ... ?

    # 100%
    p.animate(len(sorted_dirs))
    if not have_ipython:
        print '\n'
    
    # if only counting, get total total and finish up:
    if only_count:
        total = sum([i[1] for i in main_totals[1:]])
        main_totals.append([u'Total', total])
        years = []
        counts = []
        for year, count in main_totals[1:]:
            years.append(year)
            counts.append(count)
        stotals = pd.Series(counts, index = years, name = 'Total')
        # no results branch:
        outputnames = collections.namedtuple('interrogation', ['query', 'stotal', 'old_totals'])
        query_options = [path, query, options] 
        output = outputnames(query_options, stotals, main_totals)
        if have_ipython:
            clear_output()
        return output

    # flatten and sort master list, in order to make a list of unique words
    allwords = [item for sublist in allwords_list for item in sublist]
    allwords.sort()
    unique_words = set(allwords)
    
    # make a list of lists to which we can add each
    # subcorpus' result, plus a total ...
    list_words = []
    for word in unique_words:
        list_words.append([word])

    # make dictionary of every subcorpus and store in dicts
    dicts = []
    p = ProgressBar(len(results_list))
    the_big_dict = {}
    for index, subcorpus in enumerate(results_list):
        subcorpus_name = subcorpus[0]
        subcorpus_data = subcorpus[1]
        p.animate(index)
        dictionary = Counter(subcorpus_data)       
        dicts.append(dictionary)
        
        # make each result
        for word in list_words:
            getval = dictionary[word[0]]
            try:
                word.append([int(subcorpus_name), getval])
            except ValueError:
                word.append([subcorpus_name, getval])
    
    #make pandas table
    for word in unique_words:
        the_big_dict[word] = [each_dict[word] for each_dict in dicts]
    pandas_frame = DataFrame(the_big_dict, index = sorted_dirs)
    #pandas[u'Total'] = sum([pandas_frame.T[d] for d in sorted_dirs])
    pandas_frame['Total'] = pandas_frame.sum(axis=1)
    pandas_frame = pandas_frame.T
    pandas_frame['Total'] = pandas_frame.sum(axis=1)
    pandas_frame = pandas_frame.T
    tot = pandas_frame.ix['Total']
    pandas_frame = pandas_frame[tot.argsort()[::-1]]
    #pandas_frame = pandas_frame.drop('Total', axis = 0)
    move_totals = list(pandas_frame.columns)
    move_totals.remove('Total')
    move_totals.append('Total')
    pandas_frame = pandas_frame[move_totals]

    # 100%            
    p.animate(len(results_list))

    # return pandas/csv table of most common results in each subcorpus
    if table_size > max([len(d) for d in dicts]):
        table_size = max([len(d) for d in dicts])
    df = tabler(sorted_dirs, dicts, table_size)
    


    # do totals (and keep them), then sort list by total
    # depnum is a little different, though
    if depnum:
        list_words.sort(key=lambda x: int(x[0]))
        main_totals = depnum_reorder(list_words, output = 'totals') 
        list_words = depnum_reorder(list_words, output = 'results') 
    
    for word in list_words:
        total = sum([i[1] for i in word[1:]])
        word.append([u'Total', total])
    list_words = sorted(list_words, key=lambda x: x[-1], reverse = True) # does this need to be int!?
    
    # reconstitute keyword scores, because we earlier
    # this means that keyness scores are a bit off. not good.
    if keywording:
        for res in list_words:
            for datum in res[1:]:
                datum[1] = datum[1] * 10

    # add total to main_total
    total = sum([i[1] for i in main_totals[1:]])
    main_totals.append([u'Total', total])
    years = []
    counts = []
    for year, count in main_totals[1:]:
        years.append(year)
        counts.append(count)
    stotals = pd.Series(counts, index = years)

    #make results into named tuple
    query_options = [path, query, options] 

    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals', 'table', 'old_results', 'old_totals'])
    output = outputnames(query_options, pandas_frame, stotals, df, list_words, main_totals)

    time = strftime("%H:%M:%S", localtime())
    if have_ipython:
        clear_output()
    
    # warnings if nothing generated
    # should these 'break'?
    if not only_count:
        print '%s: Finished! %d unique results, %d total.' % (time, len(list_words), main_totals[-1][-1])
        if len(list_words) == 0:
            warnings.warn('No results produced. Maybe your query needs work.')
            return
    else:
        print '%s: Finished! %d total.' % (time, main_totals[-1][-1])
    if len(main_totals) == 0:
        warnings.warn('No totals produced. Maybe your query needs work.')
        return
    if main_totals[-1][1] == 0:
        warnings.warn('Total total of zero. Maybe your query needs work.')
        return
    return output

