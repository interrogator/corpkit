"""
A corpkit interpreter!

todo:

* edit and visualise methods
* export

"""

import os
from corpkit import *
from corpkit.cql import remake_special
from corpkit.constants import transshow, transobjs

def interpreter(debug=False):

    allig = '\n\n   Welcome!\n'
    allig += "            .-._   _ _ _ _ _ _ _ _\n" \
         "   .-''-.__.-'00  '-' ' ' ' ' ' ' ' '-.\n" \
         "   '.___ '    .   .--_'-' '-' '-' _'-' '._\n" \
         "   V: V 'vv-'   '_   '.       .'  _..' '.'.\n"\
         "     '=.____.=_.--'   :_.__.__:_   '.   : :\n"\
         "             (((____.-'        '-.  /   : :\n"\
         "                               (((-'\ .' /\n"\
         "                             _____..'  .'\n"\
         "                            '-._____.-'"

    global result
    result = None

    global previous
    previous = []

    def show_help(command):
        if command == 'corpus':
            global corpus
            print(corpus.name)
        elif command == 'result':
            global result
            print(result.results)
        elif command == 'concordance':
            global result
            print(result.concordance)
        elif command == 'previous':
            global previous
            for index, entry in enumerate(list(reversed(previous)), start=1):
                print('%d\nCommand: %s\nOutput:\n%s' % (index, entry[0], str(entry[1])))
        else:
            print('Not done yet, sorry!')

    def set_corpus(tokens):
        path = tokens[0]
        if os.path.exists(path) or os.path.exists(os.path.join('data', path)):
            global corpus
            corpus = Corpus(path)
            return corpus
        else:
            return

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
        # now we have long-short
        srch = srch.lower()
        transobjs = {v.lower(): k.replace(' ', '-') for k, v in transobjs.items()}
        transshow = {v.lower(): k.replace(' ', '-') for k, v in transshow.items()}
        ngram = srch.startswith('n')
        colls = srch.startswith('b')
        srch = srch.lstrip('rb')

        if '-' not in srch:
            if srch in transobjs:
                string = transobjs.get(srch) + 'w'
            elif srch in transshow:
                string = 'm' + transshow.get(srch)
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


    def parse_search_args(tokens):
        kwargs = {'conc': True}
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
        for i, token in enumerate(search_related):
            if token in ['for', 'and', 'not']:
                if search_related[i+1] == 'not':
                    continue
                k = search_related[i+1]
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

        withs = {}
        skips = []
        for i, token in enumerate(with_related):
            if i in skips or token == 'and':
                continue
            if token == 'not':
                withs[with_related[i+1].lower()] = False
                skips.append(i+1)
            elif '=' not in token:
                withs[token.lower()] = True
            elif '=' in token:
                k, v = token.lower().split('=', 1)
                if v.isdigit():
                    v = int(v)
                withs[k] = v


        kwargs['search'] = search
        kwargs['exclude'] = exclude
        kwargs['show'] = show
        kwargs.update(withs)

        return kwargs

    def search_corpus(tokens):
        global corpus
        kwargs = parse_search_args(tokens)

        print(kwargs)

        result = corpus.interrogate(**kwargs)
        return result

    def show_path(tokens):
        for token in tokens:
            print(token + ':\n\t')
            print ('\t' + '\n\t'.join([i for i in os.listdir(token) if not i.startswith('.')]))
        return

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
        else:
            print('Done:', repr(out))
        return out
        
    def splitter(command):
        """better tokeniser for query, that allows tregex vals"""
        return

    def export_result(tokens):
        if tokens[0] == 'result':
            global result
            obj = result.results
        elif tokens[0] == 'concordance':
            global result
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






    def run_previous(tokens):
        global previous
        output = list(reversed(previous))[int(tokens[0]) - 1][0]
        tokens = [i.rstrip(',') for i in output.split()]
        return run_command(tokens)

    get_command = {'set': set_corpus,
                   'show': show_path,
                   'search': search_corpus,
                   'info': get_info,
                   'export': export_result,
                   'redo': run_previous}

    def unrecognised(*args, **kwargs):
        print('unrecognised!')

    output = True
    print(allig + '\n')
    while output:
        if debug:
            global corpus
            corpus = Corpus('jb-parsed')
        output = raw_input('\ncorpkit > ')
        
        if output.lower() == 'exit':
            break

        if not output:
            output = True
            continue
        
        tokens = output.split()
        print('command', tokens)
        
        if len(tokens) == 1:
            show_help(tokens[0])
            continue

        out = run_command(tokens)

        #if command == unrecognised:
        #    continue
        #if not command:
        #    continue

if __name__ == '__main__':
    interpreter(debug=True)
