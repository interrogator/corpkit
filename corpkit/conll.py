"""
corpkit: process CONLL formatted data
"""

def parse_conll(f,
                first_time=False,
                just_meta=False):
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
                         names=head, index_col=['s', 'i'])
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

def make_concx(series, matches, metadata, df, 
               conc, fsi_index=False, category=False, show_conc_metadata=False,
               only_format_match=True, **kwargs):
    """
    Make concordance lines

    Speed this up?
    """
    import pandas as pd

    conc_lines = []
    fname = kwargs.get('filename', '')
    ngram_mode = kwargs.get('ngram_mode')
    add_meta = show_conc_metadata
    
    if not conc:
        return conc_lines
    
    #maxc, cconc = kwargs.get('maxconc', (False, False))
    #if maxc and maxc < cconc:
    #    return []

    if ngram_mode:
        for s, i in set(matches):
            mid_toks = []
            for n in range(kwargs.get('gramsize') + 1):
                mid_toks.append((s, i+n))
            sent = df.loc[s]
            first, last = mid_toks[0][1], mid_toks[-1][1]
            if only_format_match:
                start = ' '.join(list(sent.loc[:first]['w']))
                end = ' '.join(list(sent.loc[last+1:]['w']))
            else:
                start = ' '.join(list(series.loc[s,:first]))
                end = ' '.join(list(series.loc[s,last+1:]))
            middle = ' '.join(series[s][first:last])

            sname = metadata[s].get('speaker', 'none')
            lin = [fname, sname, start, middle, end]
            for k, v in sorted(metadata[s].items()):
                if k in ['speaker', 'parse', 'sent_id']:
                    continue
                if isinstance(add_meta, list):
                    if k in add_meta:
                        lin.append(v)
                elif add_meta:
                    lin.append(v)
            conc_lines.append(lin)
        return conc_lines

    for s, i in sorted(set(matches)):
        #thecount = matches.count((s, i))
        sent = df.loc[s]
        if only_format_match:
            start = ' '.join(list(sent.loc[:i-1]['w']))
            end = ' '.join(list(sent.loc[i+1:]['w']))
        else:
            start = ' '.join(list(series.loc[s,:i-1]))
            end = ' '.join(list(series.loc[s,i+1:]))
        middles = series[s, i]
        #print(start, end)
        sname = metadata[s].get('speaker', 'none')

        if not isinstance(middles, pd.core.series.Series):
            middles = [middles]
        
        for middle in middles:
            ix = '%d,%d' % (s, i)    
            lin = [ix, category, fname, sname, start, middle, end]

            for k, v in sorted(metadata[s].items()):

                if k in ['speaker', 'parse', 'sent_id']:
                    continue

                if isinstance(add_meta, list):
                    if k in add_meta:
                        lin.append(v)
                elif add_meta is True:
                    lin.append(v)

            conc_lines.append(lin)

    return conc_lines

def make_series(ser, df=False, obj=False, att=False, adj=False, tomove=False):
    """
    To apply to a DataFrame to add complex criteria, like 'gf'
    """
    # todo:
    # collocation?
    # ngram
    from pandas import Series
    if obj == 'g':
        idxs = [(ser.name[0], ser[obj])]
        if idxs[0][1] == 0:
            return Series(['root'])
        else:
            ss = Series(list(df[att].loc[idxs]))
            return ss

    elif obj == 'd':
        idxs = [(ser.name[0], int(i)) for i in ser[obj].split(',')]
        ss = Series(list(df[att].loc[idxs]))
        return ss

    elif obj == 'r': # get the representative
        cohead = ser['c'].rstrip('*')
        refs = df[df['c'] == cohead + '*']
        return Series(refs[att].ix[0])

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

#def just_g(idxs, df=False, idxs=[]):
#    ser.name[0]
#    df.apply()
#    fidx = [(s, df.loc[s, i]['g']) for s, i in idxs]
#    return df[attr][fidx]

