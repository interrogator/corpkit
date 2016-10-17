"""
corpkit: process CONLL formatted data
"""

def parse_conll(f,
                first_time=False,
                just_meta=False,
                usecols=None):
    """
    Take a file and return pandas dataframe with multiindex and metadata
    """
    import pandas as pd
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    # go to corpkit.constants to modify the order of columns if yours are different
    from corpkit.constants import CONLL_COLUMNS as head
    
    with open(f, 'r') as fo:
        data = fo.read().strip('\n')
    splitdata = []
    metadata = {}
    count = 1
    sents = data.split('\n\n')    
    for sent in sents:
        metadata[count] = {}
        for line in sent.split('\n'):
            if line and not line.startswith('#') \
                and not just_meta:
                splitdata.append('\n%s' % line)
            else:
                line = line.lstrip('# ')
                if '=' in line:
                    field, val = line.split('=', 1)
                    metadata[count][field] = val
        count += 1
    if just_meta:
        return metadata

    # happens with empty files
    if not splitdata:
        return

    # determine the number of columns we need
    l = len(splitdata[0].strip('\t').split('\t'))
    head = head[:l]
    
    # if formatting for the first time, add sent ids
    if first_time:
        for i, d in enumerate(splitdata, start=1):
            d = d.replace('\n', '\n%s\t' % str(i))
            splitdata[i-1] = d

    # turn into something pandas can read    
    data = '\n'.join(splitdata)
    data = data.replace('\n\n', '\n') + '\n'

    # remove slashes as early as possible
    data = data.replace('/', '-slash-')

    # open with sent and token as multiindex
    try:
        df = pd.read_csv(StringIO(data), sep='\t', header=None,
                         names=head, index_col=['s', 'i'], usecols=usecols)
    except ValueError:
        return
    df._metadata = metadata
    return df

def get_dependents_of_id(idx, df=False, repeat=False, attr=False, coref=False):
    """
    Get dependents of a token
    """

    sent_id, tok_id = getattr(idx, 'name', idx)
    deps = df.ix[sent_id, tok_id]['d'].split(',')
    out = []
    for govid in deps:
        if attr:
            # might not exist...
            try:
                tok = getattr(df.ix[sent_id,int(govid)], attr, False)
                if tok:
                    out.append(tok)
            except (KeyError, IndexError):
                pass
        else:
            out.append((sent_id, int(govid)))
    return out

def get_governors_of_id(idx, df=False, repeat=False, attr=False, coref=False):
    """
    Get governors of a token
    """
    
    # it can be a series or a tuple
    sent_id, tok_id = getattr(idx, 'name', idx)
    # get the governor id
    govid = df['g'].loc[sent_id, tok_id]
    if attr:
        return getattr(df.loc[sent_id,govid], attr, 'root')
    return [(sent_id, govid)]

    #sent = df.xs(sent_id, level='s', drop_level=False)
    #res = list(i for i, tk in sent.iterrows() if tk['g'] == tok_id)
    #if repeat is not False:
    #    return [res[repeat-1]]
    #else:
    #    return res

def get_match(idx, df=False, repeat=False, attr=False, **kwargs):
    """
    Dummy function, for the most part
    """
    sent_id, tok_id = getattr(idx, 'name', idx)
    if attr:
        return df[attr].ix[sent_id, tok_id]
    return [(sent_id, tok_id)]

def get_head(idx, df=False, repeat=False, attr=False, **kwargs):
    """
    Get the head of a 'constituent'---'
    for 'corpus linguistics', if 'corpus' is searched, return 'linguistics'
    """

    sent_id, tok_id = getattr(idx, 'name', idx)
    #sent = df.ix[sent_id]
    token = df.ix[sent_id, tok_id]

    if not hasattr(token, 'c'):
        # this should error, because the data isn't there at all
        lst_of_ixs = [(sent_id, tok_id)]

    elif token['c'] == '_':
        lst_of_ixs = [(sent_id, tok_id)]
    # if it is the head, return it
    elif token['c'].endswith('*'):
        lst_of_ixs = [(sent_id, tok_id)]
    else:
        # should be able to speed this one up!
        just_same_coref = df.loc[sent_id][df.loc[sent_id]['c'] == token['c'] + '*']
        if not just_same_coref.empty:
            lst_of_ixs = [(sent_id, i) for i in just_same_coref.index]
        else:
            lst_of_ixs = [(sent_id, tok_id)]
    if attr:
        lst_of_ixs = [df.loc[i][attr] for i in lst_of_ixs]
    return lst_of_ixs

def get_representative(idx,
                       df=False,
                       repeat=False,
                       attr=False,
                       **kwargs):
    """
    Get the representative coref head
    """
    sent_id, tok_id = getattr(idx, 'name', idx)

    token = df.ix[sent_id, tok_id]
    # if no corefs at all
    if not hasattr(token, 'c'):
        # this should error, because the data isn't there at all
        lst_of_ixs = [(sent_id, tok_id)]     
    # if no coref available
    elif token['c'] == '_':
        lst_of_ixs = [(sent_id, tok_id)]
    else:
        just_same_coref = df.loc[df['c'] == token['c'] + '*']
        if not just_same_coref.empty:
            lst_of_ixs = [just_same_coref.iloc[0].name]
        else:
            lst_of_ixs = [(sent_id, tok_id)]
    
    if attr:
        lst_of_ixs = [df.ix[i][attr] for i in lst_of_ixs]

    return lst_of_ixs

