def dep_searcher(sents,
                 search,
                 show = 'w',
                 dep_type = 'collapsed-ccprocessed-dependencies',
                 regex_nonword_filter = r'[A-Za-z0-9:_]',
                 concordancing = False,
                 exclude = False,
                 excludemode = 'any',
                 searchmode = 'all'):
    import re
    from corenlp_xml.document import Document
    from collections import Counter
    from corpkit.build import flatten_treestring
    from corpkit.process import filtermaker
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

    2. exclude entries if need be

    3. return '/'-sep list of 'show' keyword arg:
       governor
       dependent
       function
       pos
       lemma
       word
       index
       distance
       
       ... or just return int count.
       """

    def get_deps(sentence, dep_type):
        if dep_type == 'basic-dependencies':
            return sentence.basic_dependencies
        if dep_type == 'collapsed-dependencies':
            return sentence.collapsed_dependencies
        if dep_type == 'collapsed-ccprocessed-dependencies':
            return sentence.collapsed_ccprocessed_dependencies

    result = []
    for s in sents:
        lks = []
        deps = get_deps(s, dep_type)
        tokens = s.tokens
        for opt, pat in search.items():
            #pat = filtermaker(pat)
            if opt == 'g':
                for l in deps.links:
                    if re.match(pat, l.governor.text):
                        lks.append(s.get_token_by_id(l.dependent.idx))
            elif opt == 'd':
                for l in deps.links:
                    if re.match(pat, l.dependent.text):
                        lks.append(s.get_token_by_id(l.governor.idx))
            elif opt == 'f':
                for l in deps.links:
                    if re.match(pat, l.type):
                        lks.append(s.get_token_by_id(l.dependent.idx))
            elif opt == 'p':
                for tok in tokens:
                    if re.match(pat, tok.pos):
                        lks.append(tok)
            elif opt == 'l':
                for tok in tokens:
                    if re.match(pat, tok.lemma):
                        lks.append(tok)
            elif opt == 'w':
                for tok in tokens:
                    if re.match(pat, tok.word):
                        lks.append(tok)
            elif opt == 'i':
                for tok in tokens:
                    if re.match(pat, str(tok.id)):
                        lks.append(tok)

        # only return results if all conditions are met
        if searchmode == 'all':
            counted = Counter(lks)
            lks = [k for k, v in counted.items() if v >= len(search.keys())]

        if not concordancing:
            lks = list(set([x for x in lks if re.search(regex_nonword_filter, x.word)]))

        if exclude is not False:
            to_remove = []
            for op, pat in exclude.items():
                pat = filtermaker(pat)
                for tok in lks:
                    if op == 'g':
                        for l in deps.links:
                            if re.match(pat, l.governor.text):
                                to_remove.append(s.get_token_by_id(l.governor.idx))
                    elif op == 'd':
                        for l in deps.links:
                            if re.match(pat, l.dependent.text):
                                to_remove.append(s.get_token_by_id(l.dependent.idx))
                    elif op == 'f':
                        for l in deps.links:
                            if re.match(pat, l.type):
                                to_remove.append(s.get_token_by_id(l.dependent.idx))
                    elif op == 'p':
                        for tok in tokens:
                            if re.match(pat, tok.pos):
                                to_remove.append(tok)
                    elif op == 'l':
                        for tok in tokens:
                            if re.match(pat, tok.lemma):
                                to_remove.append(tok)
                    elif op == 'w':
                        for tok in tokens:
                            if re.match(pat, tok.word):
                                to_remove.append(tok)
                    elif op == 'i':
                        for tok in tokens:
                            if re.match(pat, str(tok.id)):
                                to_remove.append(tok)

            if excludemode == 'all':
                counted = Counter(to_remove)
                to_remove = [k for k, v in counted.items() if v >= len(exclude.keys())]
            for i in to_remove:
                try:
                    lks.remove(i)
                except ValueError:
                    pass

        if 'c' in show:
            result.append(len(lks))
            continue

        if concordancing:
            for lk in lks: # for each concordance match
                one_result = []
                windex = int(lk.id) - 1
                speakr = s.speakername
                if not speakr:
                    speakr = ''
                conc_line = [speakr]
                # format a single word correctly
                for tok in s.tokens:

                    single_wd = {}
                    intermediate_result = []
                    if 'w' in show:
                        single_wd['w'] = tok.word
                    if 'l' in show:
                        single_wd['l'] = tok.lemma
                    if 'p' in show:
                        single_wd['p'] = tok.pos
                    if 'f' in show:
                        for lin in deps.links:
                            single_wd['f'] = '.'
                            if tok.id == lin.dependent.idx:
                                single_wd['f'] = lin.type
                                break
                    if 'i' in show:
                        single_wd['i'] = str(tok.id)
                    
                    for i in show:
                        intermediate_result.append(single_wd[i])
                    one_result.append('/'.join(intermediate_result))
                # now we have formatted tokens as a list. we need to split
                # it into start, middle and end
                start = ' '.join([w for index, w in enumerate(one_result) if index < windex])
                middle = one_result[windex]
                end = ' '.join([w for index, w in enumerate(one_result) if index > windex])
                for bit in start, middle, end:
                    conc_line.append(bit)
                result.append(conc_line)
        else:
            # figure out what to show
            for lk in lks:
                single_result = {}
                

                if 'w' in show:
                    single_result['w'] = 'none'
                    if lemmatise:
                        single_result['w'] = lk.lemma
                    else:
                        single_result['w'] = lk.word

                if 'l' in show:
                    single_result['l'] = lk.lemma

                if 'p' in show:
                    single_result['p'] = 'none'
                    postag = lk.pos
                    if lemmatise:
                        if postag.lower() in taglemma.keys():
                            single_result['p'] = taglemma[postag.lower()]
                        else:
                            single_result['p'] = postag.lower()
                    else:
                        single_result['p'] = postag
                    if not single_result['p']:
                        single_result['p'] == 'none'

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

                if 'r' in show:
                    all_lks = [l for l in deps.links]
                    distance = distancer(all_lks, lk)
                    if distance:
                        single_result['r'] = str(distance)
                    else:
                        single_result['r'] = '-1'

                if 'i' in show:
                    single_result['i'] = str(lk.id)

                if 'c' not in show:
                    
                    # add them in order
                    out = []
                    for i in show:
                        out.append(single_result[i])

                    result.append('/'.join(out))
    
    if 'c' in show:
        result = sum(result)

    return result