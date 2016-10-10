from __future__ import print_function

from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

def quickview(results, n=25):
    """
    View top n results as painlessly as possible.

    :param results: Interrogation data
    :type results: :class:``corpkit.interrogation.Interrogation``
    :param n: Show top *n* results
    :type n: int
    :returns: None
    """

    import corpkit
    import pandas as pd
    import numpy as np
    import os
    import corpkit
    from corpkit.interrogation import Interrogation

    # handle dictionaries too:
    dictpath = 'dictionaries'
    savedpath = 'saved_interrogations'

    # too lazy to code this properly for every possible data type:
    if n == 'all':
        n = 9999

    dtype = corpkit.interrogation.Interrogation

    if isinstance(results, STRINGTYPE):
        if os.path.isfile(os.path.join(dictpath, results)):
            from corpkit.other import load
            results = load(results, loaddir=dictpath)

        elif os.path.isfile(os.path.join(savedpath, results)):
            from corpkit.other import load
            results = load(results)
        else:
            raise OSError('File "%s" not found.' % os.path.abspath(results))

    elif isinstance(results, Interrogation):
        if getattr(results, 'results'):
            datatype = results.results.iloc[0,0].dtype
            if datatype == 'int64':
                option = 't'
            else:
                option = '%'
            rq = results.query.get('operation', False)
            if rq:
                rq = rq.lower()
                if rq.startswith('k'):
                    option = 'k'
                if rq.startswith('%'):
                    option = '%'
                if rq.startswith('/'):
                    option = '/'
            try:
                the_list = list(results.results.columns)[:n]
            except:
                the_list = list(results.results.index)[:n]
        else:
            print(results.totals)
            return
    else:
        raise ValueError('Results not recognised.')

    # get longest word length for justification
    longest = max([len(i) for i in the_list])

    for index, entry in enumerate(the_list):
        if option == 't':
            if isinstance(results, Interrogation):
                if hasattr(results, 'results'):
                    to_get_from = results.results
                    tot = to_get_from[entry].sum()
                else:
                    to_get_from = results.totals
                    tot = to_get_from[entry]
            print('%s: %s (n=%d)' %(str(index).rjust(3), entry.ljust(longest), tot))
        elif option == '%' or option == '/':
            if isinstance(results, Interrogation):
                to_get_from = results.totals
                tot = to_get_from[entry]
                totstr = "%.3f" % tot
                print('%s: %s (%s%%)' % (str(index).rjust(3), entry.ljust(longest), totstr)) 
            elif dtype == corpkit.interrogation.Results:
                print('%s: %s (%s)' %(str(index).rjust(3), entry.ljust(longest), option))
            elif dtype == corpkit.interrogation.Totals:
                tot = results[entry]
                totstr = "%.3f" % tot
                print('%s: %s (%s%%)' % (str(index).rjust(3), entry.ljust(longest), totstr)) 
        elif option == 'k':
            print('%s: %s (l/l)' %(str(index).rjust(3), entry.ljust(longest)))
        else:
            print('%s: %s' %(str(index).rjust(3), entry.ljust(longest)))