def get_all_corefs(s, i, df, coref=False):
    # if not in coref mode, skip
    if not coref:
        return [(s, i)]
    # if the word was not a head, forget it
    if not df.ix[s,i]['c'].endswith('*'):
        return [(s, i)]
    try:
        # get any other mention head for this coref chain
        just_same_coref = df.loc[df['c'] == df.ix[s,i]['c']]
        return list(just_same_coref.index)
    except:
        return [(s, i)]

def search_this(df, obj, attrib, pattern, adjacent=False, coref=False):
    """
    Search the dataframe for a single criterion
    """
    import re
    out = []

    # if searching by head, they need to be heads
    if obj == 'r':
        df = df.loc[df['c'].endswith('*')]

    # cut down to just tokens with matching attr
    # but, if the pattern is 'any', don't bother
    if hasattr(pattern, 'pattern') and pattern.pattern == r'.*':
        matches = df
    else:
        matches = df[df[attrib].fillna('').str.contains(pattern)]

    # functions for getting the needed object
    revmapping = {'g': get_dependents_of_id,
                  'd': get_governors_of_id,
                  'm': get_match,
                  'h': get_all_corefs,
                  'r': get_representative}

    getfunc = revmapping.get(obj)

    for idx in list(matches.index):

        if adjacent:
            if adjacent[0] == '+':
                tomove = -int(adj[1])
            elif adjacent[0] == '-':
                tomove = int(adj[1])
            idx = (idx[0], idx[1] + tomove)
        
        for mindex in getfunc(idx, df=df, coref=coref):

            if mindex:
                out.append(mindex)

    return list(set(out))

def show_fix(show):
    """show everything"""
    objmapping = {'d': get_dependents_of_id,
                  'g': get_governors_of_id,
                  'm': get_match,
                  'h': get_head}

    out = []
    for val in show:
        adj, val = determine_adjacent(val)
        obj, attr = val[0], val[-1]
        obj_getter = objmapping.get(obj)
        out.append(adj, val, obj, attr, obj_getter)
    return out

def dummy(x, *args, **kwargs):
    return x

def format_toks(to_process, show, df):
    """
    Format matches by show values
    """

    import pandas as pd

    objmapping = {'d': get_dependents_of_id,
                  'g': get_governors_of_id,
                  'm': get_match,
                  'h': get_head}

    sers = []

    dmode = any(x.startswith('d') for x in show)
    if dmode:
        from collections import defaultdict
        dicts = defaultdict(dict)

    for val in show:
        adj, val = determine_adjacent(val)
        if adj:
            if adj[0] == '+':
                tomove = int(adj[1])
            elif adj[0] == '-':
                tomove = -int(adj[1])

        obj, attr = val[0], val[-1]
        func = objmapping.get(obj, dummy)
        out = defaultdict(dict) if dmode else []
        for ix in list(to_process.index):
            piece = False
            if adj:
                ix = (ix[0], ix[1] + tomove)
                if ix not in df.index:
                    piece = 'none'
            if not piece:
                if obj == 'm':
                    piece = df.loc[ix][attr.replace('x', 'p')]
                    if attr == 'x':
                        from corpkit.dictionaries.word_transforms import taglemma
                        piece = taglemma.get(piece.lower(), piece.lower())
                    piece = [piece]
                else:
                    piece = func(ix, df=df, attr=attr)
                    if not isinstance(piece, list):
                        piece = [piece]
                if dmode:
                    dicts[ix][val] = piece
                else:
                    out.append(piece[0])

        if not dmode:
            ser = pd.Series(out, index=to_process.index)
            ser.name = val
            sers.append(ser)

    if not dmode:
        dx = pd.concat(sers, axis=1)
        if len(dx.columns) == 1:
            return dx.iloc[:,0]
        else:
            return dx.apply('/'.join, axis=1)
    else:
        index = []
        data = []
        for ix, dct in dicts.items():
            max_key, max_value = max(dct.items(), key=lambda x: len(x[1]))
            for val, pieces in dct.items():
                if len(pieces) == 1:
                    dicts[ix][val] = pieces * len(max_value)

            for tup in list(zip(*[i for i in dct.values()])):
                index.append(ix)
                data.append('/'.join(tup))
        return pd.Series(data, index=pd.MultiIndex.from_tuples(index))


