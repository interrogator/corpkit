def quickview(results, n = 25):
    """view top n results of results.

    Ideally, pass it interrogator() or plotter output. It will also accept DatFrames
    or Series (i.e. .results or .totals branches."""

    import corpkit
    import pandas
    import numpy
    import os

    # handle dictionaries too:
    dictpath = 'data/dictionaries'
    savedpath = 'data/saved_interrogations'

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
            raise ValueError('File %s not found in data/saved_interrogations or data/dictionaries')

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

def save_result(interrogation, savename, savedir = 'data/saved_interrogations'):
    """Save an interrogation as pickle to savedir"""
    import collections
    from collections import namedtuple, Counter
    import pickle
    import os
    import pandas
    from time import localtime, strftime
    import nltk

    if type(interrogation) == str or type(interrogation) == unicode:
        raise TypeError('First argument (i.e. the thing to save) cannot be a string.')

    if savename.endswith('.p'):
        savename = savename[:-2]

    def urlify(s):
        "Turn savename into filename"
        import re
        s = s.lower()
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
        type(interrogation) == dict or \
        type(interrogation) == collections.Counter or \
        type(interrogation) == nltk.text.Text:
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
    print '\n%s: Data saved: %s\n' % (time, fullpath)
    f.close()

def load_result(savename, loaddir = 'data/saved_interrogations'):
    """Reloads a save_result as namedtuple"""
    import collections
    import pickle
    import os
    import pandas
    import nltk
    if not savename.endswith('.p'):
        savename = savename + '.p'
    
    notfound = True
    
    def namesuggester(entered_name, searched_dir):
        import nltk
        from itertools import groupby
        from operator import itemgetter
        names = os.listdir(searched_dir)
        res = {}
        for n in names:
            sim = nltk.metrics.distance.edit_distance(entered_name, n, transpositions=False)
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

    while notfound:
        try:
            unpickled = pickle.load(open(os.path.join(loaddir, savename), 'rb'))
            notfound = False
        except IOError:
            sel = namesuggester(savename, loaddir)
            if not sel:
                return
            else:
                savename = sel + '.p'

    if type(unpickled) == pandas.core.frame.DataFrame or \
    type(unpickled) == pandas.core.series.Series or \
    type(unpickled) == dict or \
    type(unpickled) == collections.Counter or \
    type(unpickled) == nltk.text.Text:
        output = unpickled

    if len(unpickled) == 1:
        if type(unpickled[0]) == pandas.core.frame.DataFrame or \
        type(unpickled[0]) == pandas.core.series.Series or \
        type(unpickled[0]) == dict or \
        type(unpickled[0]) == collections.Counter or \
        type(unpickled[0]) == nltk.text.Text:
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

def report_display():
    """Displays/downloads the risk report, depending on your browser settings"""
    class PDF(object):
        def __init__(self, pdf, size=(200,200)):
            self.pdf = pdf
            self.size = size
        def _repr_html_(self):
            return '<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)
        def _repr_latex_(self):
            return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)
    return PDF('report/risk_report.pdf',size=(800,650))

def ipyconverter(inputfile, outextension):
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
    """make a new project in current directory"""
    import os
    import shutil
    import stat
    import platform
    import corpkit
    from time import strftime, localtime

    path_to_corpkit = os.path.dirname(corpkit.__file__)
    thepath, corpkitname = os.path.split(path_to_corpkit)
    
    # make project directory
    fullpath = os.path.join(loc, name)
    os.makedirs(fullpath)

    # make other directories
    dirs_to_make = ['data', 'images']
    subdirs_to_make = ['dictionaries', 'saved_interrogations', 'corpus']
    for directory in dirs_to_make:
        os.makedirs(os.path.join(fullpath, directory))
    for subdir in subdirs_to_make:
        os.makedirs(os.path.join(fullpath, 'data', subdir))
    # copy the bnc dictionary to data/dictionaries
    shutil.copy(os.path.join(thepath, 'dictionaries', 'bnc.p'), os.path.join(fullpath, 'data', 'dictionaries'))
    # if not GUI
    if not root:
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
    "Searches a tree with Tregex and returns matching terminals"
    import os
    from corpkit.other import tregex_engine
    from corpkit.tests import check_dit
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
    """Creates a named tuple for a list of named queries to count.

    Pass in something like:

    [[u'NPs in corpus', r'NP'], [u'VPs in corpus', r'VP']]"""

    import collections
    import os
    import pandas
    import pandas as pd
    from time import strftime, localtime
    from corpkit.interrogator import interrogator
    from corpkit.editor import editor

    if quicksave:
        savedir = 'data/saved_interrogations'
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
        from corpkit.other import save_result
        save_result(results, quicksave)
    return results


    # if nothing, the query's fine! 

