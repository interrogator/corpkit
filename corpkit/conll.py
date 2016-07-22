"""Process CONLL formatted data"""

def parse_conll(f):
    """take a file and return pandas dataframe with multiindex"""
    import pandas as pd
    head = ['s', 'i', 'w', 'l', 'p', 'n', 'g', 'f']
    with open(f, 'r') as fo:
        data = fo.read().strip('\n')
    splitdata = ['\n%s' % x for x in data.split('\n\n')]
    for i, d in enumerate(splitdata):
        d = d.replace('\n', '\n%s\t' % str(i))
        splitdata[i] = d
    data = '\n'.join(splitdata)
    data = data.replace('\n\n', '\n') + '\n'
    import StringIO
    #data = '\n'.join(['%s\t%s' % (i, x) for i, x in enumerate(data.splitlines())])
    return pd.read_csv(StringIO.StringIO(data), sep='\t', header=None, names=head, index_col=['s', 'i'])

def get_dependents_of_id(df, sent_id, tok_id, repeat=False):
    """get governors of a token"""
    justgov = df.loc[df['g'] == tok_id].xs(sent_id, level='s', drop_level=False)
    #print(df.ix[sent_id, tok_id]['w'])
    #for i, x in list(justgov.index):
    #    print(df.ix[sent_id, tok_id]['w'], df.ix[i, x]['w'])
    if repeat is not False:
        return [justgov.index[repeat - 1]]
    else:
        return list(justgov.index)

def get_governors_of_id(df, sent_id, tok_id, repeat=False):
    """get dependents of a token"""
    govid = df.ix[sent_id, tok_id]['g']
    return [(sent_id, govid)]

    #sent = df.xs(sent_id, level='s', drop_level=False)
    #res = list(i for i, tk in sent.iterrows() if tk['g'] == tok_id)
    #if repeat is not False:
    #    return [res[repeat-1]]
    #else:
    #    return res

def get_match(df, sent_id, tok_id, repeat=False):
    """dummy function"""
    return [(sent_id, tok_id)]

def get_conc_start_end(df, only_format_match, show, idx, new_idx):
    """return the left and right context of a concordance line"""
    # todo: these aren't always aligning for some reason!
    sent_id, tok_id = idx
    new_sent, new_tok = new_idx
    sent = df.xs(sent_id, level='s', drop_level=False)
    if only_format_match:
        start = ' '.join(t['w'] for i, t in sent.iterrows() if i[1] < tok_id)
        end = ' '.join(t['w'] for i, t in sent.iterrows() if i[1] > new_tok)
        return start, end
    else:
        start = []
        end = []
        for t in list(df.ix[sent_id].index):
            out = show_this(df, [(sent_id, t)], show, conc=False)
            if not out:
                continue
            else:
                out = out[0]
            if t[1] < tok_id:
                start.append(str(out[0]))
            elif t[1] > new_tok:
                end.append(str(out[0]))
        return ' '.join(start), ' '.join(end)

def search_this(df, obj, attrib, pattern, adjacent=False):
    """search the dataframe for a single criterion"""
    
    import re
    # this stores indexes (sent, token) of matches
    matches = []

    # iterate over all tokens
    for idx, token in df.iterrows():
        sent_id, tok_id = idx

        # if in adjacent mode, be recursive?
        if adjacent:
            import operator
            mapping = {'+': operator.add, '-': operator.sub}
            old_idx, old_token, old_tok_id = idx, token, tok_id
            op, spaces = adjacent[0], int(adjacent[1])
            op = mapping.get(op)
            idx = (sent_id, op(tok_id, spaces))
            try:
                token = df.ix[idx]
            except IndexError:
                continue
        if not hasattr(token, attrib):
            continue
        if not re.search(pattern, token[attrib]):
            continue

        if adjacent:
            idx = old_idx
            tok_id = old_tok_id
        
        if obj == 'm':
            matches.append(idx)
        elif obj == 'd':
            govs = get_governors_of_id(df, sent_id, tok_id)
            for idx in govs:
                matches.append(idx)
        elif obj == 'g':
            deps = get_dependents_of_id(df, sent_id, tok_id)
            if not deps:
                matches.append(None)
            for idx in deps:
                matches.append(idx)

    return matches