def make_series(ser, df=False, obj=False,
                att=False, adj=False):
    """
    To apply to a DataFrame to add complex criteria, like 'gf'
    """
    # todo:
    # collocation
    # ngram
    if obj == 'g':
        if ser[obj] == 0:
            return 'root'
        else:
            try:
                return df[att][ser.name[0], ser[obj]]
            # this keyerror can happen if governor is punctuation, for example
            except KeyError:
                return

    # if dependent, we need to return a df-like thing instead
    elif obj == 'd':
        #import pandas as pd
        idxs = [(ser.name[0], int(i)) for i in ser[obj].split(',')]
        dat = df[att].ix[idxs]

        return dat

    # todo: fix everything below here
    elif obj == 'r': # get the representative
        cohead = ser['c'].rstrip('*')
        refs = df[df['c'] == cohead + '*']
        return refs[att].ix[0]

    elif obj == 'h': # get head
        cohead = ser['c']
        if cohead.endswith('*'):
            return ser[att]
        else:
            sent = df[att].loc[ser.name[0]]
            return sent[sent['c'] == cohead + '*']

    # potential naming conflict with sent index ...
    elif obj == 's': # get whole phrase"
        cohead = ser['c']
        sent = df[att].loc[ser.name[0]]
        return sent[sent['c'] == cohead.rstrip('*')].values
    
def joiner(ser):
    return ser.str.cat(sep='/') 

def make_new_for_dep(dfmain, dfdep, name):
    """
    If showind dependent, we have to make a whole new dataframe

    :param dfmain: dataframe with everything in it
    :param dfdep: dataframe with just dependent
    """
    import pandas as pd
    import numpy as np
    new = []
    newd = []
    index = []
    for (i, ml), (_, dl) in zip(dfmain.iterrows(), dfdep.iterrows()):
        if all(pd.isnull(i) for i in dl.values):
            index.append(i)
            new.append(ml)
            newd.append('none')
            continue
        else:
            for bit in dl:
                if pd.isnull(bit):
                    continue
                index.append(i)
                new.append(ml)
                newd.append(bit)
    
    #todo: account for no matches
    index = pd.MultiIndex.from_tuples(index, names=['s', 'i'])
    newdf = pd.DataFrame(new, index=index)
    newdf[name] = newd
    return newdf

def turn_pos_to_wc(ser, showval):
    if not showval:
        return ser
    import pandas as pd
    from corpkit.dictionaries.word_transforms import taglemma   
    vals = [taglemma.get(piece.lower(), piece.lower())
                  for piece in ser.values]
    news = pd.Series(vals, index=ser.index)
    news.name = ser.name[:-1] + 'x'
    return news

def concline_generator(matches, idxs, df, metadata,
                       add_meta, category, fname, preserve_case=False):
    """
    Get all conclines

    :param matches: a list of formatted matches
    :param idxs: their (sent, word) idx
    """
    conc_res = []
    # potential speedup: turn idxs into dict
    from collections import defaultdict
    mdict = defaultdict(list)
    # if remaking idxs here, don't need to do it earlier
    idxs = list(matches.index)
    for mid, (s, i) in zip(matches, idxs):
    #for s, i in matches:
        mdict[s].append((i, mid))
    # shorten df to just relevant sents to save lookup time
    df = df.loc[list(mdict.keys())]
    # don't look up the same sentence multiple times
    for s, tup in sorted(mdict.items()):
        sent = df.loc[s]
        if not preserve_case:
            sent = sent.str.lower()
        meta = metadata[s]
        sname = meta.get('speaker', 'none')
        for i, mid in tup:
            if not preserve_case:
                mid = mid.lower()
            ix = '%d,%d' % (s, i)
            start = ' '.join(sent.loc[:i-1].values)
            end = ' '.join(sent.loc[i+1:].values)
            lin = [ix, category, fname, sname, start, mid, end]
            if add_meta:
                for k, v in sorted(meta.items()):
                    if k in ['speaker', 'parse', 'sent_id']:
                        continue
                    if isinstance(add_meta, list):
                        if k in add_meta:
                            lin.append(v)
                    elif add_meta is True:
                        lin.append(v)
            conc_res.append(lin)
    return conc_res

def p_series_to_x_series(val):
    return taglemma.get(val.lower(), val.lower())