def interroplot(path, query):
    """Interrogates path with Tregex query, gets relative frequencies, and plots the top seven results"""
    from corpkit import interrogator, editor, plotter
    quickstart = interrogator(path, 'words', query)
    edited = editor(quickstart.results, '%', quickstart.totals, print_info = False)
    plotter(str(path), edited.results)

def datareader(data, plaintext = False, **kwargs):
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
    from corpkit.other import tregex_engine
    from corpkit.tests import check_dit
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

def tregex_engine(query = False, 
                  options = False, 
                  corpus = False,  
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
    import subprocess 
    import re
    from time import localtime, strftime
    from corpkit.tests import check_dit
    from dictionaries.word_transforms import wordlist

    on_cloud = check_dit()

    def find_wordnet_tag(tag):
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
        else:
            tregex_command = ["tregex.sh"]
        if not query:
            query = 'NP'
        # if checking for trees, use the -T option
        if check_for_trees:
            options = ['-T']

        filenaming = False
        #try:
        #    if '-f' in options:
        #        filenaming = True
        #except:
        #    pass

        if return_tuples or lemmatise:
            options = ['-o']
        # append list of options to query 
        if options:
            [tregex_command.append(o) for o in options]
        if query:
            tregex_command.append(query)
        if corpus:
            tregex_command.append(corpus)
        # do query
        try:
            res = subprocess.check_output(tregex_command, stderr=subprocess.STDOUT).splitlines()
        # exception handling for regex error
        except Exception, e:
            res = str(e.output).split('\n')

        if check_query:
            # define error searches 
            tregex_error = re.compile(r'^Error parsing expression')
            regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')
            # if tregex error, give general error message
            if re.match(tregex_error, res[0]):
                tregex_error_output = ""
                time = strftime("%H:%M:%S", localtime())
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Error parsing Tregex query.' % time
                    return False
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
    # find end of stderr
    regex = re.compile('(Reading trees from file|using default tree)')
    # remove stderr at start
    std_last_index = res.index(next(s for s in res if re.search(regex, s)))
    res = res[std_last_index + 1:]
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

def load_all_results(data_dir = 'data/saved_interrogations', root = False):
    """load every saved interrogation in data_dir into a dict"""
    import os
    import time
    from corpkit.other import load_result
    from time import localtime, strftime
    r = {}
    fs = [f for f in os.listdir(data_dir) if f.endswith('.p')]
    if len(fs) == 0:
        if not root:
            raise ValueError('No interrogations found in %s' % datadir)
        else:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations found in %s' % (thetime, datadir)
    l = 0
    for finding in fs:
        try:
            r[os.path.splitext(finding)[0]] = load_result(finding, loaddir = data_dir)
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s loaded as %s.' % (time, finding, os.path.splitext(finding)[0])
            l += 1
            if root:
                root.update()
        except:
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s failed to load. Try using load_result to find out the matter.' % (time, finding)
            if root:
                root.update()
    time = strftime("%H:%M:%S", localtime())
    print '%s: %d interrogations loaded from %s.' % (time, l, os.path.basename(data_dir))
    return r

def texify(series, n = 20, colname = 'Keyness', toptail = False, sort_by = False):
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
    from corpkit.other import tregex_engine
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
    import nltk
    from nltk.corpus import wordnet
    if pos:
        syns = wordnet.synsets(word, pos = pos)
    else:
        syns = wordnet.synsets(word)
    return list(set([l.name().replace('_', ' ').lower() for s in syns for l in s.lemmas()]))

def synonym_dictmaker(df):
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
    
def pmultiquery(path, 
    option = 'c', 
    query = 'any', 
    sort_by = 'total', 
    quicksave = False,
    num_proc = 'default', 
    function_filter = False,
    **kwargs):
    """Parallel process multiple queries or corpora.

    This function is used by interrogator if:

        a) path is a list of paths
        b) query is a dict of named queries.
    
    This function needs joblib 0.8.4 or above in order to run properly."""
    
    import collections
    import os
    import pandas
    import pandas as pd
    from collections import namedtuple
    from time import strftime, localtime
    from corpkit.interrogator import interrogator
    from corpkit.editor import editor
    from corpkit.other import save_result
    try:
        from joblib import Parallel, delayed
    except:
        raise ValueError('joblib, the module used for multiprocessing, cannot be found. ' \
                         'Install with:\n\n        pip install joblib')
    import multiprocessing
    num_cores = multiprocessing.cpu_count()

    def best_num_parallel(num_cores, num_queries):
        """decide how many parallel processes to run

        the idea, more or less, is to """
        if num_queries <= num_cores:
            return num_queries
        if num_queries > num_cores:
            if (num_queries / num_cores) == num_cores:
                return int(num_cores)
            if num_queries % num_cores == 0:
                return max([int(num_queries / n) for n in range(2, num_cores) if int(num_queries / n) <= num_cores])        
            else:
                import math
                if (float(math.sqrt(num_queries))).is_integer():
                    square_root = math.sqrt(num_queries)
                    if square_root <= num_queries / num_cores: 
                        return int(square_root)    
        return num_queries / ((num_queries / num_cores) + 1)

    # are we processing multiple queries or corpora?
    # find out optimal number of cores to use.
    multiple_option = False
    multiple_corpora = False

    if type(path) != str:
        multiple_corpora = True
        num_cores = best_num_parallel(num_cores, len(path))
    elif type(query) != str:
        multiple_corpora = False
        num_cores = best_num_parallel(num_cores, len(query))
    elif type(function_filter) != str:
        multiple_option = True
        num_cores = best_num_parallel(num_cores, len(function_filter.keys()))

    if num_proc != 'default':
        num_cores = num_proc

    # make sure quicksaves are right type
    if quicksave is True:
        raise ValueError('quicksave must be string when using pmultiquery.')
    
    # the options that don't change
    d = {'option': option,
         'paralleling': True,
         'function': 'interrogator'}

    # add kwargs to query
    for k, v in kwargs.items():
        d[k] = v

    # make a list of dicts to pass to interrogator,
    # with the iterable unique in every one
    ds = []
    if multiple_corpora and not multiple_option:
        path = sorted(path)
        for index, p in enumerate(path):
            name = os.path.basename(p)
            a_dict = dict(d)
            a_dict['path'] = p
            a_dict['query'] = query
            a_dict['outname'] = name
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif not multiple_corpora and not multiple_option:
        import collections
        for index, (name, q) in enumerate(query.items()):
            a_dict = dict(d)
            a_dict['path'] = path
            a_dict['query'] = q
            a_dict['outname'] = name
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_option:
        import collections
        for index, (name, q) in enumerate(function_filter.items()):
            a_dict = dict(d)
            a_dict['path'] = path
            a_dict['query'] = query
            a_dict['outname'] = name
            a_dict['function_filter'] = q
            a_dict['printstatus'] = False
            ds.append(a_dict)

    time = strftime("%H:%M:%S", localtime())
    if multiple_corpora and not multiple_option:
        print ("\n%s: Beginning %d parallel corpus interrogations:\n              %s" \
           "\n          Query: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, "\n              ".join(path), query) )

    elif not multiple_corpora and not multiple_option:
        print ("\n%s: Beginning %d parallel corpus interrogations: %s" \
           "\n          Queries: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, path, "', '".join(query.values())) )

    elif multiple_option:
        print ("\n%s: Beginning %d parallel corpus interrogations (multiple options): %s" \
           "\n          Query: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, path, query) )

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    res = Parallel(n_jobs=num_cores)(delayed(interrogator)(**x) for x in ds)
    res = sorted(res)

    # turn list into dict of results, make query and total branches,
    # save and return
    if not option.startswith('c'):
        out = {}
        print ''
        for (name, data), d in zip(res, ds):
            if not option.startswith('k'):
                outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
                stotal = data.sum(axis = 1)
                stotal.name = u'Total'
                output = outputnames(d, data, stotal)
            else:
                outputnames = collections.namedtuple('interrogation', ['query', 'results'])
                output = outputnames(d, data)
            out[name] = output
    
        # could be wrong for unstructured corpora?
        num_diff_results = len(data)
        time = strftime("%H:%M:%S", localtime())
        print "\n%s: Finished! Output is a dictionary with keys:\n\n         '%s'\n" % (time, "'\n         '".join(sorted(out.keys())))
        if quicksave:
            for k, v in out.items():
                save_result(v, k, savedir = 'data/saved_interrogations/%s' % quicksave)
        return out
    # make query and total branch, save, return
    else:
        out = pd.concat(res, axis = 1)
        out = editor(out, sort_by = sort_by, print_info = False, keep_stats = False)
        time = strftime("%H:%M:%S", localtime())
        print '\n%s: Finished! %d unique results, %d total.' % (time, len(out.results.columns), out.totals.sum())
        if quicksave:
            from corpkit.other import save_result
            save_result(out, quicksave)
        return out

def as_regex(lst, boundaries = 'w', case_sensitive = False, inverse = False):
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
    """show lines.ix[index][link] as frame"""
    url = lines.ix[index]['link'].replace('<a href=', '').replace('>link</a>', '')
    return HTML('<iframe src=%s width=1000 height=500></iframe>' % url)

