
def conc(corpus,
         search,
         query = 'any',
         show = 'w', 
         dep_type = 'collapsed-ccprocessed-dependencies',
         n = 100, 
         random = False, 
         split_sents = True,
         only_unique = True,
         window = 100,
         regex_nonword_filter = r'[A-Za-z0-9:_]',
         exclude = False,
         excludemode = 'any',
         searchmode = 'all',
         add_links = False,
         show_links = False,
         print_status = True,
         print_output = True,
         just_speakers = False,
         root = False,
         **kwargs): 
    """
    A concordancer for Tregex queries, CoreNLP dependencies, tokenised data or plaintext.

    :param corpus: path to corpus, subcorpus or file
    :type corpus: str
    :param search: criteria to match
    :type search: dict
    :param query: query string, if not using dict search
    :type query: str/list
    :param show: ordered list of what to return ['w', 'p'] will return 'cats/NNS'
    :type show: list
    :param window: how many characters of context on either side
    :type window: int
    :param random: randomise results
    :type random: bool
    :param split_sents: do sentence tokenisation before searching
    :type split_sents: bool
    :param dep_type: which dependency grammar to search
    :type dep_type: str
    :param n: number of results to return
    :type n: int
    :param regex_nonword_filter: a regular expression to exclude non-words
    :type regex_nonword_filter: raw string
    :param exclude: criteria to exclude when matching
    :type exclude: dict
    :param excludemode: exclude any exclude criterion, or all
    :type excludemode: str ('any'/'all')
    :param searchmode: only keep matches matching all search criteria
    :type searchmode: str ('any'/'all')
    :param just_speakers: limit search to particular speaker(s)
    :type just_speakers: list of speaker names
    :returns: Pandas DataFrame containing concordance lines
    """

    locs = locals()

    import corpkit
    import os
    import re
    import pandas as pd

    # shitty thing to hardcode
    pd.set_option('display.max_colwidth', 100)
    
    from pandas import DataFrame
    from time import localtime, strftime    
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    from corpkit.process import tregex_engine
    from corpkit.tests import check_pytex, check_dit
    from corpkit.depsearch import dep_searcher

    from corpkit.textprogressbar import TextProgressBar
    from corpkit.process import animator

    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    from corpkit.process import determine_datatype
    datatype, singlefile = determine_datatype(corpus)

    from corpkit.process import searchfixer
    search, search_iterable = searchfixer(search, query, datatype)

    from corpkit.process import parse_just_speakers
    just_speakers = parse_just_speakers(just_speakers, corpus)

    can_do_fast = False
    using_tregex = False
    if 't' in search.keys():
        using_tregex = True
        if just_speakers is False:
            can_do_fast = True


    # allow a b and c shorthand
    allowed_dep_types = {'a': 'basic-dependencies', 
                         'b': 'collapsed-dependencies',
                         'c': 'collapsed-ccprocessed-dependencies'}
    if dep_type in allowed_dep_types.keys():
        dep_type = allowed_dep_types[dep_type]

    def make_conc_lines_from_whole_mid(wholes, middle_column_result, speakr = False):
        if speakr is False:
            speakr = ''
        conc_lines = []
        # remove duplicates from results
        unique_wholes = []
        unique_middle_column_result = []
        duplicates = []
        for index, ((f, whole), mid) in enumerate(zip(wholes, middle_column_result)):
            if '-join-'.join([f, whole, mid]) not in duplicates:
                duplicates.append('-join-'.join([f, whole, mid]))
                unique_wholes.append([f, whole])
                unique_middle_column_result.append(mid)

        # split into start, middle and end, dealing with multiple occurrences
        for index, ((f, whole), mid) in enumerate(zip(unique_wholes, unique_middle_column_result)):
            reg = re.compile(r'([^a-zA-Z0-9-]|^)(' + re.escape(mid) + r')([^a-zA-Z0-9-]|$)', re.IGNORECASE | re.UNICODE)
            offsets = [(m.start(), m.end()) for m in re.finditer(reg,whole)]
            for offstart, offend in offsets:              
                start, middle, end = whole[0:offstart].strip(), whole[offstart:offend].strip(), whole[offend:].strip()
                conc_lines.append([os.path.basename(f), speakr, start, middle, end])
        return conc_lines

    # this is a list of lists
    conc_lines = []

    if using_tregex and 't' in show:
        options = '-s'
    else:
        options = '-t'
    if can_do_fast:
        speakr = ''
        tregex_engine(query = search['t'], check_query = True, root = root)
        wholes = tregex_engine(query = search['t'], 
                                options = ['-o', '-w', '-f', options], 
                                corpus = corpus,
                                preserve_case = True,
                                root = root)
        middle_column_result = tregex_engine(query = search['t'], 
                                options = ['-o', options], 
                                corpus = corpus,
                                preserve_case = True,
                                root = root)

        concs = make_conc_lines_from_whole_mid(wholes, middle_column_result)
        for l in concs:
            conc_lines.append(l)

    else:
        if 't' in search.keys():
            if search['t'].startswith(r'\b'):
                search['t'] = search['t'][2:]
            if search['t'].endswith(r'\b'):
                search['t'] = search['t'][:-2]

        # make list of filepaths
        fs_to_conc = []
        if singlefile:
            fs_to_conc.append(corpus)
        else:
            for r, dirs, fs in os.walk(corpus):
                for f in fs:
                    if not os.path.isfile(os.path.join(r, f)):
                        continue
                    if not f.endswith('.txt') and not f.endswith('.xml') and not f.endswith('.p'):
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

        tstr = '%d/%d' % (0, len(fs_to_conc))
        if print_status and not root and not singlefile:
            print '\n'
            p = animator(None, None, init = True, tot_string = tstr, length = len(fs_to_conc))
        numdone = 0
        for index, filepath in enumerate(fs_to_conc):
            f = os.path.basename(filepath)
            if num_fs > 1:
                if 'note' in kwargs.keys():
                    kwargs['note'].progvar.set((index) * 100.0 / num_fs)
                else:
                    if print_status:
                        tstr = '%d/%d' % (numdone, len(fs_to_conc))
                        animator(p, numdone, tstr)
            numdone += 1
            if root:
                root.update()
            with open(filepath, "r") as text:
                parsetreedict = {}
                data = text.read()
                if datatype == 'plaintext':
                    import chardet
                    enc = chardet.detect(data)
                    data = unicode(data, enc['encoding'], errors = 'ignore')
                if datatype == 'plaintext' or datatype == 'tokens':
                    if datatype == 'tokens':
                        import pickle
                        try:
                            lstokens = pickle.load(open(filepath, 'rb'))
                        except EOFError:
                            thetime = strftime("%H:%M:%S", localtime())
                            print '%s: File "%s" could not be opened.' % (thetime, os.path.basename(filepath))
                        data = ' '.join(lstokens)
                        if split_sents:
                            lines = data.split(' . ')
                        else:
                            lines = [data.replace('\n', '')]
                    else:
                        if split_sents:
                            lines = data.splitlines()
                        else:
                            lines = [data.replace('\n', '')]
                    for l in lines:
                        if split_sents:
                            m = re.compile(r'(?i)^(.*?)(\b' + query + r'\b)(.*)$', re.UNICODE)
                        else:
                            m = re.compile(r'(?i)(.{,%s})(\b' % window + query + r'\b)(.{,%s})' % window, re.UNICODE)
                        if split_sents:
                            mat = re.search(m, l)
                        else:
                            mat = re.findall(m, l)
                        if split_sents:
                            if mat:
                                last_num = len(mat.groups())
                                conc_lines.append([f, '', mat.group(1), mat.group(2), mat.group(last_num)])
                        else:
                            if mat:
                                #print len(mat)
                                for ent in mat:
                                    #print len(ent)
                                    last_num = len(ent) - 1
                                    conc_lines.append([f, '', ent[0], ent[1], ent[last_num]])

                if any(f.endswith('.xml') for f in fs_to_conc):
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
                    kkw = {}
                    if singlefile:
                        if print_status:
                            if not root:
                                print '\n'
                                tstr = '%d/%d' % (0, nsents)
                                p = animator(None, None, init = True, tot_string = tstr, length = nsents)
                                kkw = {'progbar' : p}

                    if 't' not in search and datatype == 'parse':
                        conclines = dep_searcher(sents, search, 
                                                 concordancing = True, 
                                                 show = show,
                                                 dep_type = dep_type,
                                                 exclude = exclude,
                                                 searchmode = searchmode,
                                                 excludemode = excludemode,
                                                 **kkw)
                        for line in conclines:
                            line.insert(0, f)
                            conc_lines.append(line)
                    else:   
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
                            if 't' in search:
                                parsetreedict[speakr].append(parsetree)
                                continue

                    if 't' in search:
                        for speakr, dt in parsetreedict.items():
                            trees_as_string = '\n'.join(dt)
                            if 't' in show:
                                options = '-s'
                            else:
                                options = '-t'
                            with open('tmp.txt', 'w') as fo:
                                fo.write(trees_as_string.encode('utf-8', errors = 'ignore'))
                            tregex_engine(query = search['t'], check_query = True, root = root)
                            wholes = tregex_engine(query = search['t'], 
                                        options = ['-o', '-w', options], 
                                        corpus = 'tmp.txt',
                                        preserve_case = True,
                                        root = root)
                            middle_column_result = tregex_engine(query = search['t'], 
                                        options = ['-o', options], 
                                        corpus = 'tmp.txt',
                                        preserve_case = True,
                                        root = root)

                            # add filenames back
                            wholes = [[f, w] for w in wholes]

                            concs = make_conc_lines_from_whole_mid(wholes, middle_column_result, speakr = speakr)
                            
                            for l in concs:
                                conc_lines.append(l)

    # does not keep results ordered!
    try:
        os.remove('tmp.txt')
    except:
        pass

    if have_ipython:
        clear_output()

    def uniquify(conc_lines):
        from collections import OrderedDict
        od = OrderedDict()
        unique_lines = []
        checking = []
        for index, (f, speakr, start, middle, end) in enumerate(conc_lines):
            joined = ' '.join([speakr, start, 'MIDDLEHERE:', middle, ':MIDDLEHERE', end])
            if joined not in checking:
                unique_lines.append(conc_lines[index])
            checking.append(joined)
        return unique_lines

    if only_unique:
        unique_results = uniquify(conc_lines)
    else:
        unique_results = conc_lines

    #make into series
    series = []
    pindex = 'f s l m r'.encode('utf-8').split()

    for fname, spkr, start, word, end in unique_results:
        spkr = unicode(spkr, errors = 'ignore')
        fname = os.path.basename(fname)
        #start = start.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        #word = word.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        #end = end.replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
        #spaces = ' ' * (maximum / 2 - (len(word) / 2))
        #new_word = spaces + word + spaces

        # the use of ascii here makes sure the string formats ok, but will also screw over
        # anyone doing non-english work. so, change to utf-8, then fix errors as they come
        # in the corpkit-gui "add_conc_lines_to_window" function
        series.append(pd.Series([fname.encode('ascii', errors = 'ignore'), \
                                 spkr.encode('ascii', errors = 'ignore'), \
                                 start.encode('ascii', errors = 'ignore'), \
                                 word.encode('ascii', errors = 'ignore'), \
                                 end.encode('ascii', errors = 'ignore')], index = pindex))

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

    if 'note' in kwargs.keys():
        kwargs['note'].progvar.set(100)

    if print_output:

        formatl = lambda x: "{0}".format(x[-window:])
        formatf = lambda x: "{0}".format(x[-20:])
        #formatr = lambda x: 
        formatr = lambda x: "{{:<{}s}}".format(df['r'].str.len().max()).format(x[:window])
        st = df.head(n).to_string(header = False, formatters={'l': formatl,
                                                              'r': formatr,
                                                              'f': formatf}).splitlines()
        
        # hack because i can't figure out formatter:
        rem = '\n'.join([re.sub('\s*\.\.\.\s*$', '', s) for s in st])
        print rem

    from corpkit.interrogation import Concordance
    output = Concordance(df)
    try:
        del locs['corpus']
    except:
        pass
    output.query = locs
    return output
