
def conc(corpus, query, 
        n = 100, 
        random = False, 
        window = 40, 
        trees = False,
        plaintext = 'guess',
        add_links = False,
        show_links = False,
        print_status = True,
        print_output = True,
        root = False): 
    """A concordancer for Tregex queries over trees or regexes over plain text"""
    import os
    import re
    import pandas as pd
    from pandas import DataFrame
    from time import localtime, strftime
    
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    from corpkit.other import tregex_engine
    from corpkit.tests import check_pytex, check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    
    # convert list to query
    if type(query) == list:
        from corpkit.other import as_regex
        query = r'/%s/ !< __' % as_regex(query, boundaries = 'line')
    
    # lazy, daniel!
    if n == 'all':
        n = 99999
    if window == 'all':
        window = 500

    # check query
    good_tregex_query = tregex_engine(query, check_query = True)
    if good_tregex_query is False:
        return

    # make sure there's a corpus
    if not os.path.exists(corpus):
        if root:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Corpus directory not found: %s' %(time, corpus)
            return
        else:
            raise ValueError('Corpus file or folder not found: %s' % corpus)

    # welcome message
    if print_status:
        time = strftime("%H:%M:%S", localtime())
        print "\n%s: Getting concordances for %s ... \n          Query: %s\n" % (time, corpus, query)
    output = []

    if plaintext == 'guess':
        if not tregex_engine(corpus = corpus, check_for_trees = True):
            plaintext = True
        else:
            plaintext = False

    if trees:
        options = '-s'
    else:
        options = '-t'
    if not plaintext:
        whole_results = tregex_engine(query, 
                                  options = ['-o', '-w', options], 
                                  corpus = corpus,
                                  preserve_case = True)
        middle_column_result = tregex_engine(query, 
                                  options = ['-o', options], 
                                  corpus = corpus,
                                  preserve_case = True)
    
    if plaintext:
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

    try:
        # get longest middle column result, or discover no results and raise error
        maximum = len(max(middle_column_result, key=len))
    except ValueError:
        if print_status:
            time = strftime("%H:%M:%S", localtime())
            print "\n%s: No matches found." % time
        return

    zipped = zip(whole_results, middle_column_result)
    unique_results = []

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
        start = start.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        word = word.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        end = end.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        #spaces = ' ' * (maximum / 2 - (len(word) / 2))
        #new_word = spaces + word + spaces
        series.append(pd.Series([start.encode('utf-8', errors = 'ignore'), word.encode('utf-8', errors = 'ignore'), end.encode('utf-8', errors = 'ignore')], index = [lname.encode('utf-8', errors = 'ignore'), mname.encode('utf-8', errors = 'ignore'), rname.encode('utf-8', errors = 'ignore')]))

    # randomise results...
    if random:
        from random import shuffle
        shuffle(series)

    try:
        df = pd.concat(series, axis = 1).T
    except ValueError:
        raise ValueError("No results found, I'm afraid. Check your query and path.")

    if add_links:

        def _add_links(lines, links = False, show = 'thread'):
            link = "http://www.healthboards.com/boards/bipolar-disorder/695089-labels.html"
            linktext = '<a href="%s>link</a>' % link
            import pandas as pd
            inds = list(df.index)
            num_objects = len(list(df.index))
            ser = pd.Series([link for n in range(num_objects)], index = inds)
            lines['link'] = ser
            return lines
        
        df = _add_links(df)
        
    # make temporary
    pd.set_option('display.max_columns', 500)
    pd.set_option('max_colwidth',window * 2)
    pd.set_option('display.width', 1000)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('colheader_justify', 'left')
    if add_links:
        if not show_links:
            if print_output:
                print df.drop('link', axis = 1).head(n).to_string(header = False, formatters={rname:'{{:<{}s}}'.format(df[rname].str.len().max()).format})
        else:
            if print_output:
                print HTML(df.to_html(escape=False))
    else:
        if print_output:
            print df.head(n).to_string(header = False, formatters={rname:'{{:<{}s}}'.format(df[rname].str.len().max()).format})

    if not add_links:
        df.columns = ['l', 'm', 'r']
    else:
        df.columns = ['l', 'm', 'r', 'link']
    return df

# r'/NN.?/ < /(?i)\brisk/ $ (/NN.?/ < /(?i)factor >># NP)' 