def concprinter(dataframe, kind='string', n=100,
                window=35, columns='all', **kwargs):
    """
    Print conc lines nicely, to string, latex or csv

    :param df: concordance lines from :class:``corpkit.corpus.Concordance``
    :type df: pd.DataFame 
    :param kind: output format
    :type kind: str ('string'/'latex'/'csv')
    :param n: Print first n lines only
    :type n: int/'all'
    :returns: None
    """
    import corpkit

    df = dataframe.copy().fillna('')

    if n > len(df):
        n = len(df)
    if not kind.startswith('l') and kind.startswith('c') and kind.startswith('s'):
        raise ValueError('kind argument must start with "l" (latex), "c" (csv) or "s" (string).')
    import pandas as pd

    # shitty thing to hardcode
    pd.set_option('display.max_colwidth', 100)

    if isinstance(n, int):
        to_show = df.head(n)
    elif n is False:
        to_show = df
    elif n == 'all':
        to_show = df
    else:
        raise ValueError('n argument "%s" not recognised.' % str(n))

    def resize_by_window_size(df, window):
        df.is_copy = False
        df['l'] = df['l'].str.slice(start=-window, stop=None)
        df['l'] = df['l'].str.rjust(window)
        df['r'] = df['r'].str.slice(start=0, stop=window)
        df['r'] = df['r'].str.ljust(window)
        df['m'] = df['m'].str.ljust(df['m'].str.len().max())
        return df

    to_show.is_copy = False
    if window:
        to_show = resize_by_window_size(to_show, window)

    if columns != 'all':
        to_show = to_show[columns]

    if kind.startswith('s'):
        functi = pd.DataFrame.to_string
    if kind.startswith('l'):
        functi = pd.DataFrame.to_latex
    if kind.startswith('c'):
        functi = pd.DataFrame.to_csv
        kwargs['sep'] = ','
    if kind.startswith('t'):
        functi = pd.DataFrame.to_csv
        kwargs['sep'] = '\t'

    # automatically basename subcorpus for show
    if 'c' in list(df.columns):
        import os
        df['c'] = df['c'].apply(os.path.basename)

    if 'f' in list(df.columns):
        import os
        df['f'] = df['f'].apply(os.path.basename)

    return_it = kwargs.pop('return_it', False)
    print_it = kwargs.pop('print_it', True)

    if return_it:
        return functi(to_show, header=kwargs.get('header', False), **kwargs)
    else:
        print('\n')
        print(functi(to_show, header=kwargs.get('header', False), **kwargs))
        print('\n')

def save(interrogation, savename, savedir='saved_interrogations', **kwargs):
    """
    Save an interrogation as pickle to *savedir*.

       >>> interro_interrogator(corpus, 'words', 'any')
       >>> save(interro, 'savename')

    will create ``./saved_interrogations/savename.p``

    :param interrogation: Corpus interrogation to save
    :type interrogation: corpkit interogation/edited result
    
    :param savename: A name for the saved file
    :type savename: str
    
    :param savedir: Relative path to directory in which to save file
    :type savedir: str
    
    :param print_info: Show/hide stdout
    :type print_info: bool
    
    :returns: None
    """

    try:
        import cPickle as pickle
    except ImportError:
        import pickle as pickle
    import os
    from time import localtime, strftime
    import corpkit
    from corpkit.process import makesafe, sanitise_dict

    from corpkit.interrogation import Interrogation
    from corpkit.corpus import Corpus, Datalist

    print_info = kwargs.get('print_info', True)

    def make_filename(interrogation, savename):
        """create a filename"""
        if '/' in savename:
            return savename

        firstpart = ''
        if savename.endswith('.p'):
            savename = savename[:-2]    
        savename = makesafe(savename, drop_datatype=False, hyphens_ok=True)
        if not savename.endswith('.p'):
            savename = savename + '.p'
        if hasattr(interrogation, 'query') and isinstance(interrogation.query, dict):
            corpus = interrogation.query.get('corpus', False)
            if corpus:
                if isinstance(corpus, STRINGTYPE):
                    firstpart = corpus
                else:
                    if isinstance(corpus, Datalist):
                        firstpart = Corpus(corpus).name
                    if hasattr(corpus, 'name'):
                        firstpart = corpus.name
                    else:
                        firstpart = ''
        
        firstpart = os.path.basename(firstpart)

        if firstpart:
            return firstpart + '-' + savename
        else:
            return savename

    savename = make_filename(interrogation, savename)

    # delete unpicklable parts of query
    if hasattr(interrogation, 'query') and isinstance(interrogation.query, dict):
        iq = interrogation.query
        if iq:
            from types import ModuleType, FunctionType, BuiltinMethodType, BuiltinFunctionType
            interrogation.query = {k: v for k, v in iq.items() if not isinstance(v, ModuleType) \
                and not isinstance(v, FunctionType) \
                and not isinstance(v, BuiltinFunctionType) \
                and not isinstance(v, BuiltinMethodType)}
        else:
            iq = {}

    if savedir and not '/' in savename:
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        fullpath = os.path.join(savedir, savename)
    else:
        fullpath = savename

    while os.path.isfile(fullpath):
        selection = INPUTFUNC(("\nSave error: %s already exists in %s.\n\n" \
                "Type 'o' to overwrite, or enter a new name: " % (savename, savedir)))

        if selection == 'o' or selection == 'O':
            os.remove(fullpath)
        else:
            selection = selection.replace('.p', '')
            if not selection.endswith('.p'):
                selection = selection + '.p'
                fullpath = os.path.join(savedir, selection)

    if hasattr(interrogation, 'query'):
        interrogation.query = sanitise_dict(interrogation.query)

    with open(fullpath, 'wb') as fo:
        pickle.dump(interrogation, fo)
    
    time = strftime("%H:%M:%S", localtime())
    if print_info:
        print('\n%s: Data saved: %s\n' % (time, fullpath))

