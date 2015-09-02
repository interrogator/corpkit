
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

    if query == 'any':
        query = r'.*'
    
    # convert list to query
    if type(query) == list:
        from other import as_regex
        if option.startswith('t'):
            query = r'/%s/ !< __' % as_regex(query, boundaries = 'line')
        else:
            query = as_regex(query, boundaries = 'w')

    can_do_fast = False
    if option.startswith('t'):
        if just_speakers is False:
            can_do_fast = True

    just_speakers_is_list = False
    if type(just_speakers) == list:
        just_speakers_is_list = True

    if type(just_speakers) == str:
        if just_speakers.lower() != 'all':
            just_speakers = [just_speakers]

    def get_deps(sentence, dep_type):
        if dep_type == 'basic-dependencies':
            return sentence.basic_dependencies
        if dep_type == 'collapsed-dependencies':
            return sentence.collapsed_dependencies
        if dep_type == 'collapsed-ccprocessed-dependencies':
            return sentence.collapsed_ccprocessed_dependencies

    conc_lines = []
    if option.startswith('t'):
        if trees:
            options = '-s'
        else:
            options = '-t'
    if can_do_fast:
        speakr = ''
        tregex_engine(query = query, check_query = True, root = root)
        wholes = tregex_engine(query = query, 
                                options = ['-o', '-w', '-f', options], 
                                corpus = corpus,
                                preserve_case = True,
                                root = root)
        middle_column_result = tregex_engine(query = query, 
                                options = ['-o', options], 
                                corpus = corpus,
                                preserve_case = True,
                                root = root)
        for (f, whole), mid in zip(wholes, middle_column_result):
            reg = re.compile(r'(' + re.escape(mid) + r')', re.IGNORECASE)
            start, middle, end = re.split(reg, whole, 1)
            conc_lines.append([os.path.basename(f), speakr, start, middle, end])
    else:

        fs_to_conc = []
        for r, dirs, fs in os.walk(corpus):
            for f in fs:
                if not os.path.isfile(os.path.join(r, f)):
                    continue
                if not f.endswith('.txt') and not f.endswith('.xml'):
                    continue
                fs_to_conc.append(os.path.join(r, f))

        def normalise(concline):
            import re
            reg = re.compile(r'\([^ ]+')
            spaces = re.compile(r'\s+')
            concline = re.sub(reg, '', concline)
            concline = re.sub(spaces, ' ', concline)
            concline = concline.replace(')', '').replace('  ', ' ')
            return concline.strip()

        num_fs = len(fs_to_conc)
        for index, filepath in enumerate(fs_to_conc):
            f = os.path.basename(filepath)
            if num_fs > 1:
                if 'note' in kwargs.keys():
                    kwargs['note'].progvar.set((index) * 100.0 / num_fs)
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Extracting data from %s ...' % (thetime, f)
            if root:
                root.update()
            with open(filepath, "rb") as text:
                parsetreedict = {}
                data = text.read()
                if option.startswith('p') or option.startswith('l'):
                    if option.startswith('l'):
                        lstokens = pickle.load(open(filepath, 'rb'))
                        data = ' '.join(tokens)
                        data = data.split(' . ')
                    else:
                        lines = data.splitlines()
                    for l in lines:
                        m = re.compile(r'^(.*?)(' + query + r')(.*)$', re.IGNORECASE)
                        mat = re.search(m, l)
                        if mat:
                            conc_lines.append([f, '', mat.group(1), mat.group(2), mat.group(3)])
                    continue
                from corenlp_xml.document import Document
                corenlp_xml = Document(data)
                #corenlp_xml = Beautifulcorenlp_xml(data, parse_only=justsents)  
                if just_speakers:
                    for s in just_speakers:
                        parsetreedict[s] = []
                    sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                    #sents = [s for s in corenlp_xml.find_all('sentence') \
                    #if s.speakername.text.strip() in just_speakers]
                else:
                    sents = corenlp_xml.sentences
                nsents = len(sents)
                for i, s in enumerate(sents):
                    if num_fs == 1:
                        if 'note' in kwargs.keys():
                            kwargs['note'].progvar.set((index) * 100.0 / nsents)
                            if root:
                                root.update()
                    try:
                        speakr = s.speakername.strip()
                    except:
                        speakr = '' 
                    parsetree = s.parse_string
                    if option.startswith('t'):
                        parsetreedict[speakr].append(parsetree)
                        continue
                    elif option.startswith('d'): 
                        #right_dependency_grammar = s.find_all('dependencies', type=dep_type, limit = 1)
                        deps = get_deps(s, dep_type)
                        if dep_function == 'any' or dep_function is False:
                            wdsmatching = [l.dependent.text.strip() for l in deps.links \
                                           if re.match(query, l.dependent.text.strip())]
                        else:
                            comped = re.compile(dep_function, re.IGNORECASE)
                            #goodsent = any(re.match(query, l.dependent.text.strip()) for l in deps.links if re.match(comped, l.type.strip()))
                            wdsmatching = [l.dependent.text.strip() for l in deps.links \
                                           if re.match(comped, l.type.strip()) and \
                                           re.match(query, l.dependent.text.strip())]
                        # this is shit, needs indexing or something
                        for wd in wdsmatching:
                            line = normalise(parsetree)
                            start, middle, end = re.split(r'(' + wd + r')', line, 1)
                            conc_lines.append([f, speakr, start, middle, end])

                if option.startswith('t'):
                    for speakr, dt in parsetreedict.items():
                        trees_as_string = '\n'.join(dt)
                        if trees:
                            options = '-s'
                        else:
                            options = '-t'
                        with open('tmp.txt', 'w') as fo:
                            fo.write(trees_as_string.encode('utf-8', errors = 'ignore'))
                        tregex_engine(query = query, check_query = True, root = root)
                        wholes = tregex_engine(query = query, 
                                    options = ['-o', '-w', options], 
                                    corpus = 'tmp.txt',
                                    preserve_case = True,
                                    root = root)
                        middle_column_result = tregex_engine(query = query, 
                                    options = ['-o', options], 
                                    corpus = 'tmp.txt',
                                    preserve_case = True,
                                    root = root)
                        for whole, mid in zip(wholes, middle_column_result):
                            reg = re.compile(r'(' + re.escape(mid) + r')', re.IGNORECASE)
                            start, middle, end = re.split(reg, whole, 1)
                            conc_lines.append([f, speakr, start, middle, end])

    # does not keep results ordered!
    try:
        os.remove('tmp.txt')
    except:
        pass

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

    if series == []:
        if root:
            print 'No results found, sorry.'
            return
        else:
            raise ValueError("No results found, I'm afraid. Check your query and path.")

    df = pd.concat(series, axis = 1).T


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

    if 'note' in kwargs.keys():
        kwargs['note'].progvar.set(100)

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
