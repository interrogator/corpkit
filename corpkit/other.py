def quickview(results, n = 25):
    import corpkit
    """view top n results of results.

    Ideally, pass it interrogator() or plotter output. It will also accept DatFrames
    or Series (i.e. .results or .totals branches."""

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
            datatype = results.query['datatype']
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
            datatype = results.query['datatype']
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
        if type(results.iloc[0][0]) == numpy.int64:
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
    import corpkit
    """print conc lines nicely, to string, latex or csv"""
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
    import corpkit
    """Save an interrogation as pickle to savedir"""
    import collections
    from collections import namedtuple, Counter
    import pickle
    import os
    import pandas
    from time import localtime, strftime
    # import nltk

    if type(interrogation) == str or type(interrogation) == unicode:
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

    if type(interrogation) == pandas.core.frame.DataFrame or \
        type(interrogation) == pandas.core.series.Series or \
        type(interrogation) == collections.Counter:
        # removing this nltk support for now
        # or \ type(interrogation) == nltk.text.Text:
        temp_list = [interrogation]
    elif len(interrogation) == 2:
        temp_list = [interrogation.query, interrogation.totals]
    elif len(interrogation) == 3:
        if interrogation.query['function'] == 'interrogator':
            if interrogation.query['query'].startswith('k'):
                temp_list = [interrogation.query, interrogation.results, interrogation.table]
            else:
                temp_list = [interrogation.query, interrogation.results, interrogation.totals]
        else:
            temp_list = [interrogation.query, interrogation.results, interrogation.totals]
    elif len(interrogation) == 4:
        temp_list = [interrogation.query, interrogation.results, interrogation.totals, interrogation.table]
    f = open(fullpath, 'w')
    pickle.dump(temp_list, f)
    time = strftime("%H:%M:%S", localtime())
    if print_info:
        print '\n%s: Data saved: %s\n' % (time, fullpath)
    f.close()

def load_result(savename, loaddir = 'saved_interrogations', only_concs = False):
    """Reloads a save_result as namedtuple. it needs a filename and path to saved files"""
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

def report_display():
    import corpkit
    """Displays/downloads the risk report, depending on your browser settings"""
    class PDF(object):
        def __init__(self, pdf, size=(200,200)):
            import corpkit
            self.pdf = pdf
            self.size = size
        def _repr_html_(self):
            import corpkit
            return '<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)
        def _repr_latex_(self):
            import corpkit
            return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)
    return PDF('report/risk_report.pdf',size=(800,650))

def ipyconverter(inputfile, outextension):
    import corpkit
    """ipyconverter converts ipynb files to various formats.

    This function calls a shell script, rather than using an API. 
    The first argument is the ipynb file. 
    The second argument is the file extension of the output format, which may be 'py', 'html', 'tex' or 'md'.

    Example usage: ipyconverter('infile.ipynb', 'tex')

    This creates a .tex file called infile-converted.tex
    """
    import os
    if outextension == 'py':
        outargument = '--to python ' # the trailing space is important!
    if outextension == 'tex':
        outargument = '--to latex '
    if outextension == 'html':
        outargument = '--to html '
    if outextension == 'md':
        outargument = '--to md '
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '-converted.' + outextension
    shellscript = 'ipython nbconvert ' + outargument + inputfile + ' --stdout > ' + output
    print "Shell command: " + shellscript
    os.system(shellscript)

def conv(inputfile, loadme = True):
    import corpkit
    """A .py to .ipynb converter that relies on old code from IPython.

    You shouldn't use this: I only am while I'm on a deadline.
    """
    import os, sys
    import pycon.current as nbf
    import IPython
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '.ipynb'
    badname = outbasename + '.nbconvert.ipynb'
    print '\nConverting ' + inputfile + ' ---> ' + output + ' ...'
    nb = nbf.read(open(inputfile, 'r'), 'py')
    nbf.write(nb, open(output, 'w'), 'ipynb')
    os.system('ipython nbconvert --to=notebook --nbformat=4 %s' % output)
    os.system('mv %s %s' % (badname, output))
    if loadme:
        os.system('ipython notebook %s' % output)
    #nbnew = open(output, 'r')
    #IPython.nbformat.v4.convert.upgrade(nbnew, from_version=3, from_minor=0)
    print 'Done!\n'