def load(savename, loaddir='saved_interrogations'):
    """
    Load saved data into memory:

        >>> loaded = load('interro')

    will load ``./saved_interrogations/interro.p`` as loaded

    :param savename: Filename with or without extension
    :type savename: str
    
    :param loaddir: Relative path to the directory containg *savename*
    :type loaddir: str
    
    :param only_concs: Set to True if loading concordance lines
    :type only_concs: bool

    :returns: loaded data
    """    
    try:
        import cPickle as pickle
    except ImportError:
        import pickle as pickle
    import os
    if not savename.endswith('.p'):
        savename = savename + '.p'

    if loaddir:
        if '/' not in savename:
            fullpath = os.path.join(loaddir, savename)
        else:
            fullpath = savename
    else:
        fullpath = savename

    with open(fullpath, 'rb') as fo:
        data = pickle.load(fo)
    return data

def loader(savedir='saved_interrogations'):
    """Show a list of data that can be loaded, and then load by user input of index"""
    import glob
    import os
    import corpkit
    from corpkit.other import load
    fs = [i for i in glob.glob(r'%s/*' % savedir) if not os.path.basename(i).startswith('.')]
    string_to_show = '\nFiles in %s:\n' % savedir
    most_digits = max([len(str(i)) for i, j in enumerate(fs)])
    for index, fname in enumerate(fs):
        string_to_show += str(index).rjust(most_digits) + ':\t' + os.path.basename(fname) + '\n'
    print(string_to_show)
    INPUTFUNC('Enter index of item to load: ')
    if ' ' in index or '=' in index:
        if '=' in index:
            index = index.replace(' = ', ' ')
            index = index.replace('=', ' ')
        varname, ind = index.split(' ', 1)
        globals()[varname] = load(os.path.basename(fs[int(ind)]))
        print("%s = %s. Don't do this again." % (varname, os.path.basename(fs[int(ind)])))
        return
    try:
        index = int(index)
    except:
        raise ValueError('Selection not recognised.')
    return load(os.path.basename(fs[index]))

def new_project(name, loc='.', **kwargs):
    """Make a new project in ``loc``.

    :param name: A name for the project
    :type name: str
    :param loc: Relative path to directory in which project will be made
    :type loc: str

    :returns: None
    """
    import corpkit
    import os
    import shutil
    import stat
    import platform
    from time import strftime, localtime

    root = kwargs.get('root', False)

    path_to_corpkit = os.path.dirname(corpkit.__file__)
    thepath, corpkitname = os.path.split(path_to_corpkit)
    
    # make project directory
    fullpath = os.path.join(loc, name)
    try:
        os.makedirs(fullpath)
    except:
        if root:
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Directory already exists: "%s"' %( thetime, fullpath))
            return
        else:
            raise
    # make other directories
    dirs_to_make = ['data', 'images', 'saved_interrogations', \
      'saved_concordances', 'dictionaries', 'exported', 'logs']
    #subdirs_to_make = ['dictionaries', 'saved_interrogations']
    for directory in dirs_to_make:
        os.makedirs(os.path.join(fullpath, directory))
    #for subdir in subdirs_to_make:
        #os.makedirs(os.path.join(fullpath, 'data', subdir))
    # copy the bnc dictionary to dictionaries

    def resource_path(relative):
        import os
        return os.path.join(os.environ.get("_MEIPASS2",os.path.abspath(".")),relative)

    corpath = os.path.dirname(corpkit.__file__)
    if root:
        corpath = corpath.replace('/lib/python2.7/site-packages.zip/corpkit', '')
    baspat = os.path.dirname(corpath)
    dicpath = os.path.join(corpath, 'dictionaries')
    try:
        shutil.copy(os.path.join(dicpath, 'bnc.p'), os.path.join(fullpath, 'dictionaries'))
    except:
        # find out why bnc not found!
        if root:
            try:
                shutil.copy(resource_path(os.path.join('dictionaries', 'bnc.p')), os.path.join(fullpath, 'dictionaries'))
            except:
                pass

    if not root:
        thetime = strftime("%H:%M:%S", localtime())
        print('\n%s: New project created: "%s"\n' % (thetime, name))
        
