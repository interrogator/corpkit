
def keywords(data, 
             dictionary = 'bnc.p', 
             clear = True, 
             printstatus = True, 
             **kwargs):
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
    from corpkit.query import check_dit

    on_cloud = check_dit()

    # turn all sentences into long string
    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating keywords and ngrams... \n" % time
    good = datareader(data, on_cloud = on_cloud)
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


# from Spindle: just altered dictionary stuff and number to show
def ngrams(words, n=2):
    return (tuple(words[i:i+n]) for i in range(0, len(words) - (n - 1)))

# from Spindle
def keywords_and_ngrams(input, thresholdLL=19, thresholdBigrams=2, dictionary = 'bnc.p'):
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
    return (listKeywords, listBigrams)
