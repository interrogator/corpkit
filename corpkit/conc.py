
def conc(corpus, 
        query, 
        option = 'tregex',
        dep_function = 'any',
        dep_type = 'basic-dependencies',
        n = 100, 
        random = False, 
        window = 100, 
        trees = False,
        plaintext = False, #'guess',
        add_links = False,
        show_links = False,
        print_status = True,
        print_output = True,
        just_speakers = False,
        root = False,
        **kwargs): 
    """A concordancer for Tregex queries and dependencies"""
    import corpkit
    import os
    import re
    import pandas as pd
    from pandas import DataFrame
    from time import localtime, strftime
    from bs4 import BeautifulSoup, SoupStrainer
    
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
        from other import as_regex
        if option.startswith('t'):
            query = r'/%s/ !< __' % as_regex(query, boundaries = 'line')
        else:
            query = as_regex(query, boundaries = 'w')

    fs_to_conc = [f for f in os.listdir(corpus) if os.path.isfile(os.path.join(corpus, f))]
    fs_to_conc = [f for f in fs_to_conc if f.endswith('.txt') or f.endswith('.xml')]

    def normalise(concline):
        import re
        reg = re.compile(r'\([^ ]+')
        spaces = re.compile(r'\s+')
        concline = re.sub(reg, '', concline)
        concline = re.sub(spaces, ' ', concline)
        concline = concline.replace(')', '').replace('  ', ' ')
        return concline.strip()

    conc_lines = []

    # if tregex, i could make a dict of filepaths, speakernames, trees
    # i could pass in all trees to tregex as stdin, then i could
    # look 
    num_fs = len(fs_to_conc)
    for index, f in enumerate(fs_to_conc):
        if num_fs > 1:
            if 'note' in kwargs.keys():
                kwargs['note'].progvar.set((index) * 100.0 / num_fs)

        from time import localtime, strftime
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Extracting data from %s ...' % (thetime, f)
        if root:
            root.update()
        filepath = os.path.join(corpus, f)
        with open(filepath, "rb") as text:
            data = text.read()
            if option.startswith('p') or option.startswith('l'):
                if option.startswith('l'):
                    lstokens = pickle.load(open(filepath, 'rb'))
                    data = ' '.join(tokens)
                    data = data.split(' . ')
                else:
                    lines = data.splitlines()
                for l in lines:
                    mat = re.search(r'^(.*?)(' + query + r')(.*)$', l)
                    if mat:
                        conc_lines.append([f, '', mat.group(1), mat.group(2), mat.group(3)])
                
            justsents = SoupStrainer('sentences')
            soup = BeautifulSoup(data, parse_only=justsents)  
            if just_speakers:  
                sents = [s for s in soup.find_all('sentence') \
                if s.speakername.text.strip() in just_speakers]
            else:
                sents = [s for s in soup.find_all('sentence')]
            nsents = len(sents)
            for i, s in enumerate(sents):
                if num_fs == 1:
                    if 'note' in kwargs.keys():
                        kwargs['note'].progvar.set((index) * 100.0 / nsents)
                        if root:
                            root.update()
                try:
                    speakr = s.speakername.text.strip()
                except:
                    speakr = '' 
                parsetree = s.parse.text
                if option.startswith('t'):
                    if trees:
                        options = '-s'
                    else:
                        options = '-t'

                    wholes = tregex_engine(query, 
                                options = ['-o', '-w', '-filter', options], 
                                corpus = parsetree,
                                preserve_case = True,
                                root = root)
                    middle_column_result = tregex_engine(query, 
                                options = ['-o', '-filter', options], 
                                corpus = parsetree,
                                preserve_case = True,
                                root = root)
                    for whole, mid in zip(wholes, middle_column_result):
                        reg = re.compile(r'(' + re.escape(mid) + r')')
                        start, middle, end = re.split(reg, whole, 1)
                        conc_lines.append([f, speakr, start, middle, end])
                elif option.startswith('d'):
                    right_dependency_grammar = s.find_all('dependencies', type=dep_type, limit = 1)
                    for dep in right_dependency_grammar[0].find_all('dep'):
                        for dependent in dep.find_all('dependent', limit = 1):
                            matchdep = dependent.get_text().strip()
                            if re.match(query, matchdep):
                                role = dep.attrs.get('type').strip()
                                if dep_function != 'any':
                                    if not re.match(dep_function, role):
                                        continue
                                line = normalise(s.parse.text)
                                start, middle, end = re.split(r'(' + query + r')', line, 1)
                                conc_lines.append([f, speakr, start, middle, end])

    # does not keep results ordered!
    unique_results = [list(x) for x in set(tuple(x) for x in conc_lines)]

    #make into series
    series = []
    pindex = 'f s l m r'.encode('utf-8').split()

    for fname, spkr, start, word, end in unique_results:
        import os
        fname = os.path.basename(fname)
        start = start.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        word = word.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        end = end.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        #spaces = ' ' * (maximum / 2 - (len(word) / 2))
        #new_word = spaces + word + spaces
        series.append(pd.Series([fname.encode('utf-8', errors = 'ignore'), \
                                 spkr.encode('utf-8', errors = 'ignore'), \
                                 start.encode('utf-8', errors = 'ignore'), \
                                 word.encode('utf-8', errors = 'ignore'), \
                                 end.encode('utf-8', errors = 'ignore')], index = pindex))

    # randomise results...
    if random:
        from random import shuffle
        shuffle(series)

    try:
        df = pd.concat(series, axis = 1).T
    except ValueError:
        if root:
            print 'No results found, sorry.'
            return
        else:
            raise ValueError("No results found, I'm afraid. Check your query and path.")

    if not add_links:
        df.columns = ['f', 's', 'l', 'm', 'r']
    else:
        df.columns = ['f', 's', 'l', 'm', 'r', 'link']

    if all(x == '' for x in list(df['s'].values)):
        df.drop('s', axis = 1, inplace = True)

    formatl = lambda x: "{0}".format(x[-window:])
    formatf = lambda x: "{0}".format(x[-20:])
    #formatr = lambda x: 
    formatr = lambda x: "{{:<{}s}}".format(df['r'].str.len().max()).format(x[:window])
    st = df.head(n).to_string(header = False, formatters={'l': formatl,
                                                          'r': formatr,
                                                          'f': formatf}).splitlines()
    
    # hack because i can't figure out formatter:
    rem = '\n'.join([re.sub('\s*\.\.\.\s*$', '', s) for s in st])
    if print_output:
        print rem
    return df

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
        df.columns = ['f', 'l', 'm', 'r']
    else:
        df.columns = ['f', 'l', 'm', 'r', 'link']
    return df

# r'/NN.?/ < /(?i)\brisk/ $ (/NN.?/ < /(?i)factor >># NP)' 