def load_all_results(data_dir='saved_interrogations', **kwargs):
    """
    Load every saved interrogation in data_dir into a dict:

        >>> r = load_all_results()

    :param data_dir: path to saved data
    :type data_dir: str

    :returns: dict with filenames as keys
    """
    import os
    from time import localtime, strftime
    from other import load
    from process import makesafe

    root = kwargs.get('root', False)
    note = kwargs.get('note', False)    
    
    datafiles = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) \
                 and f.endswith('.p')]

    # just load first n (for testing)
    if kwargs.get('n', False):
        datafiles = datafiles[:kwargs['n']]

    output = {}

    l = 0
    for index, f in enumerate(datafiles):    
        try:
            loadname = f.replace('.p', '')
            output[loadname] = load(f, loaddir = data_dir)
            time = strftime("%H:%M:%S", localtime())
            print('%s: %s loaded as %s.' % (time, f, makesafe(loadname)))
            l += 1
        except:
            time = strftime("%H:%M:%S", localtime())
            print('%s: %s failed to load. Try using load to find out the matter.' % (time, f))
        if note and len(datafiles) > 3:
            note.progvar.set((index + 1) * 100.0 / len(datafiles))
        if root:
            root.update()
    time = strftime("%H:%M:%S", localtime())
    print('%s: %d interrogations loaded from %s.' % (time, l, os.path.basename(data_dir)))
    from interrogation import Interrodict
    return Interrodict(output)

def texify(series, n=20, colname='Keyness', toptail=False, sort=False):
    """turn a series into a latex table"""
    import corpkit
    import pandas as pd
    if sort:
        df = pd.DataFrame(series.order(ascending=False))
    else:
        df = pd.DataFrame(series)
    df.columns = [colname]
    if not toptail:
        return df.head(n).to_latex()
    else:
        comb = pd.concat([df.head(n), df.tail(n)])
        longest_word = max([len(w) for w in list(comb.index)])
        tex = ''.join(comb.to_latex()).split('\n')
        linelin = len(tex[0])
        try:
            newline = (' ' * (linelin / 2)) + ' &'
            newline_len = len(newline)
            newline = newline + (' ' * (newline_len - 1)) + r'\\'
            newline = newline.replace(r'    \\', r'... \\')
            newline = newline.replace(r'   ', r'... ', 1)
        except:
            newline = r'...    &     ... \\'
        tex = tex[:n+4] + [newline] + tex[n+4:]
        tex = '\n'.join(tex)
        return tex


