"""
In here are functions used internally by corpkit,  
not intended to be called by users.
"""

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

def tregex_engine(corpus=False,  
                  options=False, 
                  query=False, 
                  check_query=False,
                  check_for_trees=False,
                  just_content_words=False,
                  root=False,
                  preserve_case=False,
                  **kwargs):
    """
    Run a Java Tregex query
    
    :param query: tregex query
    :type query: str
    
    :param options: list of tregex options
    :type options: list of strs -- ['-t', '-o']
    
    :param corpus: place to search
    :type corpus: str
    
    :param check_query: just make sure query ok
    :type check_query: bool
    
    :param check_for_trees: find out if corpus contains parse trees
    :type check_for_trees: bool

    :returns: list of search results

    """
    import corpkit
    add_corpkit_to_path()
    
    # in case someone compiles the tregex query
    try:
        query = query.pattern
    except AttributeError:
        query = query
    
    import subprocess 
    from subprocess import Popen, PIPE, STDOUT

    import re
    from time import localtime, strftime
    from corpkit.dictionaries.word_transforms import wordlist
    import os
    import sys

    DEVNULL = open(os.devnull, 'w')

    if check_query or check_for_trees:
        send_stderr_to = subprocess.STDOUT
        send_stdout_to = DEVNULL
    else:
        send_stderr_to = DEVNULL
        send_stdout_to = subprocess.STDOUT

    filtermode = False
    if isinstance(options, list):
        filtermode = '-filter' in options
    if filtermode:
        options.pop(options.index('-filter'))

    treenumbermode = '-n' in options
    speaker_data = kwargs.get('speaker_data')

    on_cloud = checkstack('/opt/python/lib')

    # if check_query, enter the while loop
    # if not, get out of it
    an_error_occurred = True

    # site pack path
    corpath = os.path.join(os.path.dirname(corpkit.__file__))
    cor1 = os.path.join(corpath, 'tregex.sh')
    cor2 = os.path.join(corpath, 'corpkit', 'tregex.sh')

    # pyinstaller
    pyi = sys.argv[0].split('Contents/MacOS')[0] + 'Contents/MacOS/tregex.sh'

    possible_paths = ['tregex.sh', corpath, pyi, cor1, cor2]

    while an_error_occurred:
        tregex_file_found = False
        for i in possible_paths:
            if os.path.isfile(i):
                tregex_command = [i]
                tregex_file_found = True
                break
        if not tregex_file_found:
            thetime = strftime("%H:%M:%S", localtime())
            print("%s: Couldn't find Tregex in %s." % (thetime, ', '.join(possible_paths)))
            return False

        if not query:
            query = 'NP'
        # if checking for trees, use the -T option
        if check_for_trees:
            options = ['-o', '-T']

        filenaming = False
        if isinstance(options, list):
            if '-f' in options:
                filenaming = True

        # append list of options to query 
        if options:
            if '-s' not in options and '-t' not in options:
                options.append('-s')
        else:
            options = ['-o', '-t']
        for opt in options:
            tregex_command.append(opt)       
        if query:
            tregex_command.append(query)
        
        # if corpus is string or unicode, and is path, add that
        # if it's not string or unicode, it's some kind of corpus obj
        # in which case, add its path var

        if corpus:
            if isinstance(corpus, STRINGTYPE):
                if os.path.isdir(corpus) or os.path.isfile(corpus):
                    tregex_command.append(corpus)
                else:
                    filtermode = True
            elif hasattr(corpus, 'path'):
                tregex_command.append(corpus.path)
        
        if filtermode:
            tregex_command.append('-filter')

        if not filtermode:
            res = subprocess.check_output(tregex_command, stderr=send_stderr_to)
            res = res.decode(encoding='UTF-8').splitlines()
        else:
            p = Popen(tregex_command, stdout=PIPE, stdin=PIPE, stderr=send_stderr_to)
            p.stdin.write(corpus.encode('UTF-8', errors='ignore'))
            res = p.communicate()[0].decode(encoding='UTF-8').splitlines()
            p.stdin.close()
        
        # Fix up the stderr stdout rubbish
        if check_query:
            # define error searches 
            tregex_error = re.compile(r'^Error parsing expression')
            regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')
            # if tregex error, give general error message
            if re.match(tregex_error, res[0]):
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print('%s: Error parsing Tregex query.' % time)
                    return False
                time = strftime("%H:%M:%S", localtime())

                selection = INPUTFUNC('\n%s: Error parsing Tregex expression "%s".'\
                                      '\nWould you like to:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, query))
                if 'a' in selection.lower():
                    query = INPUTFUNC('\nNew Tregex query: ')
                elif 'b' in selection.lower():
                    print('')
                    return False
            
            # if regex error, try to help
            elif re.match(regex_error, res[0]):
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print('%s: Regular expression in Tregex query contains an error.' % time)
                    return False
                info = res[0].split(':')
                index_of_error = re.findall(r'index [0-9]+', info[1])
                justnum = index_of_error[0].split('dex ')
                spaces = ' ' * int(justnum[1])
                remove_start = query.split('/', 1)
                remove_end = remove_start[1].split('/', -1)
                time = strftime("%H:%M:%S", localtime())
                selection = INPUTFUNC('\n%s: Error parsing regex inside Tregex query: %s'\
                '. Best guess: \n%s\n%s^\n\nYou can either: \n' \
                '              a) rewrite it now\n' \
                '              b) exit\n\nYour selection: ' % \
                    (time, str(info[1]), str(remove_end[0]), spaces))
                if 'a' in selection:
                    query = INPUTFUNC('\nNew Tregex query: ')
                elif 'b' in selection:
                    print('')
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

    res = [r.strip() for r in res if r.strip()]

    # this is way slower than it needs to be, because it searches a whole subcorpus!
    if check_for_trees:
        if res[0].startswith('1:Next tree read:'):
            return True
        else:
            return False
    # return if no matches
    if not res:
        return []

    # make unicode and lowercase
    make_tuples = []

    # we need to get the data into tuples of equal length
    # the tuple should be n (file, speakername, result)

    if filenaming and any(x.startswith('# /') for x in res):
        for index, r in enumerate(res):
            if r.startswith('# /'):
                make_tuples.append([r, res[index + 1]])
        res = make_tuples
        # this deals with filtermode, slow_tregex, files_as_subcorpora...
    else:
        res = [[kwargs.get('filename', ''), x] for x in res] 

    # if we had numbered trees, remove numbers if no speaker data
    if treenumbermode:
        for fname, line in res:
            num, data = line.split(': ', 1)
            if speaker_data:
                speaker = speaker_data[int(num) - 1]
            else:
                speaker = ''
            make_tuples.append([fname, speaker, data])
        res = make_tuples
    elif not treenumbermode:
        res = [[a, '', b] for a, b in res]

    make_tuples = []
    if not preserve_case:
        for line in res:
            line[-1] = line[-1].lower().replace('/', '-slash-')
            make_tuples.append(line)
        res = make_tuples
    return res

def show(lines, index, show='thread'):
    """show lines.ix[index][link] as frame"""
    import corpkit
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
        if 'note' in list(kwargs.keys()):
            path_within_gui = os.path.join(nltkpath.split('/lib/python2.7')[0], 'nltk_data')
            if path_within_gui not in nltk.data.path:
                nltk.data.path.append(path_within_gui)
            if path_within_gui.replace('/nltk/', '/', 1) not in nltk.data.path:
                nltk.data.path.append(path_within_gui.replace('/nltk/', '/', 1))

def get_gui_resource_dir():
    import inspect
    import os
    import sys
    if sys.platform == 'darwin':
        fext = 'app'
    else:
        fext = 'exe'
    corpath = corpath = __file__
    extens = '.%s' % fext
    apppath = corpath.split(extens , 1)
    resource_path = ''
    # if not an .app
    if len(apppath) == 1:
        resource_path = os.path.dirname(corpath)
    else:
        apppath = apppath[0] + extens
        appdir = os.path.dirname(apppath)
        if sys.platform == 'darwin':
            #resource_path = os.path.join(apppath, 'Contents', 'Resources')
            resource_path = os.path.join(apppath, 'Contents', 'MacOS')
        else:
            resource_path = appdir
    return resource_path

def get_fullpath_to_jars(path_var):
    """when corenlp is needed, this sets corenlppath as the path to jar files,
    or returns false if not found"""
    import os
    important_files = ['stanford-corenlp-3.5.2-javadoc.jar', 'stanford-corenlp-3.5.2-models.jar',
                   'stanford-corenlp-3.5.2-sources.jar', 'stanford-corenlp-3.5.2.jar']
    # if user selected file in parser dir rather than dir,
    # get the containing dir
    path_var_str = path_var.get()

    if os.path.isfile(path_var_str):
        path_var_str = os.path.dirname(path_var_str.rstrip('/'))
    # if the user selected the subdir:
    if all(os.path.isfile(os.path.join(path_var_str, f)) for f in important_files):
        path_var.set(path_var_str)
        return True

    # if the user selected the parent dir:
    if os.path.isdir(path_var_str):
        # get subdirs containing the jar
        try:
            find_install = [d for d in os.listdir(path_var_str) \
                if os.path.isdir(os.path.join(path_var_str, d)) \
                and os.path.isfile(os.path.join(path_var_str, d, 'jollyday.jar'))]
        except OSError:
            pass
        if len(find_install) > 0:
            path_var.set(os.path.join(path_var_str, find_install[0]))
            return True

    # need to fix this duplicated code
    try:
        home = os.path.expanduser("~")
        try_dir = os.path.join(home, 'corenlp')
        if os.path.isdir(try_dir):
            path_var_str = try_dir
            # get subdirs containing the jar
            try:
                find_install = [d for d in os.listdir(path_var_str) \
                    if os.path.isdir(os.path.join(path_var_str, d)) \
                    and os.path.isfile(os.path.join(path_var_str, d, 'jollyday.jar'))]
            except OSError:
                pass
            if len(find_install) > 0:
                path_var.set(os.path.join(path_var_str, find_install[0]))
                return True
    except:
        pass
    return False

def determine_datatype(path):
    """
    Determine if plaintext, tokens or parsed XML
    """
    import os
    from collections import Counter
    exts = []
    if not os.path.isdir(path) and not os.path.isfile(path):
        raise ValueError("Corpus path '%s' doesn't exist." % path)
    singlefile = False
    if os.path.isfile(path):
        singlefile = True
        if '.' in path:
            exts = [os.path.splitext(path)[1]]
        else:
            exts = ['.txt']
    else:
        for (root, dirs, fs) in os.walk(path):
            for f in fs:
                if '.' in f:
                    ext = os.path.splitext(f)[1]
                    exts.append(ext)
    counted = Counter(exts)
    counted.pop('', None)
    try:
        mc = counted.most_common(1)[0][0]
    except IndexError:
        mc = '.txt'
    
    lookup = {'.txt': 'plaintext',
              '.conll': 'conll'}

    return lookup.get(mc, 'plaintext'), singlefile

def filtermaker(the_filter, case_sensitive=False, **kwargs):
    import re
    from corpkit.dictionaries.process_types import Wordlist
    from time import localtime, strftime
    root = kwargs.get('root')
    if isinstance(the_filter, (list, Wordlist)):
        from corpkit.other import as_regex
        the_filter = as_regex(the_filter, case_sensitive=case_sensitive)
    try:
        output = re.compile(the_filter)
        is_valid = True
    except:
        is_valid = False
        if root:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Filter %s' % (thetime, error_message))
            return 'Bad query'
    
    while not is_valid:
        if root:
            time = strftime("%H:%M:%S", localtime())
            print(the_filter)
            print('%s: Invalid the_filter regular expression.' % time)
            return False
        time = strftime("%H:%M:%S", localtime())
        selection = INPUTFUNC('\n%s: filter regular expression " %s " contains an error. You can either:\n\n' \
            '              a) rewrite it now\n' \
            '              b) exit\n\nYour selection: ' % (time, the_filter))
        if 'a' in selection:
            the_filter = INPUTFUNC('\nNew regular expression: ')
            try:
                output = re.compile(r'\b' + the_filter + r'\b')
                is_valid = True
            except re.error:
                is_valid = False
        elif 'b' in selection:
            print('')
            return False
    return output

def searchfixer(search, query, datatype=False):
    """
    Normalise query/search value
    """
    if isinstance(search, STRINGTYPE) and isinstance(query, dict):
        return search
    if isinstance(search, STRINGTYPE):
        srch = search[0].lower()
        if not srch.startswith('t') and not srch.lower().startswith('n'):
            if query == 'any':
                query = r'.*'
        search = {search: query}
    return search

def is_number(s):
    """
    Check if str can be can be made into float/int
    """
    try:
        float(s) # for int, long and float
        return True
    except ValueError:
        try:
            complex(s) # for complex
            return True
        except ValueError:
            return False
    except TypeError:
        return False

def animator(progbar,
             count,
             tot_string=False,
             linenum=False,
             terminal=False,
             init=False,
             length=False,
             quiet=False,
             **kwargs
            ):
    """
    Animates progress bar in unique position in terminal
    Multiple progress bars not supported in jupyter yet.
    """

    # if ipython?
    welcome_message = kwargs.pop('welcome_message', '')
    if welcome_message:
        welcome_message = welcome_message.replace('Interrogating corpus ... \n', '')
        welcome_message = welcome_message.replace('Concordancing corpus ... \n', '')
        welcome_message = welcome_message.replace('\n', '<br>').replace(' ' * 17, '&nbsp;' * 17)
    else:
        welcome_message = ''
    if init:
        from traitlets import TraitError
        try:
            from ipywidgets import IntProgress, HTML, VBox
            from IPython.display import display
            progress = IntProgress(min=0, max=length, value=1)
            using_notebook = True
            progress.bar_style = 'info'
            label = HTML()
            label.font_family = 'monospace'
            gblabel = HTML()
            gblabel.font_family = 'monospace'
            box = VBox(children=[label, progress, gblabel])
            display(box)
            return box
        except TraitError:
            pass
        except ImportError:
            pass
        # newest ipython error
        except AttributeError:
            pass
    if not init:
        try:
            from ipywidgets.widgets.widget_box import Box
            if isinstance(progbar, Box):
                label, progress, goodbye = progbar.children
                progress.value = count
                if count == length:
                    progress.bar_style = 'success'
                else:
                    label.value = '%s\nInterrogating: %s ...' % (welcome_message, tot_string)
                return
        except:
            pass

    # add startnum
    start_at = kwargs.get('startnum', 0)
    if start_at is None:
        start_at = 0.0
    denominator = kwargs.get('denom', 1)
    if kwargs.get('note'):
        if count is None:
            perc_done = 0.0
        else:
            perc_done = (count * 100.0 / float(length)) / float(denominator)
        kwargs['note'].progvar.set(start_at + perc_done)
        kwargs['root'].update()
        return

    if init:
        from corpkit.textprogressbar import TextProgressBar
        return TextProgressBar(length, dirname=tot_string)
        # this try is for sublime text nosetests, which don't take terminal object
    try:
        with terminal.location(0, terminal.height - (linenum + 1)):
            if tot_string:
                progbar.animate(count, tot_string, quiet=quiet)
            else:
                progbar.animate(count, quiet=quiet)
    # typeerror for nose
    except:
        if tot_string:
            progbar.animate(count, tot_string, quiet=quiet)
        else:
            progbar.animate(count, quiet=quiet)


def parse_just_speakers(just_speakers, corpus):
    if just_speakers is True:
        just_speakers = ['each']
    if just_speakers is False or just_speakers is None:
        return False
    if isinstance(just_speakers, STRINGTYPE):
        just_speakers = [just_speakers]
    if isinstance(just_speakers, list):
        if just_speakers == ['each']:
            from build import get_speaker_names_from_parsed_corpus
            just_speakers = get_speaker_names_from_parsed_corpus(corpus)
    return just_speakers


def get_deps(sentence, dep_type):
    if dep_type == 'basic-dependencies':
        return sentence.basic_dependencies
    if dep_type == 'collapsed-dependencies':
        return sentence.collapsed_dependencies
    if dep_type == 'collapsed-ccprocessed-dependencies':
        return sentence.collapsed_ccprocessed_dependencies

def timestring(input):
    """print with time prepended"""
    from time import localtime, strftime
    thetime = strftime("%H:%M:%S", localtime())
    print('%s: %s' % (thetime, input.lstrip()))

def makesafe(variabletext, drop_datatype=True, hyphens_ok=False):
    import re
    from corpkit.process import is_number
    if hyphens_ok:
        variable_safe_r = re.compile(r'[^A-Za-z0-9_-]+', re.UNICODE)
    else:
        variable_safe_r = re.compile(r'[^A-Za-z0-9_]+', re.UNICODE)
    try:
        txt = variabletext.name.split('.')[0]
    except AttributeError:
        txt = variabletext.split('.')[0]
    if drop_datatype:
        txt = txt.replace('-parsed', '')
    txt = txt.replace(' ', '_')
    if not hyphens_ok:
        txt = txt.replace('-', '_')
    variable_safe = re.sub(variable_safe_r, '', txt)
    if is_number(variable_safe):
        variable_safe = 'c' + variable_safe
    return variable_safe

def interrogation_from_conclines(newdata):
    """
    Make new interrogation result from its conc lines
    """
    from collections import Counter
    from pandas import DataFrame
    from corpkit.editor import editor
    results = {}
    conc = newdata
    subcorpora = list(set(conc['c']))
    for subcorpus in subcorpora:
        counted = Counter(list(conc[conc['c'] == subcorpus]['m']))
        results[subcorpus] = counted

    the_big_dict = {}
    unique_results = set([item for sublist in list(results.values()) for item in sublist])
    for word in unique_results:
        the_big_dict[word] = [subcorp_result[word] for name, subcorp_result \
                              in sorted(results.items(), key=lambda x: x[0])]
    # turn master dict into dataframe, sorted
    df = DataFrame(the_big_dict, index=sorted(results.keys())) 
    df = editor(df, sort_by='total', print_info=False)
    df.concordance = conc
    return df

def checkstack(the_string):
    """checks for pytex"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    return as_string.lower().count(the_string) > 1

def check_tex(have_ipython=True):
    """
    See if tex is available
    """
    import os
    if have_ipython:
        checktex_command = 'which latex'
        o = get_ipython().getoutput(checktex_command)[0]
        have_tex = not o.startswith('which: no latex in')
    else:
        import subprocess
        FNULL = open(os.devnull, 'w')
        checktex_command = ["which", "latex"]
        try:
            o = subprocess.check_output(checktex_command, stderr=FNULL)
            have_tex = True
        except subprocess.CalledProcessError:
            have_tex = False
    return have_tex


    
def get_corenlp_path(corenlppath):
    """
    Find a working CoreNLP path.
    Return a dir containing jars
    """

    import os
    import sys
    import re
    import glob
    

    cnlp_regex = re.compile(r'stanford-corenlp-[0-9\.]+\.jar')

    # if something has been passed in, find that first
    if corenlppath:
        # if it's a file, get the parent dir
        if os.path.isfile(corenlppath):
            corenlppath = os.path.dirname(corenlppath)
            if any(re.search(cnlp_regex, f) for f in os.listdir(corenlppath)):
                return corenlppath
        # if it's a dir, check if dir contains jar
        elif os.path.isdir(corenlppath):
            if any(re.search(cnlp_regex, f) for f in os.listdir(corenlppath)):
                return corenlppath
            # if it doesn't contain jar, get subdir by glob
            globpath = os.path.join(corenlppath, 'stanford-corenlp*')
            poss = [i for i in glob.glob(globpath) if os.path.isdir(i)]
            if poss:
                poss = poss[-1]
            if any(re.search(cnlp_regex, f) for f in os.listdir(poss)):
                return poss

    # put possisble paths into list
    pths = ['.', 'corenlp',
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), 'corenlp')]
    if isinstance(corenlppath, STRINGTYPE):
        pths.append(corenlppath)
    possible_paths = os.getenv('PATH').split(os.pathsep) + sys.path + pths
    # remove empty strings
    possible_paths = set([i for i in possible_paths if os.path.isdir(i)])

    # check each possible path
    for path in possible_paths:
        if any(re.search(cnlp_regex, f) for f in os.listdir(path)):
            return path
    # check if it's a parent
    for path in possible_paths:
        globpath = os.path.join(path, 'stanford-corenlp*')
        cnlp_dirs = [d for d in glob.glob(globpath)
                     if os.path.isdir(d)]
        for cnlp_dir in cnlp_dirs:
            if any(re.search(cnlp_regex, f) for f in os.listdir(cnlp_dir)):
                return cnlp_dir
    return

def unsplitter(data):
    """unsplit contractions and apostophes from tokenised text"""
    

    if isinstance(data, STRINGTYPE):
        replaces = [("$ ", "$"),
                    ("`` ", "``"),
                    (" ,", ","),
                    (" .", "."),
                    ("'' ", "''"),
                    (" n't", "n't"),
                    (" 're", "'re"),
                    (" 'm", "'m"),
                    (" 's", "'s"),
                    (" 'd", "'d"),
                    (" 'll", "'ll"),
                    ('  ', ' ')
                   ]
        for find, replace in replaces:
            data = data.replace(find, replace)
        return data
    else:
        unsplit = []
        for index, t in enumerate(data):
            if index == 0 or index == len(data) - 1:
                unsplit.append(t)
                continue
            if "'" in t and not t.endswith("'"):
                rejoined = ''.join([data[index - 1], t])
                unsplit.append(rejoined)
            else:
                if not "'" in data[index + 1]:
                    unsplit.append(t)
    return unsplit

def classname(cls):
    """Create the class name str for __repr__"""
    return '.'.join([cls.__class__.__module__, cls.__class__.__name__])


def format_middle(tree, show, df=False, sent_id=False, ixs=False):
    tree_vals = {}
    if 't' in show or 'mt' in show:
        tre = str(tree).replace('/', '-slash')
        # todo?

    if 'mw' in show:
        tree_vals['mw'] = [i.replace('/', '-slash-') for i in tree.leaves()]
    if 'ml' in show:
        print(df)
        tree_vals['ml'] = [df.loc[sent_id, i]['l'] for i in ixs]
    if 'mp' in show:
        tree_vals['mp'] = [y for x, y in tree.pos()]
    if 'mx' in show:
        from corpkit.dictionaries import taglemma
        tree_vals['mx'] = [taglemma.get(y.lower(), y) for x, y in tree.pos()]

    output = []
    zipped = zip(*[tree_vals[i] for i in show])

    for tup in zipped:
        output.append('/'.join(tup))
    # now we have [a/a, nicer/nice, day/day]
    return ' '.join(output)

def format_conc(tups, show, df=False, sent_id=False, root=False, ixs=False):
    """
    Prepare start or end of tgrepped conc lines
    """
    tree_vals = {}
    if 't' in show or 'mt' in show:
        tre = str(root).replace('/', '-slash')
        # todo?
    if 'mw' in show:
        tree_vals['mw'] = [w.replace('/', '-slash-') for w, p, i in tups]
    if 'ml' in show:
        tree_vals['ml'] = [df.loc[sent_id, i]['l'] for i in ixs]
    if 'mp' in show:
        tree_vals['mp'] = [p.replace('/', '-slash-') for w, p, i in tups]
    if 'mx' in show:
        from corpkit.dictionaries import taglemma
        tree_vals['mx'] = [taglemma.get(p.lower(), p) for w, p, i in tups]
    if 'ms' in show:
        tree_vals['ms'] = [str(sent_id) for i in tups]
    if 'mi' in show:
        tree_vals['mi'] = [str(i) for w, p, i in tups]

    output = []
    zipped = zip(*[tree_vals[i] for i in show])

    for tup in zipped:
        output.append('/'.join(tup))
    # now we have [a/a, nicer/nice, day/day]
    return ' '.join(output)

def show_tree_as_per_option(show, tree, sent=False, df=False,
                            sent_id=False, conc=False,
                            only_format_match=True):
    """
    Turn a ParentedTree into shown output

    :returns: tok_id, metcat, start, middle, end
    """
    # make a list of all indices
    start = False
    end = False
    metcat = False
    
    # here, we need to get the indexes of the first and last
    # token in the match, when the tree is flattened.
    # i wonder if there is an easier way!
    all_leaf_positions = tree.root().treepositions(order='leaves')
    match_position = tree.treeposition()
    ixs = [e for e, i in enumerate(all_leaf_positions, start=1) \
           if i[:len(match_position)] == match_position]

    # get the data from the left and right
    if conc:
        start = [(w, p, i) for i, (w, p) in enumerate(tree.root().pos(), start=1)
                 if i < ixs[0]]
        end = [(w, p, i) for i, (w, p) in enumerate(tree.root().pos(), start=1)
                 if i > ixs[-1]]

    middle = format_middle(tree, show, df=df, sent_id=sent_id, ixs=ixs)

    if conc:
        if not only_format_match:
            start_ixes = list(range(1, len(start)+1))
            end_ixes = list(range(ixs[-1]+1, len(end)+1))
            start = format_conc(start, show, df=df, sent_id=sent_id, root=tree.root(), ixs=start_ixes)
            end = format_conc(end, show, df=df, sent_id=sent_id, root=tree.root(), ixs=end_ixes)
        else:
            start = ' '.join([w for w, p, i in start])
            end = ' '.join([w for w, p, i in end])

    return ixs[0], start, middle, end

def tgrep(parse_string, search):
    """
    Uses tgrep to search a Sentence

    :param sents: Sentences from CoreNLP XML
    :type sents: `list` of `Sentence` objects

    :param search: A search query
    :type search: `str` -- Tgrep query
    """
    from nltk.tree import ParentedTree
    from nltk.tgrep import tgrep_nodes, tgrep_positions
    pt = ParentedTree.fromstring(parse_string)
    ptrees = [i for i in list(tgrep_nodes(search, [pt])) if i]
    return [item for sublist in ptrees for item in sublist]

def canpickle(obj):
    """determine if object can be pickled"""
    import os
    try:
        from cPickle import UnpickleableError as unpick_error
        import cPickle as pickle
        from cPickle import PicklingError as unpick_error_2
    except ImportError:
        import pickle
        from pickle import UnpicklingError as unpick_error
        from pickle import PicklingError as unpick_error_2

    mode = 'w' if PYTHON_VERSION == 2 else 'wb'
    with open(os.devnull, mode) as fo:
        try:
            pickle.dump(obj, fo)
            return True
        except (unpick_error, TypeError, unpick_error_2) as err:
            return False

def sanitise_dict(d):
    """
    Make a dict that works as query attribute
    """
    if not isinstance(d, dict):
        return
    newd = {}
    if d.get('kwargs') and isinstance(d['kwargs'], dict):
        for k, v in d['kwargs'].items():
            if canpickle(v) and not isinstance(v, type):
                newd[k] = v
    for k, v in d.items():
        if canpickle(v) and not isinstance(v, type):
            newd[k] = v
    return newd

def saferead(path):
    """
    Read a file with detect encoding
    
    :returns: text and its encoding
    """
    import chardet
    import sys
    if sys.version_info.major == 3:
        enc = 'utf-8'
        try:
            with open(path, 'r', encoding=enc) as fo:
                data = fo.read()
        except:
            with open(path, 'rb') as fo:
                data = fo.read().decode('utf-8', errors='ignore')
        return data, enc
    else:
        with open(path, 'r') as fo:
            data = fo.read()
        try:
            enc = 'utf-8'
            data = data.decode(enc)
        except UnicodeDecodeError:
            enc = chardet.detect(data)['encoding']
            data = data.decode(enc, errors='ignore')
        return data, enc

def urlify(s):
    "Turn title into filename"
    import re
    s = s.lower()
    s = re.sub(r"[^\w\s-]", '', s)
    s = re.sub(r"\s+", '-', s)
    s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
    return s

def get_speakername(sent):
    """Return speakername without CoreNLP_XML"""
    sn = sent._element.xpath('speakername/text()')
    return str(sn[0]) if sn else ''

def gui():
    import os
    from corpkit.gui import corpkit_gui
    current = os.getcwd()
    corpkit_gui(noupdate=True, loadcurrent=current)


def dictformat(d, query=False):
    """
    Format a dict search query
    """
    from corpkit.constants import transshow, transobjs
    if isinstance(d, STRINGTYPE) and isinstance(query, dict):
        newd = {}
        for k, v in query.items():
            newd[k] = fix_search({d: v})
        return dictformat(newd)
        if query:
            sformat = dictformat(query)
            return sformat
        else:
            return d
    if all(isinstance(i, dict) for i in d.values()):
        sformat = '\n'
        for k, v in d.items():
            sformat += '             ' + k + ':'
            sformat += dictformat(v)
        return sformat
    if len(d) == 1 and d.get('v'):
        return 'Features'
    sformat = '\n'
    for k, v in d.items():
        adj = ''
        if k[0] in ['-', '+']:
            adj = ' ' + k[:2]
            k = k[2:]
        if k == 't':
            dratt = ''
        else:
            dratt = transshow.get(k[-1], k[-1])
        if len(k) > 1:
            drole = transobjs.get(k[0], k[0])
        else:
            drole = ''
        if k == 't':
            drole = 'Trees'
        vform = getattr(v, 'pattern', v)
        sformat += '                %s %s %s: %s\n' % (adj, drole, dratt.lower(), vform)
    return sformat


def fix_search(search, case_sensitive=False, root=False):
    """if search has nested dicts, remove them"""
    ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 's']
    
    # handle the possibility of nesting queries
    nestq = False
    if isinstance(search, dict):
        if all(isinstance(v, dict) for v in search.values()):
            nestq = True
            for v in search.values():
                if not all(x.islower() and x.isalpha() and len(x) < 4 for x in v.keys()):
                    nestq = False
    if nestq:
        newd = {}
        for k, v in search.items():
            newd[k] = fix_search(v)
        return newd

    newsearch = {}

    if not search:
        return
    if isinstance(search, STRINGTYPE):
        return search
    if search.get('t'):
        return search
    trees = 't' in search.keys()
    for srch, pat in search.items():
        if len(srch) == 1 and srch in ends:
            if trees:
                pass
            else:
                srch = 'm%s' % srch
        if len(srch) == 3 and srch[0] in ['+', '-']:
            srch = list(srch)
            if srch[-1] in ends:
                srch.insert(2, 'm')
            else:
                srch.append('w')
            srch = ''.join(srch)
        if isinstance(pat, dict):
            for k, v in list(pat.items()):
                if k != 'w':
                    newsearch[srch + k] = pat_format(v, case_sensitive=case_sensitive, root=root)
                else:
                    newsearch[srch] = pat_format(v, case_sensitive=case_sensitive, root=root)
        else:
            newsearch[srch] = pat_format(pat, case_sensitive=case_sensitive)
    return newsearch

def pat_format(pat, case_sensitive=False, root=False):
    from corpkit.dictionaries.process_types import Wordlist
    import re
    if pat == 'any':
        return re.compile(r'.*')
    if isinstance(pat, Wordlist):
        pat = list(pat)
    if isinstance(pat, list):
        if all(isinstance(x, int) for x in pat):
            pat = [str(x) for x in pat]
        pat = filtermaker(pat, case_sensitive=case_sensitive, root=root)
    else:
        if isinstance(pat, int):
            return pat
        if isinstance(pat, re._pattern_type):
            return pat
        if case_sensitive:
            pat = re.compile(pat)
        else:
            pat = re.compile(pat, re.IGNORECASE)
    return pat

def make_name_to_query_dict(existing={}):
    from corpkit.constants import transshow, transobjs
    for l, o in transobjs.items():
        if o == 'Match':
            o = ''
        else:
            o = o + ' '
        for m, p in sorted(transshow.items()):
            if m in ['n', 't']:
                continue
            if p != 'POS' and o != '':
                p = p.lower()
            existing['%s%s' % (o, p)] = '%s%s' % (l, m)
    return existing

def get_index_name(corpus, subcorpora, just_speakers):
    """
    Name df index---just_speakers will be deprecated soon
    """
    lst = []
    if subcorpora:
        return subcorpora
    elif just_speakers == 'each' or just_speakers == ['each']:
        lst.append('speaker')
    if corpus.level == 'c':
        lst.append('folder')
    elif corpus.level == 's':
        lst.append('file')
    if len(lst) == 1:
        return lst[0]
    else:
        return lst

def make_savename_for_features(corpname=False, obj='features', subcorpora=False):
    subc = subcorpora if subcorpora else ''
    if isinstance(subcorpora, list):
        subc = '-'.join(subcorpora)
    if subc in ['default', 'folders', 'folder']:
        subc = ''
    if corpname:
        obj = corpname + '-' + obj
    if subc:
        obj = obj + '-' + subc
    return obj

def auto_usecols(search, exclude, show, usecols):
    """
    Figure out if we can speed up conll parsing based on search,
    exclude and show. the return value is passed to pandas.read_csv
    so that only relevant columns are parsed.

    If usecols isn't None, the user has specified needed cols.

    todo: coref
    """
    if usecols:
        return usecols
    from corpkit.constants import CONLL_COLUMNS

    # get all objs from search, exclude and show
    needed = []
    for i in search.keys():
        if 'g' in i:
            needed.append('d')
        elif 'd' in i:
            needed.append('g')
        needed.append(i)
    if isinstance(exclude, dict):
        for i in exclude.keys():
            needed.append(i)
    if isinstance(show, list):
        for i in show:
            needed.append(i)
    else:
        needed.append(show)
    # get the obj and attr from these
    stcols = []
    for i in needed:
        stcols.append(i[-1])
        try:
            stcols.append(i[-2])
        except:
            pass
    # word class is pos
    stcols = ['p' if i == 'x' else i for i in stcols]
    # we always get word right now, but could remove '2' in the future
    # also, sent index violates conll-u, so that might change
    out = [0, 1, 2]
    for n, c in enumerate(CONLL_COLUMNS):
        if c in stcols and c not in out:
            out.append(n)
    return out

def format_tregex(results, show=False, lemtag=False, exclude=False,
                  excludemode=False, translated_option=False,
                  lem_instance=False, whole=False,
                  speaker_data=False, countmode=False):
    """
    Format tregex by show list
    """
    import re

    if countmode:
        return results

    if not results:
        return

    done = []

    fnames, snames, results = zip(*results)

    # this needs to be standardised!
    new_show = [x.lstrip('m') for x in show]
    new_show = ['w' if not x else x for x in new_show]

    if 'l' in new_show or 'x' in new_show:
        from corpkit.process import lemmatiser
        lemmata = lemmatiser(results, tag=lemtag,
                             lem_instance=lem_instance,
                             translated_option=translated_option)
    else:
        lemmata = [None for i in results]
    for word, lemma in list(zip(results, lemmata)):
        bits = []
        if exclude and exclude.get('w'):
            if len(list(exclude.keys())) == 1 or excludemode == 'any':
                if re.search(exclude.get('w'), word):
                    continue
            if len(list(exclude.keys())) == 1 or excludemode == 'any':
                if re.search(exclude.get('l'), lemma):
                    continue
            if len(list(exclude.keys())) == 1 or excludemode == 'any':
                if re.search(exclude.get('p'), word):
                    continue
            if len(list(exclude.keys())) == 1 or excludemode == 'any':
                if re.search(exclude.get('x'), lemma):
                    continue
        if exclude and excludemode == 'all':
            num_to_cause_exclude = len(list(exclude.keys()))
            current_num = 0
            if exclude.get('w'):
                if re.search(exclude.get('w'), word):
                    current_num += 1
            if exclude.get('l'):
                if re.search(exclude.get('l'), lemma):
                    current_num += 1
            if exclude.get('p'):
                if re.search(exclude.get('p'), word):
                    current_num += 1
            if exclude.get('x'):
                if re.search(exclude.get('x'), lemma):
                    current_num += 1   
            if current_num == num_to_cause_exclude:
                continue                 

        for i in new_show:
            if i == 't':
                bits.append(word)
            if i == 'l':
                bits.append(lemma)
            elif i == 'w':
                bits.append(word)
            elif i == 'p':
                bits.append(word)
            elif i == 'x':
                bits.append(lemma)
        joined = '/'.join(bits)
        done.append(joined)

    done = list(zip(fnames, snames, done))
    
    return done

def make_conc_lines_from_whole_mid(wholes,
                                   middle_column_result,
                                   show=False,
                                   category=False,
                                   filename=False):
    """
    Create concordance line output from tregex output
    """
    import re
    import os
    if not wholes and not middle_column_result:
        return []

    conc_lines = []
    # remove duplicates from results
    unique_wholes = []
    unique_middle_column_result = []
    duplicates = []

    word_index = show.index('w') if 'w' in show else 0

    metcat = category if category else ''

    for (f, sk, whole), mid in list(zip(wholes, middle_column_result)):
        mid = mid[-1]
        joined = '-join-'.join([f, sk, whole, mid])
        if joined not in duplicates:
            duplicates.append(joined)
            unique_wholes.append([f, sk, whole])
            unique_middle_column_result.append(mid)

    # split into start, middle and end, dealing with multiple occurrences
    # this fails when multiple show values are given, because they are slash separated...
    for (f, sk, whole), mid in list(zip(unique_wholes, unique_middle_column_result)):
        mid = mid.split('/')[word_index]
        reg = re.compile(r'([^a-zA-Z0-9-]|^)(' + re.escape(mid) + r')([^a-zA-Z0-9-]|$)', \
                         re.IGNORECASE | re.UNICODE)
        offsets = [(m.start(), m.end()) for m in re.finditer(reg, whole)]
        for offstart, offend in offsets:
            start, middle, end = whole[0:offstart].strip(), whole[offstart:offend].strip(), \
                                 whole[offend:].strip()
            # lin = [ix, category, fname, sname, start, mid, end]
            conc_lines.append(['_,_', metcat, os.path.basename(f), sk, start, middle, end])
    return conc_lines

def gettag(query, lemmatag=False):
    """
    Find tag for WordNet lemmatisation
    """
    if lemmatag:
        return lemmatag

    tagdict = {'n': 'n',
               'j': 'a',
               'v': 'v',
               'a': 'r'}

    # in case someone compiles the tregex query
    query = getattr(query, 'pattern', query)
    qr = query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', '')
    firstletter = next((c for c in qr if c.isalpha()), 'n')
    return tagdict.get(firstletter.lower(), 'n')

def lemmatiser(list_of_words, tag, translated_option,
               lem_instance=False, preserve_case=False):
    """
    Take a list of unicode words and a tag and return a lemmatised list
    """
    from corpkit.dictionaries.word_transforms import wordlist, taglemma
    if not lem_instance:
        from nltk.stem.wordnet import WordNetLemmatizer
        lem_instance = WordNetLemmatizer()
    output = []
    for word in list_of_words:
        if 'u' in translated_option:
            word = taglemma.get(word.lower(), 'Other')
        else:
            word = wordlist.get(word, lem_instance.lemmatize(word, tag))
        output.append(word)
    return output

