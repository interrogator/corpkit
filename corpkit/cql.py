"""
Translating between CQL and corpkit's native 
"""

def remake_special(querybit, customs=False, return_list=False, **kwargs):
    """
    Expand references to wordlists in queries
    """
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

    if not any(x in querybit.upper() for x in mapped.keys()):
        return querybit
    thereg = r'(?i)(' + '|'.join(mapped.keys()) + r'):([A-Z0-9]+)'
    splitup = re.split(thereg, querybit)
    fixed = []
    skipme = []
    for i, bit in enumerate(splitup):
        if i in skipme:
            continue
        if mapped.get(bit.upper()):
            att = getattr(mapped[bit.upper()], splitup[i+1].lower())
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

def parse_quant(quant):
    """
    Normalise quanitifers
    """
    if quant.startswith('}{'):
        quant = quant.strip('}{ ')
        if ',' in quant:
            return quant.replace(',', ':')
        else:
            return quant
    return quant

def process_piece(piece, op='=', quant=False, **kwargs):
    """
    Make a single search obj and value
    """

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
        if show == 'deprel':
            show = 'Function'
        elif show == 'pos':
            show = 'POS'
        form = '{} {}'.format(obj.title(), show.lower())
    else:
        form = target.title()
        if form == 'Deprel':
            form = 'Function'
        elif form == 'Pos':
            form = 'POS'
    return translator.get(form), criteria


def tokenise_cql(query):
    """
    Take a cql query and return a list of tuples
    which is token, quantifer
    """
    quantstarts = ['+', '{', ',', '}', '?', '*']
    tokens = ''
    count = 0
    for i, t in enumerate(query):
        if t == '[':
            count += 1
        if t == ']':
            count -= 1
        if count != 0:
            tokens += t
        else:
            if count == 0 and t == ']':
                try:
                    if not query[i+1].isspace():
                        tokens += t
                        tokens += '\n'
                    else:
                        tokens += t
                except IndexError:
                    pass
            # separate on space between tokens
            elif t.isspace():
                tokens += '\n'
            # if part of quantifier
            if t in quantstarts or t.isdigit():
                tokens += t
    tokens = tokens.split('\n')
    skips = []
    out = []
    for i, t in enumerate(tokens):
        if i in skips:
            continue
        # get next token
        try:
            nextt = tokens[i+1]
        except IndexError:
            # if it's the last token, if not quantifier, add it
            if not t:
                continue
            if t[0] not in quantstarts:
                out.append([t, False])
                continue
        if any(nextt.startswith(x) for x in quantstarts):
            out.append([t, nextt])
            skips.append(i+1)
        else:
            out.append([t, False])
    return out

def to_corpkit(cstring, **kwargs):
    """
    Turn CQL into corpkit (two dict) format
    """
    sdict = {}
    edict = {}
    cstring = tokenise_cql(cstring)
    for i, (c, q) in enumerate(cstring):
        if q:
            i = parse_quant(q)
        c = c.strip('[] ')
        clist = c.split(' & ')
        for piece in clist:
            targ, crit = process_piece(piece, op='!=', quant=q, **kwargs)
            if targ is False and crit is False:
                targ, crit = process_piece(piece, op='=', quant=q, **kwargs)
                # assume it's just a word without operator
                if targ is False and crit is False:
                    if i > 0 or isinstance(i, str):
                        b = '+{}w'.format(i)
                        sdict[b] = piece.strip('"')
                    else:
                        sdict['w'] = piece.strip('"')
                else:
                    if i > 0 or isinstance(i, str):
                        targ = '+%s%s' % (str(i), targ)
                    sdict[targ] = crit
            else:
                if i > 0 or isinstance(i, str):
                    targ = '+{}{}'.format(i, targ)
                edict[targ] = crit

    return sdict, edict

def to_cql(dquery, exclude=False, **kwargs):
    """
    Turn dictionary query into cql format
    """
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


