
def keywords(data, dictionary = 'bnc.p', clear = True, printstatus = True, **kwargs):
    """Feed this function some data and get its keywords.

    You can use dictmaker() to build a new dictionary 
    to serve as reference corpus, or use bnc.p

    A list of what counts as data is available in the 
    docstring of datareader().
    """
    
    import re
    import time
    from time import localtime, strftime

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    from corpkit.keys import ngrams, keywords_and_ngrams
    from corpkit.edit import datareader

    # turn all sentences into long string
    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating keywords and ngrams... \n" % time
    good = datareader(data)
    keywords, ngrams = keywords_and_ngrams(good, dictionary = dictionary, **kwargs)
    keywords_list_version = []
    for index, item in enumerate(keywords):
        aslist = [index, item[0], item[1]]
        keywords_list_version.append(aslist)
    ngrams_list_version = []
    for index, item in enumerate(ngrams):
        joined_ngram = ' '.join(item[0])
        aslist = [index, joined_ngram, item[1]]
        ngrams_list_version.append(aslist)
    if clear:
        clear_output()    
    return keywords_list_version, ngrams_list_version


#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# from Spindle



def ngrams(words, n=2):
    return (tuple(words[i:i+n]) for i in range(0, len(words) - (n - 1)))

def keywords_and_ngrams(input, nKeywords=1000, thresholdLL=19, nBigrams=250, thresholdBigrams=2, dictionary = 'bnc.p'):
    from collections import defaultdict
    import math
    import json
    import os
    from dictionaries.stopwords import stopwords as my_stopwords
    import cPickle as pickle
    try:
        fdist_dictfile = pickle.load( open( dictionary, "rb" ) )
    except IOError:
        try:
            fdist_dictfile = pickle.load( open( os.path.join('data/dictionaries', dictionary), "rb" ) )
        except IOError:
            try:
                import corpkit
                path_to_corpkit = os.path.dirname(corpkit.__file__)
                thepath, corpkitname = os.path.split(path_to_corpkit)
                dictionaries_path = os.path.join(thepath, 'dictionaries')
                fdist_dictfile = pickle.load( open( os.path.join(dictionaries_path, dictionary), "rb" ) )
            except IOError:
                raise IOError('Could not find %s in current directory, data/dictionaries or %s' % (dictionary, dictionaries_path))
    
    # Total number of words in Spoken BNC
    dictsum = sum(fdist_dictfile.itervalues())
    fdistText = defaultdict(int)
    sumText = 0
    listWords = []
    listSentences = []
    
    if isinstance(input,str):
        listSentences = [input]
    else:
        listSentences = input
    
    for line in listSentences:
        for w in line.split():
            w = w.lower()
            listWords.append(w)
            sumText = sumText+1
            if w not in my_stopwords and w.isalpha() and len(w) > 2:
                fdistText[w] = fdistText[w]+1

    dicLL = {}

    for k, v in fdistText.items():
        a = fdist_dictfile.get(k)
        b = fdistText.get(k)
        c = dictsum
        d = sumText
        if a == None:
            a = 0
        if b == None:
            b = 0
        E1 = float(c)*((float(a)+float(b))/ (float(c)+float(d)))
        E2 = float(d)*((float(a)+float(b))/ (float(c)+float(d)))
        if a == 0:
            logaE1 = 0
        else:
            logaE1 = math.log(a/E1)  
        dicLL[k] = float(2* ((a*logaE1)+(b*math.log(b/E2))))

    sortedLL = sorted(dicLL, key=dicLL.__getitem__, reverse=True)
    listKeywords = [(k, dicLL[k]) for k in sortedLL if k.isalpha() and dicLL[k] > thresholdLL]

    keywords = [keyw[0] for keyw in listKeywords]
    counts = defaultdict(int)
    for ng in ngrams(listWords, 2):
        counts[ng] += 1

    listBigrams = []
    for c, ng in sorted(((c, ng) for ng, c in counts.iteritems()), reverse=True):
        w0 = ng[0]
        w1 = ng[1]
        if w0 in keywords and w1 in keywords and c>thresholdBigrams:
            listBigrams.append((ng, c))
    return (listKeywords[0:nKeywords], listBigrams[0:nBigrams])



