"""
corpkit: process CONLL formatted data
"""

from corpkit.matches import Token, Count

def parse_conll(f,
                first_time=False,
                just_meta=False,
                usecols=None,
                index_col=['i'],
                corp_folder=False,
                corpus_name=False):
    """
    Make a pandas.DataFrame with metadata from a CONLL-U file
    
    Args:
        f (str): Filepath
        first_time (bool, optional): If True, add in sent index
        just_meta (bool, optional): Return only a metadata `dict`
        usecols (None, optional): Which columns must be parsed by pandas.read_csv
    
    Returns:
        pandas.DataFrame: DataFrame containing tokens and a ._metadata attribute
    """
    import pandas as pd
    import os
    import re
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    from collections import defaultdict

    # go to corpkit.constants to modify the order of columns if yours are different
    from corpkit.constants import CONLL_COLUMNS as head

    with open(f, 'r') as fo:
        data = fo.read().strip('\n')

    splitdata = []
    metadata = {}
    sents = data.split('\n\n')  
    basedict = defaultdict(set)
    fname = os.path.basename(f)
    fname = re.sub(r'(-[0-9][0-9][0-9]|).txt.conll$', '', fname)

    basedict['file'].add(fname)
    if corp_folder:
        basedict['folder'].add(corp_folder)
    if corpus_name:
        basedict['corpus'].add(corpus_name)

    for count, sent in enumerate(sents, start=1):
        metadata[count] = basedict.copy()
        for line in sent.split('\n'):
            if line and not line.startswith('#') \
                and not just_meta:
                continue
            else:
                line = line.lstrip('# ')
                if '=' in line:
                    field, val = line.split('=', 1)
                    if field == 'parse':
                        metadata[count][field].add(val)
                    else:
                        for x in val.split(','):
                            metadata[count][field].add(x)
        metadata[count] = {k: ','.join(v) for k, v in metadata[count].items()}
    if just_meta:
        return metadata

    # happens with empty files
    if not metadata:
        return

    try:
        df = pd.read_csv(f, sep='\t', header=None, na_filter=False, memory_map=True, comment="#",
                     names=head, usecols=None, index_col=index_col, engine='c')
    except KeyError:
        return
    c = 0
    newlev = []
    for i in df.index:
        try:
            if int(i) == 1:
                c += 1
        except:
            pass
        newlev.append((c, i))
    ix = pd.MultiIndex.from_tuples(newlev)
    df.index = ix
    df._metadata = metadata
    return df

def search_this(df, obj, attrib, pattern, adjacent=False, coref=False, corpus=False, matches=False,
                subcorpora=False, metadata=False, fobj=False, corpus_name=False, conc=True):
    """
    Search the dataframe for a single criterion

    :return: a defaultdict with subcorpora as keys and results as values
    """
    import re
   
    # if searching by head, they need to be heads
    if obj == 'h':
        df = df.loc[df['c'].endswith('*')]

    out = []

    # cut down to just tokens with matching attr
    # but, if the pattern is 'any', don't bother
    if attrib in ['s', 'i']:
        ix = df.index
        df = df.reset_index()
        attrib = 'level_0' if attrib == 's' else 'level_1'
        df['level_0'] = df['level_0'].astype(str)
        df['level_1'] = df['level_1'].astype(str)
        df.index = ix

    if hasattr(pattern, 'pattern') and pattern.pattern == r'.*':
        xmatches = df
    else:
        xmatches = df[df[attrib].fillna('').str.contains(pattern)]

    tokks = xmatches.apply(row_tok_apply, axis=1, df=df, fobj=fobj, metadata=metadata, matches=matches, conc=conc)
    tokks = tokks.values

    if coref:
        tokks = tokks.corefs()
    #else:
    #    the_tokens = tokks

    for tok in tokks:

        if obj == 'g':
            for depe in tok.dependents:
                out.append(depe)

        if obj == 'a':
            for depe in tok.descendents:
                out.append(depe)

        elif obj == 'd':
            out.append(tok.governor)

        elif obj == 'o':
            for govo in tok.ancestors:
                out.append(govo)

        elif obj == 'm':
            out.append(tok)

        elif obj == 'h':
            out.append(tok.head())

        elif obj == 'r':
            out.append(tok(representative()))

    return out
    
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

