"""
corpkit: Interrogate a parsed corpus
"""

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC


def welcome_printer(search, cname, optiontext, return_it=False, printstatus=True):
    """Print welcome message"""
    from time import localtime, strftime
    if printstatus:
        thetime = strftime("%H:%M:%S", localtime())
        from corpkit.process import dictformat
        sformat = dictformat(search)
        welcome = ('\n%s: Interrogating %s ...\n          %s\n          ' \
                    'Query: %s\n          Interrogating corpus ... \n' % \
                  (thetime, cname, optiontext, sformat))
        if return_it:
            return welcome
        else:
            print(welcome)

def make_result_from_counter(cntr, subcorpora, show=False):
    import pandas as pd
    index = []
    data = []
    for k, v in cntr.items():
        index.append(tuple([k.metadata.get(x) for x in subcorpora]))
        data.append(k)
    ix = pd.MultiIndex.from_tuples(index)
    return pd.DataFrame(data, index=ix)

def fix_show_bit(show_bit):
    """
    Take a single search/show_bit type, return match
    """
    ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 's', 'a', 'e', 'c']
    starts = ['d', 'g', 'm', 'b', 'h', '+', '-', 'r', 'c']
    show_bit = show_bit.lstrip('n')
    show_bit = show_bit.lstrip('b')
    show_bit = list(show_bit)
    if show_bit[-1] not in ends:
        show_bit.append('w')
    if show_bit[0] not in starts:
        show_bit.insert(0, 'm')
    return ''.join(show_bit)

def add_adj_for_ngram(show, gramsize):
    """
    If there's a gramsize of more than 1, remake show
    for ngramming
    """
    if gramsize == 1:
        return show
    out = []
    for i in show:
        out.append(i)
    for i in range(1, gramsize):
        for bit in show:
            out.append('+%d%s' % (i, bit))
    return out

def fix_show(show, gramsize):
    """
    Lowercase anything in show and turn into list
    """
    if isinstance(show, list):
        show = [i.lower() for i in show]
    elif isinstance(show, STRINGTYPE):
        show = show.lower()
        show = [show]
    show = [fix_show_bit(i) for i in show]
    return add_adj_for_ngram(show, gramsize)

