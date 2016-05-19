from __future__ import print_function

def dep_searcher(sents,
                 search,
                 show=['w'],
                 dep_type='collapsed-ccprocessed-dependencies',
                 regex_nonword_filter=r'[A-Za-z0-9:_]',
                 do_concordancing=False,
                 exclude=False,
                 excludemode='any',
                 searchmode='all',
                 case_sensitive=False,
                 only_format_match=False,
                 speaker=False,
                 gramsize=2,
                 nopunct=True,
                 split_contractions=False,
                 window=2,
                 language_model=False,
                 **kwargs
                ):
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
    Search corenlp dependency parse.
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
    import re
    from corenlp_xml.document import Document
    from collections import Counter
    from corpkit.build import flatten_treestring
    from corpkit.process import filtermaker, animator, get_deps

    is_a_word = re.compile(regex_nonword_filter)

    #if any(x.startswith('n') for x in show) \
    #if any(x.startswith('b') for x in show):
    #    only_format_match = True

    ####################################################
    ################ SEARCH FUNCTIONS ##################
    ####################################################
    
    bmatch = {'d': 'governor',
              'g': 'dependent'}
    fmatch = {'g': 'governor',
              'd': 'dependent'}

    attr_trans = {'p': 'pos',
                  'x': 'pos',
                  'i': 'id',
                  'w': 'word',
                  'l': 'lemma'}

    def locate_tokens(tok, deprole, attr):
        ret = set()
        if deprole == 'm':
            if attr == 'f':
                return set([s.get_token_by_id(tok.id)])
            else:
                return set([tok])
        else:
            in_deps = [i for i in deps.links if getattr(i, fmatch[deprole]).idx == tok.id]
            for lnk in in_deps:
                ret.add(s.get_token_by_id(getattr(lnk, bmatch[deprole]).idx))
            return ret

    def simple_searcher(deprole, pattern, attr):
        if attr == 'f':
            return search_function(deprole, pattern)
        elif attr == 'r':
            return distance_searcher(tokens, pattern)
        else:
            attrib = attr_trans.get(attr, attr)
        matches = set()
        for tok in tokens:
            tosearch = getattr(tok, attrib)
            # deal with possible ints
            if isinstance(pattern, int) and isinstance(tosearch, int):
                if pattern != tosearch:
                    continue
            elif isinstance(tosearch, int) and not isinstance(pattern, int):
                tosearch = str(tosearch)        
            if attr == 'x':
                from corpkit.dictionaries.word_transforms import taglemma
                tosearch = taglemma.get(tosearch.lower(), tosearch.lower())
            if not re.search(pattern, tosearch):
                continue
            matches |= locate_tokens(tok, deprole, attr)
        return matches

    def search_function(deprole, pattern):
        matches = set()
        for tok in tokens:
            for l in deps.links:
                if not re.search(pat, l.type):
                    continue
                if deprole == 'm':
                    matches.add(s.get_token_by_id(l.dependent.idx))
                else:
                    in_deps = [i for i in deps.links if getattr(i, fmatch[deprole]).idx == tok.id]
                    for lnk in in_deps:
                        matches.add(s.get_token_by_id(getattr(lnk, bmatch[deprole]).idx))
        return matches

    def distance_searcher(tosearch, pattern):
        matches = set()
        for t in tosearch:
            dist = distancer(deps.links, t)
            if dist is None or dist is False:
                continue
            try:
                if int(dist) == int(pattern):
                    matches.add(t)
            except TypeError:
                if re.search(pattern, str(dist)):
                    matches.add(t)
        return matches

    ####################################################
    ################## SHOW FUNCTIONS ##################
    ####################################################

    lookup = {'w': 'word',
              'l': 'lemma',
              'p': 'pos',
              'i': 'id'}

    def show_this(tokenx, this):

        if this == 'f':
            return show_function(tokenx)
        if this == 'r':
            return show_distance(tokenx)

        t = lookup.get(this, this)
        if t == 'x':
            from corpkit.dictionaries.word_transforms import taglemma
            postp = taglemma
        elif t == 'i':
            from corpkit.dictionaries.word_transforms import wordlist
            postp = wordlist
        else:
            postp = {}

        if hasattr(tokenx, t):
            att = getattr(tokenx, t)
            return postp.get(att, att)
        else:
            return tokenx

    def show_function(tok):
        if tok == 'root':
            return 'tok'        
        for i in deps.links:
            if i.dependent.idx == tok.id:
                return i.type.rstrip(',')
        return 'none'


    def show_distance(token_set):
        """broken"""
        fs = set()
        for tok in token_set:
            if tok == 'root':
                fs.add(tok)
                continue
            all_matching_tokens = [l for l in deps.links]
            distance = distancer(all_matching_tokens, tok)
            if distance is not False and distance is not None:
                fs.add(str(distance))
        return fs

    def show_governor(tok):
        for i in deps.links:
            if i.dependent.idx == tok.id:
                gov = s.get_token_by_id(i.governor.idx)
                if gov:
                    return gov
                else:
                    return 'root'
        return 'none' # not possible?

    def show_dependent(tok):
        """this has been hacked, needs rewriting"""
        for i in deps.links:
            if i.governor.idx == tok.id:
                dep = s.get_token_by_id(i.dependent.idx)
                if dep:
                    return dep
                else:
                    return 'none'
        return 'none'

    def show_match(tok):
        return tok

    def show_next(token_set, _):
        """get token to the right"""
        nexts = set()
        for tok in token_set:
            current_index = tokens.index(tok)
            try:
                nexts.add(tokens[current_index + 1])
            except IndexError:
                pass
        return nexts

    lookup_show = {'g': show_governor,
                   'd': show_dependent,
                   'm': show_match}

    ####################################################
    ################ PROCESSING FUNCS ##################
    ####################################################

    def get_list_of_lookup_funcs(show_bit):
        """take a single search/show_bit type, return match"""
        #show_bit = [i.lstrip('n').lstrip('b') for i in show_bit]
        ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 'r']
        starts = ['d', 'g', 'm', 'n', 'b']
        show_bit = show_bit.lstrip('n')
        show_bit = show_bit.lstrip('b')
        show_bit = list(show_bit)
        if show_bit[-1] not in ends:
            show_bit.append('w')
        if show_bit[0] not in starts:
            show_bit.insert(0, 'm')
        return lookup_show.get(show_bit[0]), show_bit[1]
       # return [(lookup_show.get(i, show_this), i) for i in show_bit]

    def fix_search(search):
        """if search has nested dicts, remove them"""
        ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x']
        if not search:
            return
        newsearch = {}
        for srch, pat in search.items():
            if len(srch) == 1 and srch in ends:
                srch = 'm%s' % srch

            if isinstance(pat, dict):
                for k, v in list(pat.items()):
                    if k != 'w':
                        newsearch[srch + k] = pat_format(v)
                    else:
                        newsearch[srch] = pat_format(v)
            else:
                newsearch[srch] = pat_format(pat)
        return newsearch

    def do_single_search(srch, pattern):
        """get results from single search criterion"""
        deprole, attr = srch[0], srch[-1]
        matching_tokens = simple_searcher(deprole, pattern, attr)
        return matching_tokens

    def distancer(matching_tokens, token):
        "determine number of jumps to root"      
        c = 0
        # get the gov index, stop when it's zero
        root_found = False
        while not root_found:
            if c == 0:
                try:
                    link_to_check = next(i for i in matching_tokens \
                                         if i.dependent.idx == token.id)
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
                link_to_check = [l for l in matching_tokens \
                                 if l.dependent.idx == gov_index]
                if len(link_to_check) > 0:
                    link_to_check = link_to_check[0]
                else:
                    break
                c += 1
        if c < 30:
            return c

    def pat_format(pat):
        from corpkit.dictionaries.process_types import Wordlist
        if pat == 'any':
            return re.compile(r'.*')
        if isinstance(pat, Wordlist):
            pat = list(pat)
        if isinstance(pat, list):
            if all(isinstance(x, int) for x in pat):
                pat = [str(x) for x in pat]
            pat = filtermaker(pat, case_sensitive=case_sensitive, root=kwargs.get('root'))
        else:
            if isinstance(pat, int):
                return pat
            if case_sensitive:
                pat = re.compile(pat)
            else:
                pat = re.compile(pat, re.IGNORECASE)
        return pat

    def process_a_match(match, tokens):
        """
        Take a single search match and return a list of results and conc lines
        """
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
        """
        Get first and last index in token list for a token
        """
        try:
            py_index = tokens.index(match)
        except ValueError:
            return False, False
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
        """
        For ngrams, etc., we have to repeat over results. so, this is for 
        each repeat
        """
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

        if not language_model:
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

            # if we are not concordancing, here's a list of toks in the ngram
            else:
                tokens = tokens[first_in_gram:last_in_gram+1]

        if any(x.startswith('b') for x in show):
            separator = '_'
        else:
            separator = ' '
        if language_model:
            separator = '-spl-it-'

        # now, for each word in the matching sentence, format it.
        # note that if we're not doing concordancing, or if only formatting 
        # the match (or not concordancing), len(tokens) == 1
        processed_toklist = []
        for token in tokens:
            single_result = process_a_token(token, show)
            if single_result:
                processed_toklist.append(single_result)
        
        if language_model:
            return '-spl-it-'.join(processed_toklist), conc_line
            #return tuple(processed_toklist), conc_line
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
        """
        Take entire show argument, and a token of interest,
        and return slash sep token
        """
        result = []
        for val in show:
            get_tok, show_bit = get_list_of_lookup_funcs(val)
            tok = get_tok(token)
            to_show = show_this(tok, show_bit)
            if isinstance(exclude, dict) and val in exclude:
                if re.search(exclude[val], to_show):
                    return
            result.append(to_show)
        if result:
            if nopunct:
                if not all(re.search(is_a_word, i) for i in result):
                    return
            if kwargs.get('no_root'):
                if any(i == 'root' for i in result):
                    return
            if kwargs.get('no_none'):
                if any(i == 'none' for i in result):
                    return

        return '/'.join(i.replace('/', '-slash') for i in result)

    def remove_by_mode(matching_tokens, mode):
        """
        If search/excludemode is 'all', remove words that don't always appear.
        """
        if mode == 'any':
            return matching_tokens
        from collections import Counter
        counted = Counter(matching_tokens)
        must_contain = len(search)
        return [k for k, v in counted.items() if v >= must_contain]

    ####################################################
    ################## BEGIN WORKFLOW ##################
    ####################################################

    # if we're doing ngrams or collocations, we need to repeat over the data
    # otherwise it's just once
    repeats = 1
    if any(x.startswith('n') for x in show):
        repeats = gramsize
    if any(x.startswith('b') for x in show):
        repeats = (window * 2) + 1

    # store results here
    result = []
    conc_result = []

    # fix search and excludes
    search = fix_search(search)
    exclude = fix_search(exclude)

    # iterate over sentences
    for s in sents:

        # all search matches go here
        matching_tokens = []
        deps = get_deps(s, dep_type)
        # remove punctuation if need be
        if nopunct:
            tokens = [w for w in s.tokens if re.search(is_a_word, w.word)]
        else:
            tokens = s.tokens
        # identify matching Token objects
        #matching_tokens = get_matches_from_sent(s, search, deps, tokens, 
        #                                        dep_type, mode=searchmode)
        for srch, pat in search.items():
            deprole, attr = srch[0], srch[-1]
            matching_tokens += simple_searcher(deprole, pat, attr)

        matching_tokens = remove_by_mode(matching_tokens, searchmode)

        # exclude in the same way if need be
        removes = []
        if exclude:
            for excl, expat in exclude.items():
                exclv, exattr = excl[0], excl[-1]
                for remove in simple_searcher(exclv, expat, exattr):
                    removes.append(remove)

            removes = remove_by_mode(removes, excludemode)
                
            # do removals
            for i in removes:
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

    if isinstance(do_concordancing, basestring) and \
        do_concordancing.lower() == 'only':
        result = []

    if not do_concordancing:
        conc_result = []

    return result, conc_result