def pytoipy(inputfile):
    import corpkit
    """A .py to .ipynb converter.

    This function converts .py files to ipynb.
    Comments in the .py file can be used to delimit cells, headings, etc. For example:

    # <headingcell level=1>
    # A heading 
    # <markdowncell>
    # *This text is in markdown*
    # <codecell>
    # print 'hello'

    Example usage: pytoipy('filename.py')
    """
    import os
    import IPython.nbformat.current as nbf
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '.ipynb'
    print '\nConverting ' + inputfile + ' ---> ' + output + ' ...'
    nb = nbf.read(open(inputfile, 'r'), 'py')
    nbf.write(nb, open(output, 'w'), 'ipynb')
    print 'Done!\n'

def new_project(name, loc = '.', root = False):
    import corpkit
    """make a new project in current directory"""
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
            print '%s: Directory already exists: "%s"' %( time, fullpath)
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
        shutil.copy(os.path.join(thepath, 'dictionaries', 'bnc.p'), os.path.join(fullpath, 'dictionaries'))
        # make a blank ish notebook
        newnotebook_text = open(os.path.join(thepath, corpkitname, 'blanknotebook.ipynb')).read()
        fixed_text = newnotebook_text.replace('blanknotebook', str(name))
        with open(os.path.join(fullpath, name + '.ipynb'), 'wb') as handle:
            handle.write(fixed_text)
            handle.close
        if platform.system() == 'Darwin':
            shtext = '#!/bin/bash\n\npath=$0\ncd ${path%%/*.*}\nipython notebook %s.ipynb\n' % name
            with open(os.path.join(fullpath, 'launcher.sh'), 'wb') as handle:
                handle.write(shtext)
                handle.close
            # permissions for sh launcher
            st = os.stat(os.path.join(fullpath, 'launcher.sh'))
            os.chmod(os.path.join(fullpath, 'launcher.sh'), st.st_mode | 0111)
            print '\nNew project made: %s\nTo begin, either use:\n\n    ipython notebook %s.ipynb\n\nor run launcher.sh.\n\n' % (name, name)
        else:
            print '\nNew project made: %s\nTo begin, either use:\n\n    ipython notebook %s.ipynb\n\n' % (name, name)
    else:
        time = strftime("%H:%M:%S", localtime())
        print '%s: New project created: "%s"' % (time, name)

def searchtree(tree, query, options = ['-t', '-o']):
    import corpkit
    "Searches a tree with Tregex and returns matching terminals"
    import os
    from other import tregex_engine
    from tests import check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    fo = open('tree.tmp',"w")
    fo.write(tree + '\n')
    fo.close()
    result = tregex_engine(query = query, check_query = True)
    result = tregex_engine(query = query, options = options, corpus = "tree.tmp")
    os.remove("tree.tmp")
    return result

def quicktree(sentence):
    import corpkit
    """Parse a sentence and return a visual representation in IPython"""
    import os
    from nltk import Tree
    from nltk.draw.util import CanvasFrame
    from nltk.draw import TreeWidget
    try:
        from stat_parser import Parser
    except:
        raise ValueError('PyStatParser not found.')
    try:
        from IPython.display import display
        from IPython.display import Image
    except:
        pass
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    parser = Parser()
    parsed = parser.parse(sentence)
    cf = CanvasFrame()
    tc = TreeWidget(cf.canvas(),parsed)
    cf.add_widget(tc,10,10) # (10,10) offsets
    cf.print_to_file('tree.ps')
    cf.destroy()
    if have_ipython:
        tregex_command = 'convert tree.ps tree.png'
        result = get_ipython().getoutput(tregex_command)
    else:
        tregex_command = ["convert", "tree.ps", "tree.png"]
        result = subprocess.check_output(tregex_command)    
    os.remove("tree.ps")
    return Image(filename='tree.png')
    os.remove("tree.png")

def multiquery(corpus, query, sort_by = 'total', quicksave = False):
    import corpkit
    """Creates a named tuple for a list of named queries to count.

    Pass in something like:

    [[u'NPs in corpus', r'NP'], [u'VPs in corpus', r'VP']]"""

    import collections
    import os
    import pandas
    import pandas as pd
    from time import strftime, localtime
    from interrogator import interrogator
    from editor import editor

    if quicksave:
        savedir = 'saved_interrogations'
        if not quicksave.endswith('.p'):
            quicksave = quicksave + '.p'
        fullpath = os.path.join(savedir, quicksave)
        while os.path.isfile(fullpath):
            selection = raw_input("\nSave error: %s already exists in %s.\n\nPick a new name: " % (savename, savedir))
            if not selection.endswith('.p'):
                selection = selection + '.p'
                fullpath = os.path.join(savedir, selection)

    results = []
    for name, pattern in query:
        result = interrogator(corpus, 'count', pattern)
        result.totals.name = name # rename count
        results.append(result.totals)
    results = pd.concat(results, axis = 1)

    results = editor(results, sort_by = sort_by, print_info = False, keep_stats = False)
    time = strftime("%H:%M:%S", localtime())
    print '%s: Finished! %d unique results, %d total.' % (time, len(results.results.columns), results.totals.sum())
    if quicksave:
        from other import save_result
        save_result(results, quicksave)
    return results


    # if nothing, the query's fine! 

