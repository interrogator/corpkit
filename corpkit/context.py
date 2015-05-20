
def eugener(path, 
            query, 
            depth = 5, 
            top = 20, 
            lemmatise = False,
            remove_closed_class = False,
            remove_regex_from_table = False,
            remove_zero_depth = False):
    """ 
    get most frequent words in corpus path to left and right

    path: path to corpus containing subcorpora
    query: word to be zero depth
    depth: number of places left and right to look
    top: number of entries to return
    """
    import os
    import nltk
    import re
    from collections import Counter
    import pandas as pd
    from corpkit.progressbar import ProgressBar

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

    on_cloud = check_dit()
    regex = re.compile(query)
    wordregex = re.compile('[A-Za-z0-9]')

    print ''
    
    def find_wordnet_tag(tag):
        if tag.startswith('J'):
            tag = 'a'
        elif tag.startswith('V') or tag.startswith('M'):
            tag = 'v'
        elif tag.startswith('N'):
            tag = 'n'
        elif tag.startswith('R'):
            tag = 'r'
        else:
            tag = False
        return tag

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
        if have_ipython:
            if on_cloud:
                tregex_command = 'sh tregex.sh -o \'__ <# (__ !< __)\' %s 2>/dev/null' %(subcorpus)
            else:
                tregex_command = 'tregex.sh -o \'__ <# (__ !< __)\' %s 2>/dev/null' %(subcorpus)
            result_with_blanklines = get_ipython().getoutput(tregex_command)
            results = [line for line in result_with_blanklines if line]
        else:
            if on_cloud:
                tregex_command = ["sh", "tregex.sh", "-o", '__ <# (__ !< __)', "%s" % subcorpus]
            else:
                tregex_command = ["tregex.sh", "-o", '__ <# (__ !< __)', "%s" % subcorpus]
            FNULL = open(os.devnull, 'w')
            results = subprocess.check_output(tregex_command, stderr=FNULL)
            results = os.linesep.join([s for s in results.splitlines() if s]).split('\n')
        # unicode        
        results = [unicode(r, 'utf-8', errors = 'ignore') for r in results]
        
        # so we now have a list of unicode items in this format: '(NNP Eugene)'.
        
        # turn this into a list of words or lemmas, with or without closed words
        processed = []
        for result in results:
            # remove brackets and split on first space
            result = result.lstrip('(')
            result = result.rstrip(')')
            tag, word = result.split(' ', 1)
            # get wordnet tag from stanford tag
            wordnet_tag = find_wordnet_tag(tag)
            if lemmatise:
                # do manual lemmatisation first
                if word in wordlist:
                    word = wordlist[word]
                # do wordnet lemmatisation
                if wordnet_tag:
                    word = lmtzr.lemmatize(word, wordnet_tag)
                    processed.append(word)
                # what to do with closed class words?
                else:
                    if not remove_closed_class:
                        processed.append(word)
            # without lemmatisation, what to do with closed class words
            else:
                if not remove_closed_class:
                    processed.append(word)
                else:
                    if wordnet_tag:
                        processed.append(word)

        # lowercase
        processed = [r.lower() for r in processed]

        # remove punct
        processed = [w for w in processed if re.search(wordregex, w)]

        # a place for info about each corpus
        # word list to use later
        all_words = []
        dicts = []

        # go left and right depth times (for 2, makes [-2, -1, 0, 1, 2])
        for i in range(-depth, (depth + 1)):
            newdict = Counter()
            matching = []
            # go through each token
            for index, token in enumerate(processed):
                # if token matches risk expression
                if re.search(regex, token):
                    # get the word at depth index
                    # try statement for cases where the target word index isn't there
                    try:
                        if i < 0:
                            num = index - abs(i)
                            matching.append(processed[num])
                        else:
                            matching.append(processed[index + i])
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
        if remove_regex_from_table:
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
        print item, '\n', data[item].head(), '\n'
    return dfs

