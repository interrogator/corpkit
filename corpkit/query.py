#!/usr/local/bin/ipython

#   Interrogating parsed corpora and plotting the results: interrogator
#   Author: Daniel McDonald
#   MIT LICENSE

def interrogator(path, options, query, 
                lemmatise = False, 
                dictionary = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                usa_english = True, 
                phrases = False, 
                dep_type = 'basic-dependencies'):
    
    """
    Interrogate a parsed corpus using Tregex queries, dependencies, or for
    keywords/ngrams

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
    usa_english : Boolean
        convert all to U.S. English
    phrases : Boolean
        Use if your expected results are multiword and thus need tokenising
    dictionary : string
        The name of a dictionary made with dictmaker() for keywording.
        BNC included as default.
    dep_type : str
        the kind of Stanford CoreNLP dependency parses you want to use:
        - 'basic-dependencies' (best lemmatisation right now, default)
        - 'collapsed-dependencies'
        - 'collapsed-ccprocessed-dependencies'

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
    from collections import Counter
    from time import localtime, strftime

    import nltk
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.query import query_test, check_dit, check_pytex
    from corpkit.progressbar import ProgressBar
    import dictionaries
    from dictionaries.word_transforms import wordlist, usa_convert, deptags, taglemma

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
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases:
            list_of_matches = [nltk.word_tokenize(i) for i in list_of_matches]
        if lemmatise:
            tag = gettag(query)
            list_of_matches = lemmatiser(list_of_matches, tag)
        if titlefilter:
            list_of_matches = titlefilterer(list_of_matches)
        if usa_english:
            list_of_matches = usa_english_maker(list_of_matches)
        
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

    def usa_english_maker(list_of_matches):
        from dictionaries.word_transforms import usa_convert
        output = []
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

    def govrole(soup):
        """print funct:gov"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    role = dep.attrs.get('type')
                    gov = dep.find_all('governor')
                    govword = gov[0].get_text()
                    # very messy here, sorry
                    if lemmatise is True:
                        if role in deptags:
                            thetag = deptags[role]
                        else:
                            thetag = None
                        if not thetag:
                            if lemmatag:
                                thetag = lemmatag
                            else:
                                thetag = 'v'
                        if word in wordlist:
                            word = wordlist[word]
                        govword = lmtzr.lemmatize(govword, thetag)
                    colsep = role + u':' + govword
                    result.append(colsep)
        return result

    def funct(soup):
        """"print functional role"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    result.append(dep.attrs.get('type'))
        return result

    def depnummer(soup):
        """print dependency number"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    # get just the number
                    result.append(int(dependent.attrs.get('idx')))
        return result

    def depnum_reorder(results_list, output = 'results'):
        """reorder depnum results and/or generate totals list"""
        yearlist = [[unicode(i[0])] for i in results_list[0][1:]]
        #print yearlist
        totallist = [u'Totals']
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

    # a few things are off by default:
    only_count = False
    keywording = False
    n_gramming = False
    dependency = False
    depnum = False

    # check if pythontex is being used:
    # have_python_tex = check_pythontex()

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
    elif options.startswith('n') or options.startswith('N') or options.startswith('d') or options.startswith('D'):
        depnum = True
        dependency = True
        optiontext = 'Dependency index number only.'
    elif options.startswith('f') or options.startswith('F'):
        dependency = True
        optiontext = 'Functional role only.'
    elif options.startswith('g') or options.startswith('G'):
        dependency = True
        optiontext = 'Role and governor.'
    else:
        raise ValueError("'%s' option not recognised. See docstring for possible options." % options)
    
    # dependencies can't be phrases
    if dependency:
        import gc
        from bs4 import BeautifulSoup, SoupStrainer
        regex = re.compile(query)
        phrases = False

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
    
    # treat as one large corpus if no subdirs found
    if len(sorted_dirs) == 0:
        import warnings
        warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        sorted_dirs = [os.path.basename(path)]
    
    # some empty lists we'll need
    allwords_list = []
    results_list = []
    main_totals = [u'Totals']

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
                    just_good_deps = SoupStrainer('dependencies', type=dep_type)

                    soup = BeautifulSoup(data, parse_only=just_good_deps)
                    if options.startswith('g') or options.startswith('G'):
                        result_from_file = govrole(soup)
                    if options.startswith('f') or options.startswith('F'):
                        result_from_file = funct(soup)
                    if options.startswith('n') or options.startswith('N') or options.startswith('d') or options.startswith('D'):
                        result_from_file = depnummer(soup)
                if result_from_file is not None:
                    for entry in result_from_file:
                        result.append(entry)

                # attempt to stop memory problems. 
                # not sure if this helps, though:
                soup.decompose()
                soup = None
                data = None
                gc.collect()

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
        # no results branch:
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        query_options = [path, query, options] 
        output = outputnames(query_options, main_totals)
        if have_ipython:
            clear_output()
        return output

    # flatten and sort master list
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
    for index, subcorpus in enumerate(results_list):
        subcorpus_name = subcorpus[0]
        subcorpus_data = subcorpus[1]
        p.animate(index)
        dictionary = Counter(subcorpus_data)
        dicts.append(dictionary)
        for word in list_words:
            getval = dictionary[word[0]]
            try:
                word.append([int(subcorpus_name), getval])
            except ValueError:
                word.append([subcorpus_name, getval])

    # 100%            
    p.animate(len(results_list))

    # do totals (and keep them), then sort list by total
    if depnum:
        list_words.sort(key=lambda x: int(x[0]))
        main_totals = depnum_reorder(list_words, output = 'totals') 
        list_words = depnum_reorder(list_words, output = 'results') 
    
    for word in list_words:
        total = sum([i[1] for i in word[1:]])
        word.append([u'Total', total])
    list_words = sorted(list_words, key=lambda x: x[-1], reverse = True) # does this need to be int!?
    
    # reconstitute keyword scores, because we earlier
    if keywording:
        for res in list_words:
            for datum in res[1:]:
                datum[1] = datum[1] * 10

    # add total to main_total
    total = sum([i[1] for i in main_totals[1:]])
    main_totals.append([u'Total', total])

    #make results into named tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [path, query, options] 
    output = outputnames(query_options, list_words, main_totals)
    if have_ipython:
        clear_output()
    return output