def interroplot(path, query):
    import corpkit
    """Interrogates path with Tregex query, gets relative frequencies, and plots the top seven results"""
    from corpkit import interrogator, editor, plotter
    quickstart = interrogator(path, 'words', query)
    edited = editor(quickstart.results, '%', quickstart.totals, print_info = False)
    plotter(str(path), edited.results)

def datareader(data, plaintext = False, **kwargs):
    import corpkit
    """
    Returns a string of plain text from a number of kinds of data.

    The kinds of data currently accepted are:

    path to corpus : all trees are flattened
    path to subcorpus : all trees are flattened
    conc() output (list of concordance lines)
    csv file generated with conc()
    a string of text
    """
    import os
    import pandas
    from other import tregex_engine
    from tests import check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    tregex_engine_used = False
    
    # if unicode, make it a string
    if type(data) == unicode:
        if not os.path.isdir(data):
            if not os.path.isfile(data):
                return good
    if type(data) == str:
        # if it's a file, read it
        if os.path.isfile(data):
            good = open(data).read()
        # if it's a dir, flatten all trees
        elif os.path.isdir(data):
            # get all sentences newline separated
            query = r'__ !< __'
            options = ['-o', '-t']

            # if lemmatise, we get each word on a newline
            if 'lemmatise' in kwargs:
                if kwargs['lemmatise'] is True:
                    query = r'__ <# (__ !< __)'
                    options = ['-o']
 
            # check for trees ...
            #while plaintext is False:
                #for f in first_twenty:
                    #plaintext = tregex_engine(corpus = f, check_for_trees = True)
            
            if not plaintext:
                tregex_engine_used = True
                results = tregex_engine(corpus = data,
                                              options = options,
                                              query = query, 
                                              **kwargs)
            else:
                results = []
                fs = [os.path.join(data, f) for f in os.listdir(data)]
                # do recursive if need
                if any(os.path.isdir(f) for f in fs):
                    recursive_files = []
                    for dirname, dirnames, filenames in os.walk(data):
                        for filename in filenames:
                            recursive_files.append(os.path.join(dirname, filename))
                    fs = recursive_files
                
                import nltk
                sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
                for f in fs:
                    raw = unicode(open(f).read(), 'utf-8', errors = 'ignore')
                    sents = sent_tokenizer.tokenize(raw)
                    tokenized_sents = [nltk.word_tokenize(i) for i in sents]
                    for sent in tokenized_sents:
                        for w in sent:
                            results.append(w.lower()) 

            return results

            #good = '\n'.join(results)
        # if a string of text, 
        else:
            good = data
    # if conc results, turn into string...
    elif type(data) == pandas.core.frame.DataFrame:
        # if conc lines:
        try:
            if list(data.columns) == ['l', 'm', 'r']:
                conc_lines = True
            else:
                conc_lines = False
        except:
            conc_lines = False
        if conc_lines:
            # may not be unicode!?
            good = [' '.join(list(data.ix[l])) for l in list(data.index)]

    else:
        good = data

    # make unicode
    if not tregex_engine_used:
        try:
            good = unicode(good, 'utf-8', errors = 'ignore')
        except TypeError:
            pass

    return good