def fast_simple_conc(dfss, idxs, show,
                     metadata=False,
                     add_meta=False, 
                     fname=False,
                     category=False,
                     only_format_match=True,
                     conc=False):
    """
    Fast, simple concordancer, heavily conditional
    to save time.
    """
    if dfss.empty:
        return [], []
        
    import pandas as pd
    conc_res = []
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
    
    # add index as column if need be
    if any(i.endswith('s') for i in show):
        df['ms'] = df.index.labels[0].apply(str)
    if any(i.endswith('i') for i in show):
        df['mi'] = df.index.labels[1].apply(str)
    
    # if the showing can't come straight out of the df, 
    # we can add columns with the necessary information
    if not simple:
        formatted = []
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
                from corpkit.dictionaries.word_transforms import taglemma                
                ser.values = [taglemma.get(piece.lower(), piece.lower())
                              for piece in ser.values]

            # adjmode simply shifts series and index
            if adj:
                #todo: this shifts next sent into previous sent!
                ser = ser.shift(tomove)
                ser = ser.fillna('none')

            # dependent mode produces multiple matches
            # so, we have to make a new dataframe with duplicate indexes
            # todo: what about when there are two dep options?
            if ob in ['d']:
                if only_format_match:
                    df = make_new_for_dep(matches, ser, i)
                else:
                    df = make_new_for_dep(to_proc, ser, i)
            # if not making a new df, just create the col name and add it
            # to our list of series
            else:
                ser.name = adjname + i
                formatted.append(ser)
                
        # now we add the columns to the dataframe 
        if not dmode:
            for l in formatted:
                df[l.name] = l

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

    if not conc:
        # todo: is matches.values faster?
        return list(matches), []

    # do concordancing as fast as possible
    for mid, (s, i) in zip(matches, idxs):
        meta = metadata[s]
        ix = '%d,%d' % (s, i)
        sent = df.loc[s]
        start = ' '.join(sent.loc[:i-1].values)
        end = ' '.join(sent.loc[i+1:].values)
        sname = meta.get('speaker', 'none')
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

    return list(matches), conc_res