def fast_simple_conc(dfss, idxs, show,
                     metadata=False,
                     add_meta=False, 
                     fname=False,
                     category=False,
                     only_format_match=True,
                     conc=False,
                     preserve_case=False):
    """
    Fast, simple concordancer, heavily conditional
    to save time.
    """
    if dfss.empty:
        return [], []
        
    import pandas as pd

    # best case, the user doesn't want any gov-dep stuff
    simple = all(i.startswith('m') for i in show)
    # worst case, the user wants something from dep
    dmode = any(x.startswith('d') for x in show)
    # make a quick copy if need be because we modify the df
    df = dfss.copy() if not simple else dfss
    # add text to df columns so that it resembles 'show' values
    lst = ['s', 'i', 'w', 'l', 'f', 'p']
    df.columns = ['m' + i if len(i) == 1 and i in lst \
                  else i for i in list(df.columns)]

    # this is the data needed for concordancing
    df_for_lr = df['mw'] if only_format_match else df

    just_matches = df.loc[idxs]
    
    # if the showing can't come straight out of the df, 
    # we can add columns with the necessary information
    if not simple:
        formatted = []
        import numpy as np
        for ind, i in enumerate(show):
            # nothing to do if it's an m feature
            if i.startswith('m'):
                continue
            # defaults for adjacent work
            adj, tomove, adjname = False, False, ''
            adj, i = determine_adjacent(i)
            adjname = ''.join(adj) if hasattr(adj, '__iter__') else ''
            
            # get number of places to shift left or right
            if adj:
                if adj[0] == '+':
                    tomove = -int(adj[1])
                elif adj[0] == '-':
                    tomove = int(adj[1])

            # cut df down to just needed bits for the sake of speed
            # i.e. if we want gov func, get only gov and func cols
            ob, att = i[0], i[-1]
            xmode = att == 'x'
            if xmode:
                att = 'p'
                show[ind] = show[ind][:-1] + 'p'
            # for corefs, we also need the coref data
            if ob in ['c', 'h', 's']:
                dfx = df[['c', att]]
            else:
                lst = ['s', 'i', 'w', 'l', 'f', 'p']
                if att in lst and ob != 'm':
                    att = 'm' + att
                if ob == 'm':
                    dfx = df[['m' + att]]
                else:
                    dfx = df[[ob, att]]
            # decide if we need to format everything
            if not conc or only_format_match:
                to_proc = just_matches
            else:
                to_proc = df
            # now we get or generate the new column
            if ob == 'm':
                ser = to_proc['m' + att]
            else:
                ser = to_proc.apply(make_series, df=dfx, obj=ob, att=att, axis=1)
            if xmode:
                ser = ser.apply(p_series_to_x_series)

            # adjmode simply shifts series and index
            if adj:
                #todo: this shifts next sent into previous sent!
                ser = ser.shift(tomove)
                ser = ser.fillna('none')

            # dependent mode produces multiple matches
            # so, we have to make a new dataframe with duplicate indexes
            # todo: what about when there are two dep options?
            ser.name = adjname + i
            if ob != 'd':
                df[ser.name] = ser
            else:
                df = make_new_for_dep(df, ser, i)

        df = df.fillna('none')


    # x is wordclass. so, we just get pos and translate it
    nshow = [(i.replace('x', 'p'), i.endswith('x')) for i in show]

    # generate a series of matches with slash sep if multiple show vals
    if len(nshow) > 1:

        if conc and not only_format_match:
            first = turn_pos_to_wc(df[nshow[0][0]], nshow[0][1])
            llist = [turn_pos_to_wc(df[sho], xmode) for sho, xmode in nshow[1:]]
            df = first.str.cat(others=llist, sep='/')
            matches = df[idxs]
        else:
            justm = df.loc[idxs]
            first = turn_pos_to_wc(justm[nshow[0][0]], nshow[0][1])
            llist = [turn_pos_to_wc(justm[sho], xmode) for sho, xmode in nshow[1:]]
            matches = first.str.cat(others=llist, sep='/')
            if conc:
                df = df_for_lr
    else:
        if conc and not only_format_match:
            df = turn_pos_to_wc(df[nshow[0][0]], nshow[0][1])
            matches = df[idxs]
        else:
            matches = turn_pos_to_wc(df[nshow[0][0]][idxs], nshow[0][1])
            if conc:
                df = df_for_lr
    
    # get rid of (e.g.) nan caused by no_punct=True
    matches = matches.dropna(axis=0, how='all')
    if not preserve_case:
        matches = matches.str.lower()

    if not conc:
        # todo: is matches.values faster?
        return list(matches), []
    else:
        conc_res = concline_generator(matches, idxs, df,
                                      metadata, add_meta,
                                      category, fname,
                                      preserve_case=preserve_case)

    return list(matches), conc_res

def show_this(df, matches, show, metadata, conc=False,
              coref=False, category=False, show_conc_metadata=False, **kwargs):

    only_format_match = kwargs.pop('only_format_match', True)
    ngram_mode = kwargs.get('ngram_mode', True)
    preserve_case = kwargs.get('preserve_case', False)

    matches = sorted(list(matches))

    # add index as column if need be
    if any(i.endswith('s') for i in show):
        df['ms'] = [str(i) for i in df.index.labels[0]]
    if any(i.endswith('i') for i in show):
        df['mi'] = [str(i) for i in df.index.labels[1]]
    
    # attempt to leave really fast
    if kwargs.get('countmode'):
        return len(matches), {}
    if len(show) == 1 and not conc:
        if show[0] in ['ms', 'mi', 'mw', 'ml', 'mp', 'mf']:
            get_fast = df.loc[matches][show[0][-1]]
            if not preserve_case:
                get_fast = get_fast.str.lower()
            return list(get_fast), {}

    # todo: make work for ngram, collocate and coref
    if all(i[0] in ['m', 'g', '+', '-', 'd'] for i in show):
        return fast_simple_conc(df,
                                matches,
                                show,
                                metadata,
                                show_conc_metadata,
                                kwargs.get('filename', ''),
                                category,
                                only_format_match,
                                conc=conc,
                                preserve_case=preserve_case)

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
    """
    If mode is all, remove any entry that occurs < len(criteria)
    """
    if mode == 'any':
        return set(matches)
    if mode == 'all':
        from collections import Counter
        counted = Counter(matches)
        return set(k for k, v in counted.items() if v >= len(criteria))

