def keywords(data, 
             dictionary = 'bnc.p', 
             clear = True, 
             printstatus = True, 
             n = 'all', 
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
    from dictionaries.stopwords import stopwords as my_stopwords

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.keys import keywords_and_ngrams, get_ref_corpus
    from corpkit.other import datareader


    loaded_ref_corpus = get_ref_corpus(dictionary)

    # turn all sentences into long string
    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating keywords ...\n" % time
    
    # get list of words
    good = datareader(data, **kwargs)

    # remove bad stuff from result
    regex_nonword_filter = re.compile("[A-Za-z]")
    good = [i for i in good if re.search(regex_nonword_filter, i)] 
    
    # get keywords as list of tuples
    kwds = keywords_and_ngrams(good, dictionary = loaded_ref_corpus, show = 'keywords', **kwargs)

    # turn into series
    import pandas as pd
    out = pd.Series([s for k, s in kwds], index = [k for k, s in kwds])
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    out.name = 'keywords'
    
    # print and return
    if clear:
        clear_output()
    if printstatus:
        time = strftime("%H:%M:%S", localtime())
        print '%s: Done! %d results.\n' % (time, len(list(out.index)))

    if n  == 'all':
        n = len(out)

    return out[:n]

def ngrams(data,
           dictionary = 'bnc.p',
           clear = True, 
           printstatus = True, 
           n = 'all',
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
    from dictionaries.stopwords import stopwords as my_stopwords

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.keys import keywords_and_ngrams, get_ref_corpus
    from corpkit.other import datareader

    loaded_ref_corpus = get_ref_corpus(dictionary)

    if n == 'all':
        n = 99999

    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating ngrams... \n" % time
    good = datareader(data, **kwargs)

    regex_nonword_filter = re.compile("[A-Za-z-\']")
    good = [i for i in good if re.search(regex_nonword_filter, i) and i not in my_stopwords] 

    ngrams = keywords_and_ngrams(good, dictionary = dictionary, show = 'ngrams', **kwargs)

    import pandas as pd
    out = pd.Series([s for k, s in ngrams], index = [k for k, s in ngrams])
    out.name = 'ngrams'

    # print and return
    if clear:
        clear_output()
    if printstatus:
        time = strftime("%H:%M:%S", localtime())
        print '%s: Done! %d results.\n' % (time, len(list(out.index)))

    if n  == 'all':
        n = len(out)

    return out[:n]

# from Spindle
def keywords_and_ngrams(input, thresholdBigrams=2, 
                        dictionary = 'bnc.p', show = 'keywords',
                        **kwargs):
    from collections import defaultdict
    import math
    import re
    import json
    import os
    import cPickle as pickle
    from dictionaries.stopwords import stopwords as my_stopwords


    # from Spindle: just altered dictionary stuff and number to show
    def spindle_ngrams(words, n=2, nngram = 'all'):
        return (tuple(words[i:i+n]) for i in range(0, len(words) - (n - 1)))
    
    # Total number of words in reference corpus
    dictsum = sum(dictionary.itervalues())

    from collections import Counter
    counter_target_corpus = Counter(input)

    # target corpus word count
    sumText = sum(counter_target_corpus.values())

    dicLL = {}

    for k, b in counter_target_corpus.items():
        # to handle non-Counter dicts
        try:
            a = dictionary[k]
        except KeyError:
            a = 0
        #b = counter_target_corpus.get(k)
        c = dictsum
        d = sumText
        # this is needed 
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
    listKeywords = [(k, dicLL[k]) for k in sortedLL]

    # list of keywords
    keywords = [keyw[0] for keyw in listKeywords]
    
    ngms = spindle_ngrams(input, 2)
    counter_ngrams = Counter(ngms)

    if show == 'ngrams':
        regex_nonword_filter = re.compile("[A-Za-z]")
        # this doesn't do much now, because everything is in keywords!
        listBigrams = []
        for c, ng in sorted(((c, ng) for ng, c in counter_ngrams.items()), reverse=True):
            w0 = ng[0]
            w1 = ng[1]
            if (all([i not in my_stopwords for i in ng]) 
                and all([re.search(regex_nonword_filter, i) for i in ng]) 
                and c>thresholdBigrams):
                listBigrams.append((' '.join(ng), c))

    if show == 'keywords':
        return listKeywords
    elif show == 'ngrams':
        return listBigrams


def get_ref_corpus(dictionary):
    """Make sure we have a reference corpus"""
    import sys
    import os
    import pickle
    if not dictionary.endswith('.p'):
        dictionary = dictionary + '.p'
    dict_found = False
    while not dict_found:
        try:
            ref_corp_dict = pickle.load( open( dictionary, "rb" ) )
            dict_found = True
            return ref_corp_dict
        except IOError:
            try:
                ref_corp_dict = pickle.load( open( os.path.join('data/dictionaries', dictionary), "rb" ) )
                dict_found = True
                return ref_corp_dict
            except IOError:
                try:
                    import corpkit
                    path_to_corpkit = os.path.dirname(corpkit.__file__)
                    thepath, corpkitname = os.path.split(path_to_corpkit)
                    dictionaries_path = os.path.join(thepath, 'dictionaries')
                    ref_corp_dict = pickle.load( open( os.path.join(dictionaries_path, dictionary), "rb" ) )
                    dict_found = True
                    return ref_corp_dict
                except IOError:
                        pass

        dict_of_dicts = {}
        d_for_print = []
        
        dicts = [f for f in os.listdir('data/dictionaries') if f.endswith('.p')]
        for index, d in enumerate(dicts):
            dict_of_dicts[index] = d
            d_for_print.append('    % 2d) %s' % (index, d))
        
        d_for_print = '\n'.join(d_for_print) 

        selection = raw_input("\nDictionary not found. Select an existing dictionary or exit or type 'exit' to quit.\n\n%s\n\nYour selection: " % d_for_print)
        if selection.startswith('e'):
            import sys
            return
        else:
            try:
                dictionary = dict_of_dicts[int(selection)]
            except:
                print '\nInput "%s" not recognised.' % dictionary

