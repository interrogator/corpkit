"""
A corpkit interpreter!

todo:

* save, load
* previous results

"""

import os
import traceback
import pandas as pd

import corpkit
from corpkit import *
from corpkit.cql import remake_special
from corpkit.constants import transshow, transobjs

size = pd.util.terminal.get_terminal_size()
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 0)
import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

def interpreter(debug=False):

    allig = '\n   Welcome!\n'
    allig += "               .-._   _ _ _ _ _ _ _ _\n    " \
             ".-''-.__.-'00  '-' ' ' ' ' ' ' ' '-.\n    " \
             "'.___ '    .   .--_'-' '-' '-' _'-' '._\n    " \
             "V: V 'vv-'   '_   '.       .'  _..' '.'.\n    "\
             "  '=.____.=_.--'   :_.__.__:_   '.   : :\n    "\
             "          (((____.-'        '-.  /   : :\n    "\
             "                            (((-'\ .' /\n    "\
             "                          _____..'  .'\n    "\
             "                         '-._____.-'"

    # globally accessed
    result = None
    previous = []
    edited = None
    concordance = None
    stored = {}

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

        global corpus
        global concordance
        global edited
        global previous
        global result

        if command == 'help':
            print("\nThis is a dedicated interpreter for corpkit, a tool for creating, searching\n" \
                  "and visualising corpora. It works through a combination of objects and commands:\n\n" \
                  "Objects:\n\n\tcorpus: corpus being used\n\t" \
                  "result: interrogation output\n\t" \
                  "edited: output of an edit\n\t" \
                  "concordance: the concordance attached to an interrogation\n\t" \
                  "store: where you can store objects\n\t" \
                  "\nCommand examples:\n\n\t" \
                  "set <name>                                 Set the corpus to be searched\n\t" \
                  "parse corpus with speaker_segmentation     Make a speaker segmented parsed corpus\n\t" \
                  "search corpus for words matching '.*'      Regex search over tokens\n\t" \
                  "show result                                Look at search result\n\t" \
                  "show concordance                           Look at concordance\n\t" \
                  "edit result by skipping subcorpora '.*'    Manipulate result\n\t" \
                  "sort result by increase                    Sort results\n\t" \
                  "store edited as <name>                     Save to store with custom name\n\t" \
                  "fetch <name> as result                     Get something from store\n\t" \
                  "save result as <name>                      Save to disk\n\t" \
                  "load <name> as result                      Loading from disk\n\t" \
                  "calculate result as \% of self             Relativise frequencies\n" \
                  "ipython                                    Enter IPython with objects available"
                  "\nYou can access more specific help by doing 'help <command>'.\n") 

        if command == 'corpus':
            print(getattr(corpus, 'name', 'Corpus not set. use "set <corpusname>".'))
        if command == 'python' or command == 'ipython':
            from IPython import embed
            from IPython.terminal.embed import InteractiveShellEmbed

            # the theory is that somewhere we could get the locals from the embedded session

            s = generate_outprint()
            ret = InteractiveShellEmbed(header=s, debug=debug,
                                        exit_msg='Switching back to corpkit environment ...')
            cc = ret()
            we_need = 'corpus', 'result', 'concordance', 'edited', 'previous'
            dct = {k: v for k, v in ret.user_ns['__builtins__'].globals().items() if k in we_need}
            corpus = dct.get('corpus', corpus)
            concordance = dct.get('concordance', concordance)
            edited = dct.get('edited', edited)
            result = dct.get('result', result)
            previous = dct.get('previous', previous)

        elif command == 'result':
            print(result.results)
        elif command == 'edited':
            print(edited.results)
        elif command == 'concordance':
            print(result.concordance)
        elif command == 'previous':
            for index, entry in enumerate(list(reversed(previous)), start=1):
                print('%d\nCommand: %s\nOutput:\n%s' % (index, entry[0], str(entry[1])))
        else:
            pass

    def set_corpus(tokens):
        """
        Set the active corpus:

        :Example:

        set junglebook-parsed
        """
        path = tokens[0]
        if os.path.exists(path) or os.path.exists(os.path.join('data', path)):
            global corpus
            corpus = Corpus(path)

    def search_helper():
        search = {}
        while True:
            out = raw_input('\n    match (words, lemma, pos, func ... ) > ')
            out = out.lower()
            if not out:
                continue
            if out.startswith('done'):
                break
            val = raw_input('\n    value (regex) > ')
            if not val:
                continue
            if val.startswith('done'):
                break
            search[out.lower()[0]] = value
        return search

    def process_long_key(srch):
        from corpkit.constants import transshow, transobjs
        
        transobjs = {v.lower(): k.replace(' ', '-') for k, v in transobjs.items()}
        transshow = {v.lower(): k.replace(' ', '-') for k, v in transshow.items()}
        showplurals = {k + 's': v for k, v in transshow.items()}
        objsplurals = {k + 's': v for k, v in transobjs.items()}
        transshow.update(showplurals)
        transobjs.update(objsplurals)

        ngram = srch.startswith('n')
        colls = srch.startswith('b')
        srch = srch.lstrip('rb')

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

    def process_kwargs(tokens):

        trans = {'true': True,
                 'false': False,
                 'none': None}

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
                if tokens[i+1] == 'as':
                    val = tokens[i+2]
                    if val.isdigit():
                        val = int(val)
                    val = trans.get(val, val)
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
            return search_helper()

        search_related = []
        for token in tokens:
            search_related.append(token)
            if token in [',', 'showing', 'with']:
                break
            
        if 'showing' in tokens:
            start = tokens.index('showing')
            show_related = tokens[start+1:]
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
        
        for i, token in enumerate(search_related):
            if token in ['for', 'and', 'not']:
                if search_related[i+1] == 'not':
                    continue
                k = search_related[i+1]
                if k == 'cql':
                    cqlmode = True
                    query = next((i for i in search_related[i+2:] if i not in ['matching']), False)
                    if query:
                        search = query
                        break
                k = process_long_key(k)
                v = search_related[i+3].strip("'")
                new = remake_special(v.upper())
                if new.lower() != v:
                    v = new
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

        kwargs = {'search': search, 'exclude': exclude,
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
        global corpus
        kwargs = parse_search_args(tokens)
        
        if debug:
            print(kwargs)

        result = corpus.interrogate(**kwargs)
        return result

    def show_this(tokens):

        if tokens[0] == 'corpora':
            print ('\t' + '\n\t'.join([i for i in os.listdir('data') if not i.startswith('.')]))
        elif tokens[0].startswith('store'):
            global stored
            print(stored)
        if tokens[0] == 'saved':
            ss = [i for i in os.listdir('saved_interrogations') if not i.startswith('.')]
            print ('\t' + '\n\t'.join(ss))

    def get_info(tokens):
        pass

    def run_command(tokens):

        command = get_command.get(tokens[0], unrecognised)        
        out = command(tokens[1:])
        previous.append((output, out))
        if command == search_corpus:
            global result
            result = out
            print(out.results)
        if command == edit_something:
            if hasattr(out, 'results'):
                print(out.results)
        else:
            if debug:
                print('Done:', repr(out))
        return out
        
    def splitter(command):
        """better tokeniser for query, that allows tregex vals"""
        return

    def export_result(tokens):
        global result
        if tokens[0] == 'result':
            obj = result.results
        elif tokens[0] == 'concordance':
            obj = result.concordance
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

        global result
        global concordance
        global edited

        thing_to_edit = result
        if token == 'concordance':
            thing_to_edit = concordance
        elif token == 'edited':
            thing_to_edit = edited
        return thing_to_edit

    def sort_something(tokens):
        """sort a result or concordance line"""
        global result
        global concordance
        global edited

        thing_to_edit = get_thing_to_edit(tokens[0])

        recog = ['by', 'with', 'from']

        val = next((x for x in tokens[1:] if x not in recog), 'total')

        if thing_to_edit in [result, edited]:
            edited = thing_to_edit.edit(sort_by=val)
        else:
            concordance = thing_to_edit.sort_values(val[0], axis=1)
        return

    def edit_something(tokens):

        global result
        global concordance
        global edited



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
                new = remake_special(v.upper())
                if new.lower() != v:
                    v = new
                kwargs[k] = v
                #for x in range(i, ind+1):
                #    skips.append(x)
        if debug:
            print(kwargs)
        global edited
        edited = thing_to_edit.edit(**kwargs)

        return

    def plot_result(tokens):

        kwargs = process_kwargs(tokens)

        return


    def calculate_result(tokens):
        global result
        calcs = ['k', '%', '+', '/', '-', '*']
        operation = next((i for i in tokens if any(i.startswith(x) for x in calcs)), False)
        if not operation:
            print('bad operation')
            return
        denominator = tokens[-1]
        result = result.edit(operation, denominator)
        print(result.results)
        return

    def parse_corpus(tokens):
        if tokens[0] != 'corpus':
            print('Command not understood. Use "set <corpusname>" and "parse corpus"')
        
        global corpus

        if corpus.datatype != 'plaintext':
            print('Corpus is not plain text.')
            return
        kwargs = process_kwargs(tokens)
        parsed = corpus.parse(**kwargs)
        if parsed:
            corpus = parsed
        return

    def fetch_this(tokens):
        global result
        global concordance
        global edited
        global corpus
        global stored

        from corpkit.corpus import Corpus
        from corpkit.interrogation import Interrogation, Concordance
        
        to_fetch = stored.get(tokens[0], False)
        if not to_fetch:
            print('Not in store')
            return

        if tokens[2] == 'corpus':
            corpus = to_fetch
        elif tokens[2].startswith('conc'):
            concordance = to_fetch
        elif tokens[2] == 'result':
            result = to_fetch
        elif tokens[2] == 'edited':
            edited = to_fetch

        print('%s made into %s.' % (str(to_fetch), tokens[2]))

    def save_this(tokens):
        global result
        global concordance
        global edited

        mapping = {'result': result,
                   'concordance': concordance,
                   'edited': edited}

        to_save = mapping.get(tokens[0])
        to_save.save(tokens[2])

    def load_this(tokens):
        global result
        global concordance
        global edited
        global stored
        from corpkit.other import load
        if tokens[2] == 'result':
            result = load(tokens[0])
        if tokens[2] == 'concordance':
            concordance = load(tokens[0])
        if tokens[2] == 'edited':
            edited = load(tokens[0])
        pass

    def new_project(tokens):
        from corpkit.other import new_project
        new_project(tokens[-1])
        os.chdir(tokens[-1])

    def store_this(tokens):
        global result
        global concordance
        global edited
        global stored

        mapping = {'result': result,
                   'concordance': concordance,
                   'edited': edited}

        to_store = mapping.get(tokens[0])

        if not to_store:
            print('Not storable')
            return

        if tokens[1] == 'as':
            name = tokens[2]
        else:
            count = 0
            while str(count) in stored.keys():
                count += 1
            name = str(count)

        stored[name] = to_store

    def run_previous(tokens):
        import shlex
        global previous
        output = list(reversed(previous))[int(tokens[0]) - 1][0]
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

    global corpus
    if debug:
        try:
            corpus = Corpus('jb-parsed')
        except:
            corpus = None
    else:
        corpus = None

    while True:
        try:
            output = raw_input('\ncorpkit > ')
            
            if output.lower() in ['exit', 'quit']:
                print('\n\nBye!\n')
                break

            if not output:
                output = True
                continue
            
            tokens = shlex.split(output)
            if debug:
                print('command', tokens)
            
            if len(tokens) == 1:
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

        #if command == unrecognised:
        #    continue
        #if not command:
        #    continue

if __name__ == '__main__':
    import sys
    debug = sys.argv[-1] == 'debug'
    interpreter(debug=debug)
