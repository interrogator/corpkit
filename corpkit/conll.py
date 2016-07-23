"""Process CONLL formatted data"""

def parse_conll(f, first_time=False):
    """take a file and return pandas dataframe with multiindex"""
    import pandas as pd
    head = ['s', 'i', 'w', 'l', 'p', 'n', 'g', 'f', 'd', 'c', 'x', 'y', 'z']
    with open(f, 'r') as fo:
        data = fo.read().strip('\n')
    splitdata = []
    metadata = {}
    count = 1
    for sent in data.split('\n\n'):
        metadata[count] = {}
        for line in sent.split('\n'):
            if line and not line.startswith('#'):
                splitdata.append('\n%s' % line)
            else:
                line = line.lstrip('# ')
                if '=' in line:
                    field, val = line.split('=', 1)
                    metadata[count][field] = val
        count += 1
    # determine proper head
    l = len(splitdata[0].strip('\t').split('\t'))
    head = head[:l]
    if first_time:
        for i, d in enumerate(splitdata, start=1):
            d = d.replace('\n', '\n%s\t' % str(i))
            splitdata[i-1] = d
    data = '\n'.join(splitdata)
    data = data.replace('\n\n', '\n') + '\n'
    import StringIO
    #data = '\n'.join(['%s\t%s' % (i, x) for i, x in enumerate(data.splitlines())])
    df = pd.read_csv(StringIO.StringIO(data), sep='\t', header=None, names=head, index_col=['s', 'i'])
    return df, metadata

def get_dependents_of_id(df, sent_id, tok_id, repeat=False):
    """get governors of a token"""
    try:
        deps = df.ix[(sent_id, tok_id)]['d'].split(',')
        return [(sent_id, d) for d in deps]
    except:
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

def get_all_corefs(df, idx, token):
    if not hasattr(token, 'c'):
        return [(idx, token)]
    elif token['c'] == '_':
        return [(idx, token)]
    else:
        just_same_coref = df.loc[df['c'] == token['c']]
        for i, t in just_same_coref.iterrows():
            print(token['w'], t['w'])
        return [(i, t) for i, t in just_same_coref.iterrows()]
    return corefs

def search_this(df, obj, attrib, pattern, adjacent=False, coref=False):
    """search the dataframe for a single criterion"""
    
    import re
    # this stores indexes (sent, token) of matches
    matches = []

    # iterate over all tokens
    for idx, token in df.iterrows():
        sent_id, tok_id = idx

        # if in adjacent mode, change the token being processed
        # before changing it back later
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

        if coref:
            to_iter = get_all_corefs(df, idx, token)
        else:
            to_iter = [(idx, token)]

        for idx, token in to_iter:
            if not re.search(pattern, token[attrib]):
                continue
            print(idx, token[attrib])

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

def show_this(df, matches, show, metadata, conc=False, **kwargs):
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
                sname = metadata[idx[0]].get('speaker', 'none')
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
    """if mode is all, remove any entry that occurs < len(criteria)"""
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
             coref=False,
             **kwargs):
    """a basic pipeline for conll querying---some options still to do"""

    all_matches = []
    all_exclude = []

    if isinstance(show, str):
        show = [show]
    show = [fix_show_bit(i) for i in show]

    df, metadata = parse_conll(f)

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
        res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
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
            res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
            for r in res:
                all_exclude.append(r)

        all_exclude = remove_by_mode(all_exclude, excludemode, exclude)
        
        # do removals
        for i in all_exclude:
            try:
                all_matches.remove(i)
            except ValueError:
                pass

    return show_this(df, all_matches, show, metadata, conc, **kwargs)


