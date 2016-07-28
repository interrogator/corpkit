"""
A corpkit interpreter, with natural language commands.

todo:

* documentation
* handling of kwargs tuples etc
* checking for bugs

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

size = pd.util.terminal.get_terminal_size()
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 0)
pd.set_option('display.float_format', lambda x: '${:,.3f}'.format(x))

readline.parse_and_bind('set editing-mode vi')


# this code makes it possible to remember history from previous sessions
history_path = os.path.expanduser("~/.pyhistory")

def save_history(history_path=history_path):
    import readline
    readline.remove_history_item(readline.get_current_history_length() - 1)
    readline.write_history_file(history_path)

if os.path.exists(history_path):
    readline.read_history_file(history_path)
    readline.set_history_length(1000)

atexit.register(save_history)

readline.parse_and_bind('tab: complete')

del os, atexit, readline, rlcompleter, save_history, history_path



def interpreter(debug=False):
    import os

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

    # globally accessed

    class Objects(object):

        def __init__(self):

            from corpkit.dictionaries import wordlists, processes, roles
            from collections import defaultdict
            wl = {k: v for k, v in wordlists.__dict__.items()}
            wl.update(roles.__dict__)
            wl.update(processes.__dict__)
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
            self._in_a_project = None
            self.totals = None
            self._previous_type = None
            self._do_conc = True
            self._interactive = True
            self.wordlists = wl
            self.wordlist = None
            self._decimal = 3
            self._old_concs = []
            self._conc_colours = defaultdict(dict)
            self._conc_kwargs = {'n': 999}

    objs = Objects()

    proj_dirs = ['data', 'saved_interrogations', 'exported']
    objs._in_a_project = all(x in os.listdir('.') for x in proj_dirs)

    def generate_outprint():
        s = 'Switched to IPython ... defined variables:\n\n\t'
        s += 'corpus, results, concordance, edited ...\n\n\tType "quit" to return to corpkit environment'
        return s

    def helper(tokens):
        func = get_command.get(tokens[0], False)

        if not func:
            print('Not recognised: %s' % tokens[0])
            return

        print(getattr(func, '__doc__', 'Not written yet, sorry.'))

    def single_command_print(command):

        if command == 'ls':
            import os
            print('\n'.join(os.listdir()))

        args = []
        if isinstance(command, list):
            args = command[1:]
            command = command[0]

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
            "http://corpkit.readthedocs.io/en/latest/rst_docs/corpkit.interpreter.html.\n\n" \
            "For help on viewing results, hit '?' when in the result viewing mode. For concordances, hit 'h'.\n\n(Hit 'q' to exit help).\n\n", cmd='less -X -R -S') 

        if command == 'corpus':
            if not hasattr(objs.corpus, 'name'):
                print('Corpus not set. use "set <corpusname>".')
                return
        elif command == 'python' or command == 'ipython':
            from IPython import embed
            from IPython.terminal.embed import InteractiveShellEmbed

            # the theory is that somewhere we could get the locals from the embedded session
            # atexit_operations could be the answer

            s = generate_outprint()

            for k, v in objs.__dict__.items():
                if not k.startswith('_'):
                    locals()[k] = v

            ret = InteractiveShellEmbed(header=s,
                        dum='dum',
                        #colors='Linux',
                        exit_msg='Switching back to corpkit environment ...',
                        local_ns=locals())
            cc = ret()

        elif command in ['result', 'edited', 'totals', 'previous']:
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

        elif command == 'concordance':
            import pydoc
            
            kwargs = process_kwargs(args)
            if kwargs:
                objs._conc_kwargs = kwargs
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
                            lines_to_print.append(getattr(thing_to_color, gotnum.upper()) + line)
                        else:
                            lines_to_print.append(line)
                    pydoc.pipepager('\n'.join(lines_to_print), cmd="less -X -R")
                except ImportError:
                    pydoc.pipepager(getattr(objs, command).format(print_it=False, **objs._conc_kwargs), cmd="less -X -R")

            else:
                pydoc.pipepager(getattr(objs, command).format(print_it=False, **objs._conc_kwargs), cmd="less -X -R")
            

        elif command == 'wordlists':
            show_this([command])
        elif command == 'wordlist':
            print(objs.wordlist)

        elif command == 'features':
            print(objs.features)
        elif command == 'wordclasses':
            print(objs.wordclasses)
        elif command == 'postags':
            print(objs.postags)
        elif command == 'query':
            show_this([command])
        else:
            pass

    def set_corpus(tokens):
        """
        Set the active corpus:

        :Example:

        set junglebook-parsed
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
                    setattr(objs, i, load(objs.corpus.name + '-%s' % i))
                except (UnicodeDecodeError, IOError):
                    pass

        else:
            try:
                dirs = [x for x in os.listdir('data') if os.path.isdir(os.path.join('data', x))]
                set_corpus([dirs[int(tokens[-1])-1]])
            except:
                print('Corpus not found: %s' % tokens[0])
                return

    def search_helper(text='search'):
        if text == 'search':
            search_or_show = {}
        else:
            search_or_show = []
        while True:
            out = INPUTFUNC('\n    %s (words, lemma, pos, func ... ) > ' % text)
            out = out.lower()
            if not out:
                continue
            if out.startswith('done'):
                break
            if out == 'cql':
                cql = INPUTFUNC('\n        CQL query > ')
                return cql.strip()
            if text == 'show':
                search_or_show.append(out)
                continue
            val = INPUTFUNC('\n        value (regex) > ')
            if not val:
                continue
            if val.startswith('done'):
                break
            search_or_show[out.lower()[0]] = val
        return search_or_show

    def process_long_key(srch):
        from corpkit.constants import transshow, transobjs
        
        transobjs = {v.lower(): k.replace(' ', '-') for k, v in transobjs.items()}
        transshow = {v.lower(): k.replace(' ', '-') for k, v in transshow.items()}
        showplurals = {k + 's': v for k, v in transshow.items()}
        objsplurals = {k + 's': v for k, v in transobjs.items()}
        
        transshow['distance'] = 'r'
        transshow['ngram'] = 'n'
        transshow['distances'] = 'r'
        transshow['ngrams'] = 'n'

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
        """Parses the token after 'matching'"""
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

    def process_kwargs(tokens):

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
        tokens = tokens[1:]
        if not tokens:
            search = search_helper(text='search')
            show = search_helper(text='show')
            kwargs = {'search': search, 'show': show,
                      'cql': isinstance(search, str), 'conc': True}
            return kwargs

        search_related = []
        for token in tokens:
            search_related.append(token)
            if token in [',', 'showing', 'with']:
                break
            
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

        search = {}
        exclude = {}

        cqlmode = False
        featuresmode = False
        
        for i, token in enumerate(search_related):
            if token in ['for', 'and', 'not']:
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
                  'show': show, 'cql': cqlmode, 'conc': objs._do_conc}
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
        
        if debug:
            print(kwargs)

        objs.result = objs.corpus.interrogate(**kwargs)
        objs.totals = objs.result.totals
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
            print(objs.query)
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
        if command in [edit_something, sort_something, calculate_result]:
            from corpkit.interrogation import Concordance
            if isinstance(out, Concordance):
                objs._old_concs[-1] = objs.concordance
                if objs._interactive:
                    show_this(['concordance'])
            else:
                if objs._interactive:
                    show_this(['edited'])
                    
        else:
            if debug:
                print('Done:', repr(out))
        return out
        
    def export_result(tokens):
        if tokens[0] == 'result':
            obj = objs.result.results
        elif tokens[0] == 'concordance':
            obj = objs.result.concordance
        if len(tokens) == 1:
            print(obj.to_string())
            return
        tokens = tokens[1:]

        for i, token in enumerate(tokens):
            if token == 'to':
                buf = None
                if tokens[i+1].startswith('f'):
                    buf = tokens[i+2]
                    if os.pathsep not in buf:
                        buf = os.path.join('exported', buf)
                    obj.to_csv(buf, sep='\t')
                    print('Saved to: %s' % buf)
                    return
                elif tokens[i+1].startswith('s'):
                    print(obj.to_string(buf))
                    return
                elif tokens[i+1].startswith('c'):
                    print(obj.to_csv(buf, sep='\t'))
                    return
                elif tokens[i+1].startswith('l'):
                    print(obj.to_latex(buf))
                    return


    def interactive_edit(tokens):
        print('not done yet')
        pass

    def get_thing_to_edit(token):

        thing_to_edit = objs.result
        if token == 'concordance':
            thing_to_edit = objs.concordance
        elif token == 'edited':
            thing_to_edit = objs.edited
        return thing_to_edit

    def sort_something(tokens):
        """sort a result or concordance line"""

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
                if val.startswith('l') or val.startswith('r'):
                    l_or_r = objs.concordance[val[0]]
                    ind = int(val[1:])
                    if val[0] == 'l':
                        ind = -ind
                    else:
                        ind = ind-1
                    import numpy as np
                    # this could be upgraded to use rjust ...
                    to_sort_on = l_or_r.str.split().tolist()
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
        Visualise an interrogation
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

    def calculate_result(tokens):
        """
        Get relative frequencies, combine results, etc
        """

        calcs = ['k', '%', '+', '/', '-', '*', 'percentage']
        operation = next((i for i in tokens if any(i.startswith(x) for x in calcs)), False)
        if not operation:
            if tokens[-1].startswith('conc'):
                res = objs.concordance.calculate()
                objs.result = res.results
                objs.totals = res.totals
                if objs._interactive:
                    show_this('result')
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
        """
        if passedin:
            to_save = passedin
        else:
            to_save = getattr(objs, tokens[0])

        if to_save == 'store' and not passedin:
            for k, v in objs.stored.items():
                save_this(['as', k], passedin=v)

        if tokens[0] == 'figure' or hasattr(to_save, 'savefig'):
            tokens[2] = os.path.join('images', tokens[2])
            to_save.savefig(tokens[2])
        else:
            to_save.save(tokens[2])


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

    def annotate_conc(tokens):
        from colorama import Fore, Back, Style, init
        init(autoreset=True)
        dflines = objs.concordance.format(print_it=False, **objs._conc_kwargs).splitlines()

        cols = []
        token = tokens[0]
        # annotate range of tokens
        if '-' in token:
            first, last = token.split('-', 1)
            if not first:
                first = 0
            if not last:
                last = len(dflines)
            for n in range(int(first), int(last)+1):
                cols.append(str(n))
        # annotate single token by index
        elif token.isdigit():
            cols.append(token)
        else:
            # regex match only what's shown in the window
            window = objs._conc_kwargs.get('window', 35)
            if token.lower() == 'm':
                slic = slice(None, None)
            elif token.lower() == 'l':
                slic = slice(-window, None)
            elif token.lower() == 'r':
                slic = slice(None, window)
            mx = max(objs.concordance[token.lower()].str.len()) if token.lower() == 'l' else 0
            mtch = objs.concordance[objs.concordance[token].str.rjust(mx).str[slic].str.contains(tokens[2])]
            matches = list(mtch.index)
            for ind in matches:
                cols.append(str(ind))

        color = tokens[-1]
        
        lines_to_print = []
        for line in dflines:
            num = line.strip().split(' ', 1)[0]

            if num in cols:
                if color.upper() in ['DIM', 'NORMAL', 'BRIGHT', 'RESET_ALL']:
                    thing_to_color = Style
                else:
                    thing_to_color = Fore
                lines_to_print.append(getattr(thing_to_color, color.upper()) + line)
                # store it to the dictionary
                objs._conc_colours[len(objs._old_concs)-1][num] = color
            elif num in objs._conc_colours[len(objs._old_concs)-1]:
                lines_to_print.append(getattr(Fore, objs._conc_colours[len(objs._old_concs)-1][num].upper()) + line)
            else:
                lines_to_print.append(line)
        import pydoc
        pydoc.pipepager('\n'.join(lines_to_print), cmd='less -X -R -S')

                
    def store_this(tokens):
        """
        Send a result into storage
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
        if tokens[0].startswith('conc'):
            objs._do_conc = not objs._do_conc
            s = 'on' if objs._do_conc else 'off'
            print('Concordancing turned %s.' % s)
        if tokens[0].startswith('autos'):
            objs._interactive = not objs._interactive
            s = 'on' if objs._interactive else 'off'
            print('Auto showing of results and concordances turned %s.' % s)            

    def run_previous(tokens):
        import shlex
        output = list(reversed(objs.previous))[int(tokens[0]) - 1][0]
        tokens = [i.rstrip(',') for i in shlex.split(output)]
        return run_command(tokens)

    def ch_dir(tokens):
        import os
        os.chdir(tokens[0])
        print(os.getcwd())
        get_prompt()

    def ls_dir(tokens):
        import os
        print('\n'.join(os.listdir(tokens[0])))

    get_command = {'set': set_corpus,
                   'show': show_this,
                   'search': search_corpus,
                   'info': get_info,
                   'parse': parse_corpus,
                   'export': export_result,
                   'redo': run_previous,
                   'mark': annotate_conc,
                   'sort': sort_something,
                   'toggle': toggle_this,
                   'edit': edit_something,
                   'ls': ls_dir,
                   'cd': ch_dir,
                   'plot': plot_result,
                   'help': helper,
                   'store': store_this,
                   'new': new_thing,
                   'fetch': fetch_this,
                   'save': save_this,
                   'load': load_this,
                   'calculate': calculate_result}

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

    def get_prompt():
        folder = os.path.basename(os.getcwd())
        proj_dirs = ['data', 'saved_interrogations', 'exported']
        objs._in_a_project = all(x in os.listdir('.') for x in proj_dirs)
        end = '*' if not objs._in_a_project else ''
        name = getattr(objs.corpus, 'name', 'no-corpus')
        return 'corpkit@%s%s:%s> ' % (folder, end, name)

    print(allig)

    if not objs._in_a_project:
        print("\nWARNING: You aren't in a project yet. Use 'new project named <name>' to make one and enter it.\n")


    def py(output):
        """
        Run text as Python code
        """
        exec(output)

    while True:
        try:
            output = INPUTFUNC(get_prompt())
            
            if output.lower() in ['exit', 'quit', 'exit()', 'quit()']:
                break

            if not output:
                output = True
                continue
            
            if output.startswith('py '):

                output = output[3:].strip().strip("'").strip('"')
                
                # is this just a terrible idea?
                for k, v in objs.__dict__.items():
                    locals()[k] = v
                exec(output, globals(), locals())
                for k, v in locals().items():
                    if hasattr(objs, k):
                        setattr(objs, k, v)
                continue

            tokens = shlex.split(output)
            if debug:
                print('command', tokens)
            
            if len(tokens) == 1:
                if tokens[0] == 'set':
                    set_corpus([])
                single_command_print(tokens[0])
                continue

            out = run_command(tokens)

        except KeyboardInterrupt:
            print('\nEnter ctrl+d, "exit" or "quit" to quit\n')
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
    debug = sys.argv[-1] == 'debug'
    interpreter(debug=debug)