def show_this(df, matches, show, conc=False, **kwargs):
    """show everything"""
    objmapping = {'d': get_dependents_of_id,
                  'g': get_governors_of_id,
                  'm': get_match}

    easy_attrs = ['w', 'l', 'p', 'f']
    strings = []
    concs = []
    # for each index tuple

    only_format_match = kwargs.get('only_format_match', True)

    for idx in matches:
        # we have to iterate over if we have dependent showing
        repeats = len(get_dependents_of_id(df, *idx)) if any(x.startswith('d') for x in show) else 1
        for repeat in range(1, repeats + 1):
            single_token_bits = []
            for val in show:
                
                if val[0] in ['+', '-']:
                    adj = (val[0], int(val[1:-2]))
                    val = val[-2:]
                else:
                    adj = False
                
                obj, attr = val[0], val[-1]
                obj_getter = objmapping.get(obj)
                
                if adj:
                    import operator
                    mapping = {'+': operator.add, '-': operator.sub}
                    op = mapping.get(adj[0])
                    new_idx = (idx[0], op(idx[1], adj[1]))
                else:
                    new_idx = idx
                # get idxs to show
                matched_idx = obj_getter(df, new_idx[0], new_idx[1], repeat=repeat)
                
                # should it really return a list if we never use all bits?
                if not matched_idx:
                    single_token_bits.append('none')
                else:
                    matched_idx = matched_idx[0]
                    piece = False
                    if attr == 's':
                        piece = str(matched_idx[0])
                    elif attr == 'i':
                        piece = str(matched_idx[1])
                    
                    if matched_idx[1] == 0:
                        if attr in easy_attrs:
                            piece = 'root'
                    else:
                        if not piece:
                            wcmode = False
                            if attr == 'x':
                                wcmode = True
                                attr = 'p'
                            try:
                                piece = df.ix[matched_idx]
                                if not hasattr(piece, attr):
                                    continue
                                piece = piece[attr].replace('/', '-slash-')
                            except IndexError:
                                continue
                            if wcmode:
                                from corpkit.dictionaries.word_transforms import taglemma
                                piece = taglemma.get(piece.lower(), piece.lower())
                    single_token_bits.append(piece)

            out = '/'.join(single_token_bits)
            strings.append(out)
            if conc and matched_idx:
                start, end = get_conc_start_end(df, only_format_match, show, idx, new_idx)
                fname = kwargs.get('filename', '')
                sname = kwargs.get('sname', '')
                concs.append([fname, sname, start, out, end])

    return strings, concs

def fix_show_bit(show_bit):
    """take a single search/show_bit type, return match"""
    #show_bit = [i.lstrip('n').lstrip('b') for i in show_bit]
    ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 'r', 's']
    starts = ['d', 'g', 'm', 'n', 'b', 'h', '+', '-']
    show_bit = show_bit.lstrip('n')
    show_bit = show_bit.lstrip('b')
    show_bit = list(show_bit)
    if show_bit[-1] not in ends:
        show_bit.append('w')
    if show_bit[0] not in starts:
        show_bit.insert(0, 'm')
    return ''.join(show_bit)


def remove_by_mode(matches, mode, criteria):
    out = []
    if mode == 'all':
        from collections import Counter
        counted = Counter(matches)
        for w in matches:
            if counted[w] == len(criteria):
                if w not in out:
                    out.append(w)
    elif mode == 'any':
        for w in matches:
            if w not in out:
                out.append(w)        
    return out

def pipeline(f,
             search,
             show,
             exclude=False,
             searchmode='all',
             excludemode='any',
             conc=False,
             **kwargs):
    """a basic pipeline for conll"""

    all_matches = []
    all_exclude = []

    if isinstance(show, str):
        show = [show]
    show = [fix_show_bit(i) for i in show]

    df = parse_conll(f)

    if kwargs.get('no_punct', False):
        df = df[df['w'].str.contains(kwargs.get('is_a_word', r'[A-Za-z0-9]'))]
        # find way to reset the 'i' index ...

    if kwargs.get('no_closed'):
        from corpkit.dictionaries import wordlists
        crit = wordlists.closedclass.as_regex(boundaries='l')
        df = df[~df['w'].str.lower.contains(crit)]

    for k, v in search.items():
        
        if k[0] in ['+', '-']:
            adj = (k[0], k[1:-2])
            k = k[-2:]
        else:
            adj = False
        res = search_this(df, k[0], k[-1], v, adjacent=adj)
        for r in res:
            all_matches.append(r)

    all_matches = remove_by_mode(all_matches, searchmode, search)
    
    if exclude:
        for k, v in exclude.items():
            if k[0] in ['+', '-']:
                adj = (k[0], k[1:-2])
                k = k[-2:]
            else:
                adj = False
            res = search_this(df, k[0], k[-1], v, adjacent=adj)
            for r in res:
                all_exclude.append(r)

        all_exclude = remove_by_mode(all_exclude, excludemode, exclude)
        
        # do removals
        for i in all_exclude:
            try:
                all_matches.remove(i)
            except ValueError:
                pass

    return show_this(df, all_matches, show, conc, **kwargs)