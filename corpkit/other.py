def quickview(results, n = 25):
    """view top n results of results.

    :param results: Interrogation/edited result to view
    :type results: corpkit.interrogation/pandas.core.frame.DataFrame
    :param n: Show top *n* results
    :type n: int
    :returns: None
    """

    import corpkit
    import pandas
    import numpy
    import os

    # handle dictionaries too:
    dictpath = 'dictionaries'
    savedpath = 'saved_interrogations'

    # too lazy to code this properly for every possible data type:
    if n == 'all':
        n = 9999

    if type(results) == str:
        if os.path.isfile(os.path.join(dictpath, results)):
            import pickle
            from collections import Counter
            unpickled = pickle.load(open(os.path.join(dictpath, results), 'rb'))
            print '\nTop %d entries in %s:\n' % (n, os.path.join(dictpath, results))
            for index, (w, f) in enumerate(unpickled.most_common(n)):
                fildex = '% 3d' % index
                print '%s: %s (n=%d)' %(fildex, w, f)
            return

        elif os.path.isfile(os.path.join(savedpath, results)):
            from corpkit import load_result
            print '\n%s loaded temporarily from file:\n' % results
            results = load_result(results)
        else:
            raise ValueError('File %s not found in saved_interrogations or dictionaries')

    if 'interrogation' in str(type(results)):
        clas = results.query['function']
        if clas == 'interrogator':
            datatype = results.results.iloc[0,0].dtype
            if datatype == 'int64':
                option = 'total'
            else:
                option = '%'
            if results.query['query'] == 'keywords':
                option = 'keywords'
            elif results.query['query'] == 'ngrams':
                option = 'ngrams'

            try:
                results_branch = results.results
                resbranch = True
            except AttributeError:
                resbranch = False
                results_branch = results

        elif clas == 'editor':
            # currently, it's wrong if you edit keywords! oh well
            datatype = results.results.iloc[0,0].dtype
            if results.query['just_totals']:
                resbranch = False
                if results.results.dtype == 'int64':
                    option = 'total'
                else:
                    option = '%' 
                results_branch = results.results
            else:
                if datatype == 'int64':
                    option = 'total'
                else:
                    option = '%'
                try:
                    results_branch = results.results
                    resbranch = True
                except AttributeError:
                    resbranch = False

    if type(results) == pandas.core.frame.DataFrame:
        results_branch = results
        resbranch = True
        if type(results.iloc[0,0]) == numpy.int64:
            option = 'total'
        else:
            option = '%'
    elif type(results) == pandas.core.series.Series:
        resbranch = False
        results_branch = results
        if type(results.iloc[0]) == numpy.int64:
            option = 'total'
        else:
            option = '%'
        if results.name == 'keywords':
            option = 'series_keywords'

    if resbranch:
        the_list = list(results_branch)[:n]
    else:
        the_list = list(results_branch.index)[:n]

    for index, w in enumerate(the_list):
        fildex = '% 3d' % index
        if option == 'keywords':
            print '%s: %s' %(fildex, w)
        elif option == '%' or option == 'ratio':
            if 'interrogation' in str(type(results)):
                tot = results.totals[w]
                totstr = "%.3f" % tot
                print '%s: %s (%s%%)' % (fildex, w, totstr)
            else:
                print '%s: %s' % (fildex, w)
        elif option == 'series_keywords':
            tot = results_branch[w]
            print '%s: %s (k=%d)' %(fildex, w, tot)

        else:
            if resbranch:
                tot = sum(i for i in list(results_branch[w]))
            else:
                tot = results_branch[w]
            print '%s: %s (n=%d)' %(fildex, w, tot)

def concprinter(df, kind = 'string', n = 100):
    """
    Print conc lines nicely, to string, latex or csv

    :param df: concordance lines from conc()
    :type df: pd.DataFame 
    :param kind: output format
    :type kind: str ('string'/'latex'/'csv')
    :param n: Print first n lines only
    :type n: int/'all'
    :returns: None
    """
    import corpkit
    if n > len(df):
        n = len(df)
    if not kind.startswith('l') and kind.startswith('c') and kind.startswith('s'):
        raise ValueError('kind argument must start with "l" (latex), "c" (csv) or "s" (string).')
    import pandas as pd
    if type(n) == int:
        to_show = df.ix[range(n)]
    elif n is False:
        to_show = df
    elif n == 'all':
        to_show = df
    else:
        raise ValueError('n argument "%s" not recognised.' % str(n))
    print ''
    if kind.startswith('s'):
        print to_show.to_string(header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format})
    if kind.startswith('l'):
        print to_show.to_latex(header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format}).replace('llll', 'lrrl', 1)
    if kind.startswith('c'):
        print to_show.to_csv(sep = '\t', header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format})
    print ''