def key_interrogator(path, options, query, lemmatise = False, 
    titlefilter = False, lemmatag = False, usa_english = True, phrases = False, dictionary = 'bnc.p'):
    """Interrogate a corpus by keyword
    """
    import os
    import re
    import signal
    import collections
    from collections import Counter
    from time import localtime, strftime

    from corpkit.query import query_test
    from corpkit.progressbar import ProgressBar
    import nltk
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    import dictionaries
    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()
        # location of words for manual lemmatisation
        from dictionaries.word_transforms import wordlist, usa_convert
        from dictionaries.manual_lemmatisation import wordlist, taglemma
    # check if we are in ipython
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    # exit on ctrl c
    def signal_handler(signal, frame):
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    def gettag(query):
        import re
        if lemmatag is False:
            # attempt to find tag from tregex query
            # currently this will fail with a query like r'/\bthis/'
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)') 
            tagchecker = re.compile(r'^[A-Z]{2,4}$')
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)')
            treebank_tag = re.findall(tagfinder, query)
            if re.match(tagchecker, treebank_tag[0]):
                if treebank_tag[0].startswith('J'):
                    tag = 'a'
                elif treebank_tag[0].startswith('V'):
                    tag = 'v'
                elif treebank_tag[0].startswith('N'):
                    tag = 'n'
                elif treebank_tag[0].startswith('R'):
                    tag = 'r'
            else:
                tag = 'n' # default to noun tag---same as lemmatiser does with no tag
        if lemmatag:
            tag = lemmatag
            tagchecker = re.compile(r'^[avrn]$')
            if not re.match(tagchecker, lemmatag):
                raise ValueError("WordNet POS tag not recognised. Must be 'a', 'v', 'r' or 'n'.")
        return tag
    
    def processwords(list_of_matches):
        if lemmatise:
            tag = gettag(query)
            list_of_matches = lemmatiser(list_of_matches, tag)
        if titlefilter:
            list_of_matches = titlefilterer(list_of_matches)
        if usa_english:
            list_of_matches = usa_english_maker(list_of_matches)
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
            if options == '-u':
                if word in taglemma:
                    word = taglemma[word]
            # only use wordnet lemmatiser for -t
            if options == '-t':
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            if phrases:
                entry.append(word)
                output.append(' '.join(entry))
            else:
                output.append(word)
        return output
        # if single words: return [lmtsr.lemmatize(word, tag) for word in list_of_matches]

    def titlefilterer(list_of_matches):
        from dictionaries.titlewords import titlewords
        from dictionaries.titlewords import determiners
        output = []
        for result in list_of_matches:
            head = result[-1]
            non_head = len(result) - 1 # ???
            title_stripped = [token for token in result[:non_head] if token.rstrip('.') not in titlewords and token.rstrip('.') not in determiners]
            title_stripped.append(head)
            if not usa_english:
                str_result = ' '.join(title_stripped)
                output.append(str_result)
            else:
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
                output.append(' '.join(result))
            else:
                try:
                    result = usa_convert[result]
                except KeyError:
                    pass
                output.append(result)
        return output

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    # welcome message based on kind of interrogation
    u_option_regex = re.compile(r'(?i)-u') # find out if u option enabled
    t_option_regex = re.compile(r'(?i)-t') # find out if t option enabled   
    o_option_regex = re.compile(r'(?i)-o') # find out if t option enabled   
    c_option_regex = re.compile(r'(?i)-c') # find out if c option enabled   
    
    only_count = False

    if re.match(u_option_regex, options):
        optiontext = 'Tags only.'
    if re.match(t_option_regex, options):
        optiontext = 'Terminals only.'
    if re.match(o_option_regex, options):
        optiontext = 'Tags and terminals.'
    if re.match(c_option_regex, options):
        only_count = True
        options = options.upper()
        optiontext = 'Counts only.'

    # begin interrogation
    time = strftime("%H:%M:%S", localtime())
    print "\n%s: Beginning corpus interrogation: %s\n          Query: '%s'\n          %s\n          Interrogating corpus ... \n" % (time, path, query, optiontext)
    
    # check that query is ok
    #query_test(query, have_ipython = have_ipython)

    sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    sorted_dirs.sort(key=int)
    if len(sorted_dirs) == 0:
        import warnings
        warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        sorted_dirs = [os.path.basename(path)]
    allwords_list = []
    results_list = []
    main_totals = [u'Totals']
    p = ProgressBar(len(sorted_dirs))
    # do interrogation with tregex
    for index, d in enumerate(sorted_dirs):
        p.animate(index)
        if len(sorted_dirs) == 1:
            subcorpus = path
        else:
            subcorpus = os.path.join(path,d)
        
        # get keywords and count, print them as result ...
        from corpkit import keywords
        keys, ngrams = keywords(subcorpus, dictionary = dictionary, printstatus = False, clear = False)
        result = []
        for index, key, score in keys:
            for index, word, score in keys:
                for _ in range(int(score) / 100.0):
                    result.append(word)
        if only_count:
            try:
                tup = [int(d), int(result[0])]
            except ValueError:
                tup = [d, int(result[0])]
            main_totals.append(tup)
            continue
        result = [unicode(match, 'utf-8', errors = 'ignore') for match in result]
        result = [w.lower() for w in result]
        result.sort()
        try:
            main_totals.append([int(d), len(result)])
        except ValueError:
            main_totals.append([d, len(result)])
        # encode text and tokenise phrase results
        if phrases:
            result = [nltk.word_tokenize(i) for i in result]
        processed_result = processwords(result)
        allwords_list.append(processed_result)
        results_list.append(processed_result)
    p.animate(len(sorted_dirs))
    if not have_ipython:
        print '\n'
    if only_count:
        total = sum([i[1] for i in main_totals[1:]])
        main_totals.append([u'Total', total])
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        query_options = [path, query, options] 
        output = outputnames(query_options, main_totals)
        if have_ipython:
            clear_output()
        return output

    # flatten list
    allwords = [item for sublist in allwords_list for item in sublist]
    allwords.sort()
    unique_words = set(allwords)
    list_words = []
    for word in unique_words:
        list_words.append([word])


    # make dictionary of every subcorpus
    dicts = []
    p = ProgressBar(len(results_list))
    for index, subcorpus in enumerate(results_list):
        p.animate(index)
        subcorpus_name = sorted_dirs[index]
        dictionary = Counter(subcorpus)
        dicts.append(dictionary)
        for word in list_words:
            getval = dictionary[word[0]]
            try:
                word.append([int(subcorpus_name), getval])
            except ValueError:
                word.append([subcorpus_name, getval])
    p.animate(len(results_list))
    # do totals (and keep them), then sort list by total
    for word in list_words:
        total = sum([i[1] for i in word[1:]])
        word.append([u'Total', total])
    list_words = sorted(list_words, key=lambda x: x[-1], reverse = True) # does this need to be int!?
    # multiply EVERYTHING by 100 because we divided by that earlier, for speed
    for res in list_words:
        for datum in res[1:]:
            datum[1] = datum[1] * 100.0
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