def determine_adjacent(original):
    if original[0] in ['+', '-']:
        adj = (original[0], original[1:-2])
        original = original[-2:]
    else:
        adj = False
    return adj, original

def process_df_for_speakers(df, metadata, criteria, coref=False,
                            feature='speakers', reverse=False):
    """
    keep just the correct speakers
    """
    if not criteria:
        df._metadata = metadata
        return df
    # maybe could be sped up, but let's not for now:
    if coref:
        df._metadata = metadata
        return df
    import re
    good_sents = []
    new_metadata = {}
    from corpkit.constants import STRINGTYPE
    # could make the below more elegant ...
    for sentid, data in sorted(metadata.items()):
        meta_value = data.get(feature, 'none')
        lst_met_vl = meta_value.split(';')
        if isinstance(criteria, list):
            if not reverse:
                if not any(i in criteria for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
            else:
                if any(i in criteria for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
        elif isinstance(criteria, (re._pattern_type, STRINGTYPE)):
            if not reverse:
                if any(re.search(criteria, i) for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
            else:
                if not any(re.search(criteria, i) for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data

    df = df.loc[good_sents]
    df = df.fillna('')
    df._metadata = new_metadata
    return df

def cut_df_by_meta(df, just_metadata, skip_metadata):
    if df is not None:
        if just_metadata:
            for k, v in just_metadata.items():
                df = process_df_for_speakers(df, df._metadata, v, feature=k)
        if skip_metadata:
            for k, v in skip_metadata.items():
                df = process_df_for_speakers(df, df._metadata, v, feature=k, reverse=True)
    return df


def tgrep_searcher(f=False,
                   metadata=False,
                   from_df=False,
                   search=False,
                   searchmode=False,
                   exclude=False,
                   excludemode=False,
                   translated_option=False,
                   subcorpora=False,
                   conc=False,
                   root=False,
                   preserve_case=False,
                   countmode=False,
                   show=False,
                   lem_instance=False,
                   lemtag=False,
                   category=False,
                   fname=False,
                   show_conc_metadata=False,
                   only_format_match=True,
                   **kwargs):

    """
    Use tgrep for constituency grammar search
    """

    from corpkit.process import show_tree_as_per_option, tgrep
    matches = []
    conc_out = []
    # in case search was a dict
    srch = search.get('t') if isinstance(search, dict) else search
    metcat = category if category else ''
    for i, sent in metadata.items():
        results = tgrep(sent['parse'], srch)
        sname = sent.get('speaker')
        metcat = category
        for res in results:
            tok_id, start, middle, end = show_tree_as_per_option(show, res, sent,
                                                  df=from_df, sent_id=i, conc=conc,
                                                  only_format_match=only_format_match)
            #middle, idx = show_tree_as_per_option(show, res, 'conll', sent, df=df, sent_id=i)
            matches.append(middle)
            if conc:
                form_ix = '%d,%d' % (i, tok_id)
                lin = [form_ix, metcat, fname, sname, start, middle, end]
                if show_conc_metadata:
                    for k, v in sorted(sent.items()):
                        if k in ['speaker', 'parse', 'sent_id']:
                            continue
                        if isinstance(show_conc_metadata, list):
                            if k in show_conc_metadata:
                                lin.append(v)
                        elif show_conc_metadata is True:
                            lin.append(v)
                conc_out.append(lin)

    return matches, conc_out

def slow_tregex(metadata=False,
                search=False,
                searchmode=False,
                exclude=False,
                excludemode=False,
                translated_option=False,
                subcorpora=False,
                conc=False,
                root=False,
                preserve_case=False,
                countmode=False,
                show=False,
                lem_instance=False,
                lemtag=False,
                from_df=False,
                fname=False,
                category=False,
                only_format_match=False,
                **kwargs):
    """
    Do the metadata specific version of tregex queries
    """

    from corpkit.process import tregex_engine, format_tregex, make_conc_lines_from_whole_mid
    
    if isinstance(search, dict):
        search = list(search.values())[0]
    
    speak_tree = [(x.get(subcorpora, 'none'), x['parse']) for x in metadata.values()]
        
    if speak_tree:
        speak, tree = list(zip(*speak_tree))
    else:
        speak, tree = [], []
    
    if all(not x for x in speak):
        speak = False

    to_open = '\n'.join(tree)

    concs = []

    if not to_open.strip('\n'):
        if subcorpora:
            return {}, {}

    ops = ['-%s' % i for i in translated_option] + ['-o', '-n']
    res = tregex_engine(query=search, 
                        options=ops, 
                        corpus=to_open,
                        root=root,
                        preserve_case=preserve_case,
                        speaker_data=False)

    res = format_tregex(res, show, exclude=exclude, excludemode=excludemode,
                        translated_option=translated_option,
                        lem_instance=lem_instance, countmode=countmode, speaker_data=False,
                        lemtag=lemtag)

    if not res:
        if subcorpora:
            return [], []

    if conc:
        ops += ['-w']
        whole_res = tregex_engine(query=search, 
                                  options=ops, 
                                  corpus=to_open,
                                  root=root,
                                  preserve_case=preserve_case,
                                  speaker_data=speak)

        # format match too depending on option
        if not only_format_match:
            whole_res = format_tregex(whole_res, show, exclude=exclude, excludemode=excludemode,
                                      translated_option=translated_option,
                                       lem_instance=lem_instance, countmode=countmode,
                                       speaker_data=speak, whole=True,
                                       lemtag=lemtag)

        # make conc lines from conc results
        concs = make_conc_lines_from_whole_mid(whole_res, res, filename=fname, show=show)
    else:
        concs = [False for i in res]

    if len(res) > 0 and isinstance(res[0], tuple):
        res = [i[-1] for i in res]

    if countmode:
        if isinstance(res, int):
            return res, False
        else:
            return len(res), False
    else:
        return res, concs

def get_stats(from_df=False, metadata=False, feature=False, root=False, **kwargs):
    """
    Get general statistics for a DataFrame
    """

    #todo: this should be moved to conll.pys
    import re
    from corpkit.dictionaries.process_types import processes
    from collections import Counter, defaultdict
    from corpkit.process import tregex_engine
    from corpkit.conll import parse_conll, pipeline, process_df_for_speakers, cut_df_by_meta

    def ispunct(s):
        import string
        return all(c in string.punctuation for c in s)

    tree = [x['parse'] for x in metadata.values()]
    
    tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                 'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                 'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                 'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                 'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                 'Clauses': r'/^S/ < __',
                 'Interrogative': r'ROOT << (/\?/ !< __)',
                 'Processes': r'/VB.?/ >># (VP !< VP >+(VP) /^(S|ROOT)/)'}

    result = Counter()

    for name in tregex_qs.keys():
        result[name] = 0

    result['Sentences'] = len(set(from_df.index.labels[0]))
    result['Passives'] = len(from_df[from_df['f'] == 'nsubjpass'])
    result['Tokens'] = len(from_df)
    # the below has returned a float before. i assume actually a nan?
    result['Words'] = len([w for w in list(from_df['w']) if w and not ispunct(str(w))])
    result['Characters'] = sum([len(str(w)) for w in list(from_df['w']) if w])
    result['Open class'] = sum([1 for x in list(from_df['p']) if x and x[0] in ['N', 'J', 'V', 'R']])
    result['Punctuation'] = result['Tokens'] - result['Words']
    result['Closed class'] = result['Words'] - result['Open class']

    to_open = '\n'.join(tree)

    if not to_open.strip('\n'):
        return {}, {}

    for name, q in sorted(tregex_qs.items()):
        options = ['-o', '-t'] if name == 'Processes' else ['-o']
        # c option removed, could cause memory problems
        #ops = ['-%s' % i for i in translated_option] + ['-o', '-n']
        res = tregex_engine(query=q, 
                            options=options,
                            corpus=to_open,  
                            root=root)

        #res = format_tregex(res)
        if not res:
            continue

        concs = [False for i in res]
        for (_, met, r), line in zip(res, concs):
            result[name] = len(res)
        if name != 'Processes':
            continue
        non_mat = 0
        for ptype in ['mental', 'relational', 'verbal']:
            reg = getattr(processes, ptype).words.as_regex(boundaries='l')
            count = len([i for i in res if re.search(reg, i[-1])])
            nname = ptype.title() + ' processes'
            result[nname] = count

        if root:
            root.update()
    return result, {}

def pipeline(f=False,
             search=False,
             show=False,
             exclude=False,
             searchmode='all',
             excludemode='any',
             conc=False,
             coref=False,
             from_df=False,
             just_metadata=False,
             skip_metadata=False,
             category=False,
             show_conc_metadata=False,
             statsmode=False,
             search_trees=False,
             lem_instance=False,
             **kwargs):
    """
    A basic pipeline for conll querying---some options still to do
    """

    if isinstance(show, str):
        show = [show]
    show = [fix_show_bit(i) for i in show]

    all_matches = []
    all_exclude = []

    if from_df is False or from_df is None:
        df = parse_conll(f, usecols=kwargs.get('usecols'))
        metadata = df._metadata
    else:
        df = from_df
        metadata = kwargs.pop('metadata')
    feature = kwargs.pop('by_metadata', False)
    df = cut_df_by_meta(df, just_metadata, skip_metadata)

    searcher = pipeline
    if statsmode:
        searcher = get_stats
    if search_trees == 'tregex':
        searcher = slow_tregex
    elif search_trees == 'tgrep':
        searcher = tgrep_searcher

    if feature:
        if df is None:
            print('Problem reading data from %s.' % f)
            return {}, {}

        # determine searcher
        resultdict = {}
        concresultdict = {}
        # get all the possible values in the df for the feature of interest
        all_cats = set([i.get(feature, 'none') for i in list(df._metadata.values())])
        for category in all_cats:
            new_df = process_df_for_speakers(df, df._metadata, category, feature=feature)
            r, c = searcher(f=False,
                            fname=f,
                            search=search,
                            exclude=exclude,
                            show=show,
                            searchmode=searchmode,
                            excludemode=excludemode,
                            conc=conc,
                            coref=coref,
                            from_df=new_df,
                            by_metadata=False,
                            category=category,
                            show_conc_metadata=show_conc_metadata,
                            lem_instance=lem_instance,
                            root=kwargs.pop('root', False),
                            subcorpora=feature,
                            metadata=new_df._metadata,
                            **kwargs)
            
            resultdict[category] = r
            concresultdict[category] = c
        return resultdict, concresultdict

    if df is None:
        print('Problem reading data from %s.' % f)
        return [], []

    kwargs['ngram_mode'] = any(x.startswith('n') for x in show)

    df = process_df_for_speakers(df, df._metadata, kwargs.get('just_speakers'), coref=coref)
    metadata = df._metadata

    if kwargs.get('no_punct', True):
        df = df[df['w'].fillna('').str.contains(kwargs.get('is_a_word', r'[A-Za-z0-9]'))]
        # remove brackets --- could it be done in one regex?
        df = df[~df['w'].str.contains(r'^-.*B-$')]

    if kwargs.get('no_closed'):
        from corpkit.dictionaries import wordlists
        crit = wordlists.closedclass.as_regex(boundaries='l', case_sensitive=False)
        df = df[~df['w'].str.contains(crit)]

    if statsmode:
        return get_stats(df, metadata, False, root=kwargs.pop('root', False), **kwargs)
    elif search_trees:
        return searcher(from_df=df,
                        search=search,
                        searchmode=searchmode,
                        exclude=exclude,
                        excludemode=excludemode,
                        conc=conc,
                        by_metadata=False,
                        metadata=metadata,
                        root=kwargs.pop('root', False),
                        fname=f,
                        show=show,
                        **kwargs)

    # do no searching if 'any' is requested
    if len(search) == 1 and list(search.keys())[0] == 'w' \
                        and hasattr(list(search.values())[0], 'pattern') \
                        and list(search.values())[0].pattern == r'.*':
        all_matches = list(df.index)
    else:
        for k, v in search.items():
            adj, k = determine_adjacent(k)
            res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
            for r in res:
                all_matches.append(r)
        all_matches = remove_by_mode(all_matches, searchmode, search)
    if exclude:
        for k, v in exclude.items():
            adj, k = determine_adjacent(k)
            res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
            for r in res:
                all_exclude.append(r)
        all_exclude = remove_by_mode(all_exclude, excludemode, exclude)
        all_matches = all_matches.difference(all_exclude)

    out, conc_out = show_this(df, all_matches, show, metadata, conc, 
                              coref=coref, category=category, 
                              show_conc_metadata=show_conc_metadata,
                              **kwargs)

    return out, conc_out

def load_raw_data(f):
    """loads the stripped and raw versions of a parsed file"""
    from corpkit.process import saferead

    # open the unparsed version of the file, read into memory
    stripped_txtfile = f.replace('.conll', '').replace('-parsed', '-stripped')
    stripped_txtdata, enc = saferead(stripped_txtfile)

    # open the unparsed version with speaker ids
    id_txtfile = f.replace('.conll', '').replace('-parsed', '')
    id_txtdata, enc = saferead(id_txtfile)

    return stripped_txtdata, id_txtdata

def get_speaker_from_offsets(stripped, plain, sent_offsets,
                             metadata_mode=False,
                             speaker_segmentation=False):
    """
    Take offsets and get a speaker ID or metadata from them
    """
    if not stripped and not plain:
        return {}
    start, end = sent_offsets
    sent = stripped[start:end]
    # find out line number
    # sever at start of match
    cut_old_text = stripped[:start]
    line_index = cut_old_text.count('\n')
    # lookup this text
    with_id = plain.splitlines()[line_index]
    
    # parse xml tags in original file ...
    meta_dict = {'speaker': 'none'}

    if metadata_mode:

        metad = with_id.strip().rstrip('>').rsplit('<metadata ', 1)
        
        import shlex
        from corpkit.constants import PYTHON_VERSION
        
        try:
            shxed = shlex.split(metad[-1].encode('utf-8')) if PYTHON_VERSION == 2 \
                else shlex.split(metad[-1])
        except:
            shxed = metad[-1].split("' ")
        for m in shxed:
            if PYTHON_VERSION == 2:
                m = m.decode('utf-8')
            # in rare cases of weirdly formatted xml:
            try:
                k, v = m.split('=', 1)
                v = v.replace(u"\u2018", "'").replace(u"\u2019", "'").strip("'").strip('"')
                meta_dict[k] = v
            except ValueError:
                continue

    if speaker_segmentation:
        split_line = with_id.split(': ', 1)
        # handle multiple tags?
        if len(split_line) > 1:
            speakerid = split_line[0]
        else:
            speakerid = 'UNIDENTIFIED'
        meta_dict['speaker'] = speakerid

    return meta_dict

def convert_json_to_conll(path,
                          speaker_segmentation=False,
                          coref=False,
                          metadata=False):
    """
    take json corenlp output and convert to conll, with
    dependents, speaker ids and so on added.

    Path is for the parsed corpus, or a list of files within a parsed corpus
    Might need to fix if outname used?
    """

    import json
    import re
    from corpkit.build import get_filepaths
    
    if isinstance(path, list):
        files = path
    else:
        files = get_filepaths(path, ext='conll')
    
    for f in files:

        if speaker_segmentation or metadata:
            stripped, raw = load_raw_data(f)
        else:
            stripped, raw = None, None

        main_out = ''
        # if the file has already been converted, don't worry about it
        # untested?
        with open(f, 'r') as fo:
            #try:
            data = json.load(fo)
            # todo: differentiate between json errors
            # rsc corpus had one json file with an error
            # outputted by corenlp, and the conversion
            # failed silently here
            #except ValueError:
            #    continue

        ref = 1
        for idx, sent in enumerate(data['sentences'], start=1):
            tree = sent['parse'].replace('\n', '')
            tree = re.sub(r'\s+', ' ', tree)

            # offsets for speaker_id
            sent_offsets = (sent['tokens'][0]['characterOffsetBegin'], \
                            sent['tokens'][-1]['characterOffsetEnd'])
            
            metad = get_speaker_from_offsets(stripped,
                                             raw,
                                             sent_offsets,
                                             metadata_mode=True,
                                             speaker_segmentation=speaker_segmentation)
                            
            output = '# sent_id %d\n# parse=%s\n' % (idx, tree)
            for k, v in sorted(metad.items()):
                output += '# %s=%s\n' % (k, v)
            for token in sent['tokens']:
                index = str(token['index'])
                # this got a stopiteration on rsc data
                governor, func = next(((i['governor'], i['dep']) \
                                         for i in sent['collapsed-ccprocessed-dependencies'] \
                                         if i['dependent'] == int(index)), ('_', '_'))
                if governor is '_':
                    depends = False
                else:
                    depends = [str(i['dependent']) for i in sent['collapsed-ccprocessed-dependencies'] if i['governor'] == int(index)]
                if not depends:
                    depends = '0'
                #offsets = '%d,%d' % (token['characterOffsetBegin'], token['characterOffsetEnd'])
                line = [idx,
                        index,
                        token['word'],
                        token['lemma'],
                        token['pos'],
                        token.get('ner', '_'),
                        governor,
                        func,
                        ','.join(depends)]
                # no ints
                line = [str(l) if isinstance(l, int) else l for l in line]

                from corpkit.constants import PYTHON_VERSION
                if PYTHON_VERSION == 2:
                    try:
                        [unicode(l, errors='ignore') for l in line]
                    except TypeError:
                        pass
                
                output += '\t'.join(line) + '\n'
            main_out += output + '\n'

        # post process corefs
        if coref:
            import re
            dct = {}
            idxreg = re.compile('^([0-9]+)\t([0-9]+)')
            splitmain = main_out.split('\n')
            # add tab _ to each line, make dict of sent-token: line index
            for i, line in enumerate(splitmain):
                if line and not line.startswith('#'):
                    splitmain[i] += '\t_'
                match = re.search(idxreg, line)
                if match:
                    l, t = match.group(1), match.group(2)
                    dct[(int(l), int(t))] = i
            
            # for each coref chain, if there are corefs
            for numstring, list_of_dicts in sorted(data.get('corefs', {}).items()):
                # for each mention
                for d in list_of_dicts:
                    snum = d['sentNum']
                    # get head?
                    # this has been fixed in dev corenlp: 'headIndex' --- could simply use that
                    # ref : https://github.com/stanfordnlp/CoreNLP/issues/231
                    for i in range(d['startIndex'], d['endIndex']):
                    
                        try:
                            ix = dct[(snum, i)]
                            fixed_line = splitmain[ix].rstrip('\t_') + '\t%s' % numstring
                            gv = fixed_line.split('\t')[6]
                            try:
                                gov_s = int(gv)
                            except ValueError:
                                continue
                            if gov_s < d['startIndex'] or gov_s > d['endIndex']:
                                fixed_line += '*'
                            splitmain[ix] = fixed_line
                            dct.pop((snum, i))
                        except KeyError:
                            pass

            main_out = '\n'.join(splitmain)

        from corpkit.constants import OPENER       
        with OPENER(f, 'w', encoding='utf-8') as fo:
            main_out = main_out.replace(u"\u2018", "'").replace(u"\u2019", "'")
            fo.write(main_out)