def conc(corpus, query, 
         n = 100, 
         random = False, 
         window = 50, 
         trees = False, 
         csvmake = False): 
    """A concordancer for Tregex queries"""
    import os
    from random import randint
    import time
    from time import localtime, strftime
    import re
    from collections import defaultdict
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    import pydoc
    from corpkit.query import query_test, check_pytex, check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    on_cloud = check_dit()
    
    def csvmaker(csvdata, sentences, csvmake):
        """Puts conc() results into tab-separated spreadsheet form"""
        # I made this before learning about Pandas etc., so there's
        # probably a much easier way to get the same result ...
        if os.path.isfile(csvmake):
            raise ValueError("CSV error: %s already exists in current directory. Move it, delete it, or change the name of the new .csv file." % csvmake)

        #make data utf 8
        uc_data = []
        uc_sentences = []
        for line in csvdata:
            newline = []
            for part in line:
                newpart = unicode(part, 'utf-8')
                newline.append(newpart)
            uc_data.append(newline)
        for sentence in sentences:
            newsentence = unicode(sentence, 'utf-8')
            uc_sentences.append(newsentence)
        csv = []
        # make first line
        topline = query + '\nTab separated, with window (n=' + str(len(csvdata)) + '):\n'
        midline = '\n\n' + query + '\nEntire sentences (n=' + str(len(sentences)) + '):\n'
        # title then years for top row
        csv.append(topline)
        # for each word
        for entry in uc_data:
            sentence = '\t'.join(entry)
            csv.append(sentence)
        csv.append(midline)
        for entry in uc_sentences:
            csv.append(entry)
        csv = '\n'.join(csv)
        # write the csv file?
        try:
            fo=open(csvmake,"w")
        except IOError:
            print "Error writing CSV file."
        fo.write(csv.encode("UTF-8"))
        fo.close()
        time = strftime("%H:%M:%S", localtime())
        print time + ": " + csvmake + " written to currect directory."
                
    def list_duplicates(seq):
        tally = defaultdict(list)
        for i,item in enumerate(seq):
            tally[item].append(i)
        return ((key,locs) for key,locs in tally.items() 
                        if len(locs)>1)

    # make sure query is valid:
    query_test(query)

    # welcome message
    time = strftime("%H:%M:%S", localtime())
    print "\n%s: Getting concordances for %s ... \n          Query: %s\n" % (time, corpus, query)
    output = []
    if trees:
        options = '-s'
    else:
        options = '-t'

    # get whole sentences:
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh -o -w %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        else:
            tregex_command = 'tregex.sh -o -w %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        whole_results = get_ipython().getoutput(tregex_command)
        result = [line for line in whole_results if line]
    else:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh", "-o", "-w", "%s" % options, '%s' % query, "%s" % corpus]
        else:
            tregex_command = ["tregex.sh", "-o", "-w", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        whole_results = subprocess.check_output(tregex_command, stderr=FNULL)
        whole_results = os.linesep.join([s for s in whole_results.splitlines() if s]).split('\n')
    
    results = list(whole_results)
    
    if csvmake:
        sentences = list(results)
    
    # get just the match of the sentence
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh -o %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        else:
            tregex_command = 'tregex.sh -o %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        middle_column_result = get_ipython().getoutput(tregex_command)
        result = [line for line in middle_column_result if line]
    else:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % corpus]
        else:
            tregex_command = ["tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        middle_column_result = subprocess.check_output(tregex_command, stderr=FNULL)
        middle_column_result = os.linesep.join([s for s in middle_column_result.splitlines() if s]).split('\n')
    tresults = list(middle_column_result)
    zipped = zip(whole_results, middle_column_result)
    all_dupes = []

    
    # make sure we have some results
    if len(zipped) == 0:
        raise ValueError("No matches found, sorry. I wish there was more I could tell you.") 

    maximum = len(max(tresults, key=len)) # longest result in characters
    csvdata = []
    unique_results = []
    for result in zipped: 
        tree = result[0]
        pattern = result[1]
        if not trees:
            regex = re.compile(r"(\b[^\s]{0,1}.{," + re.escape(str(window)) + r"})(\b" + 
            re.escape(pattern) + r"\b)(.{," + re.escape(str(window)) + r"}[^\s]\b)")
        else:
            regex = re.compile(r"(.{,%s})(%s)(.{,%s})" % (window, re.escape(pattern), window ))
        search = re.findall(regex, tree)
        for result in search:
            unique_results.append(result)
    unique_results = set(sorted(unique_results)) # make unique
    
    # from here on down needs a major cleanup ...
    for unique_result in unique_results:
        lstversion = list(unique_result)
        if len(lstversion) == 3:
            # make match red!
            # lstversion[1] = "\x1b[31m%s\x1b[0m" % lstversion[1]
            if csvmake:
                csvdata.append(lstversion)
            whitespace_first = window + 2 - len(lstversion[0])
            whitespace_second = maximum - len(lstversion[1])
            lstversion[0] = ' ' * whitespace_first + lstversion[0]
            lstversion[1] = lstversion[1] + ' ' * whitespace_second
            output.append(lstversion)
    formatted_output = []
    for index, row in enumerate(output):
        formatted_output.append(" ".join(row))
        #if noprint is False:
        if not random:
            if index < n:
                print '% 4d' % index, " ".join(row)
    if csvmake:
        csvmaker(csvdata, sentences, csvmake)
    if not random:
        return formatted_output
    if random:
        outnum = len(output)
        if n > outnum:
            n = outnum
        rand_out = []
        while len(rand_out) < n:
            randomnum = randint(0,outnum - 1)
            possible = output[randomnum]
            if possible not in rand_out:
                rand_out.append(possible)
        formatted_random_output = []
        for index, row in enumerate(rand_out):
            formatted_random_output.append(" ".join(row))
            print '% 4d' % index, " ".join(row)
        return formatted_random_output

def multiquery(corpus, query, sort_by = 'total'):
    """Creates a named tuple for a list of named queries to count.

    Pass in something like:

    [[u'NPs in corpus', r'NP'], [u'VPs in corpus', r'VP']]"""

    import collections
    from corpkit.query import interrogator
    from corpkit.edit import resorter
    from corpkit.edit import merger
    results = []
    for name, pattern in query:
        result = interrogator(corpus, 'c', pattern)
        result.totals[0] = name # rename count
        results.append(result.totals)
    if sort_by:
        results = resorter(results, sort_by = sort_by)
    tot = merger(results, r'.*', newname = 'Totals', printmerge = False)
    #print tot
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    output = outputnames(query, results, tot.totals)
    return output

def topix_search(topic_subcorpora, options, query, **kwargs):
    """Interrogates each topic subcorpus."""
    fullqueries = []
    results = [] # make empty list of results and totals
    totals = []
    for topic in topic_subcorpora: # for topic name
        result = interrogator(topic, options, query, **kwargs)
        fullqueries.append(result.query)
        try:
            results.append(result.results) # add to results
        except:
            results.append([])
        totals.append(result.totals)
    # now we should have 3x results and 3x totals, and a query
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals']) 
    output = outputnames(fullqueries, results, totals)
    return output

def query_test(query, have_ipython = False, on_cloud = False):
    """make sure a tregex query works, and provide help if it doesn't"""

    import re
    import subprocess

    # define error searches 
    tregex_error = re.compile(r'^Error parsing expression')
    regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')

    #define command and run it
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh \'%s\' 2>&1' % (query)
        else:
            tregex_command = 'tregex.sh \'%s\' 2>&1' % (query)
        testpattern = get_ipython().getoutput(tregex_command)
    else:
        if on_cloud:
            tregex_command = ['sh', 'tregex.sh', '%s' % (query)]
        else:
            tregex_command = ['tregex.sh', '%s' % (query)]
        try:
            testpattern = subprocess.check_output(tregex_command, 
                                    stderr=subprocess.STDOUT).split('\n')
        except Exception, e:
            testpattern = str(e.output).split('\n')

    # if tregex error, give general error message
    if re.match(tregex_error, testpattern[0]):
        tregex_error_output = "Error parsing Tregex expression. Check for balanced parentheses and boundary delimiters."
        raise ValueError(tregex_error_output) 
    
    # if regex error, try to help
    if re.match(regex_error, testpattern[0]):
        info = testpattern[0].split(':')
        index_of_error = re.findall(r'index [0-9]+', info[1])
        justnum = index_of_error[0].split('dex ')
        spaces = ' ' * int(justnum[1])
        remove_start = query.split('/', 1)
        remove_end = remove_start[1].split('/', -1)
        regex_error_output = 'Error parsing regex inside Tregex query:%s'\
        '. Best guess: \n%s\n%s^' % (str(info[1]), str(remove_end[0]), spaces)
        raise ValueError(regex_error_output)
    
    # if nothing, the query's fine! 

def interroplot(path, query):
    from corpkit import interrogator, plotter
    quickstart = interrogator(path, 't', query)
    plotter(str(path), quickstart.results, fract_of = quickstart.totals)

def check_pytex():
    """checks for pytex, i hope"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if 'pythontex' in as_string:
        return True
    else:
        return False

def check_dit():
    """checks if we're on the cloud ... bad way to do it..."""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if '/opt/python/lib' in as_string:
        return True
    else:
        return False
 
def check_tex(have_ipython = True):
    import os
    if have_ipython:
        checktex_command = 'which latex'
        o = get_ipython().getoutput(checktex_command)[0]
        if o.startswith('which: no latex in'):
            have_tex = False
        else:
            have_tex = True
    else:
        import subprocess
        FNULL = open(os.devnull, 'w')
        checktex_command = ["which", "latex"]
        try:
            o = subprocess.check_output(checktex_command, stderr=FNULL)
            have_tex = True
        except subprocess.CalledProcessError:
            have_tex = False
    return have_tex