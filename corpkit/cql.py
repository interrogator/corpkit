"""Translating between CQL and corpkit"""

def remake_special(querybit, **kwargs):
    from corpkit.dictionaries import roles, wordlists, processes
    mapped = {'ROLES': roles,
              'WORDLISTS': wordlists,
              'PROCESSES': processes}

    possible = ['ROLES', 'WORDLISTS', 'PROCESSES']
    if any(querybit.startswith(x) for x in possible):
        macro, micro = querybit.split(':', 1)
        return getattr(mapped[macro], micro.lower()).as_regex(**kwargs)
    else:
        return querybit

def process_piece(piece, op='=', **kwargs):
    from corpkit.process import make_name_to_query_dict
    if op not in piece:
        return False, False
    translator = make_name_to_query_dict()
    target, criteria = piece.split(op, 1)
    criteria = criteria.strip('"')
    criteria = remake_special(criteria, **kwargs)
    if '-' in target:
        obj, show = target.split('-', 1)
        show = show.lower()
        if show == 'pos':
            show = 'POS'
        form = '{} {}'.format(obj.title(), show.lower())
    else:
        form = target.title()
        if form == 'Pos':
            form = 'POS'
    return translator.get(form), criteria

def to_corpkit(cstring, **kwargs):
    sdict = {}
    edict = {}
    cstring = cstring.strip('[] ')
    clist = cstring.split(' & ')
    for piece in clist:
        targ, crit = process_piece(piece, op='!=', **kwargs)
        if targ is False and crit is False:
            targ, crit = process_piece(piece, op='=', **kwargs)
            # assume it's just a word without operator
            if targ is False and crit is False:
                sdict['w'] = piece.strip('"')
            else:
                sdict[targ] = crit
        else:
            edict[targ] = crit
    return sdict, edict

def to_cql(dquery, exclude=False, **kwargs):
    qlist = []
    from corpkit.constants import transobjs, transshow
    if exclude:
        operator = '!='
    else:
        operator = '='
    for k, v in dquery.items():
        obj, show = transobjs.get(k[0]), transshow.get(k[1])
        if obj == 'Match':
            form_bit = '{}{}'.format(show.lower(), operator)
        else:
            form_bit = '{}-{}{}'.format(obj.lower(), show.lower(), operator)
        v = getattr(v, 'pattern', v)
        if isinstance(v, list):
            v = as_regex(v, **kwargs)
        form_bit += '"{}"'.format(v)
        qlist.append(form_bit)
    return '[' + ' & '.join(qlist) + ']'


