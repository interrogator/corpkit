#!/usr/bin/python

def interrogator(path, option, query = 'any', 
                lemmatise = False, 
                dictionary = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                function_filter = False,
                table_size = 50,
                quicksave = False,
                add_to = False,
                add_pos_to_g_d_option = False,
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
    
    option : (can type letter or word): 
        - Tregex output option:
            c/count: only *count*
            w/words: only *words*
            p/pos: only *pos* tag
            b/both: *both* words and tags
        - dependency option:
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
        If you set this to a regex, for the 'g' and 'd' option, only words 
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

    from corpkit.tests import check_pytex
    from corpkit.progressbar import ProgressBar
    from corpkit.other import tregex_engine
    import dictionaries
    from dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

    the_time_started = strftime("%Y-%m-%d %H:%M:%S")

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

    regex_nonword_filter = re.compile("[A-Za-z0-9-\']")

    def signal_handler(signal, frame):
        """exit on ctrl+c, rather than just stop loop"""
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    def gettag(query, lemmatag = False):
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
            while not re.match(tagchecker, lemmatag):
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: WordNet POS tag "%s" not recognised.\n It must be:\n\n ' \
                    '              a: (adjective)' \
                    '              n: (noun)' \
                    '              r: (adverb)' \
                    '              v: (verb)\n\nYour selection: ' % (time, lemmatag))
                lemmatag = selection              
        return tag
    
    def processwords(list_of_matches):
        """edit matches from interrogations"""

        # everything should already be in unicode by this point.
        #if not dependency:
            #list_of_matches = [unicode(w, 'utf-8', errors = 'ignore') for w in list_of_matches]
        
        # remove commas for pandas csv tokeniser, which i should probably remove soon.
        list_of_matches = [w.lower().replace(',', '') for w in list_of_matches]
        
        # remove punct etc.
        if translated_option != 'o' and translated_option != 'u':
            list_of_matches = [w for w in list_of_matches if re.search(regex_nonword_filter, w)]
        
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases:
            list_of_matches = [nltk.word_tokenize(i) for i in list_of_matches]
        if lemmatise:
            tag = gettag(query, lemmatag = lemmatag)
            list_of_matches = lemmatiser(list_of_matches, tag)
        if titlefilter:
            list_of_matches = titlefilterer(list_of_matches)
        if spelling:
            list_of_matches = convert_spelling(list_of_matches, spelling = spelling)
        
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
            if translated_option.startswith('u'):
                if word in taglemma:
                    word = taglemma[word]
            # only use wordnet lemmatiser when appropriate
            if translated_option.startswith('t') or translated_option.startswith('w') or 'keyword' in query or 'ngram' in query:
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

    def convert_spelling(list_of_matches, spelling = 'US'):
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
                                result_pos = token_info[0].find_all('pos', limit = 1)[0].text
                                # could just correct spelling here ...
                                if function_filter:
                                    if re.search(funfil_regex, role):
                                        result.append(result_word)
                                else:
                                    if add_pos_to_g_d_option:
                                        colsep = role + u':' + result_pos + u':' + result_word
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
                            result_pos = token_info[0].find_all('pos', limit = 1)[0].text
                            if function_filter:
                                if re.search(funfil_regex, role):
                                    result.append(result_word)
                            else:
                                if add_pos_to_g_d_option:
                                    colsep = role + u':' + result_pos + u':' + result_word
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

    def plaintext_regex_search(pattern, plaintext_data):
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        for p in pattern:
            matches = re.findall(p, plaintext_data)
            for m in matches:
                result.append(m)
        return result

    def plaintext_simple_search(pattern, plaintext_data):
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        # this slows things down significantly ...
        tokenized = nltk.word_tokenize(plaintext_data)
        for p in pattern:
            if not any_plaintext_word:
                num_matches = tokenized.count(p)
                for m in range(num_matches):
                    result.append(p)
            else:
                for m in tokenized:
                    result.append(m)
        return result

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

                    # old method used on risk project
                    # get just the number
                    #result.append(int(dependent.attrs.get('idx')))
        
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result

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
        word_table = read_csv(StringIO(csv))
        return word_table

    # a few things are off by default:
    only_count = False
    keywording = False
    n_gramming = False
    dependency = False
    plaintext = False
    depnum = False

    # some empty lists we'll need
    dicts = []
    allwords_list = []

    # check if pythontex is being used:
    # have_python_tex = check_pythontex()

    # parse option
    # handle hyphen at start
    if option.startswith('-'):
        translated_option = option[1:]
    
    # Tregex option:
    translated_option = False
    while not translated_option:
        if option.startswith('p') or option.startswith('P'):
            optiontext = 'Part-of-speech tags only.'
            translated_option = 'u'
            if type(query) == list:
                query = r'__ < (/(?i)^(' + '|'.join(query) + r')$/ !< __)'
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif option.startswith('b') or option.startswith('B'):
            optiontext = 'Tags and words.'
            translated_option = 'o'
            if type(query) == list:
                query = r'__ < (/(?i)^(' + '|'.join(query) + r')$/ !< __)'
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif option.startswith('w') or option.startswith('W'):
            optiontext = 'Words only.'
            translated_option = 't'
            if type(query) == list:
                query = r'/(?i)^(' + '|'.join(query) + r')$/ !< __'
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif option.startswith('c') or option.startswith('C'):
            count_results = {}
            only_count = True
            translated_option = 'C'
            optiontext = 'Counts only.'
            if type(query) == list:
                query = r'/(?i)^(' + '|'.join(query) + r')$/ !< __' 
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'

        #plaintext options
        elif option.startswith('r') or option.startswith('R'):
            plaintext = True
            optiontext = 'Regular expression matches only.'
            translated_option = 'r'
            if query == 'any':
                query = r'.*'

        elif option.startswith('s') or option.startswith('S'):
            plaintext = True
            optiontext = 'Simple plain-text search.'
            translated_option = 's'
            if query == 'any':
                any_plaintext_word = True
            else:
                any_plaintext_word = False

        #keywording and n_gramming options
        elif option.startswith('k') or option.startswith('K'):
            translated_option = 'k'
            keywording = True
            optiontext = 'Keywords only.'
            if type(query) == list:
                query = r'(?i)^(' + '|'.join(query) + r')$'

        elif option.startswith('n') or option.startswith('n'):
            translated_option = 'n'
            n_gramming = True
            phrases = True
            optiontext = 'n-grams only.'
            if type(query) == list:
                query = r'(?i)\b(' + '|'.join(query) + r')\b'

        # dependency option:
        elif option.startswith('i') or option.startswith('I'):
            translated_option = 'i'
            depnum = True
            dependency = True
            optiontext = 'Dependency index number only.'
        elif option.startswith('f') or option.startswith('F'):
            translated_option = 'f'
            dependency = True
            optiontext = 'Functional role only.'
        elif option.startswith('g') or option.startswith('G'):
            translated_option = 'g'
            dependency = True
            optiontext = 'Role and governor.'
        elif option.startswith('d') or option.startswith('D'):
            translated_option = 'd'
            dependency = True
            optiontext = 'Dependent and its role.'
        else:
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: "%s" option not recognised. Option can be any of: \n\n' \
                          '              b) Get tag and word of Tregex match\n' \
                          '              c) count Tregex match\n' \
                          '              d) Get dependent of regular expression match and the r/ship\n' \
                          '              f) Get dependency function of regular expression match\n' \
                          '              g) get governor of regular expression match and the r/ship\n' \
                          '              n) get dependency index of regular expression match\n' \
                          '              p) get part-of-speech tag with Tregex\n' \
                          '              r) regular expression, for plaintext corpora\n' \
                          '              s) simple search string, for plaintext corpora\n' \
                          '              w) get word(s) returned by Tregex/keywords/ngrams\n' \
                          '              x) exit\n\nYour selection: ' % (time, option))
            option = selection

    if dependency:
        if type(query) == list:
            query = r'(?i)^(' + '|'.join(query) + r')$' 
        if query == 'any':
            query = r'.*'

    if plaintext is True:
        try:
            if tregex_engine(corpus = os.path.join(path, os.listdir(path)[-1]), check_for_trees = True):
                decision = raw_input('\nIt appears that your corpus contains parse trees. If using a plaintext search option, your counts will likely be inaccurate.\n\nHit enter to continue, or type "exit" to start again: ')
                if decision.startswith('e'):
                    return
        except:
            pass
    
    # if query is a special query, convert it:
    if query == 'any':
        if translated_option == 't' or translated_option == 'C':
            query = r'/.?[A-Za-z0-9].?/ !< __'
        if translated_option == 'u' or translated_option == 'o':
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
            loaded.query['translated_option'] == translated_option and \
            loaded.query['lemmatise'] == lemmatise and \
            loaded.query['titlefilter'] == titlefilter and \
            loaded.query['spelling'] == spelling and \
            loaded.query['dep_type'] == dep_type and \
            loaded.query['function'] == 'interrogator' and \
            loaded.query['function_filter'] == function_filter:
                dup_non_i = 'Duplicate'
            else:
                dup_non_i = 'non-identical'

            # first attempt at user input!
            while os.path.isfile(fullpath) and quicksave:
                dict_for_print = '          ' + '\n          '.join(sorted(['%s: %s' % (k, v) for k, v in loaded.query.items()])) + '\n'
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: %s interrogation found in %s:\n\n%s\n' \
                       '          You have the following options:\n\n' \
                       '              a) save with a new name\n' \
                       '              b) turn off "quicksave"\n' \
                       '              c) return the results from %s\n' \
                       '              d) delete %s\n' \
                       '              e) Quickview %s and then decide\n' \
                       '              f) exit\n\nYour selection: ' % (time, dup_non_i, fullpath, dict_for_print, fullpath, fullpath, fullpath))
                if 'a' in selection:
                    sel = raw_input('\nNew save name: ')
                    quicksave = sel
                    if not quicksave.endswith('.p'):
                        quicksave = quicksave + '.p'
                        fullpath = os.path.join(savedir, quicksave)
                elif 'b' in selection:
                    quicksave = False
                elif 'c' in selection:
                    return loaded
                elif 'd' in selection:
                    os.remove(fullpath)
                elif 'e' in selection:
                    print loaded.query
                    print '\n'
                    try:
                        print loaded.results
                    except:
                        print loaded.totals
                    print '\n'
                elif 'f' in selection:
                    print ''
                    return
                else:
                    as_str = str(selection)
                    print '          Choice "%s" not recognised.' % selection

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    # dependencies:
    # can't be phrases
    # check if regex valid
    # check if dep_type valid
    if dependency:
        import gc
        from bs4 import BeautifulSoup, SoupStrainer
        phrases = False
        if function_filter:
            try:
                funfil_regex = re.compile(function_filter)
                is_valid = True
            except:
                is_valid = False
            while not is_valid:
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: function_filter regular expression " %s " contains an error. You can either:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, function_filter))
                if 'a' in selection:
                    function_filter = raw_input('\nNew regular expression: ')
                    try:
                        funfil_regex = re.compile(r'\b' + function_filter + r'\b')
                        is_valid = True
                    except re.error:
                        is_valid = False
                elif 'b' in selection:
                    print ''
                    return

        
        allowed_dep_types = ['basic-dependencies', 'collapsed-dependencies', 'collapsed-ccprocessed-dependencies']
        while dep_type not in allowed_dep_types:
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: Dependency type "%s" not recognised. Must be one of:\n\n' \
                '              a) basic-dependencies' \
                '              b) collapsed-dependencies' \
                '              c) collapsed-ccprocessed-dependencies\n\nYour selection: ' % (time, dep_type))
            if 'a' in selection:
                dep_type = allowed_dep_types[0]
            elif 'b' in selection:
                dep_type = allowed_dep_types[1]
            elif 'c' in selection:
                dep_type = allowed_dep_types[2]
            else:
                pass

    if keywording or n_gramming:
        jcw = False
        if 'just_content_words' in kwargs:
            if kwargs['just_content_words'] is True:
                jcw = True

        if dictionary.startswith('self') or dictionary == os.path.basename(path):
            if lemmatise:
                lem = '-lemmatised'
            else:
                lem = ''
            dictionary = os.path.basename(path) + lem + '.p'
            dictpath = 'data/dictionaries'
            import pickle
            try:
                dic = pickle.load( open( os.path.join(dictpath, dictionary), "rb" ) )
            except:
                from corpkit.build import dictmaker
                time = strftime("%H:%M:%S", localtime())
                print '\n%s: Making reference corpus ...' % time
                dictmaker(path, dictionary, lemmatise = lemmatise, just_content_words = jcw)
    
    # get list of subcorpora and sort them ... user input if no corpus found
    got_corpus = False
    while got_corpus is False:
        try:
            sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
            got_corpus = True
        except OSError:
            got_corpus = False
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: Corpus directory not found: " %s ". You can either:\n\n' \
                '              a) enter a new corpus path\n' \
                '              b) exit\n\nYour selection: ' % (time, path))
            if 'a' in selection:
                path = raw_input('\nNew corpus path: ')
            elif 'b' in selection:
                print ''
                return
    
    # treat as one large corpus if no subdirs found
    one_big_corpus = False
    if len(sorted_dirs) == 0:
        warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        one_big_corpus = True
        sorted_dirs = [os.path.basename(path)]
    
    # numerically sort subcorpora if the first can be an int
    else:
        try:
            check = int(sorted_dirs[0])
            sorted_dirs.sort(key=int)
        except:
            pass

    # plaintext guessing
    # if plaintext == 'guess':
    #     if not one_big_corpus:
    #         # set to last subcorpus, just to make 'guess' quicker in my case
    #         subcorpus = os.path.join(path,sorted_dirs[-1])
    #     else:
    #         # horrible for large corpora
    #         subcorpus = path
    #     if not tregex_engine(corpus = subcorpus, check_for_trees = True):
    #         plaintext = True
    #     else:
    #         plaintext = False

    # if doing dependencies, make list of all files, and a progress bar
    if dependency or plaintext:
        all_files = []
        for d in sorted_dirs:
            if not one_big_corpus:
                subcorpus = os.path.join(path, d)
            else:
                subcorpus = path
            if dependency:
                files = [f for f in os.listdir(subcorpus) if f.endswith('.xml')]
            else:
                files = [f for f in os.listdir(subcorpus)]
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
        query = tregex_engine(query = query, check_query = True)
    
    else:
        if dependency or translated_option == 'r':
            is_valid = True
            try:
                if translated_option == 'r':
                    if type(query) == str:
                        regex = re.compile(r'\b' + query + r'\b')
                    else:
                        regex = query
                else:
                    regex = re.compile(query)
                is_valid = True
            except re.error:
                is_valid = False
            while not is_valid:
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: Regular expression " %s " contains an error. You can either:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, query))
                if 'a' in selection:
                    query = raw_input('\nNew regular expression: ')
                    try:
                        regex = re.compile(r'\b' + query + r'\b')
                        is_valid = True
                    except re.error:
                        is_valid = False
                elif 'b' in selection:
                    print ''
                    return

    #print list nicely
    if not translated_option == 's':
        qtext = query
    else:
        if type(query) == list:
            qtext = ', '.join(query)
        else:
            qtext = query

    # begin interrogation
    time = strftime("%H:%M:%S", localtime())
    print ("\n%s: Beginning corpus interrogation: %s" \
           "\n          Query: '%s'\n          %s" \
           "\n          Interrogating corpus ... \n" % (time, path, qtext, optiontext) )

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
    
            if keywording:
                result = []
                from corpkit import keywords
                spindle_out = keywords(subcorpus, dictionary = dictionary, just_content_words = jcw,
                                        printstatus = False, clear = False, lemmatise = lemmatise)
                for w in list(spindle_out.index):

                    if query != 'any':
                        if re.search(query, w):
                            result.append([w, spindle_out[w]])
                    else:
                        result.append([w, spindle_out[w]])

            elif n_gramming:
                result = []
                from corpkit import ngrams
                spindle_out = ngrams(subcorpus, dictionary = dictionary, just_content_words = jcw,
                                        printstatus = False, clear = False, lemmatise = lemmatise)
                for w in list(spindle_out.index):
                    if query != 'any':
                        if re.search(query, w):
                            for _ in range(spindle_out[w]):
                                result.append(w)
                    else:
                        for _ in range(spindle_out[w]):
                            result.append(w)

            #if tregex, search
            else:
                op = ['-o', '-' + translated_option]
                result = tregex_engine(query = query, options = op, 
                                       corpus = subcorpus)
                
                # if just counting matches, just 
                # add subcorpus name and count...
                if only_count:
                    count_results[d] = result
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
                if one_big_corpus:
                    filepath = os.path.join(path, f)
                else:
                    filepath = os.path.join(path, subcorpus_name, f)
                with open(filepath, "rb") as text:
                    data = text.read()
                    if translated_option == 'g':
                        result_from_file = govrole(data)
                    if translated_option == 'd':
                        result_from_file = deprole(data)
                    if translated_option == 'f':
                        result_from_file = funct(data)
                    if translated_option == 'i':
                        result_from_file = depnummer(data)
                    if translated_option == 'r':
                        result_from_file = plaintext_regex_search(regex, data)
                    if translated_option == 's':
                        result_from_file = plaintext_simple_search(query, data)
                if 'result_from_file' in locals():
                    for entry in result_from_file:
                        result.append(entry)

        if not keywording:
            result.sort()

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        if not keywording and not depnum:
            processed_result = processwords(result)
        if depnum:
            processed_result = result
            
        if keywording:
            allwords_list.append([w for w, score in result])
        else:
            allwords_list.append(processed_result)

            # add results master list and to results list
        
        if keywording:
            little_dict = {}
            for word, score in result:
                little_dict[word] = score
            dicts.append(Counter(little_dict))
        else:
            dicts.append(Counter(processed_result))

    if not dependency and not plaintext:
        p.animate(len(sorted_dirs))
    else:
        # weird float div by 0 zero error here for plaintext
        try:
            p.animate(total_files)
        except:
            pass

    if not have_ipython:
        print '\n'
    
    # if only counting, get total total and finish up:
    if only_count:
        stotals = pd.Series(count_results)
        stotals.name = 'Total' 
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        the_time_ended = strftime("%Y-%m-%d %H:%M:%S")
        # add option to named tuple
        the_options = {}
        the_options['path'] = path
        the_options['option'] = option
        the_options['datatype'] = stotals.dtype
        try:
            the_options['translated_option'] = translated_option
        except:
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
            if stotals.sum() > 0:
                from corpkit.other import save_result
                save_result(output, quicksave)
        
        time = strftime("%H:%M:%S", localtime())
        print '%s: Finished! %d total occurrences.\n' % (time, stotals.sum())

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
    df = DataFrame(the_big_dict, index = subcorpus_names)
    try:
        df.ix['Total'] = df.sum()
        tot = df.ix['Total']
        if not depnum:
            df = df[tot.argsort()[::-1]]
        df = df.drop('Total', axis = 0)
    except:
        pass
    # totals --- could just use the frame above ...
    stotals = df.sum(axis = 1)
    stotals.name = 'Total'

    # make result into series if only one subcorpus
    if one_big_corpus:
        try:
            df = df.T[subcorpus_names[0]]
        except:
            pass
        #df.name = query

    # return pandas/csv table of most common results in each subcorpus
    if not depnum:
        if table_size > max([len(d) for d in dicts]):
            table_size = max([len(d) for d in dicts])
        word_table = tabler(subcorpus_names, dicts, table_size)
    
    # depnum is a little different, though
    if depnum:
        df = df.T
        
    #make results into named tuple
    # add option to named tuple
    the_time_ended = strftime("%Y-%m-%d %H:%M:%S")
    the_options = {}
    the_options['function'] = 'interrogator'
    the_options['path'] = path
    the_options['option'] = option
    the_options['datatype'] = df.iloc[0].dtype
    try:
        the_options['translated_option'] = translated_option
    except:
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
        output = outputnames(the_options, df, stotals, word_table)
    if keywording:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'table'])
        output = outputnames(the_options, df, word_table)
    if depnum:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
        output = outputnames(the_options, df, stotals)        

    if have_ipython:
        clear_output()

    
    # warnings if nothing generated...
    if not one_big_corpus:
        num_diff_results = len(list(df.columns))
    else:
        num_diff_results = len(df)

    if not keywording:
        print '%s: Finished! %d unique results, %d total.\n' % (time, num_diff_results, stotals.sum())
    else:
        print '%s: Finished! %d unique results.\n' % (time, num_diff_results)
    if num_diff_results == 0:
        print '' 
        warnings.warn('No results produced. Maybe your query needs work.')
        return output
    if not keywording:
        if stotals.sum() == 0:
            print '' 
            warnings.warn('No totals produced. Maybe your query needs work.')
            return output
    if quicksave:
        if not keywording:
            if stotals.sum() > 0 and num_diff_results > 0:
                from corpkit.other import save_result
                save_result(output, quicksave)
        else:
            if num_diff_results > 0:
                from corpkit.other import save_result
                save_result(output, quicksave)

    if add_to:
        d = add_to[0]
        d[add_to[1]] = output
        return output, d
    else:
        return output









