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
from corpkit.cql import remake_special
from corpkit.constants import transshow, transobjs

size = pd.util.terminal.get_terminal_size()
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 0)

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

            self.result = None
            self.previous = []
            self.edited = None
            self.concordance = None
            self.query = None
            self.features = None
            self.postags = None
            self.wordclasses = None
            self.stored = {}
            self.figure = None

    objs = Objects()

    proj_dirs = ['data', 'saved_interrogations', 'exported']
    in_a_project = all(x in os.listdir('.') for x in proj_dirs)
    if not in_a_project:
        print("You aren't in a project yet. Use new project named <name> to make one and enter it.")

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

    def show_help(command):

        if command == 'history':
            for i in range(readline.get_current_history_length()):
                print(readline.get_history_item(i + 1))

        if command == 'help':
            import pydoc
            pydoc.pager(\
            "\nThis is a dedicated interpreter for corpkit, a tool for creating, searching\n" \
            "and visualising corpora. It works through a combination of objects and commands:\n\n" \
            "Objects:\n\n\t" \
            " +---------------+-----------------------------------------------+ \n\t"\
            " | Object        | Contains                                      | \n\t"\
            " +===============+===============================================+ \n\t"\
            " | `corpus`      | Dataset selected for parsing or searching     | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `results`     | Search output                                 | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `edited`      | Results after sorting, editing or calculating | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `concordance` | Concordance lines from search                 | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `features`    | General linguistic features of corpus         | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `wordclasses` | Distribution of word classes in corpus        | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `postags`     | Distribution of POS tags in corpus            | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `figure`      | Plotted data                                  | \n\t"\
            " +---------------+-----------------------------------------------+ \n\t"\
            " | `query`       | Values used to perform search or edit         | \n\t"\
            " +---------------+-----------------------------------------------+ "
            "\n\nCommand examples:\n\n\t" \
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | Command         | Syntax                                                                             | \n\t"\
            " +=================+====================================================================================+ \n\t"\
            " | `new`           | `new project <name>`                                                               | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `set`           | `set <corpusname>`                                                                 | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `parse`         | `parse corpus with [options]*`                                                     | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `search`        | `search corpus for [feature matching pattern]* showing [feature]* with [options]*` | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `edit`          | `edit result by [skipping subcorpora/entries matching pattern]* with [options]*`   | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `calculate`     | `calculate result/edited as operation of denominator`                              | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `sort`          | `sort result/concordance by value`                                                 | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `plot`          | `plot result/edited as line chart with [options]*`                                 | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `show`          | `show object`                                                                      | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `export`        | `export result to string/csv/latex/file <filename>`                                | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `save`          | `save object to <filename>`                                                        | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `load`          | `load object as result`                                                            | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `store`         | `store object as <name>`                                                           | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `fetch`         | `fetch <name> as object`                                                           | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `help`          | `help command/object`                                                              | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `history`       | `history`                                                                          | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `ipython`       | `ipython`                                                                          | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            " | `py`            | `py print('hello world')`                                                          | \n\t"\
            " +-----------------+------------------------------------------------------------------------------------+ \n\t"\
            "\n\nYou can access more specific help by doing 'help <command>', or by visiting\n" \
            "http://corpkit.readthedocs.io/en/latest/rst_docs/corpkit.interpreter.html.\n\n(Hit 'q' to exit help).\n\n") 

        if command == 'corpus':
            print(getattr(corpus, 'name', 'Corpus not set. use "set <corpusname>".'))
        if command == 'python' or command == 'ipython':
            from IPython import embed

            from IPython.terminal.embed import InteractiveShellEmbed

            # the theory is that somewhere we could get the locals from the embedded session
            # atexit_operations could be the answer

            s = generate_outprint()
            ret = InteractiveShellEmbed(header=s, debug=debug,
                                        exit_msg='Switching back to corpkit environment ...')
            cc = ret()
            #we_need = 'corpus', 'result', 'concordance', 'edited', 'previous'
            #dct = {k: v for k, v in ret.user_ns['__builtins__'].globals().items() if k in we_need}
            #corpus = dct.get('corpus', corpus)
            #concordance = dct.get('concordance', concordance)
            #edited = dct.get('edited', edited)
            #result = dct.get('result', result)
            #previous = dct.get('previous', previous)

        elif command in ['result', 'edited', 'concordance']:

            # this horrible code accounts for cases where we modify with exec
            toshow = getattr(getattr(objs, command), 'results', False)
            if isinstance(toshow, (pd.DataFrame, pd.Series)):
                print(toshow)
            elif toshow:
                print(toshow)
            else:
                if isinstance(getattr(objs, command, False), pd.DataFrame):
                    print(objs.result)
                else:
                    print('Nothing here yet.')
        elif command == 'features':
            print(objs.features)
        elif command == 'wordclasses':
            print(objs.wordclasses)
        elif command == 'postags':
            print(objs.postags)
        elif command == 'previous':
            for index, entry in enumerate(list(reversed(objs.previous)), start=1):
                print('%d\nCommand: %s\nOutput:\n%s' % (index, entry[0], str(entry[1])))
        else:
            pass

    def set_corpus(tokens):
        """
        Set the active corpus:

        :Example:

        set junglebook-parsed
        """
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
                except IOError:
                    pass

        else:
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

        remade = remake_special(val)
        
        if remade != val:
            return remade

        if val.isdigit():
            return int(val)
        elif val.lower() in trans.keys():
            return trans.get(val)
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
                if with_related[i+1] == 'as':
                    val = with_related[i+2]
                    val = parse_pattern(val)
                    withs[token.lower()] = val
                    skips.append(i+1)
                    skips.append(i+2)
                else:
                    withs[token.lower()] = True
            elif '=' in token:
                k, v = token.lower().split('=', 1)
                if v.isdigit():
                    v = int(v)
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
                  'show': show, 'cql': cqlmode, 'conc': True}
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
        elif tokens[0] == 'saved':
            ss = [i for i in os.listdir('saved_interrogations') if not i.startswith('.')]
            print ('\t' + '\n\t'.join(ss))
        elif tokens[0] == 'query':
            import json
            print(json.dump(objs.query))
        elif tokens[0] == 'figure':
            if hasattr(objs, 'figure') and objs.figure:
                objs.figure.show()
            else:
                print('Nothing here yet.')
        elif tokens[0] in ['features', 'wordclasses', 'postags']:
            print(getattr(objs.corpus, tokens[0]))

        elif hasattr(objs, tokens[0]):
            show_help(tokens[0])
            print("No information about: %s" % tokens[0])

    def get_info(tokens):
        pass

    def run_command(tokens):
        command = get_command.get(tokens[0], unrecognised)        
        out = command(tokens[1:])
        objs.previous.append((output, out))
        if command == search_corpus:
            if not objs.result:
                return
            objs.result = out
            print('\nresult:\n\n', out.results, '\n')
            objs.query = out.query
            objs.concordance = out.concordance
            # find out what is going on here
            objs.edited = False
        if command == edit_something:
            if hasattr(out, 'results'):
                print('\nedited:\n\n',  out.results, '\n')
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
                    obj.to_csv(buf, sep='\t')
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

        if thing_to_edit in [objs.result, objs.edited]:
            objs.edited = thing_to_edit.edit(sort_by=val)
        else:
            objs.concordance = thing_to_edit.sort_values(val[0], axis=1)
        return

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
        objs.edited = thing_to_edit.edit(**kwargs)

        return

    def plot_result(tokens):
        """
        Visualise an interrogation
        """
        
        import matplotlib.pyplot as plt
        kinds = ['line', 'heatmap', 'bar', 'barh', 'pie', 'area']
        kind = next((x for x in tokens if x in kinds), 'line')
        kwargs = process_kwargs(tokens)
        title = kwargs.pop('title', False)
        objs.figure = getattr(objs, tokens[0]).visualise(title=title, kind=kind, **kwargs)
        objs.figure.show()


    def calculate_result(tokens):
        """
        Get relative frequencies, combine results, etc
        """
        calcs = ['k', '%', '+', '/', '-', '*', 'percentage']
        operation = next((i for i in tokens if any(i.startswith(x) for x in calcs)), False)
        if not operation:
            print('Bad operation ...')
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
        print(the_obj, operation, denominator)
        objs.edited = the_obj.edit(operation, denominator)
        print('\nedited:\n\n', objs.edited.results, '\n')
        return

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
        
        to_fetch = objs.stored.get(tokens[0], False)
        if not to_fetch:
            print('Not in store: %s' % tokens[0])
            return

        if unbound:
            return to_fetch

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

        print('%s fetched as %s.' % (repr(to_fetch), tokens[2]))

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

    def new_project(tokens):
        """
        Start a new project with a name of your choice, then move into it
        """

        from corpkit.other import new_project
        new_project(tokens[-1])
        os.chdir(tokens[-1])

    def store_this(tokens):
        """
        Send a result into storage
        """

        to_store = getattr(objs, tokens[0])

        if not to_store:
            print('Not storable:' % tokens[0])
            return

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

    def run_previous(tokens):
        import shlex
        output = list(reversed(objs.previous))[int(tokens[0]) - 1][0]
        tokens = [i.rstrip(',') for i in shlex.split(output)]
        return run_command(tokens)

    get_command = {'set': set_corpus,
                   'show': show_this,
                   'search': search_corpus,
                   'info': get_info,
                   'parse': parse_corpus,
                   'export': export_result,
                   'redo': run_previous,
                   'sort': sort_something,
                   'edit': edit_something,
                   'plot': plot_result,
                   'help': helper,
                   'store': store_this,
                   'new': new_project,
                   'fetch': fetch_this,
                   'save': save_this,
                   'load': load_this,
                   'calculate': calculate_result}

    def unrecognised(*args, **kwargs):
        print('unrecognised!')

    import shlex

    print(allig)

    if debug:
        try:
            objs.corpus = Corpus('jb-parsed')
        except:
            objs.corpus = None
    else:
        objs.corpus = None

    def py(output):
        """
        Run text as Python code
        """
        exec(output)

    def get_prompt():
        folder = os.path.basename(os.getcwd())
        name = getattr(objs.corpus, 'name', 'no-corpus')
        return 'corpkit@%s:%s> ' % (folder, name)

    while True:
        try:
            output = INPUTFUNC(get_prompt())
            
            if output.lower() in ['exit', 'quit', 'exit()', 'quit()']:
                print('\n\tBye!\n')
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
                show_help(tokens[0])
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
        except Exception, err:
            traceback.print_exc()

if __name__ == '__main__':
    import sys
    debug = sys.argv[-1] == 'debug'
    interpreter(debug=debug)