def as_regex(lst, boundaries='w', case_sensitive=False, inverse=False, compile=False):
    """Turns a wordlist into an uncompiled regular expression

    :param lst: A wordlist to convert
    :type lst: list

    :param boundaries:
    :type boundaries: str -- 'word'/'line'/'space'; tuple -- (leftboundary, rightboundary)
    
    :param case_sensitive: Make regular expression case sensitive
    :type case_sensitive: bool
    
    :param inverse: Make regular expression inverse matching
    :type inverse: bool

    :returns: regular expression as string
    """
    import corpkit

    import re
    if case_sensitive:
        case = r''
    else:
        case = r'(?i)'
    if not boundaries:
        boundary1 = r''
        boundary2 = r''
    elif isinstance(boundaries, (tuple, list)):
        boundary1 = boundaries[0]
        boundary2 = boundaries[1]
    else:
        if boundaries.startswith('w') or boundaries.startswith('W'):
            boundary1 = r'\b'
            boundary2 = r'\b'
        elif boundaries.startswith('l') or boundaries.startswith('L'):
            boundary1 = r'^'
            boundary2 = r'$'
        elif boundaries.startswith('s') or boundaries.startswith('S'):
            boundary1 = r'\s'
            boundary2 = r'\s'
        else:
            raise ValueError('Boundaries not recognised. Use a tuple for custom start and end boundaries.')
    if inverse:
        inverser1 = r'(?!'
        inverser2 = r')'
    else:
        inverser1 = r''
        inverser2 = r''

    if inverse:
        joinbit = r'%s|%s' % (boundary2, boundary1)
        as_string = case + inverser1 + r'(?:' + boundary1 + joinbit.join(sorted(list(set([re.escape(w) for w in lst])))) + boundary2 + r')' + inverser2
    else:
        as_string = case + boundary1 + inverser1 + r'(?:' + r'|'.join(sorted(list(set([re.escape(w) for w in lst])))) + r')' + inverser2 + boundary2
    if compile:
        return re.compile(as_string)
    else:
        return as_string

def make_multi(interrogation, indexnames=None):
    """
    make pd.multiindex version of an interrogation (for pandas geeks)

    :param interrogation: a corpkit interrogation
    :type interrogation: a corpkit interrogation, pd.DataFrame or pd.Series

    :param indexnames: pass in a list of names for the multiindex;
                       leave as None to get them if possible from interrogation
                       use False to explicitly not get them
    :type indexnames: list of strings/None/False
    :returns: pd.DataFrame with multiindex"""

    # get proper names for index if possible
    from corpkit.constants import transshow, transobjs

    import numpy as np
    import pandas as pd

    # if it's an interrodict, we want to make it into a single df
    import corpkit
    from corpkit.interrogation import Interrodict, Interrogation
    
    seriesmode = False
    
    if isinstance(interrogation, (Interrodict, dict)):
        import pandas as pd
        import numpy as np

        flat = [[], [], []]
        
        for name, data in list(interrogation.items()):
            for subcorpus in list(data.results.index):
                # make multiindex
                flat[0].append(name)
                flat[1].append(subcorpus)
                # add results
                flat[2].append(data.results.ix[subcorpus])

        flat[0] = np.array(flat[0])
        flat[1] = np.array(flat[1])

        df = pd.DataFrame(flat[2], index=flat[:2])
        if indexnames is None:
            indexnames = ['Corpus', 'Subcorpus']
        df.index.names = indexnames
        df = df.fillna(0)
        df = df.T
        df[('Total', 'Total')] = df.sum(axis=1)
        df = df.sort_values(by=('Total', 'Total'), 
                            ascending=False).drop(('Total', 'Total'),
                            axis=1).T
        try:
            df = df.astype(int)
        except:
            pass
        return Interrogation(df, df.sum(axis=1), getattr(interrogation, 'query', None))
    # determine datatype, get df and cols
    rows=False
    if isinstance(interrogation, pd.core.frame.DataFrame):
        df = interrogation
        cols = list(interrogation.columns)
        rows = list(interrogation.index)
    elif isinstance(interrogation, pd.core.series.Series):
        cols = list(interrogation.index)
        seriesmode = True
        df = pd.DataFrame(interrogation).T
    elif isinstance(interrogation, Interrogation):
        df = interrogation.results
        if isinstance(df, pd.core.series.Series):
            cols = list(df.index)
            seriesmode = True
            df = pd.DataFrame(df).T
        else:
            cols = list(df.columns)
            rows = list(df.index)

        # set indexnames if we have them
        if indexnames is not False:
            if interrogation.query.get('show'):
                indexnames = []
                ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 's']
                for showval in interrogation.query['show']:
                    if len(showval) == 1:
                        if showval in ends:
                            showval = 'm' + showval
                        else:
                            showval = showval + 'w'
                    a = transobjs.get(showval[0], showval[0])
                    b = transshow.get(showval[-1], showval[-1])
                    indexstring = '%s %s' % (a, b.lower())
                    indexnames.append(indexstring)
            else:
                indexnames = False

    # split column names on slash
    for index, i in enumerate(cols):
        cols[index] = i.split('/')

    # make numpy arrays
    arrays = []
    for i in range(len(cols[0])):
        arrays.append(np.array([x[i] for x in cols]))
    
    # make output df, add names if we have them
    newdf = pd.DataFrame(df.T.as_matrix(), index=arrays).T
    if indexnames:
        newdf.columns.names = indexnames

    if rows:
        newdf.index = rows
    
    pd.set_option('display.multi_sparse', False)
    totals = newdf.sum(axis=1)
    query = interrogation.query
    conco = getattr(interrogation, 'concordance', None)
    return Interrogation(newdf, totals, query, conco)