def tregex_engine(corpus = False,  
                  options = False, 
                  query = False, 
                  check_query = False,
                  check_for_trees = False,
                  lemmatise = False,
                  just_content_words = False,
                  return_tuples = False,
                  root = False,
                  preserve_case = False):
    """This does a tregex query.
    query: tregex query
    options: list of tregex options
    corpus: place to search
    check_query: just make sure query ok
    check_for_trees: find out if corpus contains parse trees"""
    import corpkit
    from other import add_corpkit_to_path
    add_corpkit_to_path()
    import subprocess 
    from subprocess import Popen, PIPE, STDOUT
    import re
    from time import localtime, strftime
    from corpkit.tests import check_dit
    from dictionaries.word_transforms import wordlist
    import os

    on_cloud = check_dit()

    def find_wordnet_tag(tag):
        import corpkit
        if tag.startswith('j'):
            tag = 'a'
        elif tag.startswith('v') or tag.startswith('m'):
            tag = 'v'
        elif tag.startswith('n'):
            tag = 'n'
        elif tag.startswith('r'):
            tag = 'r'
        else:
            tag = False
        return tag

    # if check_query, enter the while loop
    # if not, get out of it
    an_error_occurred = True
    while an_error_occurred:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh"]
        if not on_cloud:
            tregex_command = ["tregex.sh"]
        if root:
            #for py2app
            corpath = os.path.dirname(corpkit.__file__)
            corpath = corpath.replace('/lib/python2.7/site-packages.zip/corpkit', '')
            tregex_command = [os.path.join(corpath, "tregex.sh")]
            # for pyinstaller
            if not os.path.isfile(os.path.join(corpath, "tregex.sh")):            
                def resource_path(relative):
                    return os.path.join(
                        os.environ.get(
                            "_MEIPASS2",
                            os.path.abspath(".")
                        ),
                        relative
                    )
                tregex_command = [resource_path("tregex.sh")]

        if not query:
            query = 'NP'
        # if checking for trees, use the -T option
        if check_for_trees:
            options = ['-T']

        filenaming = False
        try:
            if '-f' in options:
                filenaming = True
        except:
            pass

        if return_tuples or lemmatise:
            options = ['-o']
        # append list of options to query 
        if options:
            [tregex_command.append(o) for o in options]
        # dummy option
        else:
            options = ['-t']
        if query:
            tregex_command.append(query)
        if corpus:
            if os.path.isdir(corpus) or os.path.isfile(corpus):
                if '-filter' not in options:
                    tregex_command.append(corpus)
        # do query
        #try:
        if type(options) != bool:
            if not '-filter' in options:
                res = subprocess.check_output(tregex_command, stderr=subprocess.STDOUT).splitlines()
            else:
                p = Popen(tregex_command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                p.stdin.write(corpus.encode('utf-8', errors = 'ignore'))
                res = p.communicate()[0].splitlines()
                p.stdin.close()
        else:
            p = Popen(tregex_command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            p.stdin.write(corpus.encode('utf-8', errors = 'ignore'))
            res = p.communicate()[0].splitlines()
            p.stdin.close()
        # exception handling for regex error
        #except Exception, e:
        #    try:
        #        res = str(e.output).split('\n')
        #    except:
        #        raise e

        if check_query:
            # define error searches 
            tregex_error = re.compile(r'^Error parsing expression')
            regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')
            # if tregex error, give general error message
            if re.match(tregex_error, res[0]):
                tregex_error_output = ""
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Error parsing Tregex query.' % time
                    return False
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: Error parsing Tregex expression "%s".\nWould you like to:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, query))
                if 'a' in selection:
                    query = raw_input('\nNew Tregex query: ')
                elif 'b' in selection:
                    print ''
                    return False
            
            # if regex error, try to help
            elif re.match(regex_error, res[0]):
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Regular expression in Tregex query contains an error.' % time
                    return False
                info = res[0].split(':')
                index_of_error = re.findall(r'index [0-9]+', info[1])
                justnum = index_of_error[0].split('dex ')
                spaces = ' ' * int(justnum[1])
                remove_start = query.split('/', 1)
                remove_end = remove_start[1].split('/', -1)
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: Error parsing regex inside Tregex query: %s'\
                '. Best guess: \n%s\n%s^\n\nYou can either: \n' \
                '              a) rewrite it now\n' \
                '              b) exit\n\nYour selection: ' % (time, str(info[1]), str(remove_end[0]), spaces))
                if 'a' in selection:
                    query = raw_input('\nNew Tregex query: ')
                elif 'b' in selection:
                    print ''
                    return                
            else:
                an_error_occurred = False
                return query
        # if not query checking, leave this horrible while loop
        else: 
            an_error_occurred = False
    
    # counting is easy, just get out with the number
    if '-C' in options:
        return int(res[-1])

    # remove errors and blank lines
    res = [s for s in res if not s.startswith('PennTreeReader:') and s]

    # find and remove stderr lines
    if '-filter' not in options:
        n = 1
        std_last_index = res.index(next(s for s in res \
                        if s.startswith('Reading trees from file') \
                        or s.startswith('using default tree')))
    else:
        n = 2
        std_last_index = res.index(next(s for s in res \
                        if s.startswith('Parsed representation:')))
    res = res[std_last_index + n:]

    # this is way slower than it needs to be, because it searches a whole subcorpus!
    if check_for_trees:
        if res[0].startswith('1:Next tree read:'):
            return True
        else:
            return False
    # return if no matches
    if res[-1] == 'There were 0 matches in total.':
        return []
    # remove total
    res = res[:-1]
    # make unicode and lowercase
    make_tuples = []
    if filenaming:
        for index, r in enumerate(res):
            if r.startswith('# /'):
                make_tuples.append((r, res[index + 1]))
        res = make_tuples
                
    if not filenaming:
        if preserve_case:
            res = [unicode(w, 'utf-8', errors = 'ignore') for w in res]
        else:
            res = [unicode(w, 'utf-8', errors = 'ignore').lower() for w in res]
    else:
        if preserve_case:
            res = [(unicode(t, 'utf-8', errors = 'ignore'), unicode(w, 'utf-8', errors = 'ignore')) for t, w in res]
        else:
            res = [(unicode(t), unicode(w, 'utf-8', errors = 'ignore').lower()) for t, w in res]

    if lemmatise or return_tuples:
        # CAN'T BE USED WITH ALMOST EVERY OPTION!
        allwords = []
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()
         # turn this into a list of words or lemmas, with or without closed words
        for result in res:
            # remove brackets and split on first space
            result = result.lstrip('(')
            result = result.rstrip(')')
            tag, word = result.split(' ', 1)
            # get wordnet tag from stanford tag
            wordnet_tag = find_wordnet_tag(tag)
            short_tag = tag[:2]
            # do manual lemmatisation first
            if lemmatise:
                if word in wordlist:
                    word = wordlist[word]
                # do wordnet lemmatisation
                if wordnet_tag:
                    word = lmtzr.lemmatize(word, wordnet_tag)
            if just_content_words:
                if wordnet_tag:
                    if return_tuples:
                        allwords.append((word, tag))
                    else:
                        allwords.append(word)
            else:
                if return_tuples:
                    allwords.append((word, tag))
                else:
                    allwords.append(word)
        res = allwords
    if return_tuples:
        res = [(w, t.upper()) for w, t in res]
    return res

