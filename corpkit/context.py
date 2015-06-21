
def eugener(path, 
            query, 
            depth = 5, 
            top = 20, 
            lemmatise = False,
            just_content_words = False,
            remove_query_from_output = False,
            remove_zero_depth = False,
            return_tags = False):
    """ 
    ***This is probably broken now, can fix if there's a use for it.***
    
    get most frequent words in corpus path to left and right of query regex

    path: path to corpus containing subcorpora
    query: regex to match word to be zero depth
    depth: number of places left and right to look
    top: number of most frequent entries to return
    lemmatise: wordnet lemmatisation
    just_content_words: keep only n, v, a, r tagged words
    remove_query_from_output: remove o
    """
    import os
    import nltk
    import re
    from collections import Counter
    import pandas as pd
    from corpkit.progressbar import ProgressBar
    from corpkit.other import tregex_engine

    # manual lemmatisation here:
    from dictionaries.word_transforms import wordlist
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
        from IPython.display import display, clear_output
    except NameError:
        import subprocess
        have_ipython = False
    from corpkit.tests import check_dit # probably never needed
    
    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    regex = re.compile(query)
    wordregex = re.compile('[A-Za-z0-9]')

    print ''

    # get list of subcorpora
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    sorted_dirs = sorted(dirs)
    # define risk word
    # place for our output
    dfs = {}
    p = ProgressBar(len(sorted_dirs))
    for index, corpus in enumerate(sorted_dirs):
        p.animate(index)
        # search the corpus for whole sents containing risk word
        subcorpus = os.path.join(path, corpus)
        if lemmatise:
            query = r'__ <# (__ !< __)'
        else:
            query = r'__ !> __'
        results = tregex_engine(query, ['-o'], subcorpus, 
                                lemmatise = lemmatise, 
                                just_content_words = just_content_words)

        # lowercase
        processed = [(r.lower(), tag) for r, tag in processed]

        # remove punct
        processed = [w for w in processed if re.search(wordregex, w[0])]

        # a place for info about each corpus
        # word list to use later
        all_words = []
        dicts = []

        # go left and right depth times (for 2, makes [-2, -1, 0, 1, 2])
        for i in range(-depth, (depth + 1)):
            newdict = Counter()
            matching = []
            # go through each token
            for index, (token, tag) in enumerate(processed):
                # if token matches risk expression
                if re.search(regex, token):
                    # get the word at depth index
                    # try statement for cases where the target word index isn't there
                    try:
                        if i < 0:
                            num = index - abs(i)
                            if return_tags:
                                matching.append(processed[num][1])
                            else:
                                matching.append(processed[num][0])
                        else:
                            if return_tags:
                                matching.append(processed[index + i][1])
                            else:
                                matching.append(processed[index + i][0])
                    except:
                        pass
            # tally results
            counted = Counter(matching)
            # remove punctuation etc
            for key in counted:
                # commented because this stuff was moved earlier.
                #if key.isalnum():
                    #if key not in stopwords:
                    #if remove_stopwords:
                        #if key not in stopwords:
                            #newdict[key] = counted[key]
                    #else:
                        #newdict[key] = counted[key]
                newdict[key] = counted[key]
            for w in counted.keys():
                all_words.append(w)
            #top_tokens = newdict.most_common(top)
            dicts.append(newdict)
        
        # make pandas series
        sers = []
        # for each unique word
        for word in list(set(all_words)):
            #get counts for each depth
            series = [dct[word] for dct in dicts]
            # add a total
            series.append(sum([dct[word] for dct in dicts]))
            #make index names for depths plus total
            index_names = range(-depth, (depth + 1))
            index_names.append('Total')
            # turn into pandas data, and name the series the word
            ser = pd.Series(series, index = index_names)
            ser.name = word
            sers.append(ser)
        
        # concatenate series into dataframe
        df = pd.concat(sers, axis=1)

        # sort by total
        tot = df.ix['Total']
        df = df[tot.argsort()[::-1]]

        # remove words matching the regex if need be
        if remove_query_from_output:
            cols = [c for c in list(df.columns) if not re.search(regex, c)]
            df = pd.DataFrame(df[cols])
        # remove zero depth if need be
        if remove_zero_depth:
            df = df.drop(0, axis = 0)

        # just top entries
        df = pd.DataFrame(df[list(df.columns)[:top]])
        
        #transpose
        dfs[corpus] = df.T

    # complete animation, then clear
    p.animate(len(sorted_dirs))
    if have_ipython:
        clear_output()

    # some settings for good display
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('colheader_justify', 'right')

    # print the start of each frame, then return them all
    for item in sorted(dfs):
        print item, '\n', dfs[item].head(), '\n'
    return dfs