def load_raw_data(f):
    """loads the stripped and raw versions of a parsed file"""

    # open the unparsed version of the file, read into memory
    stripped_txtfile = f.replace('.conll', '').replace('-parsed', '-stripped')
    with open(stripped_txtfile, 'r') as old_txt:
        stripped_txtdata = old_txt.read()

    # open the unparsed version with speaker ids
    id_txtfile = f.replace('.conll', '').replace('-parsed', '')
    with open(id_txtfile, 'r') as idttxt:
        id_txtdata = idttxt.read()

    return stripped_txtdata, id_txtdata

def get_speaker_from_offsets(stripped, plain, sent_offsets):
    if not stripped and not plain:
        return 'none'
    start, end = sent_offsets
    sent = stripped[start:end]
    # find out line number
    # sever at start of match
    cut_old_text = stripped[:start]
    line_index = cut_old_text.count('\n')
    # lookup this text
    with_id = plain.splitlines()[line_index]
    split_line = with_id.split(': ', 1)
    if len(split_line) > 1:
        speakerid = split_line[0]
    else:
        speakerid = 'UNIDENTIFIED'
    return speakerid


def convert_json_to_conll(path, speaker_segmentation=False, coref=False):
    """
    take json corenlp output and convert to conll, with
    dependents, speaker ids and so on added.
    """

    import json
    import re
    from corpkit.build import get_filepaths

    files = get_filepaths(path, ext='conll')
    
    for f in files:

        if speaker_segmentation:
            stripped, raw = load_raw_data(f)
        else:
            stripped, raw = None, None

        main_out = ''
        with open(f, 'r') as fo:
            data = json.load(fo)

        ref = 1
        for idx, sent in enumerate(data['sentences'], start=1):
            tree = sent['parse'].replace('\n', '')
            tree = re.sub(r'\s+', ' ', tree)

            # offsets for speaker_id
            sent_offsets = (sent['tokens'][0]['characterOffsetBegin'], \
                            sent['tokens'][-1]['characterOffsetEnd'])
            speaker = get_speaker_from_offsets(stripped, raw, sent_offsets)
            output = '# sent_id %d\n# parse=%s\n# speaker=%s\n' % (idx, tree, speaker)
            
            for token in sent['tokens']:
                index = str(token['index'])
                governor, func = next((str(i['governor']), str(i['dep'])) \
                                         for i in sent['basic-dependencies'] \
                                         if i['dependent'] == int(index))
                depends = [str(i['dependent']) for i in sent['basic-dependencies'] if i['governor'] == int(index)]
                if not depends:
                    depends = '0'
                #offsets = '%d,%d' % (token['characterOffsetBegin'], token['characterOffsetEnd'])
                line = [str(idx),
                        index,
                        token['word'],
                        token['lemma'],
                        token['pos'],
                        token['ner'],
                        governor,
                        func,
                        ','.join(depends)]
                #if coref:
                #    refmatch = get_corefs(data, idx, token['index'] + 1, ref)
                #    if refmatch != '_':
                #        ref += 1
                #    sref = str(refmatch)
                #    line.append(sref)
                
                output += '\t'.join(line) + '\n'
            main_out += output + '\n'

        # post process corefs
        if coref:
            import re
            dct = {}
            idxreg = re.compile('^([0-9]+)\t([0-9]+)')
            splitmain = main_out.split('\n')
            for i, line in enumerate(splitmain):
                if line:
                    splitmain[i] += '\t_'
                match = re.search(idxreg, line)
                if match:
                    l, t = match.group(1), match.group(2)
                    dct[(int(l), int(t))] = i
            
            for numstring, list_of_dicts in sorted(data['corefs'].items()):
                for d in list_of_dicts:
                    snum = d['sentNum']
                    for i in range(d['startIndex'], d['endIndex']):
                        try:
                            ix = dct[(snum, i)]
                            splitmain[ix] = splitmain[ix].rstrip('\t_') + '\t%s' % numstring
                            dct.pop((snum, i))
                        except KeyError:
                            pass

            main_out = '\n'.join(splitmain)

        with open(f, 'w') as fo:
            fo.write(main_out)

