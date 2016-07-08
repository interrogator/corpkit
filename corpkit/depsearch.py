from __future__ import print_function
from corpkit.constants import STRINGTYPE

def dep_searcher(sents,
                 search,
                 show=['w'],
                 dep_type='collapsed-ccprocessed-dependencies',
                 regex_nonword_filter=r'[A-Za-z0-9:_]',
                 conc=False,
                 exclude=False,
                 excludemode='any',
                 searchmode='all',
                 case_sensitive=False,
                 only_format_match=False,
                 speaker=False,
                 gramsize=2,
                 no_punct=True,
                 no_closed=False,
                 whitelist=False,
                 split_contractions=False,
                 window=2,
                 language_model=False,
                 corefs=False,
                 representative=True,
                 non_representative=True,
                 **kwargs
                ):
    
    """
    Search CoreNLP XML Sentences

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
    from corpkit.process import animator

    if not sents:
        return [], []

    if any(x[0] in ['-', '+'] for x in search):
        import operator
        mapping = {'+': operator.add, '-': operator.sub}

    is_a_word = kwargs.get('is_a_word')

    if any(x.startswith('n') for x in show) or any(x.startswith('b') for x in show):
        only_format_match = True

    #if any(x.startswith('n') for x in show) and any(not x.startswith('n') for x in show):
    #    raise ValueError("Can't mix n-gram and non-ngram show values.")

    #if any(x.startswith('n') for x in show) \
    #if any(x.startswith('b') for x in show):
    #    only_format_match = True

    ####################################################
    ################ SEARCH FUNCTIONS ##################
    ####################################################
    
    bmatch = {'d': 'governor',
              'g': 'dependent',
              'h': 'head'}
    fmatch = {'g': 'governor',
              'd': 'dependent',
              'h': 'head'}

    attr_trans = {'p': 'pos',
                  'x': 'pos',
                  'i': 'id',
                  'w': 'word',
                  'l': 'lemma'}

    lookup = {'w': 'word',
              'l': 'lemma',
              'p': 'pos',
              'i': 'id',
              'x': 'pos'}

    def locate_tokens(tok, deprole, attr, adjacent=False):
        """
        take a token, return it, its gov or dependent
        """
        ret = set()
        if adjacent and adjacent[0] == '+':
            tok = s.get_token_by_id(tok.id - int(adjacent))
        elif adjacent and adjacent[0] == '-':
            tok = s.get_token_by_id(tok.id + int(adjacent))

        if deprole == 'm':
            if attr == 'f':
                return set([s.get_token_by_id(tok.id)])
            else:
                return set([tok])
        elif deprole == 'h':
            return set(get_candidates(tok, justfirst=True))

        else:
            in_deps = [i for i in deps.links if getattr(i, fmatch[deprole]).idx == tok.id]
            for lnk in in_deps:
                ret.add(s.get_token_by_id(getattr(lnk, bmatch[deprole]).idx))
            return ret

    def get_candidates(tok, justfirst=False):
        candidates = [tok]
        if not corefs:
            return candidates
        for coref in corefs:
            for index, mention in enumerate(coref.mentions):
                if not representative and mention.representative:
                    continue
                if not non_representative and not mention.representative:
                    continue
                if justfirst:
                    if index > 0:
                        return [mention.siblings[0].head]
                    else:
                        return candidates
                # if current token is a coref chain
                if tok == mention.head:
                    for sibling in mention.siblings:
                        candidates.append(sibling.head)
                    return candidates
        return candidates

    def simple_searcher(tokens, deprole, pattern, attr, repeating=True, adjacent=False):

        if attr == 'f':
            return search_function(deprole, pattern)
        elif attr == 'r':
            return distance_searcher(tokens, pattern)
        else:
            attrib = attr_trans.get(attr, attr)
        matches = set()

        for tok in tokens:

            if corefs and repeating:
                # get a list of tokens that could match, and pass those
                # recursively into this function
                candidates = get_candidates(tok)
                #
                res = simple_searcher(candidates, deprole, pattern, attr, repeating=False)
                if res:
                    matches |= locate_tokens(tok, deprole, attr)
                continue

            adjstuff = False

            # if looking at an adjacent search, select the adjacent
            # token and then check pattern against it
            if adjacent:
                op, count = adjacent
                the_id = op(tok.id, count)
                oldtok = tok
                tok = next((i for i in tokens if i.id == the_id), False)
                if not tok:
                    continue
                adjstuff = adjacent

            # get the part of the token to search (word, lemma, index, etc)
            tosearch = getattr(tok, attrib)
            # deal with possible ints
            if isinstance(pattern, int) and isinstance(tosearch, int):
                if pattern != tosearch:
                    continue
            elif isinstance(tosearch, int) and not isinstance(pattern, int):
                tosearch = str(tosearch)

            # turn pos tags into word classes
            if attr == 'x':
                from corpkit.dictionaries.word_transforms import taglemma
                tosearch = taglemma.get(tosearch.lower(), tosearch.lower())
            
            # search pattern against what we grabbed
            if not re.search(pattern, tosearch):
                continue

            # this part for adjacency searching
            #justop = {k: v for k, v in search.items()
            #          if k.startswith('+') or k.startswith('-')}
            #if not repeating:
            #    justop = False
            #if justop:
            #    needed_matches = 0
            #    for k, v in justop.items():
            #        import operator
            #        mapping = {'+': operator.add, '-': operator.sub}
            #        op, count = mapping.get(k[0]), int(k[1])
            #        newtoks = [s.get_token_by_id(op(tok.id, count))]
            #        res = simple_searcher(newtoks, k[0], v, k[-1], repeating=False)
            #        if res:
            #            needed_matches += 1
            #    if not needed_matches >= len(justop):
            #        continue

            # return governor, dependent, or match
            if adjacent:
                tok = oldtok

            matches |= locate_tokens(tok, deprole, attr, adjacent=adjstuff)

        return matches

    # i am a bottleneck
    def search_function(deprole, pattern):
        matches = set()
        if deprole == 'm':
            mcs = [v for k, v in deps._links_by_type.items() if re.search(pattern, k)]
            # for each list of links
            for el in mcs:
                # for each link
                for link in el:
                    # simple mode: add the dependent token
                    matches.add(s.get_token_by_id(link.dependent.idx))
        else:
            # can this be improved? surely somehow using _links_by_type
            for tok in tokens:
                for l in deps.links:
                    if not re.search(pattern, l.type):
                        continue
                    in_deps = [i for i in deps.links if getattr(i, fmatch[deprole]).idx == tok.id]
                    for lnk in in_deps:
                        matches.add(s.get_token_by_id(getattr(lnk, bmatch[deprole]).idx))

            # improvement here?
            #for l in deps.links:
            #    if re.search(pat, l.type):
            #        if deprole == 'g':
            #            gotten = [s.get_token_by_id(i.dependent.idx) for i in deps.links \
            #                      if i.dependent.idx == l.governor.idx]
            #        elif deprole == 'd':
            #            gotten = [s.get_token_by_id(i.dependent.idx) for i in deps.links \
            #                      if i.dependent.idx == l.governor.idx]
            #        for tk in gotten:
            #            matches.add(tk)

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

    def show_sent_id(token):
        # this could be slow
        #return int(token.getparent().getparent().get('id')) - 1
        # faster?
        return int(s.id) - 1

    ####################################################
    ################## SHOW FUNCTIONS ##################
    ####################################################

    def show_this(tokenx, this):

        if this == 'f':
            return show_function(tokenx)
        if this == 'r':
            return show_distance(tokenx)
        if this == 's':
            return show_sent_id(tokenx)

        if this == 'x':
            from corpkit.dictionaries.word_transforms import taglemma
            postp = taglemma
        elif this == 'l':
            from corpkit.dictionaries.word_transforms import wordlist
            postp = wordlist
        else:
            postp = {}

        t = lookup.get(this, this)

        if hasattr(tokenx, t):
            att = getattr(tokenx, t)
            if isinstance(att, int):
                return postp.get(att - 1, att - 1)
            else:
                return postp.get(att.lower(), att)

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

    def show_governor(tok, _):
        for i in deps.links:
            if i.dependent.idx == tok.id:
                gov = s.get_token_by_id(i.governor.idx)
                if gov:
                    return gov
                else:
                    return 'root'
        return 'none' # not possible?

    def show_adjacent(tok, repeat, space):
        import operator
        mapping = {'+': operator.add, '-': operator.sub}
        op, count = mapping.get(space[0]), int(space[1])
        return next((i for i in tokens if i.id == op(tok.id, count)), 'none')

    def show_head(tok, _):
        if not corefs:
            return 'none'
        for coref in corefs:
            for index, mention in enumerate(coref.mentions):
                if not representative and mention.representative:
                    continue
                if not non_representative and not mention.representative:
                    continue
                # if current token is a coref chain
                if tok == mention.head:
                    if index > 0:
                        return mention.siblings[0].head
                    else:
                        return tok
        return 'none'

    def show_dependent(tok, repeat):
        """get nth dependent"""
        matches = []
        for i in deps.links:
            if i.governor.idx == tok.id:
                dp = s.get_token_by_id(i.dependent.idx)
                if dp:
                    matches.append(dp)
                    if len(matches) == repeat:
                        break
        if not matches:
            return 'none'
        else:
            return matches[-1]
        
    def show_match(tok, _):
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
                   'h': show_head,
                   'm': show_match}

    ####################################################
    ################ PROCESSING FUNCS ##################
    ####################################################

    def get_list_of_lookup_funcs(show_bit):
        """take a single search/show_bit type, return match"""
        #show_bit = [i.lstrip('n').lstrip('b') for i in show_bit]
        ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 'r']
        starts = ['d', 'g', 'm', 'n', 'b', 'h', '+', '-']
        show_bit = show_bit.lstrip('n')
        show_bit = show_bit.lstrip('b')
        show_bit = list(show_bit)
        if show_bit[-1] not in ends:
            show_bit.append('w')
        if show_bit[0] not in starts:
            show_bit.insert(0, 'm')
        if show_bit[0] in ['+', '-']:
            return show_adjacent, show_bit[-1]
        return lookup_show.get(show_bit[0]), show_bit[1]

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

            if conc:
                for r, c in zip(res, conc_res):
                    if r and c:
                        resultlist.append(r)
                        conclist.append(c)
            else:
                for r in res:
                    resultlist.append(r)

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

    def remove_words_from_concline(start, middle, end, wordlist):
        """Remove words from conc line if they aren't in wordlist"""
        if not wordlist:
            return start, middle, end
        start = [i for i in start if i in wordlist]
        end = [i for i in end if i in wordlist]
        return start, middle, end

    def process_a_submatch(match, repeat, tokens):
        """
        For ngrams, etc., we have to repeat over results. so, this is for 
        each repeat
        """
        # make a conc line with just speaker name so far
        from corpkit.process import get_speakername
        speakr = get_speakername(s)
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
            if conc:
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
                for sing in single_result:
                    processed_toklist.append(sing)
        
        if language_model:
            return '-spl-it-'.join(processed_toklist), conc_line
            #return tuple(processed_toklist), conc_line
        
        # if no conc at all, return the empty ish one and a string of token(s)
        if not conc:
            return processed_toklist, False
        #if not conc:
        #    return processed_toklist, conc_line

        # if we're concordancing:
        # now we have formatted tokens as a list. we need to split
        # it into start, middle and end, unless only_format_match
        else:
            if not only_format_match:
                st = [w for index, w in enumerate(processed_toklist) if index < first_in_gram]
                md = [w for index, w in enumerate(processed_toklist) \
                      if index >= first_in_gram \
                      and index <= last_in_gram]
                ed = [w for index, w in enumerate(processed_toklist) if index > last_in_gram]
                
                st, md, ed = remove_words_from_concline(st, md, ed, whitelist)
                
                start = ' '.join(st)
                end = ' '.join(ed)
                middle = separator.join(md)
            else:
                middle = separator.join(processed_toklist)

            for bit in start, middle, end:
                conc_line.append(bit)

        return [middle], [conc_line]
        
    def get_num_repeats(tok):
        num = 0
        for i in deps.links:
            if i.governor.idx == tok.id:
                if s.get_token_by_id(i.dependent.idx):
                    num += 1
        return num if num else 1

    def make_unicode(s):
        if isinstance(s, (int, float)):
            s = str(s)
        try:
            return s.decode('utf-8', 'ignore')
        except (AttributeError, UnicodeEncodeError) as err:
            return s

    def process_a_token(token, show):
        """
        Take entire show argument, and a token of interest,
        and return slash sep token
        """
        #result = []
        #for val in show:
        #    get_tok, show_bit = get_list_of_lookup_funcs(val)
        #    tok = get_tok(token)
        #    to_show = show_this(tok, show_bit)
        #    if isinstance(exclude, dict) and val in exclude:
        #        if re.search(exclude[val], to_show):
        #            return
        #    result.append(to_show)
        #if result:

        results = []
        output = []
        
        # the whole operation needs to loop if we're getting dependents
        repeats = get_num_repeats(token) if any(x.startswith('d') for x in show) else 1
        
        for repeat in range(1, repeats + 1):
            single_token_bits = []
            for val in show:
                get_tok, show_bit = get_list_of_lookup_funcs(val)
                if get_tok == show_adjacent:
                    tok = get_tok(token, repeat, val)
                else:
                    # get the token we need to format
                    tok = get_tok(token, repeat)
                # get the word/lemma text of the token
                to_show = show_this(tok, show_bit)
                if isinstance(exclude, dict) and val in exclude:
                    if re.search(exclude[val], to_show):
                        return
                single_token_bits.append(to_show)
            results.append(single_token_bits)
        
        for result in results:

            # convert to unicode
            result = [make_unicode(i) for i in result]

            if no_punct:
                if not all(re.search(is_a_word, i) for i in result):
                    return
            if no_closed:
                if isinstance(no_closed, list):
                    nc = no_closed
                else:
                    from corpkit.dictionaries.wordlists import wordlists as wl
                    nc = wl.closedclass
                if all(i in nc for i in result):
                    return
            if kwargs.get('no_root'):
                if any(i == 'root' for i in result):
                    return
            if kwargs.get('no_none'):
                if any(i == 'none' for i in result):
                    return

            output.append('/'.join(i.replace('/', '-slash-') for i in result))
            
        return output

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

    deptrans = {'a': 'basic-dependencies',
                'b': 'collapsed-dependencies',
                'c': 'collapsed-ccprocessed-dependencies'}

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

    # iterate over sentences

    for s in sents:

        # all search matches go here
        matching_tokens = []
        dep_type = dep_type.replace('-', '_')
        deps = getattr(s, deptrans.get(dep_type, dep_type))
        
        # remove punctuation if need be
        tokens = s.tokens
        if no_punct:
            tokens = [w for w in tokens if re.search(is_a_word, w.word)]
        if no_closed:
            from corpkit.dictionaries.wordlists import wordlists as wl
            tokens = [w for w in tokens if w.word.lower() not in wl.closedclass]

        for srch, pat in search.items():
            if srch[0] in ['+', '-']:
                deprole, attr = srch[-2], srch[-1]   
                adj = (mapping.get(srch[0]), int(srch[1]))
            else:
                adj, deprole, attr = False, srch[0], srch[-1]
            matching_tokens += simple_searcher(tokens, deprole, pat, attr, adjacent=adj)

        matching_tokens = remove_by_mode(matching_tokens, searchmode)

        # exclude in the same way if need be
        removes = []
        if exclude:
            for excl, expat in exclude.items():
                if excl[0] in ['+', '-']:
                    exclv, exattr = excl[-2], excl[-1]   
                    adj = (mapping.get(excl[0]), int(excl[1]))
                else:
                    adj, exclv, exattr = False, excl[0], excl[-1]
                for remove in simple_searcher(tokens, exclv, expat, exattr, adjacent=adj):
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
            if conc:
                for r, c in zip(res, conc_res):
                    if r and c:
                        result.append(r)
                        conc_result.append(c)
            else:
                for r in res:
                    result.append(r)

    if 'c' in show:
        result = sum(result)

    if isinstance(conc, str) and \
        conc.lower() == 'only':
        result = []

    if not conc:
        conc_result = []

    sents = None
    deps = None
    matching_tokens = None
    tokens = None

    return result, conc_result