def p_series_to_x_series(val):
    return taglemma.get(val.lower(), val.lower())

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
    """
    Figure out if we're doing an adjacent location, get the co-ordinates
    and return them and the stripped original
    """
    if original[0] in ['+', '-']:
        adj = (original[0], original[1:-2])
        original = original[-2:]
    else:
        adj = False
    return adj, original

def cut_df_by_metadata(df, metadata, criteria, coref=False,
                            feature='speaker', method='just'):
    """
    Keep or remove parts of the DataFrame based on metadata criteria
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
        if isinstance(criteria, (list, set, tuple)):
            criteria = [i.lower() for i in criteria]
            if method == 'just':
                if any(i.lower() in criteria for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
            elif method == 'skip':
                if not any(i in criteria for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
        elif isinstance(criteria, (re._pattern_type, STRINGTYPE)):
            if method == 'just':
                if any(re.search(criteria, i, re.IGNORECASE) for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data
            elif method == 'skip':
                if not any(re.search(criteria, i, re.IGNORECASE) for i in lst_met_vl):
                    good_sents.append(sentid)
                    new_metadata[sentid] = data

    df = df.loc[good_sents]
    df = df.fillna('')
    df._metadata = new_metadata
    return df

def cut_df_by_meta(df, just, skip):
    """
    Reshape a DataFrame based on filters
    """
    if df is not None:
        if just:
            for k, v in just.items():
                df = cut_df_by_metadata(df, df._metadata, v, feature=k)
        if skip:
            for k, v in skip.items():
                df = cut_df_by_metadata(df, df._metadata, v, feature=k, method='skip')
    return df

def custom_tgrep(pattern, metadata, search_leaves=True):
    """
    Return the tree nodes in the trees which match the given pattern.
    :param pattern: a tgrep search pattern
    :type pattern: str or output of tgrep_compile()
    :param trees: a sequence of NLTK trees (usually ParentedTrees)
    :type trees: iter(ParentedTree) or iter(Tree)
    :param search_leaves: whether ot return matching leaf nodes
    :type search_leaves: bool
    :rtype: iter(tree nodes)
    """
    from nltk.tree import ParentedTree
    from corpkit.constants import STRINGTYPE

    if isinstance(pattern, (STRINGTYPE, bool)):
        from nltk.tgrep import tgrep_compile
        pattern = tgrep_compile(pattern)

    for k, v in metadata.items():
        tree = v.get('parse', None)
        if not tree:
            yield []
        tree = ParentedTree.fromstring(tree)
        root_position = tree.root().treepositions(order='leaves')
        try:
            if search_leaves:
                positions = tree.treepositions()
            else:
                positions = treepositions_no_leaves(tree)
            yield [(root_position, position, k, v) for position in positions if pattern(tree[position])]
        except AttributeError:
            yield []

def tgrep_counter(df, pattern, search_leaves=True, parent=False, metadata=False, fobj=False, root=False):
    from nltk.tree import ParentedTree
    from corpkit.constants import STRINGTYPE
    from collections import Counter
    from corpkit.matches import Token, Count, Tokens
    from corpkit.dictionaries.process_types import processes
    import re

    res = []
    procr = []

    single = False
    if not isinstance(pattern, dict):
        pattern = {'noname': pattern}
        single = True
    else:
        procq = pattern.pop('Processes', None)
        procr = tgrep_searcher(df, metadata, compiled_tgrep=procq, parent=parent, fobj=fobj)

    if isinstance(pattern, (STRINGTYPE, bool)):
        from nltk.tgrep import tgrep_compile
        pattern = tgrep_compile(pattern)

    for k, v in metadata.items():
        
        #if root:
        #    root.update()
        
        tree = v.get('parse', None)
        if not tree:
            yield []
        tree = ParentedTree.fromstring(tree)
        root_position = tree.root().treepositions(order='leaves')

        try:
            if search_leaves:
                positions = tree.treepositions()
            else:
                positions = treepositions_no_leaves(tree)
        except AttributeError:
            yield []
        
        for name, pat in pattern.items():
            try:
                s = sum([1 for position in positions if pat(tree[position])])
            except AttributeError:
                s = 0
            i = 'x'
            res.append(Count(k, i, name, metadata[k], s))

        for ptype in ['mental', 'relational', 'verbal']:
            nname = ptype.title() + ' processes'
            reg = getattr(processes, ptype).lemmata.as_regex(boundaries='l')
            count = len([i for i in procr if re.search(reg, i[0].l)])
            res.append(Count(k, 'x', nname, num=count, metadata=metadata))

        #res.append(Count(s, 'x', 'Sentences', metadata=metadata, parent=parent, num=len(set(df.index.labels[0]))))
        sent = df.loc[k]
        res.append(Count(s, 'x', 'Passives', metadata=metadata, parent=parent, num=len(sent[sent['f'] == 'nsubjpass'])))
        res.append(Count(s, 'x', 'Tokens', metadata=metadata, parent=parent, num=len(sent)))
        w = len([w for w in list(sent['w']) if w and not ispunct(str(w))])
        res.append(Count(s, 'x', 'Words', metadata=metadata, parent=parent, num=w))
        res.append(Count(s, 'x', 'Characters', metadata=metadata, parent=parent, num=sum([len(str(w)) for w in list(sent['w']) if w])))
        oc = sum([1 for x in list(sent['p']) if x and x[0] in ['N', 'J', 'V', 'R']])
        res.append(Count(s, 'x', 'Open class', metadata=metadata, parent=parent, num=oc))
        res.append(Count(s, 'x', 'Punctuation', metadata=metadata, parent=parent, num=len(sent) - w))
        res.append(Count(s, 'x', 'Closed class', metadata=metadata, parent=parent, num=w - oc))

    if single:
        res = res.pop('noname')

    return res

def tgrep_searcher(df, metadata, compiled_tgrep=False, parent=False, fobj=False, **kwargs):
    
    #from nltk.tgrep import tgrep_nodes
    #trees = [ParentedTree.fromstring(i.get('parse', '')) for i in metadata.values()]
    from corpkit.matches import Token, Tokens
    out = []
    all_matches = custom_tgrep(compiled_tgrep, metadata)
    for sent_matches in all_matches:
        if not sent_matches:
            continue
        for all_leaf_positions, match_position, s, meta in sent_matches:
            #if i == 1:
            #    all_leaf_positions = match.root().treepositions(order='leaves')
            #match_position = match.treeposition()
            ixs = [e for e, x in enumerate(all_leaf_positions, start=1) \
                   if x[:len(match_position)] == match_position]
            span = []
            for ix in ixs:
                try:
                    rowd = df.loc[s, ix].to_dict()
                except TypeError:
                    continue
                t = Token(ix, df, s, fobj, metadata=metadata[s], parent=parent, **rowd)
                span.append(t)
            if span:
                tkspn = Tokens(span, s, df, match_position, metadata=metadata[s])
                out.append(tkspn)
    return out

def ispunct(s):
    import string
    return all(c in string.punctuation for c in s)

def get_stats(df=False, metadata=False, root=False, parent=False, fobj=False, compiled_tgrep=False, **kwargs):
    """
    Get general statistics for a DataFrame
    """
    import re
    from corpkit.dictionaries.process_types import processes
    from collections import Counter, defaultdict

    # check calls on this
    tregex_qs = make_compiled_statsqueries()
    return list(tgrep_counter(df, pattern=tregex_qs, search_leaves=True, fobj=fobj,
                                parent=parent, metadata=metadata, root=root))

def row_tok_apply(row, df=False, fobj=False, metadata=False, matches=False, conc=True):
    from corpkit.matches import Token

    t = Token(row.name[1], df, row.name[0], fobj, metadata[row.name[0]], matches, conc=conc, **row.to_dict())
    return t

def pipeline(fobj=False,
             search=False,
             show=False,
             exclude=False,
             searchmode='all',
             excludemode='any',
             conc=True,
             coref=False,
             from_df=False,
             just=False,
             skip=False,
             show_conc_metadata=False,
             lem_instance=False,
             subcorpora=False,
             corpus_name=False,
             corpus=False,
             matches=False,
             multiprocess=False,
             compiled_tgrep=False,
             **kwargs):
    """
    A basic pipeline for conll querying---some options still to do
    """
    from collections import Counter
    from corpkit.matches import Token

    all_matches = []
    all_exclude = []
    all_res = []

    # todo: this could become obsolete
    corp_folder = False
    if getattr(fobj, 'parent', False):
        corp_folder = fobj.parent

    df = parse_conll(fobj.path, usecols=kwargs.get('usecols'), corpus_name=corpus_name, corp_folder=corp_folder)

    # can fail here if df is none
    if df is None:
        print('Problem reading data from %s.' % fobj.path)
        return [], []
    metadata = df._metadata

    # determine which subsearcher to use
    searcher = pipeline
    if 'v' in search:
        searcher = get_stats
    if 't' in search:
        searcher = tgrep_searcher

    # first column should always be strings!
    try:
        df['w'].str
    except AttributeError:
        raise AttributeError("CONLL data doesn't match expectations. " \
                             "Try the corpus.conll_conform() method to " \
                             "convert the corpus to the latest format.")

    # strip out punctuation by regex
    if kwargs.get('no_punct', True):
        df = df[df['w'].fillna('').str.contains(kwargs.get('is_a_word', r'[A-Za-z0-9]'))]
    
        # remove brackets --- could it be done in one regex?
        df = df[~df['w'].str.contains(r'^-.*B-$')]

    if kwargs.get('no_closed'):
        from corpkit.dictionaries import wordlists
        crit = wordlists.closedclass.as_regex(boundaries='l', case_sensitive=False)
        df = df[~df['w'].str.contains(crit)]

    # todo: get these two to use same call sig
    if searcher in [get_stats, tgrep_searcher]:
        return searcher(df, metadata, root=kwargs.pop('root', False), compiled_tgrep=compiled_tgrep, parent=matches, fobj=fobj, **kwargs)
    
    # do no searching if 'any' is requested
    # doesn't work?
    if len(search) == 1 and list(search.keys())[0] == 'mw' \
                        and hasattr(list(search.values())[0], 'pattern') \
                        and list(search.values())[0].pattern == r'.*':
        tokks = df.apply(row_tok_apply, axis=1, df=df, fobj=fobj, metadata=metadata, matches=matches, conc=conc)
        all_res = list(tokks.values)
    else:
        for k, v in search.items():
            adj, k = determine_adjacent(k)
            all_res += search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref, subcorpora=subcorpora, metadata=metadata,
                                   fobj=fobj, corpus_name=corpus_name, corpus=corpus, matches=matches, conc=conc)
        if searchmode == 'all' and len(search) > 1:
            all_res = sorted([k for k, v in Counter(all_res).items() if v == len(search)])

    if exclude:
        for k, v in exclude.items():
            adj, k = determine_adjacent(k)
            all_exclude += search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref, subcorpora=subcorpora, metadata=metadata,
                                   fobj=fobj, corpus_name=corpus_name, corpus=corpus, matches=matches, conc=conc)
        #all_exclude = remove_by_mode(all_exclude, excludemode, exclude)
        if excludemode == 'all':
            all_exclude = set(k for k, v in Counter(all_exclude).items() if v == len(search))
        else:
            all_exclude = set(all_exclude)
        
        all_res = sorted(list(set(all_res).difference(all_exclude)))

    if multiprocess:
        for i in all_res:
            del i.parent

    return all_res

    out, conc_out = show_this(df, all_res, show, metadata, conc, 
                              coref=coref, category=category, 
                              show_conc_metadata=show_conc_metadata,
                              **kwargs)

    return out, conc_out

def load_raw_data(f):
    """
    Loads the stripped and raw versions of a parsed file
    """
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
                          metadata=False,
                          just_files=False):
    """
    take json corenlp output and convert to conll, with
    dependents, speaker ids and so on added.

    Path is for the parsed corpus, or a list of files within a parsed corpus
    Might need to fix if outname used?
    """

    import json
    import re
    from corpkit.build import get_filepaths
    from corpkit.constants import CORENLP_VERSION, OPENER
    
    # todo: stabilise this
    #if CORENLP_VERSION == '3.7.0':
    #    coldeps = 'enhancedPlusPlusDependencies'
    #else:
    #    coldeps = 'collapsed-ccprocessed-dependencies'

    print('Converting files to CONLL-U...')

    if just_files:
        files = just_files
    else:
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
        with OPENER(f, 'r') as fo:
            #try:

            try:
                data = json.load(fo)
            except ValueError:
                continue
            # todo: differentiate between json errors
            # rsc corpus had one json file with an error
            # outputted by corenlp, and the conversion
            # failed silently here
            #except ValueError:
            #    continue

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
                            
            # currently there is no standard for sent_id, so i'm leaving it out, but
            # if https://github.com/UniversalDependencies/docs/issues/273 is updated
            # then i could switch it back
            #output = '# sent_id %d\n# parse=%s\n' % (idx, tree)
            output = '# parse=%s\n' % tree
            for k, v in sorted(metad.items()):
                output += '# %s=%s\n' % (k, v)
            for token in sent['tokens']:
                index = str(token['index'])
                # this got a stopiteration on rsc data
                governor, func = next(((i['governor'], i['dep']) \
                                         for i in sent.get('enhancedPlusPlusDependencies',
                                                  sent.get('collapsed-ccprocessed-dependencies')) \
                                         if i['dependent'] == int(index)), ('_', '_'))
                if governor is '_':
                    depends = False
                else:
                    depends = [str(i['dependent']) for i in sent.get('enhancedPlusPlusDependencies',
                               sent.get('collapsed-ccprocessed-dependencies')) if i['governor'] == int(index)]
                if not depends:
                    depends = '0'
                #offsets = '%d,%d' % (token['characterOffsetBegin'], token['characterOffsetEnd'])
                line = [index,
                        token['word'],
                        token['lemma'],
                        token['pos'],
                        token.get('ner', '_'),
                        '_', # this is morphology, which is unannotated always, but here to conform to conll u
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
                
                output += '\t'.join(line).replace('#', '-hash-').replace('/', '-slash-') + '\n'
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

def make_compiled_statsqueries():
    from nltk.tgrep import tgrep_compile
    tregex_qs = {#'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S '\
                 #'!$-- VP !$ VP)) !<< (/\?/ !< __) !<<\' /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                 'Open interrogative': r"ROOT < SBARQ <<' (/\?/ !< __)", 
                 #'Closed interrogative': r"ROOT < ((SQ < (NP $, VP)) << (/\?/ !< __)) | < ((/S|SBAR/ < (VP $, NP)) <<' (/\?/ !< __)))",
                 'Unmodalised declarative': r"ROOT < (S < (/NP|SBAR|VP/ $, (VP !< MD)))",
                 'Modalised declarative': r"ROOT < (S < (/NP|SBAR|VP/ $, (VP < MD)))",
                 'Clauses': r"/^S/ < __",
                 'Interrogative': r"ROOT << (/\?/ !< __)",
                 'Processes': r"/VB.*/ >-1 VP"}
    out = {}
    for k, v in sorted(tregex_qs.items()):
        out[k] = tgrep_compile(v)
    return out