def interrogator(corpus, 
    search='w', 
    query='any',
    show='w',
    exclude=False,
    excludemode='any',
    searchmode='all',
    case_sensitive=False,
    save=False,
    subcorpora=False,
    just_metadata=False,
    skip_metadata=False,
    preserve_case=False,
    lemmatag=False,
    files_as_subcorpora=False,
    only_unique=False,
    only_format_match=True,
    multiprocess=False,
    spelling=False,
    regex_nonword_filter=r'[A-Za-z0-9]',
    gramsize=1,
    conc=False,
    maxconc=9999,
    window=None,
    no_closed=False,
    no_punct=True,
    discard=False,
    **kwargs):
    """
    Interrogate corpus, corpora, subcorpus and file objects.
    See corpkit.interrogation.interrogate() for docstring
    """


    conc = kwargs.get('do_concordancing', conc)
    quiet = kwargs.get('quiet', False)
    coref = kwargs.pop('coref', False)
    show_conc_metadata = kwargs.pop('show_conc_metadata', False)
    fsi_index = kwargs.pop('fsi_index', True)
    dep_type = kwargs.pop('dep_type', 'collapsed-ccprocessed-dependencies')

    nosubmode = subcorpora is None
    #todo: temporary
    #if getattr(corpus, '_dlist', False):
    #    subcorpora = 'file'

    # store kwargs and locs
    locs = locals().copy()
    locs.update(kwargs)
    locs.pop('kwargs', None)

    import codecs
    import signal
    import os
    from time import localtime, strftime
    from collections import Counter

    import pandas as pd
    from pandas import DataFrame, Series

    from corpkit.interrogation import Interrogation, Interrodict
    from corpkit.matches import Matches
    from corpkit.corpus import Datalist, Corpora, Corpus, File, Subcorpus
    from corpkit.process import (tregex_engine, get_deps, unsplitter, sanitise_dict, 
                                 animator, filtermaker, fix_search,
                                 pat_format, auto_usecols, format_tregex,
                                 make_conc_lines_from_whole_mid)
    from corpkit.other import as_regex
    from corpkit.dictionaries.process_types import Wordlist
    from corpkit.build import check_jdk
    from corpkit.conll import pipeline
    from corpkit.process import delete_files_and_subcorpora
    
    have_java = check_jdk()

    if isinstance(corpus, list):
        corpus = Datalist(corpus)

    # remake corpus without bad files and folders 
    corpus, skip_metadata, just_metadata = delete_files_and_subcorpora(corpus, skip_metadata, just_metadata)

    # so you can do corpus.interrogate('features/postags/wordclasses/lexicon')
    if search == 'features':
        search = 'v'
        query = 'any'
    if search in ['postags', 'wordclasses']:
        query = 'any'
        preserve_case = True
        show = 'p' if search == 'postags' else 'x'
        # use tregex if simple because it's faster
        # but use dependencies otherwise
        search = 't' if not subcorpora and not just_metadata and not skip_metadata and have_java else {'w': 'any'}
    if search == 'lexicon':
        search = 't' if not subcorpora and not just_metadata and not skip_metadata and have_java else {'w': 'any'}
        query = 'any'
        show = ['w']

    if not kwargs.get('cql') and isinstance(search, STRINGTYPE) and len(search) > 3:
        raise ValueError('search argument not recognised.')

    import re
    if regex_nonword_filter:
        is_a_word = re.compile(regex_nonword_filter)
    else:
        is_a_word = re.compile(r'.*')

    from traitlets import TraitError

    # convert cql-style queries---pop for the sake of multiprocessing
    cql = kwargs.pop('cql', None)
    if cql:
        from corpkit.cql import to_corpkit
        search, exclude = to_corpkit(search)

    def signal_handler(signal, _):
        """
        Allow pausing and restarting whn not in GUI
        """
        if root:
            return  
        import signal
        import sys
        from time import localtime, strftime
        signal.signal(signal.SIGINT, original_sigint)
        thetime = strftime("%H:%M:%S", localtime())
        INPUTFUNC('\n\n%s: Paused. Press any key to resume, or ctrl+c to quit.\n' % thetime)
        time = strftime("%H:%M:%S", localtime())
        print('%s: Interrogation resumed.\n' % time)
        signal.signal(signal.SIGINT, signal_handler)

    def ispunct(s):
        import string
        return all(c in string.punctuation for c in s)

    def uniquify(conc_lines):
        """get unique concordance lines"""
        from collections import OrderedDict
        unique_lines = []
        checking = []
        for index, (_, speakr, start, middle, end) in enumerate(conc_lines):
            joined = ' '.join([speakr, start, 'MIDDLEHERE:', middle, ':MIDDLEHERE', end])
            if joined not in checking:
                unique_lines.append(conc_lines[index])
            checking.append(joined)
        return unique_lines

    def compiler(pattern):
        """
        Compile regex or fail gracefully
        """
        if hasattr(pattern, 'pattern'):
            return pattern
        import re
        try:
            if case_sensitive:
                comped = re.compile(pattern)
            else:
                comped = re.compile(pattern, re.IGNORECASE)
            return comped
        except:
            import traceback
            import sys
            from time import localtime, strftime
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Query %s' % (thetime, error_message))
            if root:
                return 'Bad query'
            else:
                raise ValueError('%s: Query %s' % (thetime, error_message))

    def determine_search_func(show):
        """Figure out what search function we're using"""

        simple_tregex_mode = False
        statsmode = False
        tree_to_text = False
        search_trees = False
        optiontext = "Querying CONLL data"
            
        simp_crit = all(not i for i in [kwargs.get('tgrep'),
                                        files_as_subcorpora,
                                        subcorpora,
                                        just_metadata,
                                        skip_metadata])

        if search.get('t') and simp_crit:
            if have_java:
                simple_tregex_mode = True
            else:
                search_trees = 'tgrep'
            optiontext = 'Searching parse trees'

        elif datatype == 'conll':
        
            if any(i.endswith('t') for i in search.keys()):
                if have_java and not kwargs.get('tgrep'):
                    search_trees = 'tregex'
                else:
                    search_trees = 'tgrep'
                optiontext = 'Searching parse trees'
            elif any(i.endswith('v') for i in search.keys()):
                # either of these searchers now seems to work
                #seacher = get_stats_conll
                statsmode = True
                optiontext = 'General statistics'
            elif any(i.endswith('r') for i in search.keys()):
                optiontext = 'Distance from root'
            else:
                optiontext = 'Querying CONLL data'

        return optiontext, simple_tregex_mode, statsmode, tree_to_text, search_trees

    def get_tregex_values(show):
        """If using Tregex, set appropriate values

        - Check for valid query
        - Make 'any' query
        - Make list query
        """

        translated_option = 't'
        if isinstance(search['t'], Wordlist):
            search['t'] = list(search['t'])
        q = tregex_engine(corpus=False,
                          query=search.get('t'),
                          options=['-t'],
                          check_query=True,
                          root=root,
                          preserve_case=preserve_case
                         )

        # so many of these bad fixing loops!
        nshow = []
        for i in show:
            if i == 'm':
                nshow.append('w')
            else:
                nshow.append(i.lstrip('m'))
        show = nshow

        if q is False:
            if root:
                return 'Bad query', None
            else:
                return 'Bad query', None

        if isinstance(search['t'], list):
            regex = as_regex(search['t'], boundaries='line', case_sensitive=case_sensitive)
        else:
            regex = ''

        # listquery, anyquery, translated_option
        treg_dict = {'p': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'pl': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'x': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     't': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'o'],
                     'w': [r'/%s/ !< __' % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'c': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'C'],
                     'l': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'u': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'v']
                    }

        newshow = []

        listq, anyq, translated_option = treg_dict.get(show[0][-1].lower())
        newshow.append(translated_option)
        for item in show[1:]:
            _, _, noption = treg_dict.get(item.lower())
            newshow.append(noption)

        if isinstance(search['t'], list):
            search['t'] = listq
        elif search['t'] == 'any':   
            search['t'] = anyq
        return search['t'], newshow

    def correct_spelling(a_string):
        """correct spelling within a string"""
        if not spelling:
            return a_string
        from corpkit.dictionaries.word_transforms import usa_convert
        if spelling.lower() == 'uk':
            usa_convert = {v: k for k, v in list(usa_convert.items())}
        bits = a_string.split('/')
        for index, i in enumerate(bits):
            converted = usa_convert.get(i.lower(), i)
            if i.islower() or preserve_case is False:
                converted = converted.lower()
            elif i.isupper() and preserve_case:
                converted = converted.upper()
            elif i.istitle() and preserve_case:
                converted = converted.title()
            bits[index] = converted
        r = '/'.join(bits)
        return r

    def goodbye_printer(return_it=False, only_conc=False):
        """Say goodbye before exiting"""
        if not kwargs.get('printstatus', True):
            return
        thetime = strftime("%H:%M:%S", localtime())
        if only_conc:
            finalstring = '\n\n%s: Concordancing finished! %s results.' % (thetime, format(len(conc_df), ','))
        else:
            finalstring = '\n\n%s: Interrogation finished!' % thetime
            if countmode:
                finalstring += ' %s matches.' % format(tot, ',')
            else:
                finalstring += ' %s unique results, %s total occurrences.' % (format(numentries, ','), format(total_total, ','))
        if return_it:
            return finalstring
        else:
            print(finalstring)

    def get_conc_colnames(corpus,
                          fsi_index=False,
                          simple_tregex_mode=False):
    
        fields = []
        base = 'c f s l m r'
        
        if simple_tregex_mode:
            base = base.replace('f ', '')

        if fsi_index and not simple_tregex_mode:
            base = 'i ' + base
        
        if PYTHON_VERSION == 2:
            base = base.encode('utf-8').split()
        else:
            base = base.split() 

        if show_conc_metadata:
            from corpkit.build import get_all_metadata_fields
            meta = get_all_metadata_fields(corpus.path)

            if isinstance(show_conc_metadata, list):
                meta = [i for i in meta if i in show_conc_metadata]
            #elif show_conc_metadata is True:
            #    pass
            for i in sorted(meta):
                if i in ['speaker', 'sent_id', 'parse']:
                    continue
                if PYTHON_VERSION == 2:
                    base.append(i.encode('utf-8'))
                else:
                    base.append(i)
        return base

    def make_conc_obj_from_conclines(conc_results, fsi_index=False):
        """
        Turn conclines into DataFrame
        """
        from corpkit.interrogation import Concordance
        #fsi_place = 2 if fsi_index else 0

        all_conc_lines = []
        for sc_name, resu in sorted(conc_results.items()):
            if only_unique:
                unique_results = uniquify(resu)
            else:
                unique_results = resu
            #make into series
            for lin in unique_results:
                #spkr = str(spkr, errors = 'ignore')
                #if not subcorpora:
                #    lin[fsi_place] = lin[fsi_place]
                #lin.insert(fsi_place, sc_name)

                if len(lin) < len(conc_col_names):
                    diff = len(conc_col_names) - len(lin)
                    lin.extend(['none'] * diff)

                all_conc_lines.append(Series(lin, index=conc_col_names))

        try:
            conc_df = pd.concat(all_conc_lines, axis=1).T
        except ValueError:
            return
        
        if all(x == '' for x in list(conc_df['s'].values)) or \
           all(x == 'none' for x in list(conc_df['s'].values)):
            conc_df.drop('s', axis=1, inplace=True)

        locs['corpus'] = corpus.name

        if maxconc:
            conc_df = Concordance(conc_df[:maxconc])
        else:
            conc_df = Concordance(conc_df)
        try:
            conc_df.query = locs
        except AttributeError:
            pass
        return conc_df

    def lowercase_result(res):
        """      
        Take any result and do spelling/lowercasing if need be

        todo: remove lowercase and change name
        """
        if not res or statsmode:
            return res
        # this is likely broken, but spelling in interrogate is deprecated anyway
        if spelling:
            res = [correct_spelling(r) for r in res]
        return res

    def postprocess_concline(line, fsi_index=False, conc=False):
        # todo: are these right?
        if not conc:
            return line
        subc, star, en = 0, 2, 5
        if fsi_index:
            subc, star, en = 2, 4, 7
        if not preserve_case:
            line[star:en] = [str(x).lower() for x in line[star:en]]
        if spelling:
            line[star:en] = [correct_spelling(str(b)) for b in line[star:en]]
        return line

    def make_progress_bar(corpus_iter):
        """generate a progress bar"""

        total_files = len(corpus_iter)

        par_args = {'printstatus': kwargs.get('printstatus', True),
                    'root': root, 
                    'note': note,
                    'quiet': quiet,
                    'length': total_files,
                    'startnum': kwargs.get('startnum'),
                    'denom': kwargs.get('denominator', 1)}

        term = None
        if kwargs.get('paralleling', None) is not None:
            from blessings import Terminal
            term = Terminal()
            par_args['terminal'] = term
            par_args['linenum'] = kwargs.get('paralleling')

        if in_notebook:
            par_args['welcome_message'] = welcome_message

        outn = kwargs.get('outname', '')
        if outn:
            outn = getattr(outn, 'name', outn)
            outn = outn + ': '

        tstr = '%s%d/%d' % (outn, current_iter, total_files)
        p = animator(None, None, init=True, tot_string=tstr, **par_args)
        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
        animator(p, current_iter, tstr, **par_args)
        return p, outn, total_files, par_args

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')
    language_model = kwargs.get('language_model')

    # set up pause method
    original_sigint = signal.getsignal(signal.SIGINT)
    if kwargs.get('paralleling', None) is None:
        if not root:
            original_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal_handler)

    # find out about concordancing
    only_conc = False
    no_conc = False
    if conc is False:
        no_conc = True
    if isinstance(conc, str) and conc.lower() == 'only':
        only_conc = True
        no_conc = False
    numconc = 0

    # wipe non essential class attributes to not bloat query attrib
    if isinstance(corpus, Corpus):
        import copy
        corpus = copy.copy(corpus)
        for k, v in corpus.__dict__.items():
            if isinstance(v, (Interrogation, Interrodict)):
                corpus.__dict__.pop(k, None)

    # convert path to corpus object
    if not isinstance(corpus, (Corpus, Corpora, Subcorpus, File, Datalist)):
        if not multiprocess and not kwargs.get('outname'):
            corpus = Corpus(corpus, print_info=False)

    # figure out how the user has entered the query and show, and normalise
    from corpkit.process import searchfixer
    search = searchfixer(search, query)
    show = fix_show(show, gramsize)
    locs['show'] = show

    # instantiate lemmatiser if need be
    lem_instance = False
    if any(i.endswith('l') for i in show) and isinstance(search, dict) and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lem_instance = WordNetLemmatizer()

    search = fix_search(search, case_sensitive=case_sensitive, root=root)
    exclude = fix_search(exclude, case_sensitive=case_sensitive, root=root)

    datatype = getattr(corpus, 'datatype', 'conll')
    singlefile = getattr(corpus, 'singlefile', False)
    level = getattr(corpus, 'level', 'c')


    # Determine the search function to be used #
    optiontext, simple_tregex_mode, statsmode, tree_to_text, search_trees = determine_search_func(show)

    cname = corpus.name

    locs['search'] = search
    locs['exclude'] = exclude
    locs['query'] = query
    locs['show'] = show
    locs['corpus'] = corpus
    locs['multiprocess'] = multiprocess
    locs['print_info'] = kwargs.get('printstatus', True)
    locs['subcorpora'] = subcorpora
    locs['cname'] = cname
    locs['optiontext'] = optiontext

    if multiprocess:
        signal.signal(signal.SIGINT, original_sigint)
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)

    # get corpus metadata
    
    if isinstance(save, STRINGTYPE):
        savename = corpus.name + '-' + save
    if save is True:
        raise ValueError('save must be str, not bool.')
        
    # store all results in here
    from collections import defaultdict, Counter
    results = []
    count_results = defaultdict(list)
    conc_results = defaultdict(list)

    # check if just counting, turn off conc if so
    countmode = 'c' in show or 'mc' in show
    if countmode:
        no_conc = True
        only_conc = False
    # where we are at in interrogation
    current_iter = 0

    # multiprocessing progress bar
    denom = kwargs.get('denominator', 1)
    startnum = kwargs.get('startnum', 0)
    
    # no conc for statsmode
    if statsmode:
        no_conc = True
        only_conc = False
        conc = False

    # Set some Tregex-related values
    translated_option = False
    if search.get('t'):
        query, translated_option = get_tregex_values(show)
        if query == 'Bad query' and translated_option is None:
            if root:
                return 'Bad query'
            else:
                return
    # more tregex options
    if tree_to_text:
        treg_q = r'ROOT << __'
        op = ['-o', '-t', '-w', '-f']
    elif simple_tregex_mode:
        treg_q = search['t']
        op = ['-%s' % i for i in translated_option] + ['-o', '-f']

    try:
        nam = get_ipython().__class__.__name__
        if nam == 'ZMQInteractiveShell':
            in_notebook = True
        else:
            in_notebook = False
    except TraitError:
        in_notebook = False
    except ImportError:
        in_notebook = False
    # caused in newest ipython
    except AttributeError:
        in_notebook = False
    except NameError:
        in_notebook = False

    lemtag = False
    if search.get('t'):
        from corpkit.process import gettag
        lemtag = gettag(search.get('t'), lemmatag)

    usecols = auto_usecols(search, exclude, show, kwargs.pop('usecols', None), coref=coref)

    # make the iterable, which should be very simple now
    corpus_iter = corpus.all_files if corpus.all_files else corpus

    # print welcome message
    welcome_message = welcome_printer(search, cname, optiontext, return_it=in_notebook, printstatus=kwargs.get('printstatus', True))

    # create a progress bar
    p, outn, total_files, par_args = make_progress_bar(corpus_iter)

    if conc:
        conc_col_names = get_conc_colnames(corpus,
                                           fsi_index=fsi_index,
                                           simple_tregex_mode=False)


    for f in corpus_iter:

        filepath, corefs = f.path, coref

        res = pipeline(filepath, search=search, show=show,
                                 dep_type=dep_type,
                                 exclude=exclude,
                                 excludemode=excludemode,
                                 searchmode=searchmode,
                                 case_sensitive=case_sensitive,
                                 conc=False,
                                 only_format_match=only_format_match,
                                 gramsize=gramsize,
                                 no_punct=no_punct,
                                 no_closed=no_closed,
                                 window=window,
                                 filename=f.path,
                                 coref=corefs,
                                 countmode=countmode,
                                 maxconc=(maxconc, numconc),
                                 is_a_word=is_a_word,
                                 subcorpora=subcorpora,
                                 show_conc_metadata=show_conc_metadata,
                                 just_metadata=just_metadata,
                                 skip_metadata=skip_metadata,
                                 fsi_index=fsi_index,
                                 translated_option=translated_option,
                                 statsmode=statsmode,
                                 preserve_case=preserve_case,
                                 usecols=usecols,
                                 search_trees=search_trees,
                                 lem_instance=lem_instance,
                                 lemtag=lemtag,
                                 fobj=f,
                                 corpus_name=getattr(corpus, 'corpus_name', False),
                                 **kwargs)
            
        if res == 'Bad query':
            return 'Bad query'

        results += res

        # update progress bar
        current_iter += 1
        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
        animator(p, current_iter, tstr, **par_args)

    matches = Matches(results, corpus)

    querybits = {'search': search,
                  'exclude': exclude,
                  'show': show,
                  'subcorpora': subcorpora}

    interro = Interrogation(data=matches, corpus=corpus, totals=len(matches), query=querybits)
    
    signal.signal(signal.SIGINT, original_sigint)

    return matches[:]