def load_all_results(data_dir = 'saved_interrogations', only_concs = False, **kwargs):
    import corpkit
    """load every saved interrogation in data_dir into a dict"""
    import os
    import time
    from other import load_result
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
            if type(tmp) != pandas.core.frame.DataFrame:
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
    import corpkit
    """turn a series into a latex table"""
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

def make_nltk_text(directory, 
                   collapse_dirs = True, 
                   tagged = False, 
                   lemmatise = False, 
                   just_content_words = False):
    """turn a lot of trees into an nltk style text"""
    import nltk
    import os
    from other import tregex_engine
    if type(directory) == str:
        dirs = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        if len(dirs) == 0:
            dirs = [directory]
    elif type(directory) == list:
        dirs = directory

    return_tuples = False
    if tagged:
        return_tuples = True

    if just_content_words:
        lemmatise = True

    query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
    if not return_tuples and not lemmatise:
        options = ['-o', '-t']
    else:
        options = ['-o']

    # filthy code.
    all_out = []

    for d in dirs:
        print "Flattening %s ... " % str(d)
        res = tregex_engine(corpus = d, 
                            query = query, 
                            options = options,
                            lemmatise = lemmatise,
                            just_content_words = just_content_words,
                            return_tuples = return_tuples)
        all_out.append(res)

    if collapse_dirs:
        tmp = []
        for res in all_out:
            for w in res:
                tmp.append(w)
        all_out = tmp
        textx = nltk.Text(all_out)
    else:
        textx = {}
        for name, text in zip(dirs, all_out):
            t = nltk.Text(all_out)
            textx[os.path.basename(name)] = t
    return textx

def get_synonyms(word, pos = False):
    import corpkit
    import nltk
    from nltk.corpus import wordnet
    if pos:
        syns = wordnet.synsets(word, pos = pos)
    else:
        syns = wordnet.synsets(word)
    return list(set([l.name().replace('_', ' ').lower() for s in syns for l in s.lemmas()]))

