"""
corpkit: add annotations to conll-u via concordancing
"""

def process_special_annotation(v, lin):
    """
    If the user wants a fancy annotation, like 'add middle column',
    this gets processed here. it's potentially the place where the
    user could add entropy score, or something like that.
    """
    if v not in ['i', 'index', 'm']:
        return v
    if v == 'index':
        return lin.name
    else:
        return str(lin[v])

def make_string_to_add(annotation, lin, replace=False):
    """
    Make a string representing metadata to add
    """
    from corpkit.constants import STRINGTYPE
    if isinstance(annotation, STRINGTYPE):
        if replace:
            return annotation + '\n'
        else:
            return '# tags=' + annotation + '\n'
    
    start = str()
    for k, v in annotation.items():
        # these are special names---add more?
        v = process_special_annotation(v, lin)  
        start += '# %s=%s\n' % (k, v)
    return start

def get_line_number_for_entry(filepath, si, ti, annotation):
    """
    Find the place in filename at which to add the string
    """
    partstart = '# sent_id %d' % si
    partend = '# sent_id %d' % (si + 1)
    from corpkit.constants import OPENER
    # this way iterates over the lines
    # it could also just find the 
    
    with OPENER(filepath, 'r') as fo:
        data = fo.read()
    lnum = data.split(partstart)[0].count('\n') + 2
    sent = data.split(partstart)[1].split(partend)[0]
    ixx = next((i for i, l in enumerate(sent.splitlines()) \
               if l.startswith('# tags=')), False)
    
    if ixx is False:
        return lnum, False
    else:
        repla = not isinstance(annotation, dict)
        return lnum + ixx - 2, repla


def make_contents(filepath, place, text, do_replace=False):    
    from corpkit.constants import OPENER
    with OPENER(filepath, 'r', encoding='utf-8') as fo:
        contents = fo.readlines()
    if do_replace:
        contents[place] = contents[place].rstrip('\n') + ',' + text
    else:
        contents.insert(place, text)
    return contents

def dry_run_text(filepath, contents, place, colours):
    """
    Show a dry run of what the annotations would be
    """
    import os
    contents[place] = contents[place].rstrip('\n') + '  <==========\n'
    try:
        contents[place] = colours['green'] + contents[place] + colours['reset']
    except:
        pass

    max_lines = next((i for i, l in enumerate(contents[place:]) if l == '\n'), 10)
    max_lines = 30 if max_lines > 30 else max_lines

    formline = '   Add metadata: %s   \n' % (os.path.basename(filepath))
    bars = '=' * len(formline)

    print(bars + '\n' + formline + bars)
    print(''.join(contents[place-3:max_lines+place]))

def annotate(filepath, place, text, num_done=0,
    do_replace=False, dry_run=True, colours=False):
    """
    Add annotation to a single file
    """
    from corpkit.constants import OPENER
    contents = make_contents(filepath, place, text, do_replace=do_replace)

    if dry_run and num_done < 50:
        dry_run_text(filepath,
                     contents,
                     place,
                     colours=colours)
        return

    with OPENER(filepath, 'w') as fo:
        from corpkit.constants import PYTHON_VERSION
        contents = ''.join(contents)
        if PYTHON_VERSION == 2:
            contents = contents.encode('utf-8', errors='ignore')
        fo.write(contents)

def delete_lines(corpus, annotation, dry_run=True, colour={}):
    """
    Show or delete the necessary lines
    """
    from corpkit.constants import OPENER, PYTHON_VERSION
    import re
    import os
    tagmode = True
    no_can_do = ['sent_id', 'parse']

    if isinstance(annotation, dict):
        tagmode = False
        for k, v in annotation.items():
            if k in no_can_do:
                print("You aren't allowed to delete '%s', sorry." % k)
                return
            if not v:
                v = r'.*?'
            regex = re.compile(r'(# %s=%s)\n' % (k, v), re.MULTILINE)
    else:
        if annotation in no_can_do:
            print("You aren't allowed to delete '%s', sorry." % k)
            return
        regex = re.compile(r'((# tags=.*?)%s,?(.*?))\n' % annotation, re.MULTILINE)

    fs = []
    for (root, dirs, fls) in os.walk(corpus):
        for f in fls:
            fs.append(os.path.join(root, f))
    
    for f in fs:
    
        if PYTHON_VERSION == 2:
            from corpkit.process import saferead
            data = saferead(f)[0]
        else:
            with open(f, 'rb') as fo:
                data = fo.read().decode('utf-8', errors='ignore')

        if dry_run:
            if tagmode:
                repl_str = r'\1 <=======\n%s\2\3 <=======' % colour.get('green', '')
            else:
                repl_str = r'\1 <=======\n'
            try:
                repl_str = colour['red'] + repl_str + colour['reset']
            except:
                pass
            data, n = re.subn(regex, repl_str, data)
            nspl = 100 if tagmode else 50
            delim = '<======='
            data = re.split(delim, data, maxsplit=nspl)
            toshow = delim.join(data[:nspl+1])
            toshow = toshow.rsplit('\n\n', 1)[0]
            print(toshow)
            if n > 50:
                n = n - 50
                print('\n... and %d more changes ... ' % n)

        else:
            if tagmode:
                repl_str = r'\2\3\n'
            else:
                repl_str = ''
            data = re.sub(regex, repl_str, data)
            with OPENER(f, 'w') as fo:
                from corpkit.constants import PYTHON_VERSION
                if PYTHON_VERSION == 2:
                    data = data.encode('utf-8', errors='ignore')
                fo.write(data)
                

def annotator(df_or_corpus, annotation, dry_run=True, deletemode=False):
    """
    Run the annotator pipeline over multiple files

    :param corpus: a Corpus object containing the files
    :param annotation: a str or dict containing annotation text
    :param file_sent_words: filepath-sent-word tuples to annotate

    """
    # get (fname, sent-ix, token-ix) list
    import re
    import os
    from corpkit.constants import OPENER, STRINGTYPE, PYTHON_VERSION
    colour = {}
    try:
        from colorama import Fore, init, Style
        init(autoreset=True)
        colour = {'green': Fore.GREEN, 'reset': Style.RESET_ALL, 'red': Fore.RED}
    except ImportError:
        pass
    if deletemode:
        delete_lines(df_or_corpus.path, annotation, dry_run=dry_run, colour=colour)
        return

    file_sent_words = df_or_corpus.reset_index()[['index', 'f', 'i']].values.tolist()
    out = []
    for index, fn, ix in file_sent_words:
        s, i = ix.split(',', 1)
        out.append((index, fn, int(s), int(i)))
    file_sent_words = set(out)
    
    # for each unique entry, get line number, make annotation and add
    for i, (index, fpath, si, ti) in enumerate(sorted(file_sent_words), start=1):
        line_num, do_replace = get_line_number_for_entry(fpath, si, ti, annotation)
        anno_text = make_string_to_add(annotation, df_or_corpus.ix[index], replace=do_replace)
        annotate(fpath, line_num, anno_text, num_done=i, 
             do_replace=do_replace, dry_run=dry_run, colours=colour)
        if dry_run and i > 50:
            break
    if dry_run:
        if len(file_sent_words) > 50:
            n = i - 50
            print('... and %d more changes ... ' % n)

        