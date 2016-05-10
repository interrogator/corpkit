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
                 only_format_match=False,
                 speaker=False,
                 gramsize=2,
                 nopunct=True,
                 split_contractions=False,
                 window=2):
    import re
    from corenlp_xml.document import Document
    from collections import Counter
    from corpkit.build import flatten_treestring
    from corpkit.process import filtermaker, animator, get_deps

    is_a_word = re.compile(regex_nonword_filter)

    if any(x.startswith('n') for x in show) or any(x.startswith('b') for x in show):
        only_format_match = True

    #if any(x.startswith('n') for x in show) and any(not x.startswith('n') for x in show):
    #    raise ValueError("Can't mix n-gram and non-ngram show values.")
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

    3. return results and conc lines, or just a count
       
       """

    def distancer(matching_tokens, token):
        "determine number of jumps to root"      
        c = 0
        # get the gov index, stop when it's zero
        root_found = False
        while not root_found:
            if c == 0:
                try:
                    link_to_check = next(i for i in matching_tokens if i.dependent.idx == token.id)
                except StopIteration:
                    root_found = True
                    break
                #link_to_check = token
            gov_index = link_to_check.governor.idx
            if gov_index == 0:
                root_found = True
            else:
                if c > 29:
                    root_found = True
                    break
                link_to_check = [l for l in matching_tokens if l.dependent.idx == gov_index]
                if len(link_to_check) > 0:
                    link_to_check = link_to_check[0]
                else:
                    break
                c += 1
        if c < 30:
            return c

    def pat_format(pat):
        from corpkit.dictionaries.process_types import Wordlist
        if isinstance(pat, Wordlist):
            pat = list(pat)
        if pat == 'any':
            pat = re.compile(r'.*')
        elif isinstance(pat, list):
            if all(isinstance(x, int) for x in pat):
                pat = [str(x) for x in pat]
            pat = filtermaker(pat, case_sensitive=case_sensitive)
        else:
            if case_sensitive:
                pat = re.compile(pat)
            else:
                pat = re.compile(pat, re.IGNORECASE)
        return pat

    def get_matches_from_sent(s,
                              search,
                              deps=False,
                              tokens=False, 
                              dep_type='basic-dependencies',
                              mode='all'):
        """process a sentence object, returning matching tok ids"""
        from corpkit.process import get_deps
        import re
        matching_tokens = []
        for opt, pat in list(search.items()):
            if isinstance(pat, dict):
                del search[opt]
                for k, v in list(pat.items()):
                    if k != 'w':
                        search[opt + k] = v
                    else:
                        search[opt] = v

        for opt, pat in list(search.items()):
            pat = pat_format(pat)
            if opt == 'g':
                got = []
                for l in deps.links:
                    if re.search(pat, l.governor.text):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    matching_tokens.append(i)
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
                    matching_tokens.append(i)
            elif opt == 'df':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        extra_crit = search.get('d2f')
                        if extra_crit:
                            if isinstance(extra_crit, Wordlist):
                                extra_crit = list(extra_crit)
                            if isinstance(extra_crit, list):
                                from corpkit.other import as_regex
                                extra_crit = as_regex(extra_crit, case_sensitive=case_sensitive)                            
                            for b in deps.links:
                                if re.search(extra_crit, b.type):
                                    if l.governor.idx == b.governor.idx:
                                        got.append(s.get_token_by_id(l.governor.idx))
                        else:
                            got.append(s.get_token_by_id(l.governor.idx))
                got = set(got)
                for i in got:
                    matching_tokens.append(i)
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
                    matching_tokens.append(i)
            elif opt == 'gp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.governor.idx == tok.id:
                                got.append(s.get_token_by_id(i.dependent.idx))
                got = set(got)
                for i in got:
                    matching_tokens.append(i)
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
                                        extra_crit = as_regex(extra_crit, 
                                            case_sensitive=case_sensitive)
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
                    matching_tokens.append(i)
            elif opt == 'dp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.dependent.idx == tok.id:
                                got.append(s.get_token_by_id(i.governor.idx))
                got = set(got)
                for i in got:
                    matching_tokens.append(i)

            elif opt == 'd':
                got = []
                for l in deps.links:
                    if re.search(pat, l.dependent.text):
                        got.append(s.get_token_by_id(l.governor.idx))

                got = set(got)
                for i in got:
                    matching_tokens.append(i)

            elif opt == 'f':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    matching_tokens.append(i)
            elif opt == 'p':
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        matching_tokens.append(tok)
            elif opt == 'pl':
                for tok in tokens:
                    from corpkit.dictionaries.word_transforms import taglemma
                    postag = tok.pos
                    stemmedtag = taglemma.get(postag.lower(), postag.lower())
                    if re.search(pat, stemmedtag):
                        matching_tokens.append(tok)
            elif opt == 'l':
                for tok in tokens:
                    if tok.lemma:
                        se = tok.lemma
                    elif tok.word:
                        se = tok.word
                    else:
                        continue
                    if re.search(pat, se):
                        matching_tokens.append(tok)
            elif opt == 'w':
                for tok in tokens:
                    if re.search(pat, tok.word):
                        matching_tokens.append(tok)
            elif opt == 'i':
                for tok in tokens:
                    if re.search(pat, str(tok.id)):
                        matching_tokens.append(tok)
            elif opt == 'r':
                got = []
                for tok in tokens:
                    dist = distancer(deps.links, tok)
                    if dist is not None and dist is not False:
                        try:
                            if int(dist) == int(pat):
                                matching_tokens.append(tok)

                        except TypeError:
                            if re.search(pat, str(dist)):
                                matching_tokens.append(tok)

        if mode == 'all':
            from collections import Counter
            counted = Counter(matching_tokens)
            must_contain = len(search)
            must_contain -= len([n for n in search.keys() if '2' in n])
            matching_tokens = [k for k, v in counted.items() if v >= must_contain]
        return matching_tokens

    def process_a_match(match, tokens):
        """take a single search match and return a list of results and conc lines"""
        resultlist = []
        conclist = []
        for repeat in range(repeats):
            res, conc_res = process_a_submatch(match, repeat, tokens)
            if not res and not conc_res:
                continue
            #for r, c in zip(res, conc_res):
            resultlist.append(res)
            conclist.append(conc_res)
        return resultlist, conclist

    def get_indices(match, repeat, tokens):
        """get first and last index in token list for a token"""
        
        py_index = tokens.index(match)        
        # first time around, start at the word
        # second time, at the word - 1

        # if ngramming, we need an index of the last token in the ngram
        if any(x.startswith('n') for x in show):

            first_in_gram = py_index - repeat
            last_in_gram = first_in_gram + (gramsize - 1)
        
        elif any(x.startswith('b') for x in show):
            first_in_gram = py_index - window + repeat
            last_in_gram = py_index - window + repeat
            if first_in_gram == py_index:
                return False, False
        else:
            py_index = tokens.index(match)
            first_in_gram = py_index - repeat
            last_in_gram = first_in_gram
        return first_in_gram, last_in_gram

    def process_a_submatch(match, repeat, tokens):
        """for ngrams, etc., we have to repeat over results. so, this
        is for each repeat"""

        # make a conc line with just speaker name so far
        speakr = s.speakername
        if not speakr:
            speakr = ''
        # begin building line with speaker first
        conc_line = [speakr]

        # get the index of the match in python
        first_in_gram, last_in_gram = get_indices(match, repeat, tokens)
        if first_in_gram is False and last_in_gram is False:
            return False, False

        # maybe we can't repeat over it, because it's at the start or end
        # in this case, return
        if first_in_gram < 0:
            return False, False
        if last_in_gram >= len(tokens):
            return False, False

        # by this point, we have the index of the start and end of the gram
        # now, if we don't need the whole sent, we discard it. if we don't
        # need to format it, we format it now.

        if do_concordancing:
            if only_format_match or show == ['n'] or show == ['b']:
                start = ' '.join(t.word for index, t in enumerate(tokens) \
                    if index < first_in_gram)
                end = ' '.join(t.word for index, t in enumerate(tokens) \
                    if index > last_in_gram)
                # and only process the match itself
                # redefine tokens to just be what we need        
                tokens = tokens[first_in_gram:last_in_gram+1]
                # add back the original token to left/right of collocate
                if any(x.startswith('b') for x in show):
                    if repeat == 0:
                        tokens.append(match)
                    elif repeats / repeat > 0:
                        tokens.append(match)
                    else:
                        tokens.insert(0, match)

        # if we are concordancing, here's a list of toks in the ngram
        else:
            tokens = tokens[first_in_gram:last_in_gram+1]

        if any(x.startswith('b') for x in show):
            separator = '_'
        else:
            separator = ' '

        # now, for each word in the matching sentence, format it.
        # note that if we're not doing concordancing, or if only formatting 
        # the match (or not concordancing), len(tokens) == 1
        processed_toklist = []
        for token in tokens:
            single_result = process_a_token(token, show)
            for bit in single_result:
                processed_toklist.append(bit)
        
        # if no conc at all, return the empty ish one and a string of token(s)
        if not do_concordancing:
            return ' '.join(processed_toklist), conc_line

        # if we're concordancing:
        # now we have formatted tokens as a list. we need to split
        # it into start, middle and end, unless only_format_match
        else:
            if not only_format_match:
                start = ' '.join(w for index, w in enumerate(processed_toklist) \
                                 if index < first_in_gram)
                end = ' '.join(w for index, w in enumerate(processed_toklist) \
                                 if index > last_in_gram)
                middle = separator.join(w for index, w in enumerate(processed_toklist) \
                                 if index >= first_in_gram \
                    and index <= last_in_gram)
            else:
                middle = separator.join(processed_toklist)

            for bit in start, middle, end:
                conc_line.append(bit)

        return middle, conc_line


    def process_a_token(token, show):
        # here is a dict of show type as key and data as v
        single_result = {}
        intermediate_result = []            
        # ugly code begins here. this is where we have a formatter for
        # every possible show value.

        # treat ngrams just as words now
        show = [i.lstrip('n').lstrip('b') for i in show]

        if 'w' in show:
            single_result['w'] = 'none'
            if lemmatise:
                single_result['w'] = token.lemma
            else:
                single_result['w'] = token.word
        if 'l' in show:
            from corpkit.dictionaries.word_transforms import wordlist
            lem = wordlist.get(token.lemma, token.lemma)
            single_result['l'] = lem
        if 'p' in show:
            single_result['p'] = 'none'
            postag = token.pos
            if lemmatise:
                from corpkit.dictionaries.word_transforms import taglemma
                single_result['p'] = taglemma.get(postag.lower(), postag.lower())
            else:
                single_result['p'] = postag
            if not single_result['p']:
                single_result['p'] == 'none'

        if 'pl' in show:
            single_result['pl'] = 'none'
            postag = token.pos
            from corpkit.dictionaries.word_transforms import taglemma
            single_result['pl'] = taglemma.get(postag.lower(), postag.lower())

        if 'f' in show:
            single_result['f'] = 'none'
            for i in deps.links:
                if i.dependent.idx == token.id:
                    single_result['f'] = i.type.rstrip(',')
                    break
            if single_result['f'] == '':
                single_result['f'] = 'root'

        if 'g' in show:
            single_result['g'] = 'none'
            for i in deps.links:
                if i.dependent.idx == token.id:
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
                if i.governor.idx == token.id:
                    if s.get_token_by_id(i.dependent.idx):       
                        if lemmatise:
                            r = s.get_token_by_id(i.dependent.idx).lemma
                            single_result['d'] = r
                        else:
                            single_result['d'] = i.dependent.text
                    break

        if 'gl' in show:
            single_result['gl'] = 'none'
            for i in deps.links:
                if i.dependent.idx == token.id:
                    if s.get_token_by_id(i.governor.idx):
                        single_result['gl'] = s.get_token_by_id(i.governor.idx).lemma
                    else:
                        single_result['gl'] = 'root'
                    break

        if 'dl' in show:
            single_result['dl'] = 'none'
            for i in deps.links:
                if i.governor.idx == token.id:
                    if s.get_token_by_id(i.dependent.idx):       
                        single_result['dl'] = s.get_token_by_id(i.dependent.idx).lemma
                    break

        if 'gp' in show:
            single_result['gp'] = 'none'
            for i in deps.links:
                if i.dependent.idx == token.id:
                    if s.get_token_by_id(i.governor.idx):       
                        single_result['gp'] = s.get_token_by_id(i.governor.idx).pos
                    break

        if 'dp' in show:
            single_result['dp'] = 'none'
            for i in deps.links:
                if i.governor.idx == token.id:
                    if s.get_token_by_id(i.dependent.idx):       
                        single_result['dp'] = s.get_token_by_id(i.dependent.idx).pos
                    break

        if 'df' in show:
            single_result['df'] = 'none'            
            for i in deps.links:
                if i.governor.idx == token.id:
                    single_result['df'] = i.type
                    break  

        if 'gf' in show:
            single_result['gf'] = 'none'
            
            for i in deps.links:
                # if the result is the dependent, get the governor, find where
                # it is a dependent, then gt the type
                if i.dependent.idx == token.id:
                    gv = next(x for x in deps.links if x.dependent.idx == i.governor.idx)
                    single_result['gf'] = gv.type
                    break                

        if 'r' in show:
            all_matching_tokens = [l for l in deps.links]
            distance = distancer(all_matching_tokens, token)
            if distance is not False and distance is not None:
                single_result['r'] = str(distance)
            else:
                single_result['r'] = '-1'

        if 'i' in show:
            single_result['i'] = str(token.id)

        for i in show:
            intermediate_result.append(single_result[i].replace('/', \
                '-slash-').encode('utf-8', errors='ignore'))
        return ['/'.join(intermediate_result)]


    ####################################################
    ################# BEGIN WORKFLOW ###################
    ####################################################


    # if we're doing ngrams or collocations, we need to repeat over the data
    # otherwise it's just once
    repeats = 1
    if any(x.startswith('n') for x in show):
        repeats = gramsize
    if any(x.startswith('b') for x in show):
        repeats = (window * 2) + 1

    # store data here
    result = []
    conc_result = []

    # iterate over sentences
    for s in sents:
        deps = get_deps(s, dep_type)
        
        # remove punctuation if need be
        if nopunct:
            tokens = [w for w in s.tokens if re.search(is_a_word, w.word)]
        else:
            tokens = s.tokens

        # identify matching Token objects
        matching_tokens = get_matches_from_sent(s, search, deps, tokens, 
                                                dep_type, mode=searchmode)
        
        # exclude in the same way if need be
        if exclude is not False:
            to_remove = get_matches_from_sent(s, exclude, deps, tokens, 
                                               dep_type, mode=excludemode)
            # do removals
            for i in to_remove:
                try:
                    matching_tokens.remove(i)
                except ValueError:
                    pass

        # if counting, we're done already
        if 'c' in show:
            result.append(len(matching_tokens))
            continue

        # iterate over results, entering processing loops
        for match in matching_tokens:
            # they are returned as lists, so add those to final result
            res, conc_res = process_a_match(match, tokens)
            for r, c in zip(res, conc_res):
                if r and c:
                    result.append(r)
                    conc_result.append(c)

    if 'c' in show:
        result = sum(result)

    if isinstance(do_concordancing, basestring) and do_concordancing.lower() == 'only':
        result = []

    if not do_concordancing:
        conc_result = []

    return result, conc_result