def synonym_dictmaker(df):
    import corpkit
    syn_dict = {}
    text = make_nltk_text(d)
    for w in list(df.columns):
        if w not in syn_dict.keys() and w not in syn_dict.values():
            wds = get_synonyms(w, pos = pos) + text.similar(w)[:10]
            sel = raw_input('Enter the indexes to remove from this list of proposed synonyms, or type "exit" to quit:\n\n%s\n') % '\n'.join(wds)
            if sel.startswith('e'):
                return
            for i in sel:
                del wds[i]
            for word in wds:
                syn_dict[word] = w
    return syn_dict

def as_regex(lst, boundaries = 'w', case_sensitive = False, inverse = False):
    import corpkit
    """turns a wordlist into an uncompiled regular expression"""
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
    #if no_punctuation:
    #    if not inverse:
    #        # not needed
    #        punct = r''
    #    else:
    #        punct = r'|[^A-Za-z0-9]+'
    #else:
    #    if not inverse:
    #        punct = r''
    #    else:
    #        punct = r''
    if inverse:
        joinbit = r'%s|%s' % (boundary2, boundary1)
        return case + inverser1 + r'(' + boundary1 + joinbit.join(sorted(list(set([re.escape(w) for w in lst])))) + boundary2 + r')' + inverser2
    else:
        return case + boundary1 + inverser1 + r'(' + r'|'.join(sorted(list(set([re.escape(w) for w in lst])))) + r')' + inverser2 + boundary2


def show(lines, index, show = 'thread'):
    import corpkit
    """show lines.ix[index][link] as frame"""
    url = lines.ix[index]['link'].replace('<a href=', '').replace('>link</a>', '')
    return HTML('<iframe src=%s width=1000 height=500></iframe>' % url)


def add_corpkit_to_path():
    import sys
    import os
    import inspect
    corpath = inspect.getfile(inspect.currentframe())
    baspat = os.path.dirname(corpath)
    dicpath = os.path.join(baspat, 'dictionaries')
    for p in [corpath, baspat, dicpath]:
        if p not in sys.path:
            sys.path.append(p)
        if p not in os.environ["PATH"].split(':'): 
            os.environ["PATH"] += os.pathsep + p

def add_nltk_data_to_nltk_path(**kwargs):
    import nltk
    import os
    npat = nltk.__file__
    nltkpath = os.path.dirname(npat)
    if nltkpath not in nltk.data.path:
        nltk.data.path.append(nltkpath)
        if 'note' in kwargs.keys():
            path_within_gui = os.path.join(nltkpath.split('/lib/python2.7')[0], 'nltk_data')
            if path_within_gui not in nltk.data.path:
                nltk.data.path.append(path_within_gui)

    # very temporary! -- for using .py
    nltk.data.path.append('/users/daniel/work/corpkit/nltk_data')

def get_gui_resource_dir():
    import inspect
    import os
    import sys
    if sys.platform == 'darwin':
        key = 'Mod1'
        fext = 'app'
    else:
        key = 'Control'
        fext = 'exe'
    corpath = corpath = __file__
    extens = '.%s' % fext
    apppath = corpath.split(extens , 1)
    resource_path = ''
    if len(apppath) == 1:
        resource_path = os.path.dirname(corpath)
    else:
        apppath = apppath[0] + extens
        appdir = os.path.dirname(apppath)
        if sys.platform == 'darwin':
            resource_path = os.path.join(apppath, 'Contents', 'Resources')
        else:
            resource_path = appdir
    return resource_path

def get_fullpath_to_jars(path_var):
    """when corenlp is needed, this returns the *abs path to jar files*"""
    import os
    important_files = ['stanford-corenlp-3.5.2-javadoc.jar', 'stanford-corenlp-3.5.2-models.jar',
                   'stanford-corenlp-3.5.2-sources.jar', 'stanford-corenlp-3.5.2.jar']
    
    # if user selected file in parser dir rather than dir
    if os.path.isfile(path_var):
        corenlppath.set(os.path.dirname(path_var.rstrip('/')))
    # if the user selected the subdir:
    if all(os.path.isfile(os.path.join(path_var, f)) for f in important_files):
        return path_var
    # if the user selected the parent dir:
    else:
        find_install = [d for d in os.listdir(path_var) \
           if os.path.isdir(os.path.join(path_var, d)) \
           and os.path.isfile(os.path.join(path_var, d, 'jollyday.jar'))]
        if len(find_install) > 0:
            return os.path.join(path_var, find_install[0])

    # otherwise, return false.
    recog = tkMessageBox.showwarning(title = 'CoreNLP not found', 
                        message = "CoreNLP not found in %s." % path_var)
    timestring("CoreNLP not found in %s." % path_var)
    return False
