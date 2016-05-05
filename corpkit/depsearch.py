from __future__ import print_function

def dep_searcher(sents,
                 search,
                 show='w',
                 dep_type='collapsed-ccprocessed-dependencies',
                 regex_nonword_filter=r'[A-Za-z0-9:_]',
                 do_concordancing=False,
                 exclude=False,
                 excludemode='any',
                 searchmode='all',
                 lemmatise=False,
                 case_sensitive=False,
                 progbar=False,
                 only_format_match=False,
                 speaker=False,
                 gramsize=2,
                 nopunct=True,
                 split_contractions=False,
                 window=2):
    import re
    from corenlp_xml.document import Document
    from collections import Counter
    from build import flatten_treestring
    from process import filtermaker, animator, get_deps

    nonword = re.compile(regex_nonword_filter)


    if any(x.startswith('n') for x in show) and any(not x.startswith('n') for x in show):
        raise ValueError("Can't mix n-gram and non-ngram show values.")
    """
    search corenlp dependency parse
    1. search for 'search' keyword arg
       governor
       dependent
       function
       pos
       lemma
       word
       index
       etc

    2. exclude entries if need be, using same method as search

    3. return '/'-sep list of 'show' keyword arg, or conc lines:
       governor
       dependent
       function
       pos
       lemma
       word
       index
       distance
       etc
       
       ... or just return int count.
       """

    def distancer(lks, lk):
        "determine number of jumps to root"      
        c = 0
        # get the gov index, stop when it's zero
        root_found = False
        while not root_found:
            if c == 0:
                try:
                    link_to_check = next(i for i in lks if i.dependent.idx == lk.id)
                except StopIteration:
                    root_found = True
                    break
                #link_to_check = lk
            gov_index = link_to_check.governor.idx
            if gov_index == 0:
                root_found = True
            else:
                if c > 29:
                    root_found = True
                    break
                link_to_check = [l for l in lks if l.dependent.idx == gov_index]
                if len(link_to_check) > 0:
                    link_to_check = link_to_check[0]
                else:
                    break
                c += 1
        if c < 30:
            return c

    def get_matches_from_sent(s, search, deps = False, tokens = False, 
        dep_type = 'basic-dependencies', mode = 'all'):
        """process a sentence object, returning matching tok ids"""
        from process import get_deps
        from dictionaries.process_types import Wordlist
        import re
        lks = []
        if not deps:
            deps = get_deps(s, dep_type)
        if not tokens:
            tokens = s.tokens

        for opt, pat in list(search.items()):
            if type(pat) == dict:
                del search[opt]
                for k, v in list(pat.items()):
                    if k != 'w':
                        search[opt + k] = v
                    else:
                        search[opt] = v

        for opt, pat in list(search.items()):
            if type(pat) == Wordlist:
                pat = list(pat)
            if pat == 'any':
                pat = re.compile(r'.*')
            elif type(pat) == list:
                if all(type(x) == int for x in pat):
                    pat = [str(x) for x in pat]
                pat = filtermaker(pat, case_sensitive = case_sensitive)
            else:
                if case_sensitive:
                    pat = re.compile(pat)
                else:
                    pat = re.compile(pat, re.IGNORECASE)
            if opt == 'g':
                got = []
                for l in deps.links:
                    if re.search(pat, l.governor.text):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gf':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        gov_index = l.dependent.idx
                        for l2 in deps.links:
                            if l2.governor.idx == gov_index:
                                got.append(s.get_token_by_id(l2.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'df':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        extra_crit = search.get('d2f')
                        if extra_crit:
                            if type(extra_crit) == Wordlist:
                                extra_crit = list(extra_crit)
                            if type(extra_crit) == list:
                                from other import as_regex
                                extra_crit = as_regex(extra_crit, case_sensitive = case_sensitive)                            
                            for b in deps.links:
                                if re.search(extra_crit, b.type):
                                    if l.governor.idx == b.governor.idx:
                                        got.append(s.get_token_by_id(l.governor.idx))
                        else:
                            got.append(s.get_token_by_id(l.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gl':
                got = []
                for tok in tokens:
                    if tok.lemma:
                        se = tok.lemma
                    elif tok.word:
                        se = tok.word
                    else:
                        continue
                    if re.search(pat, se):
                        for i in deps.links:
                            if i.governor.idx == tok.id:
                                got.append(s.get_token_by_id(i.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.governor.idx == tok.id:
                                got.append(s.get_token_by_id(i.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'dl':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.lemma):
                        for i in deps.links:
                            if i.dependent.idx == tok.id:
                                extra_crit = search.get('d2l')
                                if extra_crit:
                                    if isinstance(extra_crit, Wordlist):
                                        extra_crit = list(extra_crit)
                                    if isinstance(extra_crit, list):
                                        from corpkit.other import as_regex
                                        extra_crit = as_regex(extra_crit, case_sensitive = case_sensitive)                            
                                    for b in tokens:
                                        if not re.search(extra_crit, b.lemma):
                                            continue
                                        thelink = next(x for x in deps.links \
                                                       if x.dependent.idx == b.id)
                                        if thelink.governor.idx == i.governor.idx:
                                            got.append(s.get_token_by_id(i.governor.idx))
                                else:
                                    got.append(s.get_token_by_id(i.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'dp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.dependent.idx == tok.id:
                                got.append(s.get_token_by_id(i.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)

            elif opt == 'd':
                got = []
                for l in deps.links:
                    if re.search(pat, l.dependent.text):
                        got.append(s.get_token_by_id(l.governor.idx))

                got = set(got)
                for i in got:
                    lks.append(i)

            elif opt == 'f':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'p':
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        lks.append(tok)
            elif opt == 'pl':
                for tok in tokens:
                    from corpkit.dictionaries.word_transforms import taglemma
                    postag = tok.pos
                    stemmedtag = taglemma.get(postag.lower(), postag.lower())
                    if re.search(pat, stemmedtag):
                        lks.append(tok)
            elif opt == 'l':
                for tok in tokens:
                    if tok.lemma:
                        se = tok.lemma
                    elif tok.word:
                        se = tok.word
                    else:
                        continue
                    if re.search(pat, se):
                        lks.append(tok)
            elif opt == 'w':
                for tok in tokens:
                    if re.search(pat, tok.word):
                        lks.append(tok)
            elif opt == 'i':
                for tok in tokens:
                    if re.search(pat, str(tok.id)):
                        lks.append(tok)
            elif opt == 'r':
                got = []
                for tok in tokens:
                    dist = distancer(deps.links, tok)
                    if dist is not None and dist is not False:
                        try:
                            if int(dist) == int(pat):
                                lks.append(tok)

                        except TypeError:
                            if re.search(pat, str(dist)):
                                lks.append(tok)

        if mode == 'all':
            from collections import Counter
            counted = Counter(lks)
            must_contain = len(search)
            must_contain -= len([n for n in search.keys() if '2' in n])
            lks = [k for k, v in counted.items() if v >= must_contain]
        return lks

    result = []
    conc_result = []
    numdone = 0

    for s in sents:
        numdone += 1
        deps = get_deps(s, dep_type)
        tokens = s.tokens
        lks = get_matches_from_sent(s, search, deps, tokens, dep_type, mode = searchmode)

        #if not concordancing:
        #    lks = list(set([x for x in lks if x and re.search(regex_nonword_filter, x.word)]))

        if exclude is not False:
            to_remove = get_matches_from_sent(s, exclude, deps, tokens, dep_type, mode = excludemode)

            for i in to_remove:
                try:
                    lks.remove(i)
                except ValueError:
                    pass

        if progbar:
            tstr = '%d/%d' % (numdone, len(sents))
            animator(progbar, numdone, tstr)

        if 'c' in show:
            result.append(len(lks))
            continue

        # if ngramming, repeat by gramsize
        #morelks = []
        #if any(x.startswith('n') for x in show):
        #    for i in range(gramsize):
        #        for l in lks:
        #            morelks.append(l)
        #lks = morelks
        repeats = 1
        if any(x.startswith('n') for x in show):
            repeats = gramsize

        if do_concordancing:
            if split_contractions is False and 'n' in show:
                import warnings
                warnings.warn("Concordancer cannot unsplit contractions for n-grams yet, sorry.")
            for lk in lks: # for each concordance middle part
                # this loop is for ngramming
                for repeat in range(repeats):
                    if nopunct:
                        stokens = [i for i in s.tokens if re.search(nonword, i.word)]
                    else:
                        stokens = s.tokens         
                    one_result = []
                    if not lk:
                        continue
                    # get the index of the match
                    windex = (int(lk.id) - 1) - repeat
                    if any(x.startswith('n') for x in show):
                        windex2 = windex + gramsize
                    else:
                        windex2 = windex + 1
                    if windex < 0:
                        continue
                    if windex2 > len(s.tokens):
                        continue
                    speakr = s.speakername
                    if not speakr:
                        speakr = ''
                    # begin building line with speaker first
                    conc_line = [speakr]
                    # format a single word correctly
                    if only_format_match:
                        start = ' '.join(t.word for index, t in enumerate(s.tokens) \
                            if index < windex)
                        end = ' '.join(t.word for index, t in enumerate(s.tokens) \
                            if index > windex2 - 1)
                        s.tokens = [s.get_token_by_id(lk.id)]
                    for tok in stokens:

                        single_wd = {}
                        intermediate_result = []
                        if 'w' in show:
                            single_wd['w'] = tok.word
                        if 'l' in show:
                            from corpkit.dictionaries.word_transforms import wordlist
                            lem = wordlist.get(tok.lemma, tok.lemma)
                            single_wd['l'] = lem
                        if 'p' in show:
                            single_wd['p'] = tok.pos

                        if 'pl' in show:
                            single_wd['pl'] = lk.pos
                            from corpkit.dictionaries.word_transforms import taglemma
                            single_wd['pl'] = taglemma.get(lk.pos.lower(), lk.pos.lower())
                            # needed?
                            if not single_wd['pl']:
                                single_wd['pl'] == 'none'

                        if 'r' in show:
                            all_lks = [l for l in deps.links]
                            distance = distancer(all_lks, tok)
                            if distance:
                                single_wd['r'] = str(distance)
                            else:
                                single_wd['r'] = '0'
                        if 'f' in show:
                            for lin in deps.links:
                                single_wd['f'] = '.'
                                if tok.id == lin.dependent.idx:
                                    single_wd['f'] = lin.type
                                    break

                        if 'i' in show:
                            single_wd['i'] = str(tok.id)

                        if any(x.startswith('g') for x in show):
                            thegovid = next((q.governor.idx for q in deps.links \
                                            if q.dependent.idx == tok.id), False)
                            govtok = False
                            if thegovid is not False:
                                govtok = s.get_token_by_id(thegovid)
                                
                            if 'g' in show:
                                if govtok:
                                    single_wd['g'] = govtok.word
                                else:
                                    single_wd['g'] = 'none'
                            if 'gl' in show:
                                if govtok:
                                    single_wd['gl'] = govtok.lemma
                                else: 
                                    single_wd['gl'] = 'none'
                            if 'gp' in show:
                                if govtok:
                                    single_wd['gp'] = govtok.pos
                                else: 
                                    single_wd['gp'] = 'none'

                            if 'gf' in show:
                                if govtok:
                                    single_wd['gf'] = next(x.type for x in deps.links \
                                                if x.dependent.idx == thegovid)
                                else: 
                                    single_wd['gf'] = 'none'

                        if any(x.startswith('d') for x in show):
                            thedepid = next((q.dependent.idx for q in deps.links \
                                            if q.governor.idx == tok.id), False)

                            deptok = False
                            if thedepid is not False:
                                deptok = s.get_token_by_id(thedepid)

                            if 'd' in show:
                                if thedepid:
                                    single_wd['d'] = deptok.word
                                else: 
                                    single_wd['d'] = 'none'

                            if 'dl' in show:
                                if thedepid:
                                    single_wd['dl'] = deptok.lemma
                                else: 
                                    single_wd['dl'] = 'none'
                            if 'dp' in show:
                                if thedepid:
                                    single_wd['dp'] = deptok.pos
                                else: 
                                    single_wd['dp'] = 'none'
                            if 'df' in show:
                                if thedepid:
                                    single_wd['df'] = next(x.type for x in deps.links \
                                    if x.dependent.idx == thedepid)
                                else: 
                                    single_wd['df'] = 'none'

                        
                        if any(x.startswith('n') for x in show) or \
                            any(x.startswith('b') for x in show):
                            let = show[0][0]
                            if let in show:
                                single_wd[let] = tok.word
                            if let + 'l' in show:
                                from corpkit.dictionaries.word_transforms import wordlist
                                lem = wordlist.get(tok.lemma, tok.lemma)
                                single_wd[let + 'l'] = lem
                            if let + 'p' in show:
                                single_wd[let + 'p'] = tok.pos
                            if let + 'pl' in show:
                                single_wd[let + 'pl'] = lk.pos
                                from corpkit.dictionaries.word_transforms import taglemma
                                single_wd[let + 'pl'] = taglemma.get(lk.pos.lower(), lk.pos.lower())
                                # ?
                                if not single_wd[let + 'pl']:
                                    single_wd[let + 'pl'] == 'none'

                        for i in show:
                            intermediate_result.append(single_wd[i])
                        intermediate_result = [i.replace('/', '-slash-').encode('utf-8', errors = 'ignore') for i in intermediate_result]
                        one_result.append('/'.join(intermediate_result))

                    # now we have formatted tokens as a list. we need to split
                    # it into start, middle and end
                    if not only_format_match:
                        start = ' '.join(w for index, w in enumerate(one_result) if index < windex)
                        end = ' '.join(w for index, w in enumerate(one_result) if index > windex2  - 1)
                        middle = ' '.join(w for index, w in enumerate(one_result[windex:windex2]))
                    else:
                        #?
                        middle = one_result[0]

                    for bit in start, middle, end:
                        conc_line.append(bit)
                    conc_result.append(conc_line)

        # figure out what to show
        for lk in lks:
            single_result = {}
            if not lk:
                continue
            if 'w' in show:
                single_result['w'] = 'none'
                if lemmatise:
                    single_result['w'] = lk.lemma
                else:
                    single_result['w'] = lk.word
            if 'l' in show:
                from corpkit.dictionaries.word_transforms import wordlist
                lem = wordlist.get(lk.lemma, lk.lemma)
                single_result['l'] = lem
            if 'p' in show:
                single_result['p'] = 'none'
                postag = lk.pos
                if lemmatise:
                    from corpkit.dictionaries.word_transforms import taglemma
                    single_result['p'] = taglemma.get(postag.lower(), postag.lower())
                else:
                    single_result['p'] = postag
                if not single_result['p']:
                    single_result['p'] == 'none'

            if 'pl' in show:
                single_result['pl'] = 'none'
                postag = lk.pos
                from dictionaries.word_transforms import taglemma
                single_result['pl'] = taglemma.get(postag.lower(), postag.lower())

            if 'f' in show:
                single_result['f'] = 'none'
                for i in deps.links:
                    if i.dependent.idx == lk.id:
                        single_result['f'] = i.type.rstrip(',')
                        break
                if single_result['f'] == '':
                    single_result['f'] = 'root'

            if 'g' in show:
                single_result['g'] = 'none'
                for i in deps.links:
                    if i.dependent.idx == lk.id:
                        if s.get_token_by_id(i.governor.idx):
                            if lemmatise:                          
                                single_result['g'] = s.get_token_by_id(i.governor.idx).lemma
                            else:
                                single_result['g'] = i.governor.text
                        else:
                            single_result['g'] = 'root'
                        break

            if 'd' in show:
                single_result['d'] = 'none'
                for i in deps.links:
                    if i.governor.idx == lk.id:
                        if s.get_token_by_id(i.dependent.idx):       
                            if lemmatise:
                                single_result['d'] = s.get_token_by_id(i.dependent.idx).lemma
                            else:
                                single_result['d'] = i.dependent.text
                        break

            if 'gl' in show:
                single_result['gl'] = 'none'
                for i in deps.links:
                    if i.dependent.idx == lk.id:
                        if s.get_token_by_id(i.governor.idx):
                            single_result['gl'] = s.get_token_by_id(i.governor.idx).lemma
                        else:
                            single_result['gl'] = 'root'
                        break

            if 'dl' in show:
                single_result['dl'] = 'none'
                for i in deps.links:
                    if i.governor.idx == lk.id:
                        if s.get_token_by_id(i.dependent.idx):       
                            single_result['dl'] = s.get_token_by_id(i.dependent.idx).lemma
                        break

            if 'gp' in show:
                single_result['gp'] = 'none'
                for i in deps.links:
                    if i.dependent.idx == lk.id:
                        if s.get_token_by_id(i.governor.idx):       
                            single_result['gp'] = s.get_token_by_id(i.governor.idx).pos
                        break

            if 'dp' in show:
                single_result['dp'] = 'none'
                for i in deps.links:
                    if i.governor.idx == lk.id:
                        if s.get_token_by_id(i.dependent.idx):       
                            single_result['dp'] = s.get_token_by_id(i.dependent.idx).pos
                        break

            if 'df' in show:
                single_result['df'] = 'none'            
                for i in deps.links:
                    if i.governor.idx == lk.id:
                        single_result['df'] = i.type
                        break  

            if 'gf' in show:
                single_result['gf'] = 'none'
                
                for i in deps.links:
                    # if the result is the dependent, get the governor, find where
                    # it is a dependent, then gt the type
                    if i.dependent.idx == lk.id:
                        gv = next(x for x in deps.links if x.dependent.idx == i.governor.idx)
                        single_result['gf'] = gv.type
                        break                

            if 'r' in show:
                all_lks = [l for l in deps.links]
                distance = distancer(all_lks, lk)
                if distance is not False and distance is not None:
                    single_result['r'] = str(distance)
                else:
                    single_result['r'] = '-1'

            if 'i' in show:
                single_result['i'] = str(lk.id)

            if any(i.startswith('b') for i in show):
                tok_index = int(lk.id) - 1
                as_list = [w for w in s.tokens]
                as_list.pop(tok_index)
                if nopunct:
                    as_list = [w for w in as_list if re.search(nonword, w.word)]
                start = tok_index - window - 1
                if start < 0:
                    start = 0
                end = tok_index + window + 1
                sliced = as_list[start:end]
                for ctok in sliced:
                    single_result = {}
                    if 'b' in show:
                        single_result['b'] = ctok.word
                    if 'bl' in show:
                        single_result['bl'] = ctok.lemma
                    if 'bf' in show:
                        single_result['bf'] = 'none'
                        for i in deps.links:
                            if i.dependent.idx == lk.id:
                                single_result['bf'] = i.type.strip(',')
                                break
                    if 'bp' in show:
                        single_result['bp'] = ctok.pos
                    if 'bpl' in show:
                        from corpkit.dictionaries.word_transforms import taglemma
                        single_result['bpl'] = taglemma.get(ctok.pos.lower(), ctok.pos.lower())

                    lst = [single_result[i] for i in show]
                    lst = [i.replace('/', '-slash-') for i in lst]
                    joined = '/'.join(lst)
                    result.append(joined)

            # ngram showing
            elif any(i.startswith('n') for i in show):
                import string
                pystart = int(lk.id) - 1
                # iterate gramsize times over each match
                for i in range(gramsize):
                    single_result = {}
                    out = []
                    # start of gram to end of sent
                    tillend = [i for i in s.tokens[pystart-i:]]
                    # remove punct tokens
                    if nopunct:
                        tillend = [i for i in tillend if re.search(nonword, i.word)]
                    
                    # if words, we need to be able to unsplit
                    if 'n' in show or 'nw' in show:
                        if not split_contractions and len(show) > 1:
                            cant = "Can't have unsplit contractions with multiple show values."
                            raise ValueError(cant)
                        tld = [t.word.replace('/', '-slash-') for t in tillend]
                        if not split_contractions:
                            from corpkit.process import unsplitter
                            tld = unsplitter(tld)
                        tld = tld[:gramsize]
                        if len(tld) != gramsize:
                            continue
                        single_result['n'] = tld 
                    if 'nl' in show:
                        tld = [t.lemma.replace('/', '-slash-') for t in tillend[:gramsize]]
                        if len(tld) != gramsize:
                            continue
                        single_result['nl'] = tld
                    if 'np' in show:
                        tld = [t.pos for t in tillend[:gramsize]]
                        if len(tld) != gramsize:
                            continue
                        single_result['np'] = tld
                    if 'npl' in show:
                        from corpkit.dictionaries.word_transforms import taglemma
                        tld = [taglemma.get(t.pos.lower(), t.pos) for t in tillend[:gramsize]]
                        if len(tld) != gramsize:
                            continue
                        single_result['npl'] = tld
                    
                    lst_of_tokenlists = [single_result[i] for i in show]
                    # now we have
                    # show = [W, L]
                    # [['houses', 'of', 'friends'], ['house', 'of', 'friend']]
                    zipped = zip(*lst_of_tokenlists)
                    # [('houses', 'house'), ('of', 'of'), ('friends', 'friend')]
                    out = ' '.join('/'.join(i) for i in zipped)
                    result.append(out)

            else:
                if 'c' not in show:
                    # add them in order
                    out = []
                    for i in show:
                        out.append(single_result[i])

                    out = [i.replace('/', '-slash-') for i in out if i]
                    result.append('/'.join(out))
    
    if 'c' in show:
        result = sum(result)

    if type(do_concordancing) == str and do_concordancing.lower() == 'only':
        result = []
    return result, conc_result