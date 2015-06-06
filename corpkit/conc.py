
def conc(corpus, query, 
        n = 100, 
        random = False, 
        window = 40, 
        trees = False): 
    """A concordancer for Tregex queries over trees or regexes over plain text"""
    import pandas as pd
    from pandas import DataFrame
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
    from corpkit.other import tregex_engine
    from corpkit.tests import check_pytex, check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    
    # check if on the cloud, as this changes how we do tregex queries
    on_cloud = check_dit()

    # check query
    good_tregex_query = tregex_engine(query, check_query = True)

    # make sure there's a corpus
    if not os.path.exists(corpus):
        raise ValueError('Corpus file or folder not found: %s' % corpus)

    # welcome message
    time = strftime("%H:%M:%S", localtime())
    print "\n%s: Getting concordances for %s ... \n          Query: %s\n" % (time, corpus, query)
    output = []

    if trees:
        options = '-s'
    else:
        options = '-t'
    # get whole sentences:
    whole_results = tregex_engine(query, 
                                  options = ['-o', '-w', options], 
                                  corpus = corpus, 
                                  on_cloud = on_cloud)
    middle_column_result = tregex_engine(query, 
                                  options = ['-o', options], 
                                  corpus = corpus, 
                                  on_cloud = on_cloud)

    if len(whole_results) == 0:
        if not tregex_engine(corpus = corpus, check_for_trees = True):
            import nltk
            sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
            whole_results = []
            middle_column_result = []
            small_regex = re.compile(query)
            big_regex = re.compile(r'.*' + query + r'.*')
            fs = [os.path.join(corpus, f) for f in os.listdir(corpus)]
            # do recursive if need
            if any(os.path.isdir(f) for f in fs):
                recursive_files = []
                for dirname, dirnames, filenames in os.walk(corpus):
                    for filename in filenames:
                        recursive_files.append(os.path.join(dirname, filename))
                fs = recursive_files
            for f in fs:
                raw = open(f).read().replace('\n', ' ')
                # encoding ... ?
                sents = sent_tokenizer.tokenize(raw)
                for sent in sents:
                    try:
                        for match in re.findall(small_regex, raw):
                            middle_column_result.append(match)
                            whole_results.append(sent)
                    except:
                        continue
    if len(whole_results) == 0:
        if good_tregex_query:
            raise ValueError("No results found. Any chance you're trying to use a Tregex query on a plain-text corpus?")

    try:
        # get longest middle column result, or discover no results and raise error
        maximum = len(max(middle_column_result, key=len))
    except ValueError:
        raise ValueError("No matches found, sorry. I wish there was more I could tell you.")

    zipped = zip(whole_results, middle_column_result)
    unique_results = []

    # make sure we have some results
    if len(zipped) == 0:
        raise ValueError("No matches found, sorry. I wish there was more I could tell you.") 

    for whole_result, middle_part in zipped:
        if not trees:
            regex = re.compile(r"(\b[^\s]{0,1}.{," + re.escape(str(window)) + r"})(\b" + re.escape(middle_part) + r"\b)(.{," + re.escape(str(window)) + r"}[^\s]\b)")
        else:
            regex = re.compile(r"(.{,%s})(%s)(.{,%s})" % (window, re.escape(middle_part), window ))
        search = re.findall(regex, whole_result)
        for result in search:
            unique_results.append(result)
    unique_results = set(sorted(unique_results)) # make unique
    
    #make into series
    series = []

    lname = ' ' * (window/2-1) + 'l'
    # centering middle column
    #mname = ' ' * (maximum/2+1) + 'm'
    mname = ' ' * (maximum/2-1) + 'm'
    rname = ' ' * (window/2-1) + 'r'
    for start, word, end in unique_results:
        #spaces = ' ' * (maximum / 2 - (len(word) / 2))
        #new_word = spaces + word + spaces
        series.append(pd.Series([start, word, end], index = [lname, mname, rname]))

    # randomise results...
    if random:
        from random import shuffle
        series = suffle(series)

    # temp options only!! with x as y...
    df = pd.concat(series, axis = 1).T
    pd.set_option('display.max_columns', 500)
    pd.set_option('max_colwidth',window * 2)
    pd.set_option('display.width', 1000)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('colheader_justify', 'left')
    print df.head(n).to_string(header = False, formatters={rname:'{{:<{}s}}'.format(df[rname].str.len().max()).format})
    df.columns = ['l', 'm', 'r']
    return df

