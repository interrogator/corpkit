#!/usr/bin/python

def interrogator(path, 
                option, 
                query = 'any', 
                case_sensitive = False,
                lemmatise = False, 
                reference_corpus = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                function_filter = False,
                pos_filter = False,
                table_size = 50,
                quicksave = False,
                add_to = False,
                add_pos_to_g_d_option = False,
                custom_engine = False,
                post_process = False,
                printstatus = True,
                root = False,
                df1_always_df = False,
                just_speakers = False,
                **kwargs):
    """
    Interrogate a parsed corpus using Tregex queries, dependencies, or for
    keywords/ngrams

    Output: a named tuple, with 'branches':
        variable_name.query = a record of what query generated the results
        variable_name.results = a table of results, sorted by total freq
        variable_name.totals = a list of totals for each subcorpus (except when keywording)
        variable_name.table = a DataFrame showing top results in each subcorpus
        of top <table_size> results

    Parameters
    ----------

    path : str
        path to a corpus. If it contains subfolders, these will be treated
        as subcorpora. If not, the corpus will be treated as unstructured.
        if a list, it will be understood as a list of corpora.
        parallel processing will be done on each corpus. a single result will
        be outputted for the 'c' option, or else a dict will be returned, with
        corpus names as keys.
    
    option : (can type letter or word): 
        - Tregex output option:
            c/count: only *count*
            w/words: only *words*
            p/pos: only *pos* tag
            b/both: *both* words and tags
        - dependency option:
            a: get the distance from the root for each match
            i/index: get the index of words
                i.e. root = 0
            f/funct: get the semantic *function*
            g/gov: get *governor* role and governor:
                r'^good$' might return amod:day
            d/dep: get dependent and its role:
                r'^day$' might return amod:sunny
            t/token: get tokens from dependency data
            m: search by label, returning tokens
        - plaintext:
            r/regex: search plain text with query as regex
            s/simple: search for word or list of words in plaintext files
        - other:
            k/keywords: search for keywords, using reference_corpus as the reference corpus
                        use 'self' to make the whole corpus into a reference_corpus
            n/ngrams: search for ngrams in trees   
    query : str
        - a Tregex query (if using a Tregex option)
        - A regex to match a token/tokens (if using a dependencies, plaintext, or keywords/ngrams)
        - A list of words or parts of words to match (e.g. ['cat', 'dog', 'cow'])

    lemmatise : Boolean
        Do lemmatisation on results. Uses WordNet for constituency, or CoreNLP for dependency
    lemmatag : False/'n'/'v'/'a'/'r'
        explicitly pass a pos to lemmatiser
    titlefilter : Boolean
        strip 'mr, 'the', 'dr.' etc. from results (turns 'phrases' on)
    spelling : False/'US'/'UK'
        convert all to U.S. or U.K. English
    phrases : Boolean
        Use if your expected results are multiword and thus need tokenising
    reference_corpus : string
        The name of a reference_corpus for keywording.
        BNC included as default.
        'self' will make a reference_corpus from the whole corpus
    dep_type : str
        the kind of Stanford CoreNLP dependency parses you want to use:
        - 'basic-dependencies'/'a'
        - 'collapsed-dependencies'/'b'
        - 'collapsed-ccprocessed-dependencies'/'c'
    function_filter : Bool/regex
        If you set this to a regex, for the 'g' and 'd' options, only words 
        whose function matches the regex will be kept, and the tag will not be printed
    quicksave : str
       save result after interrogation has finished, using str as file name. If multiple
       results (i.e. a list of corpora or dict of queries), a folder named str will
       be created, with results for each corpus/query name.
    custom_engine : function
       pass a function to process every xml file and return a list of results
    post_process : function
       pass a function that processes every item in the list of results
    ** kwargs : Mostly exists to allow users to pass in earlier interrogation
                settings in order to reperform the search.
                gramsize: get ngrams larger than 2
                tokenizer: which tokeniser to use

    Example 1: Tree querying
    --------
    from corpkit import interrogator, plotter
    corpus = 'path/to/corpus'
    ion_nouns = interrogator(corpus, 'w', r'/NN.?/ < /(?i)ion\b'/)
    quickview(ion_nouns, 5)
    plotter('Common -ion words', ion_nouns.results, fract_of = ion_nouns.totals)

    Output:

    0: election: (n=22)
    1: decision: (n=14)
    2: question: (n=10)
    3: nomination: (n=8)
    4: recession: (n=8)

    <matplotlib figure>

    Example 2: Dependencies querying
    -----------------------
    risk_functions = interrogator(corpus, 'f', r'(?i)\brisk')
    plotter('Functions of risk words', risk_functions.results, num_to_plot = 15)

    <matplotlib figure>

    """
    import corpkit
    from other import add_corpkit_to_path
    add_corpkit_to_path()
    import os
    import re
    import signal
    import numpy
    import collections
    import warnings
    from collections import Counter
    from time import localtime, strftime
    import pandas as pd
    from pandas import DataFrame, Series
    import nltk
    import os
    import corpkit
    import gc
    from corpkit.tests import check_pytex, check_t_kinter
    from textprogressbar import TextProgressBar
    from other import tregex_engine
    import dictionaries
    from dictionaries.word_transforms import (wordlist, 
                                              usa_convert, 
                                              taglemma)

    td = {}
    from corpkit.other import add_nltk_data_to_nltk_path, add_corpkit_to_path
    if 'note' in kwargs.keys() and kwargs['note'] is not False:
        td['note'] = kwargs['note']
    add_nltk_data_to_nltk_path(**td)

    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    add_corpkit_to_path()
    tk = check_t_kinter()

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
    if hasattr(function_filter, '__iter__'):
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

    # just for me: convert spelling automatically for bipolar
    if not is_multiquery:
        if 'postcounts' in path:
            spelling = 'UK'

    
    if root:
        shouldprint = False
    else:
        shouldprint = True

    # run pmultiquery if so
    if is_multiquery:
        from corpkit.multiprocess import pmultiquery
        d = { 'path': path, 
              'option': option, 
              'query': query, 
              'lemmatise': lemmatise, 
              'reference_corpus': reference_corpus, 
              'titlefilter': titlefilter, 
              'lemmatag': lemmatag, 
              'print_info': shouldprint, 
              'spelling': spelling, 
              'phrases': phrases, 
              'dep_type': dep_type, 
              'function_filter': function_filter, 
              'table_size': table_size, 
              'quicksave': quicksave, 
              'add_to': add_to, 
              'add_pos_to_g_d_option': add_pos_to_g_d_option, 
              'custom_engine': custom_engine,
              'df1_always_df': df1_always_df,
              'just_speakers': just_speakers, 
              'root': root,
              'post_process': post_process }
        
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

    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()

    # put me in a more appropriate spot
    if custom_engine is not False:
        option = 'z'
    
    # check if we are in ipython
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    def animator(progbar, count, tot_string = False, linenum = False, terminal = False, 
                 init = False, length = False):
        """animates progress bar in unique position in terminal"""
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
        """pause on ctrl+c, rather than just stop loop"""       
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
        """find tag for lemmatisation"""
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
    
    def processwords(list_of_matches):
        """edit matches from interrogations"""

        if post_process is not False:
            list_of_matches = [post_process(m) for m in list_of_matches]
        else:
            list_of_matches = [w.lower() for w in list_of_matches]
            # remove nonwords, strip . to normalise "dr."
            if translated_option != 'o' and translated_option != 'u':
                list_of_matches = [w.lstrip('.').rstrip('.') for w in list_of_matches if re.search(regex_nonword_filter, w)]
        
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases:
            from nltk import word_tokenize as word_tokenize
            list_of_matches = [word_tokenize(i) for i in list_of_matches]
        if lemmatise:
            tag = gettag(query, lemmatag = lemmatag)
            list_of_matches = lemmatiser(list_of_matches, tag)
        if titlefilter:
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
            # only use wordnet lemmatiser when appropriate
            if translated_option.startswith('t') or translated_option.startswith('w') or 'keyword' in query or 'ngram' in query:
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            # do the manual_lemmatisation
            if dependency:
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
            non_head = len(result) - 1 # ???
            title_stripped = [token for token in result[:non_head] if token.rstrip('.') not in badwords]
            title_stripped.append(head)
            output.append(title_stripped)
        return output

    def convert_spelling(list_of_matches, spelling = 'US'):
        from dictionaries.word_transforms import usa_convert
        if spelling == 'UK':
            usa_convert = {v: k for k, v in usa_convert.items()}
        output = []
        # if we have funct:word, spellfix the word only
        if dependency and not function_filter:
            for result in list_of_matches:
                funct, word = result.split(':', 1)
                try:
                    word = usa_convert[word]
                    result = u'%s:%s' % (funct, word)
                except KeyError:
                    pass
                output.append(result)
            return output            
        # in any other case, do it normally
        else:
            for result in list_of_matches:
                if phrases:
                    for w in result:
                        try:
                            w = usa_convert[w]
                        except KeyError:
                            pass
                    output.append(result)
                else:
                    try:
                        result = usa_convert[result]
                    except KeyError:
                        pass
                    output.append(result)
            return output

    def distancer(sents):
        import re
        """return distance from root for words matching query (root = 0)"""
        result = []
        for sindex, s in enumerate(sents):
            deps = get_deps(s, dep_type)
            # skip really long sents
            if len([i for i in deps.links]) > 99:
                skipped_sents += 1
                continue

            lks = [l for l in deps.links]
            for lk in lks:
                if re.match(regex, lk.dependent.text):
                    role = lk.type
                    # stop if role is bad
                    if function_filter:
                        if not re.match(funfil_regex, role):
                            continue
                    if pos_filter:
                        pos = s.get_token_by_id(lk.governor.idx).pos
                        if re.match(pos_regex, pos):
                            continue
                    c = 0
                    # get the gov index, stop when it's zero
                    root_found = False
                    while not root_found:
                        if c == 0:
                            link_to_check = lk
                        gov_index = link_to_check.governor.idx
                        if gov_index == 0:
                            root_found = True
                        else:
                            if c > 29:
                                root_found = True
                                break
                            link_to_check = [l for l in lks if l.dependent.idx == gov_index][0]
                            c += 1
                    if c < 30:
                        result.append(c)
        return result

    def govrole(sents):
        """print funct:gov, using good lemmatisation"""
        # for each sentence
        result = []
        for s in sents:
            deps = get_deps(s, dep_type)
            # get links matching gov
            lks = [l for l in deps.links if re.match(regex, l.dependent.text)]
            for lk in lks:
                # get role
                role = lk.type
                if role == 'root':
                    result.append(u'root:root')
                    continue
                # stop if role is bad
                if function_filter:
                    if not re.match(funfil_regex, role):
                        continue
                # get word or lemma
                if not lemmatise:
                    word = lk.governor.text
                else:
                    word = s.get_token_by_id(lk.governor.idx).lemma
                # stop if pos_filtering
                if pos_filter:
                    pos = s.get_token_by_id(lk.governor.idx).pos
                    if re.match(pos_regex, pos):
                        continue
                # make result
                if not function_filter:
                    res = role + u':' + word
                else:
                    res = word
                result.append(res)
        return result

    def get_lemmata(sents):
        """search for lemmata to count"""
        from bs4 import BeautifulSoup
        import gc
        result = []
        for sent in sents:
            res = [w.lemma for w in sent.tokens if re.match(regex, w.lemma)]
            for w in res:
                result.append(w)
        return result

    def tokener(sents):
        """get tokens or lemmata from dependencies"""
        from bs4 import BeautifulSoup
        import gc
        open_classes = ['N', 'V', 'R', 'J']
        result = []
        for sent in sents:
            if lemmatise:
                res = [w.lemma for w in sent.tokens if re.match(regex, w.word)]
            else:
                res = [w.word for w in sent.tokens if re.match(regex, w.word)]
            for w in res:
                result.append(w)
        return result

    def deprole(sents):
        """print funct:dep, using good lemmatisation"""
        result = []
        for s in sents:
            deps = get_deps(s, dep_type)

            # get links matching gov
            lks = [l for l in deps.links if re.match(regex, l.governor.text)]
            for lk in lks:
                # get role
                role = lk.type
                # stop if role is bad
                if function_filter:
                    if not re.match(funfil_regex, role):
                        continue
                # get word or lemma
                if not lemmatise:
                    word = lk.dependent.text
                else:
                    word = s.get_token_by_id(lk.dependent.idx).lemma

                # stop if pos_filtering
                if pos_filter:
                    pos = s.get_token_by_id(lk.dependent.idx).pos
                    if re.match(pos_regex, pos):
                        continue
                # make result
                if not function_filter:
                    res = role + u':' + word
                else:
                    res = word
                result.append(res)
        return result

    def words_by_function(sents):
        """print match by function, using good lemmatisation"""

        # if function matches query, return word or lemma
        result = []
        for s in sents:
            deps = get_deps(s, dep_type)
            if not pos_filter and not lemmatise:
                to_return = [r.dependent.text for r in deps.links if re.match(regex, r.type)]
            else:
                if lemmatise and pos_filter:
                    to_return = [s.get_token_by_id(r.dependent.idx).lemma for r in deps.links \
                               if re.match(regex, r.type) and \
                               re.search(pos_regex, s.get_token_by_id(r.dependent.idx).pos)]
                elif lemmatise and not pos_filter:
                    to_return = [s.get_token_by_id(r.dependent.idx).lemma for r in deps.links \
                               if re.match(regex, r.type)]
                elif pos_filter and not lemmatise:
                    to_return = [r.dependent.text for r in deps.links if re.match(regex, r.type) \
                    and re.search(pos_regex, s.get_token_by_id(r.dependent.idx).pos)]
            
            for r in to_return:
                result.append(r)
        return result

    def funct(sents):
        """print functional role of regex match"""
        result = []
        for s in sents:
            deps = get_deps(s, dep_type)
            roles = [r.type for r in deps.links if re.match(regex, r.dependent.text)]
            if function_filter:
                roles = [r for r in roles if not re.search(funfil_regex, r)]                    
            for r in roles:
                result.append(r)
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
            unsplit = []
            for index, t in enumerate(list_of_toks):
                if index == 0 or index == len(list_of_toks) - 1:
                    unsplit.append(t)
                    continue
                if "'" in t:
                    rejoined = ''.join([list_of_toks[index - 1], t])
                    unsplit.append(rejoined)
                else:

                    if not "'" in list_of_toks[index + 1]:
                        unsplit.append(t)
            list_of_toks = unsplit
            
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
        return [m for m in list_of_toks if re.search(pattern, m)]

    def plaintext_regex_search(pattern, plaintext_data):
        """search for regex in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        for p in pattern:
            matches = re.findall(p, plaintext_data)
            for m in matches:
                result.append(m)
        return result

    def plaintext_simple_search(pattern, plaintext_data):
        """search for tokens in plaintext corpora"""
        if type(pattern) == str:
            pattern = [pattern]
        result = []
        for p in pattern:
            if case_sensitive:
                pat = re.compile(r'\b' + re.escape(p) + '\b')
            else:
                pat = re.compile(r'\b' + re.escape(p) + '\b', re.IGNORECASE)
            if not any_plaintext_word:
                matches = re.findall(pat, plaintext_data)
                for m in range(matches):
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
        res = tregex_engine(query = query, 
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
        import bs4    
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
                #p.animate(numdone)
            # this should show progress more often
            if 'note' in kwargs.keys() and kwargs['note'] is not False:
                kwargs['note'].progvar.set((numdone * 100.0 / (total_files * len(tregex_qs.keys())) / denom) + startnum)
        os.remove(to_open)

    def depnummer(sents):
        """get index of word in sentence?"""
        result = []
        for sent in sents:
            right_deps = sent.find("dependencies", {"type":dep_type})
            for index, dep in enumerate(right_deps.find_all('dep')):
                for dependent in dep.find_all('dependent', limit = 1):
                    word = dependent.get_text().strip()
                    if re.match(regex, word):
                        result.append(index + 1)
        return result

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
    keywording = False
    n_gramming = False
    dependency = False
    distance_mode = False
    plaintext = False
    tokens = False
    depnum = False
    statsmode = False

    # some empty lists we'll need
    dicts = []
    allwords_list = []

    # check if pythontex is being used:
    have_python_tex = check_pytex()
    
    regex_nonword_filter = re.compile("[A-Za-z0-9:_]")

    # parse option
    # handle hyphen at start
    if option.startswith('-'):
        translated_option = option[1:]
    
    # Tregex option:
    translated_option = False
    from other import as_regex
    while not translated_option:
        if option.lower().startswith('p'):
            using_tregex = True
            dep_funct = slow_tregex
            optiontext = 'Part-of-speech tags only.'
            translated_option = 'u'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif option.lower().startswith('b'):
            using_tregex = True
            dep_funct = slow_tregex
            optiontext = 'Tags and words.'
            translated_option = 'o'
            if type(query) == list:
                query = r'__ < (/%s/ !< __)' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
        elif option.lower().startswith('w'):
            using_tregex = True
            dep_funct = slow_tregex
            optiontext = 'Words only.'
            translated_option = 't'
            if type(query) == list:
                query = r'/%s/ !< __' % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'
        elif option.lower().startswith('c'):
            using_tregex = True
            dep_funct = slow_tregex
            count_results = {}
            only_count = True
            translated_option = 'C'
            optiontext = 'Counts only.'
            if type(query) == list:
                query = r'/%s/ !< __'  % as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)
            if query == 'any':
                query = r'/.?[A-Za-z0-9].?/ !< __'

        #plaintext options
        elif option.lower().startswith('r'):
            plaintext = True
            optiontext = 'Regular expression matches only.'
            translated_option = 'r'
            if query == 'any':
                query = r'.*'

        elif option.lower().startswith('s'):
            plaintext = True
            optiontext = 'Simple plain-text search.'
            translated_option = 's'
            if query == 'any':
                any_plaintext_word = True
            else:
                any_plaintext_word = False

        #keywording and n_gramming options
        elif option.lower().startswith('k'):
            translated_option = 'k'
            keywording = True
            optiontext = 'Keywords only.'
            if type(query) == list:
                query = as_regex(query, boundaries = 'line', case_sensitive = case_sensitive)

        elif option.lower().startswith('n'):
            translated_option = 'n'
            n_gramming = True
            phrases = True
            optiontext = 'n-grams only.'
            if type(query) == list:
                query = as_regex(query, boundaries = 'word', case_sensitive = case_sensitive)

        # dependency option:
        elif option.lower().startswith('z'):
            translated_option = 'z'
            dependency = True
            optiontext = 'Using custom dependency query engine.'
            dep_funct = custom_engine
        elif option.lower().startswith('i'):
            translated_option = 'i'
            depnum = True
            dependency = True
            optiontext = 'Dependency index number only.'
            dep_funct = depnummer
        elif option.lower().startswith('a'):
            translated_option = 'a'
            distance_mode = True
            dependency = True
            optiontext = 'Distance from root.'
            dep_funct = distancer
        elif option.lower().startswith('f'):
            translated_option = 'f'
            dependency = True
            optiontext = 'Functional role only.'
            dep_funct = funct
        elif option.lower().startswith('m'):
            translated_option = 'm'
            dependency = True
            optiontext = 'Matching tokens by function label.'
            dep_funct = words_by_function
        elif option.lower().startswith('g'):
            translated_option = 'g'
            dependency = True
            optiontext = 'Role and governor.'
            dep_funct = govrole
        elif option.lower().startswith('l'):
            translated_option = 'l'
            dependency = True
            optiontext = 'Lemmata only.'
            dep_funct = get_lemmata
        elif option.lower().startswith('t'):
            translated_option = 'q' # dummy
            dependency = True
            optiontext = 'Tokens only.'
            dep_funct = tokener
        elif option.lower().startswith('d'):
            translated_option = 'd'
            dependency = True
            optiontext = 'Dependent and its role.'
            dep_funct = deprole
        elif option.lower().startswith('v'):
            translated_option = 'v'
            using_tregex = True
            statsmode = True
            optiontext = 'Getting general stats.'
            dep_funct = get_stats
        elif option.lower().startswith('h'):
            translated_option = 'h'
            tokens = True
            optiontext = 'Tokens via regular expression.'
            dep_funct = tok_by_reg
        elif option.lower().startswith('e'):
            translated_option = 'e'
            tokens = True
            optiontext = 'Tokens via list.'
            dep_funct = tok_by_list
        elif option.lower().startswith('j'):
            translated_option = 'j'
            tokens = True
            lemmatise = False
            optiontext = 'Get ngrams from tokens.'
            if query == 'any':
                query = r'.*'
            if type(query) == list:
                query = as_regex(query, boundaries = 'l', case_sensitive = case_sensitive)
            else:
                if not case_sensitive:
                    query = re.compile(query, re.IGNORECASE)
                else:
                    query = re.compile(query)
            global gramsize
            if 'gramsize' in kwargs.keys():
                gramsize = kwargs['gramsize']
            else:
                gramsize = 2
            dep_funct = tok_ngrams
        else:
            time = strftime("%H:%M:%S", localtime())
            selection = raw_input('\n%s: "%s" option not recognised. Option can be any of: \n\n' \
                          '              a) Get distance from root for regex match\n' \
                          '              b) Get tag and word of Tregex match\n' \
                          '              c) count Tregex matches\n' \
                          '              d) Get dependent of regular expression match and the r/ship\n' \
                          '              e) Get tokens from tokenised text by list\n' \
                          '              f) Get dependency function of regular expression match\n' \
                          '              g) get governor of regular expression match and the r/ship\n' \
                          '              h) get tokens from tokenised text by regular expression\n' \
                          '              i) get dependency index\n '\
                          '              k) get keywords\n' \
                          '              l) get lemmata via dependencies\n'
                          '              m) get tokens by dependency role \n' \
                          '              n) get ngrams\n' \
                          '              n) get \n' \
                          '              p) get part-of-speech tag with Tregex\n' \
                          '              r) regular expression, for plaintext corpora\n' \
                          '              s) simple search string, for plaintext corpora\n' \
                          '              t) match tokens via dependencies \n' \
                          '              w) get word(s) returned by Tregex/keywords/ngrams\n' \
                          '              x) exit\n\nYour selection: ' % (time, option))
            if selection.startswith('x'):
                return
            option = selection

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
    if query == 'any':
        if translated_option == 't' or translated_option == 'C':
            query = r'/.?[A-Za-z0-9].?/ !< __'
        if translated_option == 'u' or translated_option == 'o':
            query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
    if query == 'subjects':
        query = r'__ >># @NP'
    if query == 'processes':
        query = r'/VB.?/ >># ( VP >+(VP) (VP !> VP $ NP))'
    if query == 'modals':
        query = r'MD < __'
    if query == 'participants':
        query = r'/(NN|PRP|JJ).?/ >># (/(NP|ADJP)/ $ VP | > VP)'
    if query == 'entities':
        query = r'NP <# NNP'
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
            loaded.query['function'] == 'interrogator' and \
            loaded.query['function_filter'] == function_filter:
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
            from other import as_regex
            the_filter = as_regex(the_filter, case_sensitive = case_sensitive)
        try:
            output = re.compile(the_filter)
            is_valid = True
        except:
            is_valid = False
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

    if pos_filter:
        pos_regex = filtermaker(pos_filter)
        if pos_regex is False:
            return

    # dependencies:
    # can't be phrases
    # check if regex valid
    # check if dep_type valid
    if dependency:
        if translated_option == 'v':
            names = get_speaker_names_from_xml_corpus(path)
        
        phrases = False

        if function_filter:
            funfil_regex = filtermaker(function_filter)
            if funfil_regex is False:
                return
        
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

    if keywording or n_gramming:
        jcw = False
        if 'just_content_words' in kwargs:
            if kwargs['just_content_words'] is True:
                jcw = True

        if reference_corpus.startswith('self') or reference_corpus == os.path.basename(path):
            if lemmatise:
                lem = '-lemmatised'
            else:
                lem = ''
            reference_corpus = os.path.basename(path) + lem + '.p'
            dictpath = 'data/dictionaries'
            import pickle
            try:
                dic = pickle.load( open( os.path.join(dictpath, reference_corpus), "rb" ) )
            except:
                from build import dictmaker
                time = strftime("%H:%M:%S", localtime())
                print '\n%s: Making reference corpus ...' % time
                dictmaker(path, reference_corpus, query, lemmatise = lemmatise, just_content_words = jcw)
    
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

    # plaintext guessing
    # if plaintext == 'guess':
    #     if not one_big_corpus:
    #         # set to last subcorpus, just to make 'guess' quicker in my case
    #         subcorpus = os.path.join(path,sorted_dirs[-1])
    #     else:
    #         # horrible for large corpora
    #         subcorpus = path
    #     if not tregex_engine(corpus = subcorpus, check_for_trees = True, root = root):
    #         plaintext = True
    #     else:
    #         plaintext = False

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
                files = [f for f in os.listdir(subcorpus)]
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
            query = tregex_engine(corpus = False, query = query, options = '-t', check_query = True, root = root)
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
        if using_tregex or keywording or n_gramming:
            if can_do_fast:
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
                if keywording:
                    result = []
                    from corpkit import keywords
                    spindle_out = keywords(subcorpus, reference_corpus = reference_corpus, just_content_words = jcw,
                                            printstatus = False, clear = False, lemmatise = lemmatise)
                    for w in list(spindle_out.index):

                        if query != 'any':
                            if re.search(query, w):
                                result.append([w, spindle_out[w]])
                        else:
                            result.append([w, spindle_out[w]])

                elif n_gramming:
                    result = []
                    from corpkit import ngrams
                    spindle_out = ngrams(subcorpus, reference_corpus = reference_corpus, just_content_words = jcw,
                                            printstatus = False, clear = False, lemmatise = lemmatise)
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
                        result = tregex_engine(query = query, options = op, 
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

        if dependency or plaintext or tokens or can_do_fast is False:
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
                            corenlp_xml = Document(data)
                            #corenlp_xml = Beautifulcorenlp_xml(data, parse_only=justsents)  
                            if just_speakers:  
                                sents = [s for s in corenlp_xml.sentences if s.speakername in just_speakers]
                                #sents = [s for s in corenlp_xml.find_all('sentence') \
                                #if s.speakername.text.strip() in just_speakers]
                            else:
                                sents = corenlp_xml.sentences
                            # run whichever function has been called

                            result_from_file = dep_funct(sents)

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
                    import os
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
                    if not statsmode:
                        for entry in result_from_file:
                            result.append(entry)

        if not keywording:
            result.sort()

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        if not keywording and not depnum and not distance_mode and not statsmode:
            processed_result = processwords(result)
        if depnum or distance_mode:
            processed_result = result
            
        if keywording:
            allwords_list.append([w for w, score in result])
        else:
            if not statsmode:
                allwords_list.append(processed_result)
            else:
                allwords_list.append([w for w in statsmode_results.keys()])

            # add results master list and to results list
        
        if keywording:
            little_dict = {}
            for word, score in result:
                little_dict[word] = score
            dicts.append(Counter(little_dict))
        if not keywording and not statsmode:
            dicts.append(Counter(processed_result))
        if statsmode:
            dicts.append(statsmode_results)

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
        the_options = {}
        the_options['path'] = path
        the_options['option'] = option
        the_options['datatype'] = stotals.dtype
        try:
            the_options['translated_option'] = translated_option
        except:
            the_options['translated_options'] = translated_options
        the_options['query'] = query 
        the_options['lemmatise'] = lemmatise
        the_options['reference_corpus'] = reference_corpus
        the_options['titlefilter'] = titlefilter 
        the_options['lemmatag'] = lemmatag
        the_options['spelling'] = spelling
        the_options['phrases'] = phrases
        the_options['dep_type'] = dep_type
        the_options['function_filter'] = function_filter
        the_options['table_size'] = table_size
        the_options['plaintext'] = plaintext
        the_options['quicksave'] = quicksave
        the_options['time_started'] = the_time_started
        the_options['time_ended'] = the_time_ended

        output = outputnames(the_options, stotals)
        if 'outname' in kwargs:
            stotals.name = kwargs['outname']
            return stotals
        if have_ipython:
            clear_output()
        if quicksave:
            if stotals.sum() > 0:
                from other import save_result
                save_result(output, quicksave)
        
        if printstatus:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Interrogation finished! %d total occurrences.' % (time, stotals.sum())
            if not tk:
                print ''

        if add_to:
            d = add_to[0]
            d[add_to[1]] = output
            return output, d
        else:
            return output

    # flatten and sort master list, in order to make a list of unique words
    allwords = [item for sublist in allwords_list for item in sublist]
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
            if not depnum and not distance_mode:
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
        #df.name = query
        if not distance_mode:
            df.sort(ascending = False)
        else:
            df = df.sort_index()

    # add sort info for tk
    if tk:
        df = df.T
        df['tkintertable-order'] = pd.Series([index for index, data in enumerate(list(df.index))], index = list(df.index))
        df = df.T

    # return pandas/csv table of most common results in each subcorpus
    if not depnum and not distance_mode:
        if table_size > max([len(d) for d in dicts]):
            table_size = max([len(d) for d in dicts])
        word_table = tabler(subcorpus_names, dicts, table_size)
    
    # print skipped sent information for distance_mode
    if printstatus and distance_mode and skipped_sents > 0:
        print '\n          %d sentences over 99 words skipped.\n' % skipped_sents

    if type(paralleling) == int:
        return (kwargs['outname'], df)
        
    #make results into named tuple
    # add option to named tuple
    the_time_ended = strftime("%Y-%m-%d %H:%M:%S")
    the_options = {}
    the_options['function'] = 'interrogator'
    the_options['path'] = path
    the_options['option'] = option
    try:
        the_options['datatype'] = df.iloc[0].dtype
    except:
        the_options['datatype'] = int
    try:
        the_options['translated_option'] = translated_option
    except:
        the_options['translated_options'] = translated_options
    the_options['query'] = query 
    the_options['lemmatise'] = lemmatise
    the_options['reference_corpus'] = reference_corpus
    the_options['titlefilter'] = titlefilter 
    the_options['lemmatag'] = lemmatag
    the_options['spelling'] = spelling
    the_options['phrases'] = phrases
    the_options['dep_type'] = dep_type
    the_options['function_filter'] = function_filter
    the_options['table_size'] = table_size
    the_options['plaintext'] = plaintext
    the_options['quicksave'] = quicksave
    the_options['time_started'] = the_time_started
    the_options['time_ended'] = the_time_ended

    if not keywording and not depnum and not distance_mode:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals', 'table'])
        output = outputnames(the_options, df, stotals, word_table)
    if keywording:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'table'])
        output = outputnames(the_options, df, word_table)
    if depnum or distance_mode:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
        output = outputnames(the_options, df, stotals)        

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

    if not keywording:
        if stotals.sum() == 0:
            if not root:
                print ''
                warnings.warn('No totals produced. Maybe your query needs work.')
            else:
                time = strftime("%H:%M:%S", localtime())
                print '%s: Interrogation produced no results, sorry.' % time
            return False

    time = strftime("%H:%M:%S", localtime())
    if not keywording:
        if printstatus:
            print '%s: Interrogation finished! %d unique results, %d total.' % (time, num_diff_results, stotals.sum())
            if not tk:
                print ''
    else:
        if printstatus:
            print '%s: Interrogation finished! %d unique results.' % (time, num_diff_results)
            if not tk:
                print ''

    if quicksave:
        if not keywording:
            if stotals.sum() > 0 and num_diff_results > 0:
                from other import save_result
                save_result(output, quicksave)
        else:
            if num_diff_results > 0:
                from other import save_result
                save_result(output, quicksave)

    if add_to:
        d = add_to[0]
        d[add_to[1]] = output
        return output, d
    else:
        return output










if __name__ == '__main__':
    interrogator(path, 
                option, 
                query = 'any', 
                case_sensitive = False,
                lemmatise = False, 
                reference_corpus = 'bnc.p', 
                titlefilter = False, 
                lemmatag = False, 
                spelling = False, 
                phrases = False, 
                dep_type = 'basic-dependencies',
                function_filter = False,
                pos_filter = False,
                table_size = 50,
                quicksave = False,
                add_to = False,
                add_pos_to_g_d_option = False,
                custom_engine = False,
                post_process = False,
                printstatus = True,
                root = False,
                df1_always_df = False,
                just_speakers = False,
                **kwargs)

    #import argparse
#
    #epi = "Example usage:\n\npython interrogator.py 'path/to/corpus' 'words' '/NN.?/ >># (NP << /\brisk/)' np_heads --lemmatise --spelling 'UK'" \
    #"\n\nTranslation: 'interrogate path/to/corpus for words that are heads of NPs that contain risk.\n" \
    #"Lemmatise each result, and save the result as a set of CSV files in np_heads.'\n\n"
#
    #parser = argparse.ArgumentParser(description='Interrogate a linguistic corpus in sophisticated ways', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epi)
    #import sys
    #if len(sys.argv) == 1:
    #    parser.add_argument('-p', '--path', metavar='P', type=str,
    #                             help='Path to the corpus')
    #    parser.add_argument('-o', '--option', metavar='O', type=str,
    #                             help='Search type')
    #    parser.add_argument('-q', '--query', metavar='Q',
    #                             help='Tregex or Regex query')
    #    parser.add_argument('-s', '--quicksave', type=str, metavar='S',
    #                             help='A name for the interrogation and the files it produces')
    #else:
    #    parser.add_argument('-path', metavar='P', type=str,
    #                             help='Path to the corpus')
    #    parser.add_argument('-option', metavar='O', type=str,
    #                             help='Search type')
    #    parser.add_argument('-query', metavar='Q',
    #                             help='Tregex or Regex query')
    #    parser.add_argument('-quicksave', type=str, metavar='S',
    #                             help='A name for the interrogation and the files it produces')        
#
    #parser.add_argument('-l', '--lemmatise',
    #                         help='Do lemmatisation?', action='store_true')
    #parser.add_argument('-dict', '--reference_corpus', type=str, default='bnc.p',
    #                         help='A reference_corpus file to use as a reference corpus when keywording')
    #parser.add_argument('-sp', '--spelling', type=str,
    #                         help='Normalise to US/UK spelling')
    #parser.add_argument('-t', '--titlefilter',
    #                         help='Remove some common prefixes from names, etc.', action='store_true')
    #parser.add_argument('-ph', '--phrases',
    #                         help='Tell interrogator() that you are expecting multi word results')
#
    #parser.add_argument('-dt', '--dep_type', type=str,
    #                         help='The kind of Stanford dependencies you want to search')
    #
    #args = parser.parse_args()
#
    #if not vars(args)['quicksave'] and not vars(args)['path'] and not vars(args)['option'] and not vars(args)['query']:
    #    print "\nWelcome to corpkit!\n\nThis function is called interrogator().\n\nIt allows you to search constituency trees with Tregex, Stanford Dependency parses, or plain text corpora with Regular Expressions.\n\nYou're about to be prompted for some information:\n    1) a name for the interrogation\n    2) a path to your corpus\n    3) a Tregex query or regular expression\n    4) an option, specifying the kind of search you want to do.\n"
    #    ready = raw_input("When you're ready, type 'start', or 'exit' to cancel: ")
    #    if ready.startswith('e') or ready.startswith('E'):
    #        print '\n    OK ... come back soon!\n'
    #        import sys
    #        sys.exit(0)
#
    #all_args = {}
#
    #def urlify(s):
    #    "Turn title into filename"
    #    import re
    #    s = s.lower()
    #    s = re.sub(r"[^\w\s-]", '', s)
    #    s = re.sub(r"\s+", '-', s)
    #    s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
    #    return s     
#
    #if not vars(args)['quicksave']:
    #    name = raw_input('\nName for this interrogation: ')
    #    all_args['quicksave'] = urlify(name)
    #if not vars(args)['path']:
    #    all_args['path'] = raw_input('\nPath to the corpus: ')
    #if not vars(args)['query']:
    #    print '\nFor the following sentence:\n\n    "The sunny days have come at last."\n\nyou could perform a number of kinds of searches:\n\n    - Tregex queries will search the parse tree:\n        "/NNS/" locates "days", a plural noun\n        "/NN.?/ $ (JJ < /(?i)sunny/)" locates days, sister to adjectival "sunny"\n    - Regex options are used for searching plaintext or dependencies:\n        "[A-Za-z]+s\b" will return "days"\n' 
    #    all_args['query'] = raw_input('\nQuery: ')
    #if not vars(args)['option']:
    #    print '\nSelect search option. For the following sentence:\n\n    "Some sunny days have come at last."\n\nyou could:\n\n' \
    #                      '    b) Get tag and word of Tregex match ("(nns days)"\n' \
    #                      '    c) count Tregex matches\n' \
    #                      '    d) Get dependent of regular expression match and the r/ship ("amod:sunny")\n' \
    #                      '    f) Get dependency function of regular expression match ("nsubj")\n' \
    #                      '    g) get governor of regular expression match and the r/ship ("nsubj:have")\n' \
    #                      '    n) get dependency index of regular expression match ("1")\n' \
    #                      '    p) get part-of-speech tag with Tregex ("nns")\n' \
    #                      '    r) regular expression, for plaintext corpora\n' \
    #                      '    w) get word(s) returned by Tregex/keywords/ngrams ("day/s")\n' \
    #                      '    x) exit\n' 
    #    all_args['option'] = raw_input('\nQuery option: ')
    #    if 'x' in all_args['option']:
    #        import sys
    #        sys.exit(0)
#
    #for entry in vars(args).keys():
    #    if entry not in all_args.keys():
    #        all_args[entry] = vars(args)[entry]
#
    #conf = raw_input("OK, we're ready to interrogate. If you want to exit now, type 'exit'. Otherwise, press enter to begin!")
    #if conf:
    #    if conf.startswith('e'):
    #        import sys
    #        sys.exit(0)
#
    #res = interrogator(**all_args)
    ## what to do with it!?
    #if res:
    #    import os
    #    import pandas as pd
    #    csv_path = 'data/csv_results'
    #    if not os.path.isdir(csv_path):
    #        os.makedirs(csv_path)
    #    interrogation_name = all_args['quicksave']
    #    savepath = os.path.join(csv_path, interrogation_name)
    #    if not os.path.isdir(savepath):
    #        os.makedirs(savepath)
    #    results_filename = os.path.join(savepath, '%s-results.csv' % interrogation_name)
    #    totals_filename = os.path.join(savepath, '%s-totals.csv' % interrogation_name)
    #    top_table_filename = os.path.join(savepath, '%s-top-table.csv' % interrogation_name)
    #    if res.query['translated_option'] != 'C':
    #        res.results.to_csv(results_filename, sep = '\t')
    #        res.table.to_csv(top_table_filename, sep = '\t')
    #    if res.query['query'] != 'keywords':
    #        res.totals.to_csv(totals_filename, sep = '\t')
    #    from time import localtime, strftime
    #    time = strftime("%H:%M:%S", localtime())
    #    print '%s: Created CSV files in %s\n' % (time, savepath)

