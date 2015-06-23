def keywords(data, 
             reference_corpus = 'bnc.p', 
             clear = True, 
             printstatus = True, 
             n = 'all', 
             **kwargs):
    """Feed this function some data and get its keywords.

    You can use dictmaker() to build a new reference_corpus 
    to serve as reference corpus, or use bnc.p

    A list of what counts as data is available in the 
    docstring of datareader().
    """
    
    import re
    import time
    from time import localtime, strftime
    import collections
    import pandas
    import pandas as pd
    from collections import Counter

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.keys import keywords_and_ngrams, turn_input_into_counter

    if printstatus:
        time = strftime("%H:%M:%S", localtime())
        print "\n%s: Generating keywords ...\n" % time

    loaded_target_corpus = turn_input_into_counter(data, **kwargs)
    
    loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
    
    # get keywords as list of tuples
    kwds = keywords_and_ngrams(loaded_target_corpus, loaded_ref_corpus, 
                               show = 'keywords', **kwargs)

    # turn into series
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
           reference_corpus = 'bnc.p',
           clear = True, 
           printstatus = True, 
           n = 'all',
           **kwargs):
    """Feed this function some data and get its keywords.

    You can use dictmaker() to build a new reference_corpus 
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

    from corpkit.keys import keywords_and_ngrams, turn_input_into_counter
    from corpkit.other import datareader

    loaded_ref_corpus = turn_input_into_counter(reference_corpus)

    if n == 'all':
        n = 99999

    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating ngrams... \n" % time
    good = datareader(data, **kwargs)

    regex_nonword_filter = re.compile("[A-Za-z-\']")
    good = [i for i in good if re.search(regex_nonword_filter, i) and i not in my_stopwords] 

    ngrams = keywords_and_ngrams(good, reference_corpus = reference_corpus, show = 'ngrams', **kwargs)

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
def keywords_and_ngrams(target_corpus, reference_corpus, thresholdBigrams=2, show = 'keywords',
                        **kwargs):
    import collections
    from collections import Counter
    import math
    import re
    import json
    import os
    import cPickle as pickle
    from dictionaries.stopwords import stopwords as my_stopwords

    # from Spindle: just altered reference_corpus stuff and number to show
    def spindle_ngrams(words, n=2, nngram = 'all'):
        return (tuple(words[i:i+n]) for i in range(0, len(words) - (n - 1)))

    # total number of words in target corpus
    target_sum = sum(target_corpus.itervalues())
    
    # Total number of words in reference qcorpus
    ref_sum = sum(reference_corpus.itervalues())

    dicLL = {}

    for k, b in target_corpus.items():
            a = reference_corpus[k]
            c = ref_sum
            d = target_sum
            if a == None:
                a = 0
            if b == None:
                b = 0

            # my test for if pos or neg
            neg = False
            if (b / float(d)) < (a / float(c)):
                neg = True

            E1 = float(c)*((float(a)+float(b))/ (float(c)+float(d)))
            E2 = float(d)*((float(a)+float(b))/ (float(c)+float(d)))
            if a == 0:
                logaE1 = 0
            else:
                logaE1 = math.log(a/E1)  
            score = float(2* ((a*logaE1)+(b*math.log(b/E2))))
            if neg:
                score = -score
            dicLL[k] = score
    sortedLL = sorted(dicLL, key=dicLL.__getitem__, reverse=True)
    listKeywords = [(k, dicLL[k]) for k in sortedLL]

    # list of keywords
    keywords = [keyw[0] for keyw in listKeywords]
    
    if show == 'keywords':
        return listKeywords
    
    elif show == 'ngrams':
        ngms = spindle_ngrams(target_corpus, 2)
        counter_ngrams = Counter(ngms)
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
        return listBigrams

def turn_input_into_counter(data, **kwargs):
    """from string (filepath) or variable, return a counter."""
    import sys
    import os
    import re
    import collections
    import pickle
    import pandas
    from corpkit.other import datareader
    
    dict_found = False

    if type(data) == str:
        if os.path.isdir(data):
            # get list of words
            good = datareader(data, **kwargs)
            # remove bad stuff from result
            regex_nonword_filter = re.compile("[A-Za-z]")
            data = [i for i in good if re.search(regex_nonword_filter, i)]
            return collections.Counter(data)

    while not dict_found:
        if 'interrogation' in str(type(data)):
            try:
                data = data.results
            except:
                raise ValueError("Can't find .results branch of input.")

        # if passing in results, sum them
        if type(data) == pandas.core.frame.DataFrame:
            data = data.sum()

        # count sum
        if type(data) == pandas.core.series.Series:
            data = data[data != 0]
            data = collections.Counter(data.to_dict())
            dict_found = True
            return data

        # turn notmal dicts into counter
        if type(data) == dict:
            dict_found = True
            return collections.Counter(data)
        
        # the best case scenario:
        if type(data) == collections.Counter:
            dict_found = True
            return data

        # filepath stuff
        if type(data) == str:
            if not data.endswith('.p'):
                data = data + '.p'
            try:
                ref_corp_dict = pickle.load( open( data, "rb" ) )
                dict_found = True
                return ref_corp_dict
            except IOError:
                try:
                    ref_corp_dict = pickle.load( open( os.path.join('data/dictionaries', data), "rb" ) )
                    dict_found = True
                    return ref_corp_dict
                except IOError:
                    try:
                        import corpkit
                        path_to_corpkit = os.path.dirname(corpkit.__file__)
                        thepath, corpkitname = os.path.split(path_to_corpkit)
                        dictionaries_path = os.path.join(thepath, 'dictionaries')
                        ref_corp_dict = pickle.load( open( os.path.join(dictionaries_path, data), "rb" ) )
                        dict_found = True
                        return ref_corp_dict
                    except:
                        pass

            dict_of_dicts = {}
            d_for_print = []
            
            dicts = [f for f in os.listdir('data/dictionaries') if f.endswith('.p')]
            for index, d in enumerate(dicts):
                dict_of_dicts[index] = d
                d_for_print.append('    % 2d) %s' % (index, d))
            
            d_for_print = '\n'.join(d_for_print) 

            selection = raw_input("\nReference corpus not found. Select an existing reference corpus or exit or type 'exit' to quit.\n\n%s\n\nYour selection: " % d_for_print)
            if selection.startswith('e'):
                import sys
                sys.exit()
            else:
                try:
                    data = dict_of_dicts[int(selection)]
                except:
                    print '\nInput "%s" not recognised.' % data
