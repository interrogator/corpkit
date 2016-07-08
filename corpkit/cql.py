"""
Translating between CQL and corpkit

* CQL is extended through the use of wordlists

"""

def remake_special(querybit, customs=False, return_list=False, **kwargs):
    """expand references to wordlists in queries"""
    import re
    from corpkit.dictionaries import roles, wordlists, processes
    from corpkit.other import as_regex
    
    def convert(d):
        """convert dict to named tuple"""
        from collections import namedtuple
        return namedtuple('outputnames', list(d.keys()))(**d)

    if customs:
        customs = convert(customs)

    mapped = {'ROLES': roles,
              'WORDLISTS': wordlists,
              'PROCESSES': processes,
              'LIST': customs,
              'CUSTOM': customs}

    if not any(x in querybit for x in mapped.keys()):
        return querybit
    thereg = r'(' + '|'.join(mapped.keys()) + r'):([A-Z0-9]+)'
    splitup = re.split(thereg, querybit)
    fixed = []
    skipme = []
    for i, bit in enumerate(splitup):
        if i in skipme:
            continue
        if mapped.get(bit):
            att = getattr(mapped[bit], splitup[i+1].lower())
            if hasattr(att, 'words') and att.words:
                att = att.words
            if return_list:
                return att
            att = att.as_regex(**kwargs)
            fixed.append(att)
            skipme.append(i+1)
        else:
            fixed.append(bit)
    return ''.join(fixed)   

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
    cstring = [i.strip('[] ') for i in cstring.split('] [')]
    for i, c in enumerate(cstring):
        c = c.strip('[] ')
        clist = c.split(' & ')
        for piece in clist:
            targ, crit = process_piece(piece, op='!=', **kwargs)
            if targ is False and crit is False:
                
                targ, crit = process_piece(piece, op='=', **kwargs)
                # assume it's just a word without operator
                if targ is False and crit is False:
                    if i > 0:
                        b = '+{}w'.format(i)
                        sdict[b] = piece.strip('"')
                    else:
                        sdict['w'] = piece.strip('"')
                else:
                    if i > 0:
                        targ = '+%d%s' % (i, targ)
                    sdict[targ] = crit
            else:
                if i > 0:
                    targ = '+{}{}'.format(i, targ)
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


