
def keywords(data, dictionary = 'all.p', **kwargs):
    """Feed this a csv file generated with conc() and get its keywords"""
    #import sys
    #sys.path.insert(0, 'spindle-code-master/keywords')
    #% run corpling_tools/keywords.ipy
    from corpkit.keys import ngrams, keywords_and_ngrams
    import re
    import os
    import time
    from time import localtime, strftime
    try:
        from IPython.display import display, clear_output
        have_ipython = True
    except ImportError:
        have_ipython = False
    # turn all sentences into long string
    time = strftime("%H:%M:%S", localtime())
    #if noprint is False:
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
    clear_output()    
    return keywords_list_version, ngrams_list_version


#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# from Spindle



def ngrams(words, n=2):
    return (tuple(words[i:i+n]) for i in range(0, len(words) - (n - 1)))

def keywords_and_ngrams(input, nKeywords=100, thresholdLL=19, nBigrams=25, thresholdBigrams=2, dictionary = 'bnc.p'):
    from collections import defaultdict
    import sys,os
    import math
    import json
    from dictionaries.stopwords import stopwords as my_stopwords
    import cPickle as pickle
    # Read BNC word frequency distributions using cpickle
    # Note: bnc.p contains only non stopwords
    dictfile = os.path.join(os.path.join('dictionaries', dictionary))
    fdist_dictfile = pickle.load( open( dictfile, "rb" ) )
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