def save_result(interrogation, savename, savedir = 'saved_interrogations', print_info = True):
    """
    Save an interrogation as pickle to *savedir*.

       >>> interro_interrogator(corpus, 'words', 'any')
       >>> save_result(interro, 'savename')

    will create saved_interrogations/savename.p

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
    import corpkit
    import collections
    from collections import namedtuple, Counter
    import pickle
    import os
    import pandas
    from time import localtime, strftime
    # import nltk

    
    if type(interrogation) == dict:
        savedir = os.path.join(savedir, savename)
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
    else:
        interrogation = {savename: interrogation}

    for savename, data in interrogation.items():
        
        if type(data) == str or type(data) == unicode:
            raise TypeError('First argument (i.e. the thing to save) cannot be a string.')

        if savename.endswith('.p'):
            savename = savename[:-2]

        def urlify(s):
            import corpkit
            "Turn savename into filename"
            import re
            #s = s.lower()
            s = re.sub(r"[^\w\s-]", '', s)
            s = re.sub(r"\s+", '-', s)
            s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
            return s

        savename = urlify(savename)

        if not os.path.exists(savedir):
            os.makedirs(savedir)
        
        if not savename.endswith('.p'):
            savename = savename + '.p'

        # this feature creeps me out, i don't think it's needed any more
        savename = savename.replace('lemmatised', '-lemmatised')

        fullpath = os.path.join(savedir, savename)
        while os.path.isfile(fullpath):
            selection = raw_input("\nSave error: %s already exists in %s.\n\nType 'o' to overwrite, or enter a new name: " % (savename, savedir))
            if selection == 'o' or selection == 'O':
                import os
                os.remove(fullpath)
            else:
                if not selection.endswith('.p'):
                    selection = selection + '.p'
                    fullpath = os.path.join(savedir, selection)
        
        # if it's just a table or series

        if type(data) == pandas.core.frame.DataFrame or \
            type(data) == pandas.core.series.Series or \
            type(data) == collections.Counter:
            # removing this nltk support for now
            # or \ type(data) == nltk.text.Text:
            temp_list = [data]
        elif len(data) == 2:
            temp_list = [data.query, data.totals]
        elif len(data) == 3:
            if data.query['function'] == 'interrogator':
                if data.query['query'].startswith('k'):
                    temp_list = [data.query, data.results, data.table]
                else:
                    temp_list = [data.query, data.results, data.totals]
            else:
                temp_list = [data.query, data.results, data.totals]
        elif len(data) == 4:
            temp_list = [data.query, data.results, data.totals, data.table]
        f = open(fullpath, 'w')
        pickle.dump(temp_list, f)
        time = strftime("%H:%M:%S", localtime())
        if print_info:
            print '\n%s: Data saved: %s\n' % (time, fullpath)
        f.close()

def load_result(savename, loaddir = 'saved_interrogations', only_concs = False):
    """
    Load saved data into memory:

        >>> loaded = load_result('interro')

    will load saved_interrogations/interro.p as loaded

    :param savename: Filename with or without extension
    :type savename: str
    
    :param loaddir: Relative path to the directory containg *savename*
    :type loaddir: str
    
    :param only_concs: Set to True if loading concordance lines
    :type only_concs: bool

    :returns: loaded data
    """
    import corpkit
    import collections
    import pickle
    import os
    import pandas
    if not os.path.isdir(os.path.join(loaddir, savename)):
        if not savename.endswith('.p'):
            savename = savename + '.p'
    
    def namesuggester(entered_name, searched_dir):
        """if you got the wrong name, this finds the most similar name and suggests it."""
        import corpkit
        from nltk.metrics.distance import edit_distance
        from itertools import groupby
        from operator import itemgetter
        names = os.listdir(searched_dir)
        res = {}
        for n in names:
            sim = edit_distance(entered_name, n, transpositions=False)
            res[n] = sim
        possibles = sorted([v.replace('.p', '') for k,v in groupby(sorted((v,k) for k,v in res.iteritems()), key=itemgetter(0)).next()[1]])
        sel = raw_input('\n"%s" not found. Enter one of the below, or "e" to exit:\n\n%s\n\n' % (entered_name.replace('.p', ''), '\n'.join(['    %d) "%s"' % (index + 1, sug) for index, sug in enumerate(possibles[:10])])))
        if sel.startswith('e') or sel.startswith('E'):
            return
        else:
            try:
                s = int(sel)
                return possibles[s - 1]
            except ValueError:
                return sel

    def make_into_namedtuple(unpickled):
        """take a filename, make it into named tuple"""

        # figure out what's in the unpickled data, use to turn into named tup
        if type(unpickled) == pandas.core.frame.DataFrame or \
        type(unpickled) == pandas.core.series.Series or \
        type(unpickled) == collections.Counter:
        # or \
        #type(unpickled) == nltk.text.Text:
            output = unpickled

        if len(unpickled) == 1:
            if type(unpickled[0]) == pandas.core.frame.DataFrame or \
            type(unpickled[0]) == pandas.core.series.Series or \
            type(unpickled[0]) == dict or \
            type(unpickled[0]) == collections.Counter:
            # or \
            #type(unpickled[0]) == nltk.text.Text:
                output = unpickled[0]
        elif len(unpickled) == 4:
            outputnames = collections.namedtuple('loaded_interrogation', ['query', 'results', 'totals', 'table'])
            output = outputnames(unpickled[0], unpickled[1], unpickled[2], unpickled[3])
        elif len(unpickled) == 3:
            if unpickled[0]['function'] == 'interrogator':
                if unpickled[0]['query'].startswith('k'):
                    outputnames = collections.namedtuple('loaded_interrogation', ['query', 'results', 'table'])
                else:
                    # not presently possible, i think:
                    outputnames = collections.namedtuple('loaded_interrogation', ['query', 'results', 'totals'])
            else:
                outputnames = collections.namedtuple('loaded_interrogation', ['query', 'results', 'totals'])
            output = outputnames(unpickled[0], unpickled[1], unpickled[2])
        elif len(unpickled) == 2:
            outputnames = collections.namedtuple('loaded_interrogation', ['query', 'totals'])
            output = outputnames(unpickled[0], unpickled[1])
        return output

    filepath = os.path.join(loaddir, savename)
    if os.path.isfile(filepath):
        notfound = True
        while notfound:
            filepath = os.path.join(loaddir, savename)    
            try:
                unpickled = pickle.load(open(filepath, 'rb'))
                notfound = False
            except IOError:
                sel = namesuggester(savename, loaddir)
                if not sel:
                    return
                else:
                    savename = sel + '.p'
        return make_into_namedtuple(unpickled)

    elif os.path.isdir(filepath):
        fs = [f for f in os.listdir(filepath) \
                if os.path.isfile(os.path.join(filepath, f)) and f.endswith('.p')]    
        outs = {}
        for f in fs:
            unpickled = pickle.load(open(os.path.join(filepath, f), 'rb'))    
            outs[f.replace('.p', '')] = make_into_namedtuple(unpickled)
        return outs

def new_project(name, loc = '.', root = False):
    """Make a new project in ./*loc*

    :param name: A name for the project
    :type name: str
    :param loc: Relative path to directory in which project will be made
    :type loc: str
    """
    import corpkit
    import os
    import shutil
    import stat
    import platform
    from time import strftime, localtime

    path_to_corpkit = os.path.dirname(corpkit.__file__)
    thepath, corpkitname = os.path.split(path_to_corpkit)
    
    # make project directory
    fullpath = os.path.join(loc, name)
    try:
        os.makedirs(fullpath)
    except:
        if root:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Directory already exists: "%s"' %( thetime, fullpath)
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
    if root:

        # clean this up
        import corpkit
        def resource_path(relative):
            import os
            return os.path.join(
                os.environ.get(
                    "_MEIPASS2",
                    os.path.abspath(".")
                ),
                relative
            )
        corpath = os.path.dirname(corpkit.__file__)
        corpath = corpath.replace('/lib/python2.7/site-packages.zip/corpkit', '')
        baspat = os.path.dirname(corpath)
        dicpath = os.path.join(baspat, 'dictionaries')
        try:
            shutil.copy(os.path.join(dicpath, 'bnc.p'), os.path.join(fullpath, 'dictionaries'))
        except:
            shutil.copy(resource_path('bnc.p'), os.path.join(fullpath, 'dictionaries'))

    # if not GUI
    if not root:
        time = strftime("%H:%M:%S", localtime())
        print '%s: New project created: "%s"' % (time, name)

def interroplot(path, query):
    """Demo function for interrogator/plotter.

        1. Interrogates path with Tregex query, 
        2. Gets relative frequencies
        3. Plots the top seven results

    :param path: path to corpus
    :type path: str
    
    :param query: Tregex query
    :type query: str

    """
    import corpkit
    from corpkit import interrogator, editor, plotter
    quickstart = interrogator(path, 'words', query, show = ['w'])
    edited = editor(quickstart.results, '%', quickstart.totals, print_info = False)
    plotter(str(path), edited.results)

def load_all_results(data_dir = 'saved_interrogations', only_concs = False, **kwargs):
    """
    Load every saved interrogation in data_dir into a dict:

        >>> r = load_all_results()

    :param data_dir: path to saved data
    :type data_dir: str

    :returns: dict with filenames as keys
    """
    import corpkit
    import os
    import time
    from corpkit.other import load_result
    from time import localtime, strftime
    
    def get_root_note(kwargs):
        if 'root' in kwargs.keys():
            root = kwargs['root']
        else:
            root = False
        if 'note' in kwargs.keys():
            note = kwargs['note']
        else:
            note = False       
        return root, note

    root, note = get_root_note(kwargs)

    r = {}
    fs = [f for f in os.listdir(data_dir) if f.endswith('.p') or os.path.isdir(os.path.join(data_dir, f))]
    if note and len(fs) > 3:
        note.progvar.set(0)
    if len(fs) == 0:
        if not root:
            raise ValueError('No saved data found in %s' % data_dir)
        #else:
            #thetime = strftime("%H:%M:%S", localtime())
            #if not only_concs:
            #    print '%s: No saved interrogations found in %s' % (thetime, data_dir)
            #else:
            #    print '%s: No saved concordances found in %s' % (thetime, data_dir)
            return
    l = 0
    import pandas
    for index, finding in enumerate(fs):
        try:
            tmp = load_result(finding, loaddir = data_dir, only_concs = only_concs)
            if type(tmp) != pandas.core.frame.DataFrame and type(tmp) != pandas.core.series.Series:
                if not tmp:
                    continue
            r[os.path.splitext(finding)[0]] = tmp
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s loaded as %s.' % (time, finding, os.path.splitext(finding)[0])
            l += 1
        except:
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s failed to load. Try using load_result to find out the matter.' % (time, finding)
        if note and len(fs) > 3:
            note.progvar.set((index + 1) * 100.0 / len(fs))
        if root:
            root.update()
    time = strftime("%H:%M:%S", localtime())
    print '%s: %d interrogations loaded from %s.' % (time, l, os.path.basename(data_dir))
    return r

def texify(series, n = 20, colname = 'Keyness', toptail = False, sort_by = False):
    """turn a series into a latex table"""
    import corpkit
    import pandas as pd
    if sort_by:
        df = pd.DataFrame(series.order(ascending = False))
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


def as_regex(lst, boundaries = 'w', case_sensitive = False, inverse = False):
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
    elif type(boundaries) == tuple or type(boundaries) == list:
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
        return case + inverser1 + r'(' + boundary1 + joinbit.join(sorted(list(set([re.escape(w) for w in lst])))) + boundary2 + r')' + inverser2
    else:
        return case + boundary1 + inverser1 + r'(' + r'|'.join(sorted(list(set([re.escape(w) for w in lst])))) + r')' + inverser2 + boundary2

def make_multi(interrogation, indexnames = None):    
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
    translator = {'f': 'Function',
                  'l': 'Lemma',
                  'a': 'Distance',
                  'w': 'Word',
                  't': 'Trees',
                  'i': 'Index',
                  'n': 'N-grams',
                  'p': 'POS',
                  'g': 'Governor',
                  'd': 'Dependent'}
    import numpy as np
    import pandas as pd
    # determine datatype, get df and cols
    if type(interrogation) == pd.core.frame.DataFrame:
        df = interrogation
        cols = list(interrogation.columns)
    elif type(interrogation) == pd.core.series.Series:
        cols = list(interrogation.index)
        df = pd.DataFrame(interrogation).T
    else:
        cols = list(interrogation.results.columns)
        df = interrogation.results
        # set indexnames if we have them
        if indexnames is not False:
            indexnames = [translator[i] for i in interrogation.query['show']]

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
    pd.set_option('display.multi_sparse', False)
    return newdf
