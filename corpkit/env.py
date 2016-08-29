"""
A corpkit interpreter, with natural language commands.

todo:

* documentation
* handling of kwargs tuples etc
* checking for bugs, tests
* merge entries with name

"""
from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

import os
import traceback
import pandas as pd
import readline
import atexit
import rlcompleter

import corpkit
from corpkit import *
from corpkit.constants import transshow, transobjs

# pandas display setup, though this is rarely used when LESS
# and tabview are available
size = pd.util.terminal.get_terminal_size()
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 0)
pd.set_option('display.float_format', lambda x: '${:,.3f}'.format(x))

# allow ctrl-r, etc
readline.parse_and_bind('set editing-mode vi')

# this code makes it possible to remember history from previous sessions
history_path = os.path.expanduser("~/.pyhistory")

def save_history(history_path=history_path):
    """
    On exit, add previous commands to history file
    """
    import readline

    try:
        readline.remove_history_item(readline.get_current_history_length() - 1)
    except ValueError:
        pass
    readline.write_history_file(history_path)

if os.path.exists(history_path):
    try:
        readline.set_history_length(1000)
        readline.read_history_file(history_path)
        readline.set_history_length(1000)
    except IOError:
        pass

# bind to exit
atexit.register(save_history)

# tab completion
readline.parse_and_bind('tab: complete')

del os, atexit, readline, rlcompleter, save_history, history_path