def show_this(df, matches, show, metadata, conc=False,
              coref=False, category=False, show_conc_metadata=False, **kwargs):

    only_format_match = kwargs.pop('only_format_match', True)
    ngram_mode = kwargs.get('ngram_mode', True)

    matches = sorted(list(matches))

    # attempt to leave really fast
    if kwargs.get('countmode'):
        return len(matches), {}
    if show in [['mw'], ['mp'], ['ml'], ['mi']] and not conc:
        if show == ['ms']:
            from pandas import Series
            df['s'] = [str(x) for x in df.index.labels[0]]
        if show == ['mi']:
            from pandas import Series
            df['i'] = [str(x) for x in df.index.labels[1]]
        return list(df.loc[matches][show[0][-1]]), {}
    
    # todo: make work for ngram, collocate and coref
    elif all(i[0] in ['m', 'g', '+', '-', 'd'] for i in show):
        return fast_simple_conc(df,
                                matches,
                                show,
                                metadata,
                                show_conc_metadata,
                                kwargs.get('filename', ''),
                                category,
                                only_format_match,
                                conc=conc)

    # everything below here will eventually be removed

    if ngram_mode:
        show = [x.lstrip('n') for x in show]

    # maintaining different show code for conc and non conc for speed
    if not conc:

        def dummy(x, **kwargs):
            return [x]

        def get_gov(line, df=False, attr=False):
            return getattr(df.ix[line.name[0], df.ix[line.name]['g']], attr, 'root')

        objmapping = {'d': get_dependents_of_id,
                      'g': get_governors_of_id,
                      'm': dummy,
                      'h': get_head,
                      'r': get_representative}        

        out = []
        from collections import defaultdict
        conc_out = defaultdict(list)

        for val in show:
            # todo: make into function
            adj, val = determine_adjacent(val)
            if adj:
                if adj[0] == '+':
                    tomove = int(adj[1])
                elif adj[0] == '-':
                    tomove = -int(adj[1])
            obj, attr = val[0], val[-1]
            func = objmapping.get(obj, dummy)
            
            # process everything, if we have to 
            cut_short = False
            if conc and not only_format_match:
                cut_short = True
                newm = list(df.index)
            else:
                newm = matches

            if adj:
                newm = [(s, i+tomove) for s, i in newm]

            mx = [func(idx, df=df) for idx in newm]    
            mx = [item for sublist in mx for item in sublist]
            
            # a pandas object with the token pieces, ready to join together
            # but it contains all tokens if cut_short mode
            gotten_tok_bits = df.loc[mx][attr.replace('x', 'p')].dropna()

            # if gotten_tok_bits contains every token, we can
            # get just the matches from it
            if cut_short or ngram_mode:
                gotten = df.loc[matches]
            else:
                gotten = gotten_tok_bits

            # addactual matches
            out.append(list(gotten))

        formatted = ['/'.join(x) for x in zip(*out)]
        return formatted, {}


    # do we need to format every token?
    process_all = conc and not only_format_match
    if ngram_mode:
        process_all = True

    # tokens that need formatting
    # i.e. just matches, or the whole thing
    if not process_all:
        to_process = df.loc[matches]
    else:
        to_process = df

    # make a series of formatted data
    series = format_toks(to_process, show, df)

    matches = list(series.index)
 
    # generate conc
    conc_lines = make_concx(series, matches, metadata, df,
                             conc, only_format_match=only_format_match,
                             category=category,
                             show_conc_metadata=show_conc_metadata, **kwargs)
    the_ser = list(series)
    if ngram_mode:
        the_ser = list([i[3] for i in conc_lines])
    return the_ser, conc_lines

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
        elif isinstance(criteria, (re._pattern_type, str)):
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

def pipeline(f,
             search,
             show,
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
             **kwargs):
    """a basic pipeline for conll querying---some options still to do"""

    # make file into df, get metadata
    # restrict for speakers
    # remove punct/closed words
    # get indexes of matches for every search
    # remove if not enough matches or exclude is defined
    # show: (bottleneck)
    #
    # issues: get dependents, coref

    all_matches = []
    all_exclude = []

    if from_df is False or from_df is None:
        df = parse_conll(f)
    else:
        df = from_df

    # if working by metadata feature,
    feature = kwargs.pop('by_metadata', False)

    df = cut_df_by_meta(df, just_metadata, skip_metadata)

    if feature:

        if df is None:
            print('Problem reading data from %s.' % f)
            return {}, {}

        resultdict = {}
        concresultdict = {}

        # get all the possible values in the df for the feature of interest
        all_cats = set([i.get(feature, 'none') for i in df._metadata.values()])
        for category in all_cats:
            new_df = process_df_for_speakers(df, df._metadata, category, feature=feature)
            r, c = pipeline(False, search, show,
                            exclude=exclude,
                            searchmode=searchmode,
                            excludemode=excludemode,
                            conc=conc,
                            coref=coref,
                            from_df=new_df,
                            by_metadata=False,
                            category=category,
                            show_conc_metadata=show_conc_metadata,
                            **kwargs)
            resultdict[category] = r
            concresultdict[category] = c
        return resultdict, concresultdict

    if df is None:
        print('Problem reading data from %s.' % f)
        return [], []

    kwargs['ngram_mode'] = any(x.startswith('n') for x in show)

    if isinstance(show, str):
        show = [show]
    show = [fix_show_bit(i) for i in show]

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
        
        # do removals
        all_matches = all_matches.difference(all_exclude)

    # get rid of NA results
    # this thing is slow!
    #all_matches = [i for i in all_matches if i in list(df.index)]
    #all_matches = list(df.loc[all_matches].index)

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
            for k, v in metad.items():
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

