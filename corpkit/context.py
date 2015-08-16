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
    from textprogressbar import TextProgressBar
    from other import tregex_engine

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
    from tests import check_dit # probably never needed
    
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
    p = TextProgressBar(len(sorted_dirs))
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

def get_result(corp_word_permission_tup):
    from collections import Counter
    import re
    import operator
    
    # expand tup
    word_corpus = corp_word_permission_tup[0]
    word = corp_word_permission_tup[1]

    permissive = corp_word_permission_tup[2]
    tagged = corp_word_permission_tup[3]
    regex = corp_word_permission_tup[4]

    if tagged:
        print 'Doing "%s" ...' % word[0]
        if regex:
            regex_word, regex_tag = re.compile(r'(?i)' + word[0]), re.compile(r'(?i)' + word[1])
        else:
            regex_word, regex_tag = re.compile(r'(?i)^' + word[0] + r'$'), re.compile(r'(?i)^' + word[1] + r'$')
    else:
        print 'Doing "%s" ...' % word
        regex_word = re.compile(r'(?i)^' + word + r'$')
        
    contexts = []
    if not tagged:
        for i, token in enumerate(word_corpus):
            if i == 0 or i == (len(word_corpus) - 1):
                continue
            
            if re.search(regex_word, token):
                context = (word_corpus[i - 1], word_corpus[i + 1])
                contexts.append(context)
    else:
        for i, (token, c_tag) in enumerate(word_corpus):
            if i == 0 or i == (len(word_corpus) - 1):
                continue
            if re.search(regex_word, token) and re.search(regex_tag, c_tag):
                context = (word_corpus[i - 1][0], word_corpus[i + 1][0])
                contexts.append(context)
    counted = Counter(contexts)

    # get rid of single occurrences
    singles = []
    for k, v in counted.items():
        if v == 1:
            singles.append(k)

    for s in singles:
        del counted[s]
    
    seems_similar = []

    if not tagged:
        if not permissive:
            for left, right in counted.keys():
                for i, token in enumerate(word_corpus):
                    if i == 0 or i >= (len(word_corpus) - 2):
                        continue
                    if token == left and word_corpus[i + 2] == right:
                        in_common_word = word_corpus[i + 1]
                        if not re.search(regex_word, in_common_word):
                            seems_similar.append(in_common_word)
        else:
            for left, right in counted.keys():
                for i, token in enumerate(word_corpus):
                    if i == 0 or i == (len(word_corpus) - 1):
                        continue
                    if token == left:
                        try:
                            in_common_word = word_corpus[i + 1]
                        except:
                            continue
                        if not re.search(regex_word, in_common_word):
                            seems_similar.append(in_common_word)
                    if token == right:
                        in_common_word = word_corpus[i - 1]
                        if not re.search(regex_word, in_common_word):
                            seems_similar.append(in_common_word)
    else:
        if not permissive:
            for left, right in counted.keys():
                for i, (token, c_tag) in enumerate(word_corpus):
                    if i == 0 or i >= (len(word_corpus) - 2):
                        continue
                    if token == left and word_corpus[i + 2][0] == right:
                        in_common_word, itstag = word_corpus[i + 1]
                        if not re.search(regex_word, in_common_word):
                            if re.search(regex_tag, itstag):
                                seems_similar.append(in_common_word)
        else:
            for left, right in counted.keys():
                for i, (token, c_tag) in enumerate(word_corpus):
                    if i == 0 or i == (len(word_corpus) - 1):
                        continue
                    if token == left:
                        in_common_word, itstag = word_corpus[i + 1]
                        if not re.search(regex_word, in_common_word):
                            if re.search(regex_tag, itstag):
                                seems_similar.append(in_common_word)
                    if token == right:
                        in_common_word, itstag = word_corpus[i - 1]
                        if not re.search(regex_word, in_common_word):
                            if re.search(regex_tag, itstag):
                                seems_similar.append(in_common_word)
    out_list = []
    count = Counter(seems_similar)
    count = count.most_common(len(count))
    for k, v in count:
        if v > 1:
            out_list.append((k, v))
    return (word, out_list)

def sim(corpus, words, permissive = False, regex = True):
    """corpus: list of words
       words: word or list of words to search for

       if your corpus is pos_tagged, pass words alongside tag as string

       """
    import multiprocessing
    import nltk
    import re
    import operator

    #from context import get_result
    from collections import Counter

    try:
        from joblib import Parallel, delayed
    except:
        raise ValueError('joblib, the module used for multiprocessing, cannot be found. ' \
                         'Install with:\n\n        pip install joblib')

    output = {}
    num_cores = multiprocessing.cpu_count()

    tagged = False
    if type(corpus[0]) == tuple:
        tagged = True

    print 'Removing punctuation from corpus ... '
    wordfilter = re.compile(r'^[^-][A-Za-z]')
    if not tagged:
        word_corpus = [w for w in corpus if re.search(wordfilter, w)]
    else:
        word_corpus = [(w, t) for w, t in corpus if re.search(wordfilter, w)]

    # nest word list if need be
    if not tagged:
        if type(words) == str or type(words) == unicode:
            words = [words]
    else:
        if type(words[0]) == str or type(words[0]) == unicode:
            words = [words]

    if tagged:
        if type(words[0]) != tuple:
            raise ValueError('When using tagged corpora, your wordlist must be tuples of (word, tag)')
        
    if len(words) == 1:
        input = (word_corpus, words[0], permissive, tagged, regex)
        return get_result(input)[1]
    else:
        # make tups that can be multiprocessed
        tups = [(word_corpus, word, permissive, tagged, regex) for word in words]
        # get_result returns (word, [(simword1, score), (simword2, score)])
        res = Parallel(n_jobs=num_cores)(delayed(get_result)(t) for t in tups)

        # convert result to dict
        output = {}
        for word, lst in res:
            output[word] = lst

        return output