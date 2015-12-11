#!/usr/bin/python

def interrogator(path,
                search,
                query = 'any', 
                show = 'words',
                exclude = False,
                case_sensitive = False,
                lemmatise = False, 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'collapsed-ccprocessed-dependencies',
                quicksave = False,
                printstatus = True,
                root = False,
                df1_always_df = False,
                just_speakers = False,
                excludemode = 'any',
                searchmode = 'all',
                **kwargs):
    """Interrogate a corpus of texts for a lexicogrammatical phenomenon

    :param path: Path to a corpus
    :type path: str -- corpus path; list of strings -- list of paths
    
    :param search: What query should be matching
        - t/tregex
        - w/word
        - l/lemma
        - f/function
        - g/governor
        - d/dependent
        - p/pos
        - i/index
        - n/ngrams
    :type search: str, or, for dependencies, a dict like {'w': 'help', 'p': r'^V'}

    :param searchmode: Return results matching any/all criteria
    :type searchmode: str ('any'/'all')

    :param exclude: The inverse of `search`, removing results from search
    :type exclude: dict -- {'l': 'be'}

    :param excludemode: Exclude results matching any/all criteria
    :type excludemode: str ('any'/'all')
    
    :param query: A search query for the interrogation
    :type query: str -- regex/Tregex pattern; dict -- ``{name: pattern}``; list -- word list to match

    :param show: What to output. If multiple strings are passed, results will be colon-separated, in order
        - t/tree
        - w/word
        - l/lemma
        - g/governor
        - d/dependent
        - f/function
        - p/pos
        - i/index
        - a/distance from root
    :type show: list of strings

    :param lemmatise: Do lemmatisation on results
    :type lemmatise: bool
        
    :param lemmatag: Explicitly pass a pos to lemmatiser (generally when data is unparsed)
    :type lemmatag: False/'n'/'v'/'a'/'r'
    
    :param titlefilter: Strip 'mr, 'the', 'dr.' etc. from multiword results (turns 'phrases' on)
    :type titlefilter: bool
    
    :param spelling: Convert all to U.S. or U.K. English
    :type spelling: False/'US'/'UK'
        
    :param phrases: Use if your expected results are multiword (e.g. searching for NP, with
                    show as 'w'), and thus need tokenising
    :type phrases: bool
        
    :param dep_type: The kind of Stanford CoreNLP dependency parses you want to use:
    :type dep_type: str -- 'basic-dependencies'/'a', 'collapsed-dependencies'/'b', 'collapsed-ccprocessed-dependencies'/'c'
    
    :param quicksave: Save result as pickle to saved_interrogations/*quicksave* on completion
    :type quicksave: str
    
    :param gramsize: size of ngrams (default 2)
    :type gramsize: int

    :param split_contractions: make "don't" et al into two tokens
    :type split_contractions: bool

    :param num_proc: how many parallel processes to run -- default is the number of cores
    :type num_proc: int

    :returns: A named tuple, with ``.query``, ``.results``, ``.totals`` attributes. 
              If multiprocessing is invoked, result may be a dict containing corpus names, queries or speakers as keys.

    """
    import corpkit
    from corpkit.process import add_corpkit_to_path
    from corpkit.process import tregex_engine
    from corpkit.process import add_nltk_data_to_nltk_path
    
    # some non-Python resources need to explicitly be added to path
    add_corpkit_to_path()

    import os
    import re
    import signal
    import gc

    import collections
    import warnings
    import nltk
    import numpy

    import pandas as pd
    from collections import Counter
    from time import localtime, strftime
    from pandas import DataFrame, Series

    from corpkit.tests import check_pytex, check_t_kinter
    from corpkit.textprogressbar import TextProgressBar

    import dictionaries
    from dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

    # nltk data path for tokeniser/lemmatiser
    if 'nltk_data_path' in kwargs.keys():
        if kwargs['nltk_data_path'] not in nltk.data.path:
            nltk.data.path.append(kwargs['nltk_data_path'])
    locdir = '/Users/daniel/work/corpkit/nltk_data'
    if locdir not in nltk.data.path:
        nltk.data.path.append(locdir)

    # prefer ipython to python if the user has it
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    
    # check for gui, pythontex
    tk = check_t_kinter()
    have_python_tex = check_pytex()

    # multiprocessing progress bar
    if 'denominator' in kwargs.keys():
        denom = kwargs['denominator']
    else:
        denom = 1
    if 'startnum' in kwargs.keys():
        startnum = kwargs['startnum']
    else:
        startnum = 0

    # determine if multiquery
    is_multiquery = False
    if hasattr(path, '__iter__'):
        is_multiquery = True
        if 'postounts' in path[0]:
            spelling = 'UK'
    if type(query) == dict or type(query) == collections.OrderedDict:
        is_multiquery = True
    if just_speakers:
        if just_speakers == 'each':
            is_multiquery = True
        if type(just_speakers) == str:
            if just_speakers != 'each':
                just_speakers = [just_speakers]
        if type(just_speakers) == list:
            if len(just_speakers) > 1:
                is_multiquery = True

    # regex type
    retype = type(re.compile('hello, world'))

    # just for me: convert spelling automatically for bipolar
    if not is_multiquery:
        if 'postcounts' in path:
            spelling = 'UK'

    # don't print so much stdout in the GUI
    if root:
        shouldprint = False
    else:
        shouldprint = True

    # run pmultiquery if so
    if is_multiquery:
        from corpkit.multiprocess import pmultiquery
        d = { 'path': path, 
              'search': search,
              'query': query,
              'show': show,
              'lemmatise': lemmatise, 
              'titlefilter': titlefilter, 
              'lemmatag': lemmatag, 
              'print_info': shouldprint, 
              'spelling': spelling, 
              'phrases': phrases, 
              'dep_type': dep_type, 
              'quicksave': quicksave, 
              'df1_always_df': df1_always_df,
              'just_speakers': just_speakers, 
              'root': root,}
        
        if 'note' in kwargs.keys() and kwargs['note'] is not False:
            d['note'] = kwargs['note']

        if 'num_proc' in kwargs.keys():
            d['num_proc'] = kwargs['num_proc']

        return pmultiquery(**d)

    if 'paralleling' in kwargs.keys():
        paralleling = kwargs['paralleling']
    else:
        paralleling = False

    # multiple progress bars when multiprocessing
    par_args = {}
    if not root:
        from blessings import Terminal
        term = Terminal()
        par_args['terminal'] = term
        par_args['linenum'] = paralleling

    the_time_started = strftime("%Y-%m-%d %H:%M:%S")
    
    # check if we are in ipython
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    def unsplitter(lst):
        """unsplit contractions and apostophes from tokenised text"""
        unsplit = []
        for index, t in enumerate(lst):
            if index == 0 or index == len(lst) - 1:
                unsplit.append(t)
                continue
            if "'" in t and not t.endswith("'"):
                rejoined = ''.join([lst[index - 1], t])
                unsplit.append(rejoined)
            else:
                if not "'" in lst[index + 1]:
                    unsplit.append(t)
        return unsplit

    def animator(progbar, count, tot_string = False, linenum = False, terminal = False, 
                 init = False, length = False):
        """
        Animates progress bar in unique position in terminal
        Multiple progress bars not supported in jupyter yet.
        """
        if init:
            from textprogressbar import TextProgressBar
            return TextProgressBar(length, dirname = tot_string)
        if type(linenum) == int:
            with terminal.location(0, terminal.height - (linenum + 1)):
                if tot_string:
                    progbar.animate(count, tot_string)
                else:
                    progbar.animate(count)
        else:
            if tot_string:
                progbar.animate(count, tot_string)
            else:
                progbar.animate(count) 

    def signal_handler(signal, frame):
        """
        Pause on ctrl+c, rather than just stop loop
        """       
        import signal
        import sys
        from time import localtime, strftime
        time = strftime("%H:%M:%S", localtime())
        sel = raw_input('\n\n%s: Paused. Press return to resume, or type exit to quit: \n' % time)
        if sel.startswith('e') or sel.startswith('E'):
            sys.exit(0)
        else:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Interrogation resumed.\n' % time
    signal.signal(signal.SIGINT, signal_handler)
    
    def gettag(query, lemmatag = False):
        """
        Find tag for WordNet lemmatisation
        """
        import re
        if lemmatag is False:
            tag = 'n' # same default as wordnet
            # attempt to find tag from tregex query
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)')
            tagchecker = re.compile(r'^[A-Z]{1,4}$')
            treebank_tag = re.findall(tagfinder, query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', ''))
            if re.match(tagchecker, treebank_tag[0]):
                if treebank_tag[0].startswith('J'):
                    tag = 'a'
                elif treebank_tag[0].startswith('V') or treebank_tag[0].startswith('M'):
                    tag = 'v'
                elif treebank_tag[0].startswith('N'):
                    tag = 'n'
                elif treebank_tag[0].startswith('R'):
                    tag = 'r'
        elif lemmatag:
            tag = lemmatag
            tagchecker = re.compile(r'^[avrn]$')
            while not re.match(tagchecker, lemmatag):
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: WordNet POS tag "%s" not recognised.\n It must be:\n\n ' \
                    '              a: (adjective)' \
                    '              n: (noun)' \
                    '              r: (adverb)' \
                    '              v: (verb)\n\nYour selection: ' % (time, lemmatag))
                lemmatag = selection
        return tag
    
    def processwords(list_of_matches, lemmatag = False):
        """
        Normalise matches from interrogations

        -lowercase
        -remove non alnum
        -tokenise if phrases
        -put together with slashes
        """
        list_of_matches = [w.lower() for w in list_of_matches]
        # remove nonwords, strip . to normalise "dr."
        if translated_option != 'o' and translated_option != 'u':
            list_of_matches = [w.lstrip('.').rstrip('.') for w in list_of_matches if re.search(regex_nonword_filter, w)]
    
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases and not n_gramming:
            from nltk import word_tokenize as word_tokenize
            list_of_matches = [word_tokenize(i) for i in list_of_matches]

        # this is just for plaintext ... should convert to unicode on file open
        if datatype == 'plaintext':
            try:
                list_of_matches = [unicode(w, errors = 'ignore') for w in list_of_matches]
            except TypeError:
                pass

        if not dependency and exclude and 'w' in exclude.keys():
            list_of_matches = [w for w in list_of_matches if not re.match(exclude['w'], w)]

        if lemmatise or 'l' in show:
            if not dependency:
                tag = gettag(query, lemmatag = lemmatag)
                lemmata = lemmatiser(list_of_matches, tag)
                tups = zip(list_of_matches, lemmata)
                res = []
                for w, l in tups:
                    single_result = []
                    if exclude and 'l' in exclude.keys():
                        if re.match(exclude['l'], l):
                            continue
                    if 'w' in show:
                        single_result.append(w)
                    if 'l' in show:
                        single_result.append(l)
                    # bad fix:
                    # this currently says, if pos in show, there must only be pos ...
                    if 'p' in show:
                        if lemmatise:
                            single_result.append(l)
                        else:
                            single_result.append(w)

                    single_result = '/'.join(single_result)
                    res.append(single_result)
                list_of_matches = res

        if titlefilter and not dependency:
            list_of_matches = titlefilterer(list_of_matches)
        if spelling:
            list_of_matches = convert_spelling(list_of_matches, spelling = spelling)

        
        # turn every result into a single string again if need be:
        if phrases:
            output = []
            for res in list_of_matches:
                joined = ' '.join(res)
                output.append(joined)
            return output
        else:
            return list_of_matches

    def lemmatiser(list_of_words, tag):
        """take a list of unicode words and a tag and return a lemmatised list."""
        
        output = []
        for entry in list_of_words:
            if phrases:
                # just get the rightmost word
                word = entry[-1]
                entry.pop()
            else:
                word = entry
            if translated_option.startswith('u'):
                if word in taglemma:
                    word = taglemma[word]
                else:
                    if word == 'x':
                        word = 'Other'
            # only use wordnet lemmatiser when appropriate
            elif not dependency:
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            # do the manual_lemmatisation
            else:
                if word in wordlist:
                    word = wordlist[word]
            if phrases:
                entry.append(word)
                output.append(entry)
            else:
                output.append(word)
        return output

    def titlefilterer(list_of_matches):
        from dictionaries.wordlists import wordlists
        badwords = wordlists.titles + wordlists.closedclass
        output = []
        for result in list_of_matches:
            head = result[-1]
            non_head = len(result) - 1
            title_stripped = [token for token in result[:non_head] if token.rstrip('.') not in badwords]
            title_stripped.append(head)
            output.append(title_stripped)
        return output

    def convert_spelling(list_of_matches, spelling = 'US'):
        from dictionaries.word_transforms import usa_convert
        if spelling == 'UK':
            usa_convert = {v: k for k, v in usa_convert.items()}
        output = []
        for result in list_of_matches:
            if not phrases:
                result = result.split('/')
            for index, i in enumerate(result):
                try:
                    result[index] = usa_convert[i]
                except KeyError:
                    pass
            output.append('/'.join(result))
        return output

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

    def dep_searcher(sents):
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
        
        result = []
        for s in sents:
            lks = []
            deps = get_deps(s, dep_type)
            tokens = s.tokens
            for opt, pat in search.items():
                pat = filtermaker(pat)
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

            if only_count:
                result.append(len(lks))
                continue

            # figure out what to show
            for lk in lks:
                single_result = {}
                node = deps.get_node_by_idx(lk.id)

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
                            single_result['f'] = i.type
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

                if not only_count:
                    
                    # add them in order
                    out = []
                    for i in show:
                        out.append(single_result[i])

                    result.append('/'.join(out))
        
        if 'c' in show:
            result = sum(result)

        return result

    def tok_by_list(pattern, list_of_toks):
        """search for regex in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        matches = [m for m in list_of_toks if m in pattern]
        for m in matches:
            result.append(m)
        return result

    def tok_ngrams(pattern, list_of_toks, split_contractions = True):
        from collections import Counter
        global gramsize
        import re
        ngrams = Counter()
        result = []
        # if it's not a compiled regex
        list_of_toks = [x for x in list_of_toks if re.search(regex_nonword_filter, x)]

        if not split_contractions:
            list_of_toks = unsplitter(list_of_toks)
            
            #list_of_toks = [x for x in list_of_toks if "'" not in x]
        for index, w in enumerate(list_of_toks):
            try:
                the_gram = [list_of_toks[index+x] for x in range(gramsize)]
                if not any(re.search(query, x) for x in the_gram):
                    continue
                #if query != 'any':
                #    if not any(re.search(query, w) is True for w in the_gram):
                #        continue
                ngrams[' '.join(the_gram)] += 1
            except IndexError:
                pass
        # turn counter into list of results
        for k, v in ngrams.items():
            if v > 1:
                for i in range(v):
                    result.append(k)
        return result

    def tok_by_reg(pattern, list_of_toks):
        """search for regex in plaintext corpora"""
        try:
            comped = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'

        matches = [m for m in list_of_toks if re.search(comped, m)]

        return matches

    def plaintext_regex_search(pattern, plaintext_data):
        """search for regex in plaintext corpora"""
        result = []
        #if not pattern.startswith(r'\b') and not pattern.endswith(r'\b'):
            #pattern = r'\b' + pattern + '\b'
        try:
            compiled_pattern = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'
        matches = re.findall(compiled_pattern, plaintext_data)
        for index, i in enumerate(matches):
            if type(i) == tuple:
                matches[index] = i[0]
        return matches

    def plaintext_simple_search(pattern, plaintext_data):
        """search for tokens in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        try:
            tmp = re.compile(pattern)
        except:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Query %s' % (thetime, error_message)
            return 'Bad query'

        for p in pattern:
            if case_sensitive:
                pat = re.compile(r'\b' + re.escape(p) + r'\b')
            else:
                pat = re.compile(r'\b' + re.escape(p) + r'\b', re.IGNORECASE)
            if not any_plaintext_word:
                matches = re.findall(pat, plaintext_data)
                for m in range(len(matches)):
                    result.append(p)
            else:
                for m in plaintext_data.split():
                    result.append(m)
        return result

    def get_speaker_names_from_xml_corpus(path):
        import os
        import re
        from bs4 import BeautifulSoup
        names = []
        # parsing html with regular expression! :)
        speakid = re.compile(r'<speakername>[\s\n]*?([^\s\n]+)[\s\n]*?<.speakername>', re.MULTILINE)
        for (root, dirs, fs) in os.walk(path):
            for f in fs:
                with open(os.path.join(root, f), 'r') as fo:
                    txt = fo.read()
                    res = re.findall(speakid, txt)
                    if res:
                        res = [i.strip() for i in res]
                        for i in res:
                            if i not in names:
                                names.append(i)
        return list(sorted(set(names)))

    def slow_tregex(sents):
        """do the speaker-specific version of tregex queries"""
        import os
        import bs4
        # first, put the relevant trees into temp file
        if 'outname' in kwargs.keys():
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        to_write = '\n'.join([sent._parse_string.strip() for sent in sents if sent.parse_string is not None]).encode('utf-8', errors = 'ignore')
        with open(to_open, "w") as fo:
            fo.write(to_write)
        q = search.values()[0]
        res = tregex_engine(query = q, 
                            options = ['-o', '-%s' % translated_option], 
                            corpus = to_open,
                            root = root)
        if root:
            root.update()
        os.remove(to_open)
        return res

    def get_deps(sentence, dep_type):
        if dep_type == 'basic-dependencies':
            return sentence.basic_dependencies
        if dep_type == 'collapsed-dependencies':
            return sentence.collapsed_dependencies
        if dep_type == 'collapsed-ccprocessed-dependencies':
            return sentence.collapsed_ccprocessed_dependencies

    def get_stats(sents):
        """get a bunch of frequencies on interpersonal phenomena"""
        import os
        import re  
        # first, put the relevant trees into temp file
        if 'outname' in kwargs.keys():
            to_open = 'tmp-%s.txt' % kwargs['outname']
        else:
            to_open = 'tmp.txt'
        with open(to_open, "w") as fo:
            for sent in sents:
                statsmode_results['Sentences'] += 1
                fo.write(sent.parse_string.rstrip().encode('utf-8', errors = 'ignore') + '\n')
                deps = get_deps(sent, dep_type)
                numpass = len([x for x in deps.links if x.type.endswith('pass')])
                statsmode_results['Passives'] += numpass
                statsmode_results['Tokens'] += len(sent.tokens)
                statsmode_results['Words'] += len([w for w in sent.tokens if w.word.isalnum()])
                #statsmode_results['Unique words'] += len(set([w.word.lower() for w in sent.tokens if w.word.isalnum()]))
                #statsmode_results['Unique lemmata'] += len(set([w.lemma.lower() for w in sent.tokens if w.word.isalnum()]))

        # count moods via trees          (/\?/ !< __)
        from dictionaries.process_types import processes
        from corpkit.other import as_regex
        tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     #'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                     #'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                     'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Open class words': r'/^(NN|JJ|VB|RB)/ < __',
                     'Closed class words': r'__ !< __ !> /^(NN|JJ|VB|RB)/',
                     'Clauses': r'/^S/ < __',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Mental processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.mental, boundaries = 'w'),
                     'Verbal processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.verbal, boundaries = 'w'),
                     'Relational processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % as_regex(processes.relational, boundaries = 'w')}

        for name, q in sorted(tregex_qs.items()):
            res = tregex_engine(query = q, 
                  options = ['-o', '-C'], 
                  corpus = to_open,  
                  root = root)
            statsmode_results[name] += int(res)
            global numdone
            numdone += 1
            if root:
                root.update()
            if not root:
                tot_string = str(numdone + 1) + '/' + str(total_files * len(tregex_qs.keys()))
                if 'outname' in kwargs.keys():
                    tot_string = '%s: %s' % (kwargs['outname'], tot_string)
                animator(p, numdone, tot_string, **par_args)
            if 'note' in kwargs.keys() and kwargs['note'] is not False:
                kwargs['note'].progvar.set((numdone * 100.0 / (total_files * len(tregex_qs.keys())) / denom) + startnum)
        os.remove(to_open)

    def tabler(subcorpus_names, list_of_dicts, num_rows):
        """make a word table showing num_rows results"""
        import pandas as pd
        cols = []
        for subcorp, data in zip(subcorpus_names, list_of_dicts):
            col = pd.Series([w for w, v in data.most_common(num_rows)], name = subcorp)
            cols.append(col)
        word_table = pd.concat(cols, axis = 1)
        return word_table

    # a few things are off by default:
    only_count = False
    using_tregex = False
    n_gramming = False
    dependency = False
    plaintext = False
    tokens = False
    statsmode = False
    split_con = True
    search_iterable = False

    # determine what kind of data the corpus is
    # this currently slows things down with huge corpora, 
    # so judge from folder name first  
    if type(path) == str and path.endswith('-parsed'):
        datatype = 'parse'
    elif type(path) == str and path.endswith('-tokenised'):
        datatype = 'tokens'
    else:
        from corpkit.process import determine_datatype
        datatype = determine_datatype(path)

    # some empty lists we'll need
    dicts = []
    allwords_list = []
    
    regex_nonword_filter = re.compile("[A-Za-z0-9:_]")
    
    # fix up search
    if type(search) == str:
        search = search[0].lower()
        if not search.lower().startswith('t') and not search.lower().startswith('n') \
                                              and datatype == 'parse':
            search_iterable = True
            if query == 'any':
                query = r'.*'
        search = {search: query}

    possb = ['d', 'g', 'i', 'c', 'a', 'p', 'l', 'w', 't', 'f']
    if not any(i in possb for i in search.keys()):
        raise ValueError('search argument "%s" unrecognised.' % search.keys())
    if len(search.keys()) > 1 and 't' in search.keys():
        raise ValueError('if "t" in search, it must be the only list item')

    # fix up exclude naming conventions, convert lists to regex
    fixed_exclude = {}
    if exclude:
        for k, v in exclude.items():
            if type(v) == list:
                from corpkit.other import as_regex
                v = as_regex(v, boundaries = 'l', case_sensitive = case_sensitive)
            if k != k.lower()[0]:
                fixed_exclude[k.lower()[0]] = v
            else:
                fixed_exclude[k] = v
        exclude = fixed_exclude

    if not search_iterable:
        query = search.values()[0]

    if type(show) == str or type(show) == unicode:
        show = [show.lower()[0]]

    for index, t in enumerate(show):
        show[index] = t.lower()[0]

    possb = ['d', 'g', 'i', 'c', 'a', 'p', 'l', 'w', 't', 'f']
    only_dep = ['d', 'g', 'i', 'a', 'f']
    if not any(i in possb for i in show):
        raise ValueError('show argument "%s" unrecognised.' % show)
    if len(show) > 1 and 'c' in show:
        raise ValueError('if "c" in show, it must be the only list item')
    if 't' in search.keys() and any(i in only_dep for i in show):
        raise ValueError('If searching trees, show can not include: %s' % ', '.join(only_dep))

    # Tregex option:
    translated_option = False
    from corpkit.other import as_regex
    
    if datatype == 'parse':
        if 't' in search.keys():
            using_tregex = True

    if datatype == 'plaintext':
        plaintext = True

    elif datatype == 'tokens':
        tokens = True


    if using_tregex:
        optiontext = 'Searching parse trees'
        if 'p' in show:
            dep_funct = slow_tregex
            translated_option = 'u'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 't' in show:
            dep_funct = slow_tregex
            translated_option = 'o'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif 'w' in show:
            dep_funct = slow_tregex
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'c' in show:
            dep_funct = slow_tregex
            count_results = {}
            only_count = True
            translated_option = 'C'
            if type(query) == list:
                query = r'/%s/ !< __'  % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif 'l' in show:
            dep_funct = slow_tregex
            translated_option = 't'
            lemmatise = True
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'

    elif datatype == 'plaintext':
        optiontext = 'Searching plaintext corpus'
        if 'regex' in kwargs.keys() and kwargs['regex'] is False:
            translated_option = 's'
            if query == 'any':
                any_plaintext_word = True
            else:
                any_plaintext_word = False
        else:
            translated_option = 'r'
            if query == 'any':
                query = r'[^\s]+'
            if type(query) == list:
                query = as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            
    elif datatype == 'tokens':
        if 'w' in search.keys():
            tokens = True
            if type(query) == list:
                translated_option = 'e'
                optiontext = 'Tokens via list.'
                dep_funct = tok_by_list
            else:
                translated_option = 'h'
                optiontext = 'Tokens via regular expression.'
                dep_funct = tok_by_reg
        if 'n' in search.keys():
            translated_option = 'j'
            tokens = True
            lemmatise = False
            optiontext = 'Get ngrams from tokens.'
            if query == 'any':
                query = r'.*'
            if type(query) == list:
                query = as_regex(query, boundaries = 'l', case_sensitive = case_sensitive)
            else:
                try:
                    if not case_sensitive:
                        query = re.compile(query, re.IGNORECASE)
                    else:
                        query = re.compile(query)
                except:
                    import traceback
                    import sys
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    lst = traceback.format_exception(exc_type, exc_value,
                                  exc_traceback)
                    error_message = lst[-1]
                    thetime = strftime("%H:%M:%S", localtime())
                    print '%s: Query %s' % (thetime, error_message)
                    return 'Bad query'
            global gramsize
            if 'gramsize' in kwargs.keys():
                gramsize = kwargs['gramsize']
            else:
                gramsize = 2
            dep_funct = tok_ngrams

    elif datatype == 'parse':
        if 'n' not in search.keys() and 't' not in search.keys():
            translated_option = 'y'
            dependency = True
            optiontext = 'Dependency querying...'
            dep_funct = dep_searcher
            if 'c' in show:
                count_results = {}
                only_count = True

        if 's' in search.keys():
            translated_option = 'v'
            #using_tregex = True
            statsmode = True
            optiontext = 'Getting general stats.'
            dep_funct = get_stats
            if datatype != 'parse':
                print 'Need parsed corpus for this.'
                return

    # initialise nltk lemmatiser only once
    if lemmatise or ('l' in show and not dependency):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    if 'n' in search.keys():
        if datatype == 'parse':
            translated_option = 'n'
            using_tregex = True
            optiontext = 'n-grams only.'
            n_gramming = True
        if datatype == 'tokens':
            translated_option = 'j'
            using_tregex = False
        
        if type(query) == list:
            query = as_regex(query, boundaries = 'word', case_sensitive = case_sensitive)

    if dependency:
        if type(query) == list:
            query = as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            #query = r'(?i)^(' + '|'.join(query) + r')$' 
        if query == 'any':
            query = r'.*'

    # see if fast tregex can be done instead of temp file slow way
    can_do_fast = False
    if using_tregex:
        if just_speakers is False:
            if statsmode is False:
                can_do_fast = True

    if plaintext is True:
        try:
            if tregex_engine(corpus = os.path.join(path, os.listdir(path)[-1]), check_for_trees = True, root = root):
                if not root:
                    decision = raw_input('\nIt appears that your corpus contains parse trees. If using a plaintext search option, your counts will likely be inaccurate.\n\nHit enter to continue, or type "exit" to start again: ')
                    if decision.startswith('e'):
                        return
                else:
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Corpus "%s" contains parse trees. Use "Trees" option.' % (time, os.path.basename(path))
                    root.update()
                    return False
        except:
            pass
    
    # if query is a special query, convert it:
    for k, v in search.items():
        if k == 't' and v == 'any':
            if 'l' in show or 'w' in show:
                search[k] = r'/.?[A-Za-z0-9].?/ !< __'
            else:
                search[k] = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        if k == 't' and v == 'subjects':
            search[k] = r'__ >># @NP'
        if k == 't' and v == 'processes':
            search[k] = r'/VB.?/ >># ( VP >+(VP) (VP !> VP $ NP))'
        if k == 't' and v == 'modals':
            search[k] = r'MD < __'
        if k == 't' and v == 'participants':
            search[k] = r'/(NN|PRP|JJ).?/ >># (/(NP|ADJP)/ $ VP | > VP)'
        if k == 't' and v == 'entities':
            search[k] = r'NP <# NNP'
            titlefilter = True

    # check that there's nothing in the quicksave path
    if quicksave:
        savedir = 'data/saved_interrogations'
        if not quicksave.endswith('.p'):
            quicksave = quicksave + '.p'
        fullpath = os.path.join(savedir, quicksave)
        if os.path.isfile(fullpath):
            # if the file exists, check if the query is pretty much the same
            from corpkit import load_result
            loaded = load_result(quicksave)
            if loaded.query['query'] == query and \
            loaded.query['path'] == path and \
            loaded.query['translated_option'] == translated_option and \
            loaded.query['lemmatise'] == lemmatise and \
            loaded.query['titlefilter'] == titlefilter and \
            loaded.query['spelling'] == spelling and \
            loaded.query['dep_type'] == dep_type and \
            loaded.query['function'] == 'interrogator':
                dup_non_i = 'Duplicate'
            else:
                dup_non_i = 'Non-identical'

            while os.path.isfile(fullpath) and quicksave:
                dict_for_print = '          ' + '\n          '.join(sorted(['%s: %s' % (k, v) for k, v in loaded.query.items()])) + '\n'
                time = strftime("%H:%M:%S", localtime())
                selection = raw_input('\n%s: %s interrogation found in %s:\n\n%s\n' \
                       '          You have the following options:\n\n' \
                       '              a) save with a new name\n' \
                       '              b) turn off "quicksave"\n' \
                       '              c) return the results from %s\n' \
                       '              d) delete %s\n' \
                       '              e) Quickview %s and then decide\n' \
                       '              f) exit\n\nYour selection: ' % (time, dup_non_i, fullpath, dict_for_print, fullpath, fullpath, fullpath))
                if 'a' in selection:
                    sel = raw_input('\nNew save name: ')
                    quicksave = sel
                    if not quicksave.endswith('.p'):
                        quicksave = quicksave + '.p'
                        fullpath = os.path.join(savedir, quicksave)
                elif 'b' in selection:
                    quicksave = False
                elif 'c' in selection:
                    return loaded
                elif 'd' in selection:
                    os.remove(fullpath)
                elif 'e' in selection:
                    print loaded.query
                    print '\n'
                    try:
                        print loaded.results
                    except:
                        print loaded.totals
                    print '\n'
                elif 'f' in selection:
                    print ''
                    return
                else:
                    as_str = str(selection)
                    print '          Choice "%s" not recognised.' % selection

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    def filtermaker(the_filter):
        if type(the_filter) == list:
            from corpkit.other import as_regex
            the_filter = as_regex(the_filter, case_sensitive = case_sensitive)
        try:
            output = re.compile(the_filter)
            is_valid = True
        except:
            is_valid = False
            if root:
                import traceback
                import sys
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lst = traceback.format_exception(exc_type, exc_value,
                              exc_traceback)
                error_message = lst[-1]
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: Filter %s' % (thetime, error_message)
                return 'Bad query'
        
        while not is_valid:
            if root:
                time = strftime("%H:%M:%S", localtime())
                print the_filter
                print '%s: Invalid the_filter regular expression.' % time
                return False
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: filter regular expression " %s " contains an error. You can either:\n\n' \
                '              a) rewrite it now\n' \
                '              b) exit\n\nYour selection: ' % (time, the_filter))
            if 'a' in selection:
                the_filter = raw_input('\nNew regular expression: ')
                try:
                    output = re.compile(r'\b' + the_filter + r'\b')
                    is_valid = True
                except re.error:
                    is_valid = False
            elif 'b' in selection:
                print ''
                return False
        return output

    # dependencies:
    # can't be phrases
    # check if regex valid
    # check if dep_type valid
    if dependency:
        if translated_option == 'v':
            names = get_speaker_names_from_xml_corpus(path)
        
        phrases = False
        
        allowed_dep_types = ['basic-dependencies', 'collapsed-dependencies', 'collapsed-ccprocessed-dependencies']
        
        # allow a b and c shorthand
        if dep_type == 'a':
            dep_type = allowed_dep_types[0]
        if dep_type == 'b':
            dep_type = allowed_dep_types[1]
        if dep_type == 'c':
            dep_type = allowed_dep_types[2]

        while dep_type not in allowed_dep_types:
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: Dependency type "%s" not recognised. Must be one of:\n\n' \
                '              a) basic-dependencies' \
                '              b) collapsed-dependencies' \
                '              c) collapsed-ccprocessed-dependencies\n\nYour selection: ' % (time, dep_type))
            if 'a' in selection:
                dep_type = allowed_dep_types[0]
            elif 'b' in selection:
                dep_type = allowed_dep_types[1]
            elif 'c' in selection:
                dep_type = allowed_dep_types[2]
            else:
                pass

    # get list of subcorpora and sort them ... user input if no corpus found
    got_corpus = False
    while got_corpus is False:
        try:
            sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
            got_corpus = True
        except OSError:
            got_corpus = False
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: Corpus directory not found: " %s ". You can either:\n\n' \
                '              a) enter a new corpus path\n' \
                '              b) exit\n\nYour selection: ' % (time, path))
            if 'a' in selection:
                path = raw_input('\nNew corpus path: ')
            elif 'b' in selection:
                print ''
                return
    
    # treat as one large corpus if no subdirs found
    one_big_corpus = False
    if len(sorted_dirs) == 0:
        #warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        one_big_corpus = True
        # fails if in wrong dir!
        sorted_dirs = [os.path.basename(path)]

    # numerically sort subcorpora if the first can be an int
    # could improve now with is_number, all
    else:
        try:
            check = int(sorted_dirs[0])
            sorted_dirs.sort(key=int)
        except:
            pass

    # if doing dependencies, make list of all files, and a progress bar
    if dependency or plaintext or tokens or can_do_fast is False:
        all_files = []
        for d in sorted_dirs:
            if not one_big_corpus:
                subcorpus = os.path.join(path, d)
            else:
                subcorpus = path
            if dependency:
                files = [f for f in os.listdir(subcorpus) if f.endswith('.xml')]
            else:
                files = [f for f in os.listdir(subcorpus) if not f.startswith('.')]
            
            # skip files not containing speakers...
            if just_speakers:
                rem = []
                for f in files:
                    fp = os.path.join(subcorpus, f)
                    data = open(fp, 'r').read()
                    if any('<speakername>' + name in data for name in just_speakers):
                        rem.append(f)
                files = rem

            all_files.append([d, files])
        total_files = len([item for sublist in all_files for item in sublist[1]])
        sorted_dirs = all_files
        c = 0
        if not root:
            tstr = False
            if 'outname' in kwargs.keys():
                if dependency or plaintext or tokens:
                    tstr = '%s: %d/%d' % (kwargs['outname'], 0, total_files)
                else:
                    tstr = '%s: %d/%d' % (kwargs['outname'], 0, len(sorted_dirs))
            if translated_option != 'v':
                p = animator(None, None, init = True, tot_string = tstr, length = total_files, **par_args)
                #p = TextProgressBar(total_files)
            else:
                p = animator(None, None, init = True, tot_string = tstr, length = total_files * 10, **par_args)
                #p = TextProgressBar(total_files * 10)
    
    # if tregex, make progress bar for each dir
    else:
        if not root:
            tstr = False
            if 'outname' in kwargs.keys():
                tstr = '%s: %d/%d' % (kwargs['outname'], 0, len(sorted_dirs))
            p = animator(None, None, tot_string = tstr, init = True, length = len(sorted_dirs), **par_args)

    # loop through each subcorpus
    subcorpus_names = []

    # check for valid query. so ugly.
    if using_tregex:
        if query:
            if not n_gramming:
                q = search.values()[0]
                query = tregex_engine(corpus = False, query = q, options = ['-t'], check_query = True, root = root)
                if query is False:
                    if root:
                        return 'Bad query'
                    else:
                        return
    
    else:
        if dependency or translated_option == 'r' or translated_option == 'h':
            is_valid = True
            try:
                if translated_option == 'r':
                    if type(query) == str:
                        if query.startswith(r'\b'):
                            query = query[2:]
                        if query.endswith(r'\b'):
                            query = query[:-2]
                        if case_sensitive:
                            regex = re.compile(r'\b' + query + r'\b')
                        else:
                            regex = re.compile(r'\b' + query + r'\b', re.IGNORECASE)
                    else:
                        regex = query
                else:
                    if case_sensitive:
                        regex = re.compile(query)
                    else:
                        regex = re.compile(query, re.IGNORECASE)
                is_valid = True
            except re.error:
                is_valid = False
                if root:
                    import traceback
                    import sys
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    lst = traceback.format_exception(exc_type, exc_value,
                                  exc_traceback)
                    error_message = lst[-1]
                    thetime = strftime("%H:%M:%S", localtime())
                    print '%s: Query %s' % (thetime, error_message)
                    return "Bad query"
            while not is_valid:
                time = strftime("%H:%M:%S", localtime())
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Regular expression in query contains an error.' % time
                    return 'Bad query'
                selection = raw_input('\n%s: Regular expression " %s " contains an error. You can either:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, query))
                if 'a' in selection:
                    query = raw_input('\nNew regular expression: ')
                    try:
                        if case_sensitive:
                            regex = re.compile(r'\b' + query + r'\b')
                        else:
                            regex = re.compile(r'\b' + query + r'\b', re.IGNORECASE)
                        is_valid = True
                    except re.error:
                        is_valid = False
                elif 'b' in selection:
                    print ''
                    return

    #print list nicely
    if type(query) == list:
        qtext = ', '.join(query)
    elif type(query) == str or type(query) == unicode:
        qtext = query
    else:
        qtext = 'regex'

    # horrible, format dict query
    if type(search) == dict:
        import pprint
        pp = pprint.PrettyPrinter(indent=0)
        qtext = pp.pformat(search).replace('{', '').replace('}', '')
        qtext = qtext.replace("u'", '').replace('"', '').replace("'", '').replace(', ', '\n                  ')

    global skipped_sents
    skipped_sents = 0

    # begin interrogation
    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print ("\n%s: Beginning corpus interrogation: %s" \
           "\n          Query: '%s'\n          %s" \
           "\n          Interrogating corpus ... \n" % (time, os.path.basename(path), qtext, optiontext) )
    if root:
        print '%s: Interrogating corpus ...' % time
    if root and tk:
        root.update()

    global numdone
    numdone = 0

    for index, d in enumerate(sorted_dirs):
        if using_tregex or n_gramming:
            if can_do_fast or n_gramming:
                subcorpus_name = d
                subcorpus_names.append(subcorpus_name)
                if not root:
                    if paralleling is not False:
                        tstr = '%s: %d/%d' % (kwargs['outname'], index + 1, len(sorted_dirs))
                    else:
                        tstr = False
                    animator(p, index, tstr, **par_args)
                    #animator(p, index, **par_args)
                    #p.animate(index)
                if root and tk:
                    time = strftime("%H:%M:%S", localtime())
                    if not one_big_corpus:
                        print '%s: Interrogating subcorpus: %s' % (time, subcorpus_name)
                    else:
                        print '%s: Interrogating corpus ... ' % time
                    root.update()
                    if 'note' in kwargs.keys() and kwargs['note'] is not False:
                        kwargs['note'].progvar.set(((index + 1) * 100.0 / len(sorted_dirs) / denom) + startnum)
                # get path to corpus/subcorpus
                if len(sorted_dirs) == 1:
                    subcorpus = path
                else:
                    subcorpus = os.path.join(path,subcorpus_name)
        
                if n_gramming:
                    result = []
                    if 'split_contractions' in kwargs.keys():
                        if kwargs['split_contractions'] is True:
                            split_con = True
                        elif kwargs['split_contractions'] is False:
                            split_con = False
                    from corpkit.keys import ngrams
                    if 'blacklist' in kwargs.keys():
                        the_blacklist = kwargs['blacklist']
                    else:
                        the_blacklist = False
                    if 'gramsize' in kwargs.keys():
                        gramsz = kwargs['gramsize']
                    else:
                        gramsz = 2

                    spindle_out = ngrams(subcorpus, reference_corpus = False, 
                                                    blacklist = the_blacklist,
                                                    printstatus = False, 
                                                    clear = False, 
                                                    lemmatise = lemmatise, 
                                                    split_contractions = split_con, 
                                                    whitelist = query,
                                                    gramsize = gramsz
                                                    )
                    for w in list(spindle_out.index):
                        if query != 'any':
                            if re.search(query, w):
                                for _ in range(spindle_out[w]):
                                    result.append(w)
                        else:
                            for _ in range(spindle_out[w]):
                                result.append(w)

                #if tregex, search
                else:
                    if not statsmode:
                        op = ['-o', '-' + translated_option]
                        q = search.values()[0]
                        result = tregex_engine(query = q, options = op, 
                                           corpus = subcorpus, root = root)
                        if result is False:
                            return
                    
                        # if just counting matches, just 
                        # add subcorpus name and count...
                        if only_count:
                            count_results[d] = result
                            continue

        # for dependencies, d[0] is the subcorpus name 
        # and d[1] is its file list ... 

        elif dependency or plaintext or tokens or statsmode or can_do_fast is False:
            #if not root:
                #p.animate(-1, str(0) + '/' + str(total_files))
            from collections import Counter
            statsmode_results = Counter({'Sentences': 0, 'Passives': 0, 'Tokens': 0})
            subcorpus_name = d[0]
            subcorpus_names.append(subcorpus_name)
            fileset = d[1]
            #for f in read_files:
            result = []
            for f in fileset:
                result_from_file = None
                # pass the x/y argument for more updates 
                if not root and translated_option != 'v':
                    tot_string = str(c + 1) + '/' + str(total_files)
                    if 'outname' in kwargs.keys():
                        tot_string = '%s: %s' % (kwargs['outname'], tot_string)
                    animator(p, c, tot_string, **par_args)
                    #p.animate((c), tot_string)
                if root and tk and not statsmode:
                    root.update()
                    if 'note' in kwargs.keys() and kwargs['note'] is not False:
                        kwargs['note'].progvar.set((((c + 1) * 100.0 / total_files) / denom) + startnum)
                        time = strftime("%H:%M:%S", localtime())
                        if not one_big_corpus:
                            print '%s: Interrogating subcorpus: %s' % (time, subcorpus_name)
                        else:
                            print '%s: Interrogating corpus ...' % (time)
                c += 1
                if one_big_corpus:
                    filepath = os.path.join(path, f)
                else:
                    filepath = os.path.join(path, subcorpus_name, f)
                if dependency or can_do_fast is False:
                    if not plaintext and not tokens:
                        with open(filepath, "rb") as text:
                            data = text.read()
                            from corenlp_xml.document import Document
                            try:
                                corenlp_xml = Document(data)
                            except:
                                print 'Could not read file: %s' % filepath
                                continue
                            #corenlp_xml = Beautifulcorenlp_xml(data, parse_only=justsents)  
                            if just_speakers:  
                                sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                                if not sents:
                                    continue
                                #sents = [s for s in corenlp_xml.find_all('sentence') \
                                #if s.speakername.text.strip() in just_speakers]
                            else:
                                sents = corenlp_xml.sentences
                            # run whichever function has been called
                            if translated_option == 'y':
                                result_from_file = dep_searcher(sents)
                            else:
                                result_from_file = dep_funct(sents)
                            if only_count:
                                count_results[subcorpus_name] = result_from_file

                            # memory problems
                            corenlp_xml = None
                            data = None
                            gc.collect()

                if plaintext:
                    with open(filepath, "rb") as text:
                        data = text.read()
                        if translated_option == 'r':
                            result_from_file = plaintext_regex_search(regex, data)
                        if translated_option == 's':
                            result_from_file = plaintext_simple_search(query, data)
                if tokens:
                    import pickle
                    data = pickle.load(open(filepath, "rb"))
                    #print data
                    if translated_option == 'h':
                        result_from_file = tok_by_reg(regex, data)
                    if translated_option == 'e':
                        result_from_file = tok_by_list(query, data)
                    if translated_option == 'j':
                        split_con = False
                        if 'split_contractions' in kwargs.keys():
                            if kwargs['split_contractions'] is True:
                                split_con = True
                        result_from_file = tok_ngrams(query, data, split_contractions = split_con)
                
                if result_from_file:
                    if not statsmode and not only_count:
                        for entry in result_from_file:
                            result.append(entry)

        if not statsmode and 'c' not in show:
            result.sort()

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        if not statsmode:
            processed_result = processwords(result, lemmatag = lemmatag)
            
        if not statsmode:
            allwords_list.append(processed_result)
            dicts.append(Counter(processed_result))
        if statsmode:
            dicts.append(statsmode_results)
            allwords_list.append([w for w in statsmode_results.keys()])

    if not plaintext:
        if not root:
            if paralleling is not False:
                if dependency or plaintext or tokens or can_do_fast is False:
                    tstr = '%s: %d/%d' % (kwargs['outname'], total_files, total_files)
                else:
                    tstr = '%s: %d/%d' % (kwargs['outname'], len(sorted_dirs), len(sorted_dirs))

            else:
                tstr = False
            animator(p, len(sorted_dirs), tot_string = tstr, **par_args)

            #p.animate(len(sorted_dirs))
        if 'note' in kwargs.keys() and kwargs['note'] is not False:
            kwargs['note'].progvar.set((100 / denom + startnum))
        if root and tk:
            root.update()

    else:
        # weird float div by 0 zero error here for plaintext
        try:
            if not root:
                if translated_option != 'v':
                    if paralleling is not False:
                        animator(p, total_files, kwargs['outname'], **par_args)
                    else:
                        animator(p, total_files, **par_args)
                    #p.animate(total_files)

                else:
                    if paralleling is not False:
                        animator(p, total_files * 10, kwargs['outname'], **par_args)
                    else:
                        animator(p, total_files * 10, **par_args)
                    #p.animate(total_files * 10)
            if 'note' in kwargs.keys() and kwargs['note'] is not False:
                kwargs['note'].progvar.set((100 / denom + startnum))
        except:
            pass

    if root and tk:
        root.update()

    if not have_ipython and not root and not tk:
        print '\n'
    
    # if only counting, get total total and finish up:
    if only_count:
        stotals = pd.Series(count_results)
        stotals.name = 'Total' 
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        the_time_ended = strftime("%Y-%m-%d %H:%M:%S")
        # add option to named tuple
        the_options = {'path': path,
                       'search': search,
                       'show': show,
                       'function': 'interrogator',
                       'datatype': stotals.dtype,
                       'query': query,
                       'exclude': exclude,
                       'lemmatise': lemmatise,
                       'titlefilter': titlefilter,
                       'lemmatag': lemmatag,
                       'spelling': spelling,
                       'phrases': phrases,
                       'dep_type': dep_type,
                       'quicksave': quicksave,
                       'time_started': the_time_started,
                       'time_ended': the_time_ended}

        try:
            the_options['translated_option'] = translated_option
        except:
            the_options['translated_options'] = translated_options

        output = outputnames(the_options, stotals)
        if 'outname' in kwargs:
            stotals.name = kwargs['outname']
            return stotals
        if have_ipython:
            clear_output()
        if quicksave:
            if stotals.sum() > 0:
                from corpkit.other import save_result
                save_result(output, quicksave)
        
        if printstatus:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Interrogation finished! %d total occurrences.' % (time, stotals.sum())
            if not tk:
                print ''

        return output

    # flatten and sort master list, in order to make a list of unique words
    try:
        allwords = [item for sublist in allwords_list for item in sublist]
    except TypeError:
        raise TypeError('No results found, sorry.')
    allwords.sort()
    unique_words = set(allwords)

    #make master reference_corpus
    the_big_dict = {}

    # calculate results
    # for every unique entry, find out how many times it appears per subcorpus
    for word in unique_words:
        the_big_dict[word] = [each_dict[word] for each_dict in dicts]
    
    # turn master dict into dataframe, sorted
    df = DataFrame(the_big_dict, index = subcorpus_names)

    if one_big_corpus:
        df = df.T.sort(list(df.T.columns)[0], ascending = False).T

    try:
        if not one_big_corpus:
            df.ix['Total'] = df.sum()
            tot = df.ix['Total']
            df = df[tot.argsort()[::-1]]
            df = df.drop('Total', axis = 0)
    except:
        pass

    # make totals branch
    stotals = df.sum(axis = 1)
    stotals.name = 'Total'

    # make result into series if only one subcorpus
    if one_big_corpus and not df1_always_df:
        try:
            df = df.ix[subcorpus_names[0]]
        except:
            pass
        df.sort(ascending = False)

    # if numerical colnames, sort numerically
    if show == ['r'] or show == ['i']:
       intcols = sorted([int(c) for c in list(df.columns)])
       df.columns = [str(c) for c in intcols]

    # add sort info for tk
    if tk:
        df = df.T
        df['tkintertable-order'] = pd.Series([index for index, data in enumerate(list(df.index))], index = list(df.index))
        df = df.T
    
    # print skipped sent information for distance_mode
    if printstatus and 'r' in show and skipped_sents > 0:
        print '\n          %d sentences over 99 words skipped.\n' % skipped_sents
        
    #make results into named tuple
    # add option to named tuple
    the_time_ended = strftime("%Y-%m-%d %H:%M:%S")
    the_options = {'path': path,
                       'search': search,
                       'show': show,
                       'datatype': df.iloc[0].dtype,
                       'query': query,
                       'lemmatise': lemmatise,
                       'titlefilter': titlefilter,
                       'lemmatag': lemmatag,
                       'function': 'interrogator',
                       'spelling': spelling,
                       'exclude': exclude,
                       'phrases': phrases,
                       'dep_type': dep_type,
                       'quicksave': quicksave,
                       'time_started': the_time_started,
                       'time_ended': the_time_ended}

    try:
        the_options['translated_option'] = translated_option
    except:
        the_options['translated_options'] = translated_options

    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    output = outputnames(the_options, df, stotals)

    if type(paralleling) == int:
        return (kwargs['outname'], df, stotals)
     
    if have_ipython:
        clear_output()

    # warnings if nothing generated...
    if not one_big_corpus and not df1_always_df:
        num_diff_results = len(list(df.columns))
    elif df1_always_df and not one_big_corpus:
        num_diff_results = len(list(df.columns))
    elif not df1_always_df and one_big_corpus:
        num_diff_results = len(list(df.index))
    elif df1_always_df and one_big_corpus:
        num_diff_results = len(list(df.columns))

    if num_diff_results == 0:
        if not root:
            print ''
            warnings.warn('No results produced. Maybe your query needs work.')
        else:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Interrogation produced no results, sorry.' % time
        return False

    if stotals.sum() == 0:
        if not root:
            print ''
            warnings.warn('No totals produced. Maybe your query needs work.')
        else:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Interrogation produced no results, sorry.' % time
        return False

    time = strftime("%H:%M:%S", localtime())
    if printstatus:
        print '%s: Interrogation finished! %d unique results, %d total.' % (time, num_diff_results, stotals.sum())
        if not tk:
            print ''

    if quicksave:
        if stotals.sum() > 0 and num_diff_results > 0:
            from corpkit.other import save_result
            save_result(output, quicksave)

    return output

if __name__ == '__main__':
    interrogator(path, 
                search = 'words',
                query = 'any', 
                show = 'words',
                case_sensitive = False,
                lemmatise = False, 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                quicksave = False,
                printstatus = True,
                root = False,
                df1_always_df = False,
                just_speakers = False,
                **kwargs)