if __name__ == '__main__':

    import argparse

    epi = "Example usage:\n\npython interrogator.py 'path/to/corpus' 'words' '/NN.?/ >># (NP << /\brisk/)' np_heads --lemmatise --spelling 'UK'" \
    "\n\nTranslation: 'interrogate path/to/corpus for words that are heads of NPs that contain risk.\n" \
    "Lemmatise each result, and save the result as a set of CSV files in np_heads.'\n\n"

    parser = argparse.ArgumentParser(description='Interrogate a linguistic corpus in sophisticated ways', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epi)
    import sys
    if len(sys.argv) == 1:
        parser.add_argument('-p', '--path', metavar='P', type=str,
                                 help='Path to the corpus')
        parser.add_argument('-o', '--option', metavar='O', type=str,
                                 help='Search type')
        parser.add_argument('-q', '--query', metavar='Q',
                                 help='Tregex or Regex query')
        parser.add_argument('-s', '--quicksave', type=str, metavar='S',
                                 help='A name for the interrogation and the files it produces')
    else:
        parser.add_argument('-path', metavar='P', type=str,
                                 help='Path to the corpus')
        parser.add_argument('-option', metavar='O', type=str,
                                 help='Search type')
        parser.add_argument('-query', metavar='Q',
                                 help='Tregex or Regex query')
        parser.add_argument('-quicksave', type=str, metavar='S',
                                 help='A name for the interrogation and the files it produces')        

    parser.add_argument('-l', '--lemmatise',
                             help='Do lemmatisation?', action='store_true')
    parser.add_argument('-dict', '--dictionary', type=str, default='bnc.p',
                             help='A dictionary file to use as a reference corpus when keywording')
    parser.add_argument('-sp', '--spelling', type=str,
                             help='Normalise to US/UK spelling')
    parser.add_argument('-t', '--titlefilter',
                             help='Remove some common prefixes from names, etc.', action='store_true')
    parser.add_argument('-ph', '--phrases',
                             help='Tell interrogator() that you are expecting multi word results')

    parser.add_argument('-dt', '--dep_type', type=str,
                             help='The kind of Stanford dependencies you want to search')
    
    args = parser.parse_args()

    if not vars(args)['quicksave'] and not vars(args)['path'] and not vars(args)['option'] and not vars(args)['query']:
        print "\nWelcome to corpkit!\n\nThis function is called interrogator().\n\nIt allows you to search constituency trees with Tregex, Stanford Dependency parses, or plain text corpora with Regular Expressions.\n\nYou're about to be prompted for some information:\n    1) a name for the interrogation\n    2) a path to your corpus\n    3) a Tregex query or regular expression\n    4) an option, specifying the kind of search you want to do.\n"
        ready = raw_input("When you're ready, type 'start', or 'exit' to cancel: ")
        if ready.startswith('e'):
            print '\n    OK ... come back soon!\n'
            quit()

    all_args = {}

    def urlify(s):
        "Turn title into filename"
        import re
        s = s.lower()
        s = re.sub(r"[^\w\s]", '', s)
        s = re.sub(r"\s+", '-', s)
        return s     

    if not vars(args)['quicksave']:
        name = raw_input('\nName for this interrogation: ')
        all_args['quicksave'] = urlify(name)
    if not vars(args)['path']:
        all_args['path'] = raw_input('\nPath to the corpus: ')
    if not vars(args)['query']:
        print '\nFor the following sentence:\n\n    "The sunny days have come at last."\n\nyou could perform a number of kinds of searches:\n\n    - Tregex queries will search the parse tree:\n        "/NNS/" locates "days", a plural noun\n        "/NN.?/ $ (JJ < /(?i)sunny/)" locates days, sister to adjectival "sunny"\n    - Regex options are used for searching plaintext or dependencies:\n        "[A-Za-z]+s\b" will return "days"\n' 
        all_args['query'] = raw_input('\nQuery: ')
    if not vars(args)['option']:
        print '\nSelect search option. For the following sentence:\n\n    "Some sunny days have come at last."\n\nyou could:\n\n' \
                          '    b) Get tag and word of Tregex match ("(nns days)"\n' \
                          '    c) count Tregex matches\n' \
                          '    d) Get dependent of regular expression match and the r/ship ("amod:sunny")\n' \
                          '    f) Get dependency function of regular expression match ("nsubj")\n' \
                          '    g) get governor of regular expression match and the r/ship ("nsubj:have")\n' \
                          '    n) get dependency index of regular expression match ("1")\n' \
                          '    p) get part-of-speech tag with Tregex ("nns")\n' \
                          '    r) regular expression, for plaintext corpora\n' \
                          '    w) get word(s) returned by Tregex/keywords/ngrams ("day/s")\n' \
                          '    x) exit\n' 
        all_args['option'] = raw_input('\nQuery option: ')
        if 'x' in all_args['option']:
            quit()

    for entry in vars(args).keys():
        if entry not in all_args.keys():
            all_args[entry] = vars(args)[entry]

    conf = raw_input("OK, we're ready to interrogate. If you want to exit now, type 'exit'. Otherwise, press enter to begin!")
    if conf:
        if conf.startswith('e'):
            quit()

    res = interrogator(**all_args)
    # what to do with it!?
    if res:
        import os
        import pandas as pd
        csv_path = 'data/csv_results'
        if not os.path.isdir(csv_path):
            os.makedirs(csv_path)
        interrogation_name = all_args['quicksave']
        savepath = os.path.join(csv_path, interrogation_name)
        if not os.path.isdir(savepath):
            os.makedirs(savepath)
        results_filename = os.path.join(savepath, '%s-results.csv' % interrogation_name)
        totals_filename = os.path.join(savepath, '%s-totals.csv' % interrogation_name)
        top_table_filename = os.path.join(savepath, '%s-top-table.csv' % interrogation_name)
        if res.query['translated_option'] != 'C':
            res.results.to_csv(results_filename, sep = '\t')
            res.table.to_csv(top_table_filename, sep = '\t')
        if res.query['query'] != 'keywords':
            res.totals.to_csv(totals_filename, sep = '\t')
        from time import localtime, strftime
        time = strftime("%H:%M:%S", localtime())
        print '%s: Created CSV files in %s\n' % (time, savepath)

