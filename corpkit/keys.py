def keywords(data, 
             reference_corpus = 'bnc.p', 
             clear = True, 
             printstatus = True, 
             n = 'all',
             threshold = False,
             selfdrop = True,
             editing = False,
             calc_all = True,
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
    import numpy as np
    from collections import Counter

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from keys import keywords_and_ngrams, turn_input_into_counter

    the_threshold = False

    if type(reference_corpus) == str:
        if reference_corpus == 'self':
            if type(data) == pandas.core.series.Series:
                import warnings
                warnings.warn('Using "self" option with Series as data will result in 0.0 keyness.')
            reference_corpus = data.copy()

        else:
            selfdrop = False

    # turn of selfdrop if df indices aren't shared:
    # this is skipped if loading from file or something
    if type(data) == pandas.core.frame.DataFrame and type(reference_corpus) == pandas.core.frame.DataFrame:
        ref_subc = list(reference_corpus.index)
        tg_subc = list(data.index)
        if not all([x in ref_subc for x in tg_subc]):
            selfdrop = False

    if printstatus and not editing:
        time = strftime("%H:%M:%S", localtime())
        print "\n%s: Generating keywords ...\n" % time
    
    def set_threshold_and_remove_under(reference_corpus, threshold, for_keywords = False):
        from collections import Counter
        import pandas

        if type(threshold) == str:
            if threshold.startswith('l'):
                denominator = 10000
            if threshold.startswith('m'):
                denominator = 5000
            if threshold.startswith('h'):
                denominator = 2500
            if for_keywords:
                denominator = denominator * 5 

            tot = sum(reference_corpus.values())

            the_threshold = float(tot) / float(denominator)

        else:
            the_threshold = threshold
        if printstatus:
            print 'Threshold: %d\n' % the_threshold

        # drop infrequent words from keywording
        to_drop = []
        for w, v in reference_corpus.items():
            if v < the_threshold:
                to_drop.append(w)
                #if type(data) == collections.Counter or type(data) == dict:
                    #del data[w]
                if calc_all:
                    del reference_corpus[w]

        if printstatus:
            to_show = [w for w in to_drop[:5]]
            if len(to_drop) > 10:
                to_show.append('...')
                [to_show.append(w) for w in to_drop[-5:]]
            if len(to_drop) > 0:
                print 'Removing %d entries below threshold:\n    %s' % (len(to_drop), '\n    '.join(to_show))
            if len(to_drop) > 10:
                print '... and %d more ... \n' % (len(to_drop) - len(to_show) + 1)
            else:
                print ''
        return reference_corpus, the_threshold, to_drop


    if type(data) == pandas.core.frame.DataFrame:
        loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
        # set threshold
        if threshold:
            loaded_ref_corpus, the_threshold, to_drop = set_threshold_and_remove_under(loaded_ref_corpus, threshold, for_keywords = True)
            # remove under threshold from target corpora
            data = data.drop(to_drop, errors = 'ignore', axis = 1)

        else:
            the_threshold = False

        kwds = []
        for i in list(data.index):
            # this could potentially slow down calculation using saved dicts
            if selfdrop:
                try:
                    loaded_ref_corpus = turn_input_into_counter(reference_corpus.drop(i), **kwargs)
                # if dropping doesn't work, make loaded_ref_corpus without dropping, but only once
                except:
                    try:
                        loaded_ref_corpus
                    except NameError:
                        loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
            else:
                loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
            

            loaded_target_corpus = turn_input_into_counter(data.ix[i], **kwargs)


            ser = keywords_and_ngrams(loaded_target_corpus, loaded_ref_corpus, calc_all = calc_all,
                                   show = 'keywords', **kwargs)
            # turn into series
            ser = pd.Series([s for k, s in ser], index = [k for k, s in ser])
            pd.set_option('display.float_format', lambda x: '%.2f' % x)
            ser.name = i
            kwds.append(ser)
        out = pd.concat(kwds, axis = 1)

    else:
        if selfdrop and type(reference_corpus) == pandas.core.frame.DataFrame:
            try:
                loaded_ref_corpus = turn_input_into_counter(reference_corpus.drop(data.name), **kwargs)
            except:
                try:
                    loaded_ref_corpus
                except NameError:
                    loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
        else:
            loaded_ref_corpus = turn_input_into_counter(reference_corpus, **kwargs)
    
        if threshold:
            loaded_ref_corpus, the_threshold, to_drop = set_threshold_and_remove_under(loaded_ref_corpus, threshold, for_keywords = True)
            # remove under threshold from target corpora
            
            data = data.drop(to_drop, errors = 'ignore')
        else:
            the_threshold = False

        loaded_target_corpus = turn_input_into_counter(data, **kwargs)

        kwds = keywords_and_ngrams(loaded_target_corpus, loaded_ref_corpus, calc_all = calc_all,
                               show = 'keywords', **kwargs)
        # turn into series
        out = pd.Series([s for k, s in kwds], index = [k for k, s in kwds])
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        out.name = 'keywords'

    # drop infinites and nans
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.fillna(0.0)
    
    # print and return
    if clear:
        try:
            clear_output()
        except:
            pass
    if printstatus and not editing:
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

    from keys import keywords_and_ngrams, turn_input_into_counter
    from other import datareader

    loaded_ref_corpus = turn_input_into_counter(reference_corpus)

    if n == 'all':
        n = 99999

    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print "\n%s: Generating ngrams... \n" % time
    good = datareader(data, **kwargs)

    regex_nonword_filter = re.compile("[A-Za-z-\']")
    good = [i for i in good if re.search(regex_nonword_filter, i) and i not in my_stopwords] 

    ngrams = keywords_and_ngrams(good, reference_corpus = reference_corpus, 
                                 calc_all = calc_all, show = 'ngrams', **kwargs)

    import pandas as pd
    out = pd.Series([s for k, s in ngrams], index = [k for k, s in ngrams])
    out.name = 'ngrams'

    # print and return
    if clear:
        try:
            clear_output()
        except:
            pass
    if printstatus:
        time = strftime("%H:%M:%S", localtime())
        print '%s: Done! %d results.\n' % (time, len(list(out.index)))

    if n  == 'all':
        n = len(out)

    return out[:n]

# from Spindle
def keywords_and_ngrams(target_corpus, 
                        reference_corpus, 
                        calc_all = True, 
                        thresholdBigrams=2, 
                        show = 'keywords', 
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
    if calc_all:
        wordlist = list(set(target_corpus.keys() + reference_corpus.keys()))
    else:
        wordlist = target_corpus.keys()
    for w in wordlist:
        # this try for non-Counter dicts, which return keyerror if no result
        try:
            a = reference_corpus[w]
        except:
            a = 0
        try:
            b = target_corpus[w]
        except:
            b = 0
        if 'only_words_in_both_corpora' in kwargs:
            if a == 0 and kwargs['only_words_in_both_corpora'] is True:
                continue
        c = ref_sum
        d = target_sum
        if a == None:
            a = 0
        if b == None:
            b = 0

        # my test for if pos or neg
        # try catches the unlikely 0.0 error
        neg = False
        try:
            if (b / float(d)) < (a / float(c)):
                neg = True
        except:
            pass

        E1 = float(c)*((float(a)+float(b))/ (float(c)+float(d)))
        E2 = float(d)*((float(a)+float(b))/ (float(c)+float(d)))

        if a == 0:
            logaE1 = 0
        else:
            logaE1 = math.log(a/E1)  
        if b == 0:
            logaE2 = 0
        else:
            logaE2 = math.log(b/E2)  
        score = float(2* ((a*logaE1)+(b*logaE2)))
        if neg:
            score = -score
        dicLL[w] = score
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
    from other import datareader
    
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
                    #try:
                    #    import corpkit
                    #    path_to_corpkit = os.path.dirname(corpkit.__file__)
                    #    thepath, corpkitname = os.path.split(path_to_corpkit)
                    #    dictionaries_path = os.path.join(thepath, 'dictionaries')
                    #    ref_corp_dict = pickle.load( open( os.path.join(dictionaries_path, data), "rb" ) )
                    #    dict_found = True
                    #    return ref_corp_dict
                    #except:
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