def topwords(self, datatype='n', n=10, df=False, sort=True, precision=2):

    """Show top n results in each corpus alongside absolute or relative frequencies.

    :param relative: show abs/rel frequencies
    :type relative: bool
    :param n: number of result to show
    :type n: int
    :param df: return a DataFrame instead of a string
    :type df: bool
    :param sort: sort or leave as is
    :type sort: bool, 'reverse'
    :param precision: float precision
    :type precision: int

    :Example:

    >>> data.topwords(n = 5)
        TBT            %   UST            %   WAP            %   WSJ            %
        health     25.70   health     15.25   health     19.64   credit      9.22
        security    6.48   cancer     10.85   security    7.91   health      8.31
        cancer      6.19   heart       6.31   cancer      6.55   downside    5.46
        flight      4.45   breast      4.29   credit      4.08   inflation   3.37
        safety      3.49   security    3.94   safety      3.26   cancer      3.12

    :returns: None
    """
    import corpkit
    from corpkit.interrogation import Interrogation, Interrodict
    import pandas as pd
    pd.set_option('display.float_format', lambda x: format(x, '.%df' % precision))
    strings = []
    if sort == 'reverse':
        ascend = True
        sort = True
    else:
        ascend = False

    if datatype.lower().startswith('n'):
        operation = 'n'
    if datatype.lower().startswith('k'):
        operation = 'k'
    else:
        operation = '%'
    if isinstance(self, corpkit.interrogation.Interrodict):
        to_iterate = self.items()
    else:
        if sort is True:
            to_iterate = [(x, self.results.ix[x].sort_values(ascending=ascend)) \
                          for x in list(self.results.index)]
        else:
            to_iterate = [(x, self.results.ix[x]) for x in list(self.results.index)]
    for name, data in to_iterate:
        if isinstance(self, corpkit.interrogation.Interrodict):
            if sort is True:
                data = data.results.sum().sort_values(ascending=ascend)
            else:
                data = data.results.sum()
        # todo: if already float, don't do this operation...
        if operation == '%':
            data = data * 100.0 / data.sum()
        if operation == 'n':
            data = data.astype(float)
        if df:
            data.index.name = name
            df1 = pd.DataFrame({'Result': list(data.index)[:n], operation: list(data)[:n]})
            df1 = df1[['Result', operation]]
            strings.append(df1)
            #ser1 = pd.Series(list(data.index), index = range(len(data)))[:n]
            #ser2 = pd.Series(list(data), index = range(len(data)))[:n]
            #ser1.name = 'Result'
            #ser2.name = operation
            #strings.append(ser1)
            #strings.append(ser2)
        else:
            as_str = data[:n].to_string(header=False)
            linelen = len(as_str.splitlines()[1])
            strings.append(name.ljust(linelen - 1) + '%s\n' % operation + as_str)


    # strings is a list of series as strings
    if df:
        dataframe = pd.concat(strings, axis=1, keys=[i for i, _ in to_iterate])
        return dataframe
    output = ''
    for tup in zip(*[i.splitlines() for i in strings]):
        output += '   '.join(tup) + '\n'
    print(output)