def interpreter(debug=False, fromscript=False, quiet=False):
    import os

    #def noprint(*args, **kwargs):
    #    pass

    #if quiet:
    #    print = noprint
    #else:
    #    print = print

    allig = '\n   Welcome!\n'
    allig += "               .-._   _ _ _ _ _ _ _ _\n    " \
             ".-''-.__.-'00  '-' ' ' ' ' ' ' ' '-.\n    " \
             "'.___ '    .   .--_'-' '-' '-' _'-' '._\n    " \
             "V: V 'vv-'   '_   '.       .'  _..' '.'.\n    "\
             "  '=.____.=_.--'   :_.__.__:_   '.   : :\n    "\
             "          (((____.-'        '-.  /   : :\n    "\
             "                            (((-'\ .' /\n    "\
             "                          _____..'  .'\n    "\
             "                         '-._____.-'\n"

    class Objects(object):
        """
        In here are all of the major variables being used by the interpreter
        This is much nicer than using globals
        """

        def __init__(self):

            # get dict of all possible wordlists
            from corpkit.dictionaries.roles import roles
            from corpkit.dictionaries.wordlists import wordlists
            from corpkit.dictionaries.process_types import processes
            from collections import defaultdict
            wl = wordlists._asdict()
            try:
                wl.update(roles.__dict__)
            except AttributeError:
                wl.update(roles._asdict())
            wl.update(processes.__dict__)

            # main variables the user might access
            self.result = None
            self.previous = None
            self.edited = None
            self.corpus = None
            self.concordance = None
            self.query = None
            self.features = None
            self.postags = None
            self.wordclasses = None
            self.stored = {}
            self.figure = None
            self.totals = None
            self.wordlists = wl
            self.wordlist = None

            # system toggles and references to older data
            self._in_a_project = None
            self._previous_type = None
            self._old_concs = []
            self._conc_colours = defaultdict(dict)
            self._conc_kwargs = {'n': 999}

            # user settings  (more to come?)
            self._do_conc = True
            self._interactive = True
            self._decimal = 3

    objs = Objects()

    # basic way to check that we're currently in a project, because i'm lazy
    proj_dirs = ['data', 'saved_interrogations', 'exported']
    objs._in_a_project = all(x in os.listdir('.') for x in proj_dirs)

    def generate_outprint():
        """
        Text to appear when switching to IPython
        """
        s = 'Switched to IPython ... defined variables:\n\n\t'
        s += 'corpus, results, concordance, edited ...\n\n\tType "quit" to return to corpkit environment'
        return s

    def read_script(fname):
        """
        If a sript was passed to corpkit, get lines in it, minus comments
        """
        from corpkit.constants import OPENER
        with OPENER(fname, 'r') as fo:
            data = fo.read()
        data = data.splitlines()
        data = [i for i in data if i.strip() and i.strip()[0] != '#']
        
        # turn off concordancing if it's never used in the script
        if 'concordance' not in ' '.join(data):
            objs._do_conc = False

        return list(reversed(data))

    def helper(tokens):
        """
        Give user help if they enter a command alone
        """
        func = get_command.get(tokens[0], False)

        if not func:
            print('Not recognised: %s' % tokens[0])
            return

        print(getattr(func, '__doc__', 'Not written yet, sorry.'))

    def switch_to_ipython(args):
        from IPython import embed
        from IPython.terminal.embed import InteractiveShellEmbed
        s = generate_outprint()
        for k, v in objs.__dict__.items():
            if not k.startswith('_'):
                locals()[k] = v

        ret = InteractiveShellEmbed(header=s,
                    babaii='babaii',
                    #colors='Linux',
                    exit_msg='Switching back to corpkit environment ...',
                    local_ns=locals())
        cc = ret()

    def switch_to_jupyter(args):
        comm = ["jupyter", "notebook"]
        import subprocess
        if args:
            import os
            nbfile = args[-1]
            if not nbfile.endswith('.ipynb'):
                nbfile = nbfile + '.ipynb'
            if os.path.isfile(nbfile):
                comm.append(nbfile)
        subprocess.call(comm)            


    def switch_to_gui(args):
        import subprocess
        import os
        print('Loading graphical interface ... ')
        subprocess.call(["python", "-m", 'corpkit.gui', os.getcwd()])


    def show_concordance(args, kwargs):

        import pydoc
        kwargs = process_kwargs(args)
        if kwargs:
            objs._conc_kwargs = kwargs
        if objs.concordance is None:
            print("There's no concordance here right now, sorry.")
            return
        found_the_conc = next((i for i, c in enumerate(objs._old_concs) if c.equals(objs.concordance)), None)
        if found_the_conc is None:
            #print('Nothing here yet.')
            return
        if objs._conc_colours.get(found_the_conc):
            try:
                lines_to_print = []
                from colorama import Fore, Back, Style, init
                lines = objs.concordance.format(print_it=False, **objs._conc_kwargs).splitlines()
                for line in lines:
                    num = line.strip().split(' ', 1)[0]
                    gotnum = objs._conc_colours[found_the_conc].get(num, False)
                    if gotnum:
                        if gotnum.upper() in ['DIM', 'NORMAL', 'BRIGHT', 'RESET_ALL']:
                            thing_to_color = Style
                        else:
                            thing_to_color = Fore
                        if any(i.startswith('back') for i in args):
                            thing_to_color = Back
                        lines_to_print.append(getattr(thing_to_color, gotnum.upper()) + line)
                    else:
                        lines_to_print.append(line)
                pydoc.pipepager('\n'.join(lines_to_print), cmd="less -X -R")
            except ImportError:
                pydoc.pipepager(getattr(objs, command).format(print_it=False, **objs._conc_kwargs), cmd="less -X -R")

        else:
            pydoc.pipepager(getattr(objs, command).format(print_it=False, **objs._conc_kwargs), cmd="less -X -R")


    def show_table(command):
        import tabview
        # this horrible code accounts for cases where we modify with exec
        toshow = getattr(getattr(objs, command), 'results', False)
        if isinstance(toshow, (pd.DataFrame, pd.Series)):
            tabview.view(toshow.round(objs._decimal), column_width=10)
            return
        elif toshow:
            tabview.view(toshow.round(objs._decimal), column_width=10)
            return
        else:
            if isinstance(getattr(objs, command, False), (pd.DataFrame, pd.Series)):
                tabview.view(getattr(objs, command).round(objs._decimal), column_width=10)
                return


    def single_command_print(command):
        """
        If the user enters just a single token, show them that token
        This function also processes multiword tokens sometimes, which is inconsistent.
        """

        helpable = ['calculate', 'plot', 'search', 'fetch', 'store', 'save', 'edit',
                    'export', 'sort', 'loead', 'mark', 'del']

        if isinstance(command, list) and len(command) == 1 and command[0] in helpable:
            helper(command)

        args = []
        if isinstance(command, list):
            args = command[1:]
            command = command[0]

        if command == 'ls':
            import os
            print('\n'.join(os.listdir('.')))

        if command == 'clear':
            print(chr(27) + "[2J")

        if command == 'history':
            import readline
            for i in range(readline.get_current_history_length()):
                print(readline.get_history_item(i + 1))

        if command == 'help':
            import pydoc
            pydoc.pipepager(\
            "\nThis is a dedicated interpreter for corpkit, a tool for creating, searching\n" \
            "and visualising corpora. It works through a combination of objects and commands:\n\n" \
            "Objects:\n\n" \
            " +---------------+-----------------------------------------------+ \n"\
            " | Object        | Contains                                      | \n"\
            " +===============+===============================================+ \n"\
            " | `corpus`      | Dataset selected for parsing or searching     | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `results`     | Search output                                 | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `edited`      | Results after sorting, editing or calculating | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `concordance` | Concordance lines from search                 | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `features`    | General linguistic features of corpus         | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `wordclasses` | Distribution of word classes in corpus        | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `postags`     | Distribution of POS tags in corpus            | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `figure`      | Plotted data                                  | \n"\
            " +---------------+-----------------------------------------------+ \n"\
            " | `query`       | Values used to perform search or edit         | \n"\
            " +---------------+-----------------------------------------------+ "
            "\n\nCommand examples:\n\n" \
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | Command         | Syntax                                                                             | \n"\
            " +=================+====================================================================================+ \n"\
            " | `new`           | `new project <name>`                                                               | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `add`           | `add '../corpus'`                                                                  | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `set`           | `set <corpusname>`                                                                 | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `parse`         | `parse corpus with [options]*`                                                     | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `search`        | `search corpus for [feature matching pattern]* showing [feature]* with [options]*` | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `edit`          | `edit result by [skipping subcorpora/entries matching pattern]* with [options]*`   | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `calculate`     | `calculate result/edited as operation of denominator`                              | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `sort`          | `sort result/concordance by value`                                                 | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `plot`          | `plot result/edited as line chart with [options]*`                                 | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `show`          | `show object`                                                                      | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `export`        | `export result to string/csv/latex/file <filename>`                                | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `save`          | `save object to <filename>`                                                        | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `load`          | `load object as result`                                                            | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `store`         | `store object as <name>`                                                           | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `fetch`         | `fetch <name> as object`                                                           | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `help`          | `help command/object`                                                              | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `history`       | `history`                                                                          | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `ipython`       | `ipython`                                                                          | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            " | `py`            | `py print('hello world')`                                                          | \n"\
            " +-----------------+------------------------------------------------------------------------------------+ \n"\
            "More information:\n\nYou can access more specific help by doing 'help <command>', or by visiting\n" \
            "http://corpkit.readthedocs.io/en/latest\n\n" \
            "For help on viewing results, hit '?' when in the result viewing mode. For concordances, hit 'h'.\n\n(Hit 'q' to exit help).\n\n", cmd='less -X -R -S') 

        if command == 'corpus':
            if not hasattr(objs.corpus, 'name'):
                print('Corpus not set. use "set <corpusname>".')
                return
            else:
                print(objs.corpus)
        

        elif command == 'python' or command == 'ipython':
            switch_to_ipython(args)

        elif command.startswith('jupyter') or command == 'notebook':
            switch_to_jupyter(args)

        elif command == 'gui':
            switch_to_gui(args)
        
        elif command in ['result', 'edited', 'totals', 'previous',
                         'features', 'postags', 'wordclasses']:

            show_table(command)

        elif command == 'concordance':
            show_concordance(args, kwargs)

        elif command == 'wordlists':
            show_this([command])
        elif command == 'wordlist':
            print(objs.wordlist)
        elif command == 'query':
            show_this([command])
        else:
            pass

    def set_corpus(tokens):
        """
        Set the active corpus:

        :Example:

           `set junglebook-parsed`
        """
        if tokens and tokens[0].startswith('decimal'):
            objs._decimal = int(tokens[2])
            print('Decimal places set to %d.' % objs._decimal) 
            return

        if not objs._in_a_project:
            print("Must be in project to set corpus.")
            return
        
        from corpkit.other import load
        if not tokens:
            show_this(['corpora'])
            selected = INPUTFUNC('Pick a corpus by name or number: ')
            selected = selected.strip()
            if not selected:
                return
            elif selected.isdigit():
                dirs = [x for x in os.listdir('data') if os.path.isdir(os.path.join('data', x))]
                set_corpus([dirs[int(selected)-1]])
                return
            else:
                set_corpus([selected])
                return

        path = tokens[0]
        loadsaved = len(tokens) > 1 and tokens[1].startswith('load')
        if os.path.exists(path) or os.path.exists(os.path.join('data', path)):
            
            objs.corpus = Corpus(path, load_saved=loadsaved)
            for i in ['features', 'wordclasses', 'postags']:
                try:
                    dat = load(objs.corpus.name + '-%s' % i)
                    if hasattr(dat, 'results'):
                        dat = dat.results
                    setattr(objs, i, dat)
                except (UnicodeDecodeError, IOError):
                    pass

        else:
            try:
                dirs = [x for x in os.listdir('data') if os.path.isdir(os.path.join('data', x))]
                set_corpus([dirs[int(tokens[-1])-1]])
            except:
                print('Corpus not found: %s' % tokens[0])
                return

    def parse_search_related(search_related):
        """
        parse the capitalised tokens in
        'search corpus FOR GOVERNOR-LEMMA MATCHING .* AND LEMMA MATCHING .* showing ...'
        """
        search = {}
        exclude = {}   
        searchmode = 'all'
        cqlmode = False
        featuresmode = False
        if search_related[0] != 'for':
            search_related.insert(0, 'for')
        
        for i, token in enumerate(search_related):
            if token in ['for', 'and', 'not', 'or']:
                if token == 'or':
                    searchmode = 'any'
                if search_related[i+1] == 'not':
                    continue
                if search_related[i+1] == 'features':
                    search = {'v': 'any'}
                    featuresmode = True
                    break
                k = search_related[i+1]
                if k == 'cql':
                    cqlmode = True
                    aquery = next((i for i in search_related[i+2:] if i not in ['matching']), False)
                    if aquery:
                        search = aquery
                        break
                k = process_long_key(k)
                v = search_related[i+3].strip("'")
                v = parse_pattern(v)
                if token == 'not':
                    exclude[k] = v
                else:
                    search[k] = v
        return search, exclude, searchmode, cqlmode, featuresmode

    def process_long_key(srch):
        """
        turn governor-lemma into 'gl', etc.
        """
        from corpkit.constants import transshow, transobjs
        
        transobjs = {v.lower(): k.replace(' ', '-') for k, v in transobjs.items()}
        transshow = {v.lower(): k.replace(' ', '-') for k, v in transshow.items()}
        showplurals = {k + 's': v for k, v in transshow.items()}
        objsplurals = {k + 's': v for k, v in transobjs.items()}
        
        transshow['distance'] = 'r'
        transshow['ngram'] = 'n'
        transshow['distances'] = 'r'
        transshow['ngrams'] = 'n'
        transshow['wordclass'] = 'x'
        transshow['wordclasses'] = 'x'

        transshow.update(showplurals)
        transobjs.update(objsplurals)

        ngram = srch.startswith('n')
        colls = srch.startswith('b')

        if ngram or colls:
            newsrch = srch.split('-', 1)[-1]
            if newsrch == srch:
                srch = 'nw' if ngram else 'bw'
            else:
                srch = newsrch

        srch = srch.lower()
        
        if '-' not in srch:
            if srch in transobjs:
                string = transobjs.get(srch) + 'w'
            elif srch in transshow or srch.startswith('t'):
                if not srch.startswith('t'):
                    string = 'm' + transshow.get(srch)
                else:
                    string = transshow.get(srch, 't')
            else:
                string = srch
        else:
            obj, show = srch.split('-', 1)
            string = '%s%s' % (transobjs.get(obj, obj), transshow.get(show, show))
        if ngram:
            return 'n' + string
        elif colls:
            return 'b' + string
        else:
            return string

    def parse_pattern(val):
        """
        Parse the token after 'matching'---that is, the search criteria
        """
        trans = {'true': True,
                 'false': False,
                 'none': None}

        if any(val.startswith(x) for x in ['roles', 'processes', 'wordlist']) \
            and any(x in [':', '.'] for x in val):
            lis, attrib = val.split('.', 1) if '.' in val else val.split(':', 1)
            customs = []
            from corpkit.dictionaries import roles, processes, wordlists
            mapped = {'roles': roles,
                      'processes': processes}

            if lis.startswith('wordlist'):
                return objs.wordlists.get(attrib)
            else:
                return getattr(mapped.get(lis), attrib)

        if val.isdigit():
            return int(val)
        elif val.lower() in trans.keys():
            return trans.get(val)
        # interpret columns
        elif all(i in ['c', 'f', 's', 'l', 'm', 'r'] for i in val.lower()) and len(val) <= 6:
            return [i for i in val.lower()]

        else:
            if val in dir(__builtins__) + ['any', 'all']:
                return val
            try:
                return eval(val)
            except (SyntaxError, NameError):
                return val

    def search_helper(text='search'):
        """
        Interactive mode for search, exclude or show
        """

        if text in ['search', 'exclude']:
            search_or_show = {}
        else:
            search_or_show = []
        while True:
            out = INPUTFUNC('\n    %s (words, lemma, pos, function ... ) > ' % text)
            out = out.lower()
            
            if not out:
                break
            if out.startswith('done'):
                break


            if out == 'cql':
                cql = INPUTFUNC('\n        CQL query > ')
                return cql.strip()
            if text == 'show':
                out = out.replace(', ', ' ').replace(',', ' ').replace('/', ' ')
                return out.split(' ')
                #search_or_show.append(out)
                #continue
            val = INPUTFUNC('\n        value (regex, wordlist) > ')
            if not val:
                continue
            if val.startswith('done'):
                break
            out = process_long_key(out)
            search_or_show[out] = parse_pattern(val)

        return search_or_show

    def process_kwargs(tokens):
        """
        Turn the last part of a command into a dict of kwargs
        """

        if 'with' in tokens:
            start = tokens.index('with')
            with_related = tokens[start+1:]
        else:
            with_related = []
        withs = {}
        skips = []
        for i, token in enumerate(with_related):

            if i in skips or token == 'and':
                continue
            if token == 'not':
                withs[with_related[i+1].lower()] = False
                skips.append(i+1)
            elif '=' not in token:
                if len(with_related) >= i+2 and with_related[i+1] == 'as':
                    val = with_related[i+2]
                    val = parse_pattern(val)
                    withs[token.lower()] = val
                    skips.append(i+1)
                    skips.append(i+2)
                else:
                    withs[token.lower()] = True
            elif '=' in token:
                k, v = token.lower().split('=', 1)
                v = parse_pattern(v)
                withs[k] = v
        return withs


    def parse_search_args(tokens):
        """
        Put all search arguments together---search, exclude, show, and kwargs
        """
        tokens = tokens[1:]
        
        # interactive mode
        if not tokens:
            search = search_helper(text='search')
            exclude = search_helper(text='exclude')
            show = search_helper(text='show')
            show = [process_long_key(i) for i in show]
            kwargs = {'search': search, 'show': show, 'exclude': exclude,
                      'cql': isinstance(search, str), 'conc': objs._do_conc}
            return kwargs

        search_related = []
        for token in tokens:
            search_related.append(token)
            if token in [',', 'showing', 'with', 'excluding']:
                break

        if 'excluding' in tokens:
            start = tokens.index('excluding')
            ex_related = tokens[start+1:]
            end = ex_related.index('showing') if 'showing' in ex_related else False
            if end is False:
                end = ex_related.index('with') if 'with' in ex_related else False
            if end:
                ex_related = ex_related[:end]
        else:
            ex_related = []

        if 'showing' in tokens:
            start = tokens.index('showing')
            show_related = tokens[start+1:]
            end = show_related.index('with') if 'with' in show_related else False
            if end:
                show_related = show_related[:end]
        else:
            show_related = []

        if 'with' in tokens:
            start = tokens.index('with')
            with_related = tokens[start+1:]
        else:
            with_related = []

        search, exclude, searchmode, cqlmode, featuresmode = parse_search_related(search_related)
        if not exclude and ex_related:
            exclude, _, _, _, _ = parse_search_related(ex_related)

        show = []
        if show_related:
            for token in show_related:
                token = token.rstrip(',')
                if token == 'and':
                    continue
                token = process_long_key(token)
                show.append(token)
        else:
            show = ['w']

        withs = process_kwargs(tokens)

        kwargs = {'search': search, 'exclude': exclude, 'df1_always_df': True,
                  'show': show, 'cql': cqlmode, 'conc': objs._do_conc, 'searchmode': searchmode}
        kwargs.update(withs)
        return kwargs

    def search_corpus(tokens):
        """
        Search a corpus for lexicogrammatical features. You are limited only by your imagination.
        
        :Syntax:

        search corpus for [object matching pattern]* showing [things to show]* with [extra options]*
         
        The asterisk marked parts of the query can be recursive and negated

        :Examples:

           > search corpus for cql matching '[word="test"]' showing word and lemma
           > search corpus for governor-function matching roles:process with coref
           > search corpus for trees matching "/NN.?/ >># NP" 
           > search corpus for words matching "^[abcde]" with preserve_case and case_sensitive
        """
        if not objs.corpus:
            print('Corpus not set. use "set <corpusname>".')
            return

        kwargs = parse_search_args(tokens)
        kwargs['quiet'] = quiet
        
        if debug:
            print(kwargs)

        objs.result = objs.corpus.interrogate(**kwargs)
        objs.totals = objs.result.totals
        # this should be done for pos and wordclasses too
        if kwargs['search'] == {'v': 'any'}:
            try:
                from corpkit.other import save
                save(objs.result.results, 'features')
            except:
                pass
        print('')
        return objs.result

    def show_this(tokens):
        """
        Show any object in a human-readable form
        """
        if tokens[0] == 'corpora':
            dirs = [x for x in os.listdir('data') if os.path.isdir(os.path.join('data', x))]
            dirs = ['\t%d: %s' % (i, x) for i, x in enumerate(dirs, start=1)]
            print ('\n'.join(dirs))
        elif tokens[0].startswith('store'):
            print(objs.stored)
        elif tokens[0].startswith('wordlists'):
            if '.' in tokens[0] or ':' in tokens[0]:
                if ':' in tokens[0]:
                    _, attr = tokens[0].split(':')
                else:
                    _, attr = tokens[0].split('.')
                print(objs.wordlists.get(attr))
            else:
                for k, v in sorted(objs.wordlists.items()):
                    showv = str(v[:5])
                    if len(v) > 5:
                        showv = showv.rstrip('] ') + ' ... ]'
                    print('"%s": %s' % (k, showv))

        elif tokens[0] == 'saved':
            ss = [i for i in os.listdir('saved_interrogations') if not i.startswith('.')]
            print ('\t' + '\n\t'.join(ss))
        elif tokens[0] == 'query':
            for k, v in sorted(objs.query.items()):
                print('%s: %s' % (str(k), str(v)))
        elif tokens[0] == 'figure':
            if hasattr(objs, 'figure') and objs.figure:
                objs.figure.show()
            else:
                print('Nothing here yet.')
        elif tokens[0] in ['features', 'wordclasses', 'postags']:
            print(getattr(objs.corpus, tokens[0]))

        elif hasattr(objs, tokens[0]):
            single_command_print(tokens)
        else:
            print("No information about: %s" % tokens[0])

    def get_info(tokens):
        pass

    def edit_conc(kwargs):
        from corpkit.interrogation import Concordance
        for k, v in kwargs.items():
            if k == 'just_subcorpora':
                objs.concordance = objs.concordance[objs.concordance['c'].str.contains(v)]
            elif k == 'skip_subcorpora':
                objs.concordance = objs.concordance[~objs.concordance['c'].str.contains(v)]
            elif k == 'just_entries':
                objs.concordance = objs.concordance[objs.concordance['m'].str.contains(v)]
            elif k == 'skip_entries':
                objs.concordance = objs.concordance[~objs.concordance['m'].str.contains(v)]
        objs.concordance = Concordance(objs.concordance)

        return objs.concordance
        #if objs._interactive:
        #    show_this(['concordance'])

    def edit_something(tokens):
        """
        Edit an interrogation or concordance

        :Example:

           `edit result by skippings subcorpora matching [1,2,3] with keep_top as 5`

        """

        thing_to_edit = get_thing_to_edit(tokens[0])

        trans = {'skipping': 'skip',
                 'keeping':  'just',
                 'merging':  'merge',
                 'spanning': 'span'}

        recog = ['not', 'matching', 'result', 'entry', 'entries', 'results', 'subcorpus', 'subcorpora', 'edited']

        # skip, keep, merge
        by_related = []
        if 'by' in tokens:
            start = tokens.index('by')
            by_related = tokens[start+1:]

        if not by_related:
            inter = interactive_edit(tokens)

        kwargs = {}
        skips = []
        for i, token in enumerate(by_related):
            if i in skips:
                continue
            if token in trans.keys():
                k = trans.get(token) + '_' + by_related[i+1]
                v = next((x for x in by_related[i+1:] if x not in recog), False)
                if not v:
                    print('v not found')
                    return
                v = parse_pattern(v)
                kwargs[k] = v
                #for x in range(i, ind+1):
                #    skips.append(x)
        
        # add bools etc
        morekwargs = process_kwargs(tokens)
        for k, v in morekwargs.items():
            if k not in kwargs.keys():
                kwargs[k] = v

        if debug:
            print(kwargs)

        from corpkit.interrogation import Concordance
        if isinstance(thing_to_edit, Concordance):
            edt = edit_conc(kwargs)
        else:
            edt = thing_to_edit.edit(**kwargs)
        if isinstance(edt, Concordance):
            objs.concordance = edt
        else:
            objs.edited = edt
            if hasattr(objs.edited, 'totals'):
                objs.totals = objs.edited.totals
        return edt


    def run_command(tokens):
        """
        Run command and send output to objs class
        """

        command = get_command.get(tokens[0], unrecognised)        
        out = command(tokens[1:])
        import pydoc
        import tabview
        
        # store the previous thing as previous
        attr = objmap.get(command, False)
        if attr:
            objs.previous = getattr(objs, attr)
            objs._previous_type = attr

        if command == search_corpus:
            if not objs.result:
                return
            objs.result = out
            objs.previous = out
            if objs._interactive:
                show_this(['result'])
            objs.query = out.query
            if objs._do_conc:
                objs.concordance = out.concordance
                objs._old_concs.append(objs.concordance)
            else:
                objs.concordance = None
            # find out what is going on here
            objs.edited = False

        # either all or no showing should be done here 
        if command in [edit_something, sort_something, calculate_result,
                       annotate_conc, keep_conc, del_conc]:
            from corpkit.interrogation import Concordance
            if isinstance(out, Concordance):
                objs._old_concs[-1] = objs.concordance
                if objs._interactive:
                    show_this(['concordance'] + tokens[1:])
            else:
                if objs._interactive:
                    show_this(['edited'])
                    
        else:
            if debug:
                print('Done:', repr(out))
        return out
        
    def export_result(tokens):
        """
        Send a result, edited result or concordance to file

        :Example:

           `export result as csv to out.csv`
           `export concordance as latex to concs.tex`

        """
        import os
        obj = getattr(objs, tokens[0])
        if tokens[0] == 'result':
            obj = getattr(obj, 'results', obj)
        if len(tokens) == 1:
            print(obj.to_string())
            return
        tokens = tokens[1:]

        if 'as' in tokens:
            formt = tokens[tokens.index('as') + 1][0]
            tokens = tokens[tokens.index('as') + 2:]
        else:
            formt = 'c'

        buf = tokens[-1]

        if buf == formt:
            buf = None
        
        if os.pathsep not in buf:
            buf = os.path.join('exported', buf)
        if formt == 'c':
            obj.to_csv(buf, sep='\t')
        elif formt == 's':
            obj.to_string(buf)
        elif formt == 'l':
            obj.to_latex(buf)

        if buf:
            if os.path.isfile(buf):
                print('Saved to: %s' % buf)
            else:
                print('Problem exporting file.')

    def interactive_edit(tokens):
        print('Not done yet')
        pass

    def get_thing_to_edit(token):
        thing_to_edit = objs.result
        if token == 'concordance':
            thing_to_edit = objs.concordance
        elif token == 'edited':
            thing_to_edit = objs.edited
        return thing_to_edit

    def sort_something(tokens):
        """
        Sort a result or concordance line

        """

        thing_to_edit = get_thing_to_edit(tokens[0])

        recog = ['by', 'with', 'from']

        val = next((x for x in tokens[1:] if x not in recog), 'total')

        from corpkit.interrogation import Concordance
        if not isinstance(thing_to_edit, Concordance):
            sortedd = thing_to_edit.edit(sort_by=val)
            if sortedd == 'linregress':
                raise ValueError("scipy needs to be installed for linear regression sorting.")
                return
            objs.edited = sortedd
            objs.totals = objs.edited.totals
            return objs.edited
        else:
            if val.startswith('i'):
                sorted_lines = thing_to_edit.sort_index()
            else:
                if val.startswith('l') or val.startswith('r') or val.startswith('m'):
                    l_or_r = objs.concordance[val[0]]
                    ind = int(val[1:])
                    if val[0] == 'l':
                        ind = -ind
                    else:
                        ind = ind-1
                    import numpy as np
                    
                    # bad arg parsing here!
                    if 'slashsplit' in tokens:
                        splitter = '/'
                    else:
                        splitter = ' '

                    to_sort_on = l_or_r.str.split(splitter).tolist()
                    to_sort_on = [i[ind].lower() if i and len(i) >= abs(ind) else np.nan for i in to_sort_on]
                    thing_to_edit['x'] = to_sort_on
                    val = 'x'

                elif val in ['scheme', 'color', 'colour']:
                    val = 'x'
                    num_col = objs._conc_colours[len(objs._old_concs)-1]
                    series = []
                    for i in range(len(thing_to_edit)):
                        series.append(num_col.get(str(i), 'zzzzz'))
                    thing_to_edit['x'] = series
                sorted_lines = thing_to_edit.sort_values(val[0], axis=0, na_position='first')
            
            if val == 'x':
                sorted_lines = sorted_lines.drop('x', axis=1)
            
            objs.concordance = Concordance(sorted_lines)

            # do not add new entry to old concs for sorting :)
            objs._old_concs[-1] = objs.concordance
            if objs._interactive:
                single_command_print('concordance')

    def plot_result(tokens):
        """
        Visualise an interrogation using matplotlib
        """
        
        import matplotlib.pyplot as plt
        kinds = ['line', 'heatmap', 'bar', 'barh', 'pie', 'area']
        kind = next((x for x in tokens if x in kinds), 'line')
        kwargs = process_kwargs(tokens)
        kwargs['tex'] = kwargs.get('tex', False)
        title = kwargs.pop('title', False)
        objs.figure = getattr(objs, tokens[0]).visualise(title=title, kind=kind, **kwargs)
        objs.figure.show()
        return objs.figure

    def asciiplot_result(tokens):
        """
        Visualise an interrogation with a simple ascii line chart
        """
        obj, attr = tokens[0].split(':', 1) if ':' in tokens[0] else tokens[0].split('.', 1)
        to_plot = getattr(objs, obj)
        # if it said 'asciiplot result.this on axis 1', turn it into
        # asciiplot result.this with axis as 1

        if 'on' in tokens and not 'with' in tokens:
            tokens[tokens.index('on')] = 'with'
            if tokens[tokens.index('with')+1] == 'axis':
                if tokens[tokens.index('with')+2] in [0, 1]:
                    tokens.insert(tokens.index('with')+2, 'as')

        kwargs = process_kwargs(tokens)
        to_plot.asciiplot(attr, **kwargs)

    def calculate_result(tokens):
        """
        Get relative frequencies, combine results, do keywording

        :Syntax:

        calculate <result>/<edited> as <operation> of <denominator>

        :Examples:

           > calculate result as percentage of self
           > calculate edited as percentage of features.clauses
           > calculate result as percentage of stored.myname

        """
        calcs = ['k', '%', '+', '/', '-', '*', 'percentage']
        operation = next((i for i in tokens if any(i.startswith(x) for x in calcs)), False)
        if not operation:
            if tokens[-1].startswith('conc'):
                res = objs.concordance.calculate()
                objs.result = res.results
                objs.totals = res.totals
                if objs._interactive:
                    show_this(['result'])
                return
            else:
                print('Bad operation.')
                return
        denominator = tokens[-1]
        if denominator.startswith('features'):
            attr = denominator.split('.', 1)[-1]
            denominator = objs.features[attr.title()]
        elif denominator.startswith('wordclasses'):
            attr = denominator.split('.', 1)[-1]
            denominator = objs.wordclasses[attr.title()]
        elif denominator.startswith('postags'):
            attr = denominator.split('.', 1)[-1]
            denominator = objs.postags[attr.upper()]
        elif denominator.startswith('stored'):
            attr = denominator.split('.', 1)[-1]
            denominator = fetch_this([attr], unbound=True)
        if operation == 'percentage':
            operation = '%'
        the_obj = getattr(objs, tokens[0])
        objs.edited = the_obj.edit(operation, denominator)
        if hasattr(objs.edited, 'totals'):
            objs.totals = objs.edited.totals
        #print('\nedited:\n\n', objs.edited.results, '\n')
        return objs.edited

    def parse_corpus(tokens):
        """
        Parse an unparsed corpus

        :Example:

           `parse corpus with speaker_segmentation and metadata and multiprocess as 2`

        """
        if tokens[0] != 'corpus':
            print('Command not understood. Use "set <corpusname>" and "parse corpus"')
        if not objs.corpus:
            print('Corpus not set. use "set <corpusname>" on an unparsed corpus.')
            return

        if objs.corpus.datatype != 'plaintext':
            print('Corpus is not plain text.')
            return
        kwargs = process_kwargs(tokens)
        parsed = objs.corpus.parse(**kwargs)
        if parsed:
            objs.corpus = parsed
        return

    def fetch_this(tokens, unbound=False):
        """
        Get something from storage

        :Example:

           `fetch my_result as result`
        """

        from corpkit.corpus import Corpus
        from corpkit.interrogation import Interrogation, Concordance
        
        from_wl = False
        to_fetch = objs.stored.get(tokens[0], False)

        if to_fetch is False:
            to_fetch = objs.wordlists.get(tokens[0], False)
            from_wl = True
            if to_fetch is False:
                print('Not in store or wordlists: %s' % tokens[0])
                return

        if unbound:
            return to_fetch

        if from_wl:
            objs.wordlist = to_fetch
            showv = to_fetch[:5]
            if len(to_fetch) > 5:
                showv = str(showv).rstrip('] ') + ' ... ]'
            print('%s (%s) fetched as wordlist.' % (repr(tokens[0]), showv))
            return

        if len(tokens) < 3:
            if isinstance(to_fetch, Corpus):
                weneed = 'corpus'
            elif isinstance(to_fetch, Interrogation):
                if hasattr(to_fetch, 'denominator'):
                    weneed = 'edited'
                else:
                    weneed = 'result'
            elif isinstance(to_fetch, Concordance):
                weneed = 'concordance'
        else:
            weneed = tokens[2]

        if weneed == 'corpus':
            objs.corpus = to_fetch
        elif weneed.startswith('conc'):
            objs.concordance = to_fetch
        elif weneed == 'result':
            objs.result = to_fetch
        elif weneed == 'edited':
            objs.edited = to_fetch

        print('%s fetched as %s.' % (repr(to_fetch), weneed))

    def save_this(tokens, passedin=False):
        """
        Save a result or concordance

        :Example:

           `save result as 'non_pronoun_actors'`
        """
        if passedin:
            to_save = passedin
        else:
            to_save = getattr(objs, tokens[0])

        if to_save == 'store' and not passedin:
            for k, v in objs.stored.items():
                save_this(['as', k], passedin=v)

        if tokens[0] == 'figure' or hasattr(to_save, 'savefig'):
            tokens[-1] = os.path.join('images', tokens[-1])
            to_save.savefig(tokens[-1])
        else:
            to_save.save(tokens[-1])


    def load_this(tokens):
        """
        Load data from file
        """

        from corpkit.other import load
        if tokens[2] == 'result':
            objs.result = load(tokens[0])
        if tokens[2] == 'concordance':
            objs.concordance = load(tokens[0])
        if tokens[2] == 'edited':
            objs.edited = load(tokens[0])

    def interactive_listmaker():
        done_words = []
        text = 'Enter words separated by spaces, or one per line. (Leave the line blank to end)\n\n\t> '
        while True:
            res = INPUTFUNC(text)
            text = '\t> '
            if res:
                if ',' in res:
                    words = [i.strip(', ') for i in res.split()]
                    for w in words:
                        done_words.append(w)
                else:
                    done_words.append(res.strip())
            else:                    
                return done_words
    
    def new_thing(tokens):
        """
        Start a new project with a name of your choice, then move into it
        """
        if tokens[0] == 'project':
            from corpkit.other import new_project
            new_project(tokens[-1])
            os.chdir(tokens[-1])
        if tokens[0] == 'wordlist':
            the_name = next((tokens[i+1] for i, t in enumerate(tokens) if t in ['called', 'named']), None)
            if not the_name:
                print('Syntax: new wordlist named <name>.')
                return
            if objs.wordlists.get(the_name):
                print('"%s" already exists in wordlists.' % the_name)
                return
            filename = next((tokens[i+1] for i, t in enumerate(tokens) if t in ['from']), None)
            if filename:
                with open(filename, 'r') as fo:
                    words = [i.strip() for i in fo.read().splitlines() if i]
            else:
                words = interactive_listmaker()
            if words:
                objs.wordlists[the_name] = words
                objs.wordlist = words
                print('Wordlist "%s" stored.' % the_name)

    def get_matching_indices(tokens):
        """
        Find concordance indices matching some criteria in tokens

        This can be:

            - an int as index: "20"
            - a pseudo index: "5-10"
            - a column and regex: "l matching 'regex'"
            - a colour name

        :returns: a `set` of matching indices

        """
        # what's missing from this list?
        # hard coding in case user doesn't have colorama
        colours = ['red', 'yellow', 'magenta', 'lightmagenta_ex', 'black',
                   'white', 'lightcyan_ex', 'reset', 'green', 'lightyellow_ex',
                   'lightblack_ex', 'lightwhite_ex', 'blue', 'lightblue_ex',
                   'lightgreen_ex', 'cyan', 'lightred_ex']
        cols = []
        token = tokens[0]
        if token in colours:
            colourdict = objs._conc_colours[len(objs._old_concs)-1]
            return set([k for k, v in colourdict.items() if token == v])  
            
        # annotate range of tokens
        if '-' in token:
            first, last = token.split('-', 1)
            if not first:
                first = 0
            if not last:
                last = len(objs.concordance.index)
            for n in range(int(first), int(last)+1):
                cols.append(str(n))
        # get by index/indices
        elif token.isdigit():
            cols = [i for i in tokens if i.isdigit()]
        else:
            # regex match only what's shown in the window
            window = objs._conc_kwargs.get('window', 35)
            token_bits = list(token)
            for bit in token_bits:
                if bit.lower() == 'm':
                    slic = slice(None, None)
                elif bit.lower() == 'l':
                    slic = slice(-window, None)
                elif bit.lower() == 'r':
                    slic = slice(None, window)
                # get slice for left window
                mx = max(objs.concordance[bit.lower()].str.len()) if bit.lower() == 'l' else 0
                # get the regex criteria
                if 'matching' in tokens:
                    rgx = tokens[tokens.index('matching') + 1]
                else:
                    rgx = tokens[1]
                # get the window size of context, and reduce to just windows
                trues = objs.concordance[bit].str.rjust(mx).str[slic].str.contains(rgx)
                mtch = objs.concordance[trues]
                matches = list(mtch.index)
                for ind in matches:
                    cols.append(str(ind))

        return set(cols)

    def annotate_conc(tokens):
        """
        Annotate concordance lines matching criteria with a colour or style

        :Example:

           `mark m matching 'ing$' red
        """
        from colorama import Fore, Back, Style, init
        init(autoreset=True)
        cols = get_matching_indices(tokens)
        color = tokens[-1]
        for line in cols:
            if int(line) in list(objs.concordance.index):
                objs._conc_colours[len(objs._old_concs)-1][line] = color
        single_command_print(['concordance'] + tokens)

    def add_corpus(tokens):
        """
        Copy a folder to the ./data directory of a project

        :Example:

           `add '../../data'`
        """
        import shutil
        import os
        outf = os.path.join(os.getcwd(), 'data', os.path.basename(tokens[-1]))
        shutil.copytree(tokens[-1], outf)
        print('%s added to %s.' % (tokens[-1], outf))

    def del_conc(tokens):
        """
        Delete concordance lines matching criteria

        :Example:

           `del m matching 'ing$'`
        """
        from corpkit.interrogation import Concordance
        cols = get_matching_indices(tokens)
        cols = [int(i) for i in cols]
        objs.concordance = Concordance(objs.concordance.drop(cols, axis=0))
        return objs.concordance

    def keep_conc(tokens):
        """
        Keep concordance lines matching criteria

        :Example:

           `keep m matching 'ing$'`
        """
        from corpkit.interrogation import Concordance
        cols = get_matching_indices(tokens)
        cols = [int(i) for i in cols]
        objs.concordance = Concordance(objs.concordance.loc[cols])
        return objs.concordance

    def store_this(tokens):
        """
        Send a result into storage

        :Example:

           `store result as 'processes'`

        """

        to_store = getattr(objs, tokens[0])

        #if not to_store:
        #    print('Not storable:' % tokens[0])
        #    return

        if tokens[1] == 'as':
            name = tokens[2]
        else:
            count = 0
            while str(count) in objs.stored.keys():
                count += 1
            name = str(count)
        if name in objs.stored.keys():
            cont = INPUTFUNC('%s already in store. Replace it? (y/n) ')
            if cont.lower().startswith('n'):
                return
        objs.stored[name] = to_store
        print('Stored: %s' % name)

    def toggle_this(tokens):
        """
        Toggle a specified option

        Currently available:

        - toggle conc
        - toggle interactive

        """
        if tokens[0].startswith('conc'):
            objs._do_conc = not objs._do_conc
            s = 'on' if objs._do_conc else 'off'
            print('Concordancing turned %s.' % s)
        if tokens[0].startswith('interactive'):
            objs._interactive = not objs._interactive
            s = 'on' if objs._interactive else 'off'
            print('Auto showing of results and concordances turned %s.' % s)            

    def run_previous(tokens):
        import shlex
        output = list(reversed(objs.previous))[int(tokens[0]) - 1][0]
        tokens = [i.rstrip(',') for i in shlex.split(output)]
        return run_command(tokens)

    def ch_dir(tokens):
        """
        Change directory

        :Example:

           `cd essays`

        """
        import os
        os.chdir(tokens[0])
        print(os.getcwd())
        get_prompt()

    def ls_dir(tokens):
        """
        List directory contents
        
        :Example:

           `ls data`

        """
        import os
        nonhidden = [i for i in os.listdir(tokens[0]) if not i.startswith('.')]
        print('\n'.join(nonhidden))

    get_command = {'set': set_corpus,
                   'show': show_this,
                   'search': search_corpus,
                   'info': get_info,
                   'parse': parse_corpus,
                   'export': export_result,
                   'redo': run_previous,
                   'mark': annotate_conc,
                   'del': del_conc,
                   'just': keep_conc,
                   'sort': sort_something,
                   'toggle': toggle_this,
                   'edit': edit_something,
                   'ls': ls_dir,
                   'cd': ch_dir,
                   'plot': plot_result,
                   'asciiplot': asciiplot_result,
                   'help': helper,
                   'store': store_this,
                   'new': new_thing,
                   'fetch': fetch_this,
                   'save': save_this,
                   'load': load_this,
                   'calculate': calculate_result,
                   'add': add_corpus}

    objmap = {search_corpus: 'result',
              edit_something: 'edited',
              calculate_result: 'edited',
              sort_something: 'edited',
              plot_result: 'figure',
              set_corpus: 'corpus',
              load_this: 'result'}

    def unrecognised(*args, **kwargs):
        print('unrecognised!')

    import shlex

    if debug:
        try:
            objs.corpus = Corpus('jb-parsed')
        except:
            pass

    def get_prompt(backslashed=False):
        folder = os.path.basename(os.getcwd())
        proj_dirs = ['data', 'saved_interrogations', 'exported']
        objs._in_a_project = all(x in os.listdir('.') for x in proj_dirs)
        end = '*' if not objs._in_a_project else ''
        name = getattr(objs.corpus, 'name', 'no-corpus')
        txt = 'corpkit@%s%s:%s> ' % (folder, end, name)
        if not backslashed:
            return txt
        else:
            return '... '.rjust(len(txt))

    def nest_on_semicolon(tokens):
        """
        Take a tokenised command and make a nested list,
        which accounts for ';' breaks
        """
        if ';' not in tokens:
            return [tokens]
        nested = []
        while tokens:
            s_ix = next((i for i, x in enumerate(tokens) if x == ';'), len(tokens))
            nested.append(tokens[:s_ix])
            tokens = tokens[s_ix+1:]
        return nested

    print(allig)

    if not objs._in_a_project:
        print("\nWARNING: You aren't in a project yet. "\
              "Use 'new project named <name>' to make one and enter it.\n"\
              "Alternatively, you can `cd` into an existing project now.\n")

    def py(output):
        """
        Run text as Python code
        """
        exec(output)

    # backslashed allows line breaks with backslashes ala python.
    # it's a bit of a hack, but seems to work pretty well

    backslashed = ''

    if fromscript:
        commands = read_script(fromscript)
        objs._interactive = False
    
    # the main loop, with exception handling
    while True:
        try:
            if not fromscript:
                output = INPUTFUNC(get_prompt(backslashed))
            else:
                if not commands:
                    break
                output = commands.pop()

            # terminate
            if output.lower() in ['exit', 'quit', 'exit()', 'quit()']:
                break

            # do nothing
            if not output:
                output = True
                continue
            
            # append line to previous backslashed line
            if backslashed:
                output = backslashed + output
                backslashed = ''
            
            # add to stack if backslashed or delete stack otherwise
            if output.strip().endswith("\\"):
                backslashed += output.rstrip('\\')
                continue
            else:
                backslashed = ''

             # is this just a terrible idea?
            if output.startswith('py '):

                output = output[3:].strip().strip("'").strip('"')
            
                for k, v in objs.__dict__.items():
                    locals()[k] = v
                exec(output, globals(), locals())
                for k, v in locals().items():
                    if hasattr(objs, k):
                        setattr(objs, k, v)
                continue

            # tokenise command with quotations preserved
            tokens = shlex.split(output)

            nested_tokens = nest_on_semicolon(tokens)

            for tokens in nested_tokens:
                if debug:
                    print('command', tokens)
                
                # give info if it is an info command
                if len(tokens) == 1 or tokens[0] == 'jupyter':
                    if tokens[0] == 'set':
                        set_corpus([])
                    else:
                        single_command_print(tokens)
                    continue

                # otherwise, run the command and reset the stack
                out = run_command(tokens)
                backslashed = ''

        except KeyboardInterrupt:
            print('\nEnter ctrl+d, "exit" or "quit" to quit\n')
            backslashed = ''
        except EOFError:
            import sys
            print('\n\nBye!\n')
            sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    import sys
    import pip
    import importlib
    import traceback
    import os

    def install(name, loc):
        """if we don't have a module, download it"""
        try:
            importlib.import_module(name)
        except ImportError:
            pip.main(['install', loc])

    tabview = ('tabview', 'git+https://github.com/interrogator/tabview@93644dd1f410de4e47466ea8083bb628b9ccc471#egg=tabview')
    colorama = ('colorama', 'colorama')

    if not any(arg.lower() == 'noinstall' for arg in sys.argv):
        install(*tabview)
        install(*colorama)

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[-1]):
        fromscript = sys.argv[-1]
    else:
        fromscript = False

    debug = sys.argv[-1] == 'debug'
    interpreter(debug=debug, fromscript=fromscript)
