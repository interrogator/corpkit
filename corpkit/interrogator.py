"""
corpkit: Interrogate a parsed corpus
"""

#!/usr/bin/python

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

def interrogator(corpus, 
                 search, 
                 query='any',
                 show='w',
                 exclude=False,
                 excludemode='any',
                 searchmode='all',
                 dep_type='collapsed-ccprocessed-dependencies',
                 case_sensitive=False,
                 save=False,
                 just_speakers=False,
                 preserve_case=False,
                 lemmatag=False,
                 files_as_subcorpora=False,
                 only_unique=False,
                 random=False,
                 only_format_match=False,
                 multiprocess=False,
                 spelling=False,
                 regex_nonword_filter=r'[A-Za-z0-9:_]',
                 gramsize=2,
                 split_contractions=False,
                 conc=False,
                 maxconc=9999,
                 window=4,
                 no_closed=False,
                 no_punct=True,
                 whitelist=False,
                 **kwargs
                ):
    """
    Interrogate corpus, corpora, subcorpus and file objects.
    See corpkit.interrogation.interrogate() for docstring
    """

    # in case old kwarg is used
    conc = kwargs.get('do_concordancing', conc)

    # store kwargs and locs
    locs = locals().copy()
    locs.update(kwargs)
    locs.pop('kwargs', None)

    if not kwargs.get('cql') and isinstance(search, STRINGTYPE) and len(search) > 3:
        raise ValueError('search argument not recognised.')

    import codecs
    import signal
    import os
    from time import localtime, strftime
    from collections import Counter

    import corenlp_xml
    import pandas as pd
    from pandas import DataFrame, Series

    from corpkit.interrogation import Interrogation, Interrodict
    from corpkit.corpus import Datalist, Corpora, Corpus, File, Subcorpus
    from corpkit.process import (tregex_engine, get_deps, unsplitter, sanitise_dict, 
                                 get_speakername, animator, filtermaker, fix_search,
                                 pat_format)
    from corpkit.other import as_regex
    from corpkit.dictionaries.word_transforms import wordlist, taglemma
    from corpkit.dictionaries.process_types import Wordlist
    from corpkit.build import check_jdk

    import re
    if regex_nonword_filter:
        is_a_word = re.compile(regex_nonword_filter)
    else:
        is_a_word = re.compile(r'.*')
    
    have_java = check_jdk()

    # convert cql-style queries---pop for the sake of multiprocessing
    cql = kwargs.pop('cql', None)
    if cql:
        from corpkit.cql import to_corpkit
        search, exclude = to_corpkit(search)

    def signal_handler(signal, _):
        if root:
            return
        """pause on ctrl+c, rather than just stop loop"""   
        import signal
        import sys
        from time import localtime, strftime
        signal.signal(signal.SIGINT, original_sigint)
        thetime = strftime("%H:%M:%S", localtime())
        INPUTFUNC('\n\n%s: Paused. Press any key to resume, or ctrl+c to quit.\n' % thetime)
        time = strftime("%H:%M:%S", localtime())
        print('%s: Interrogation resumed.\n' % time)
        signal.signal(signal.SIGINT, signal_handler)

    def fix_show(show):
        """lowercase anything in show and turn into list"""
        if isinstance(show, list):
            show = [i.lower() for i in show]
        elif isinstance(show, STRINGTYPE):
            show = show.lower()
            show = [show]

        # this little 'n' business is a hack: when ngramming,
        # n shows have their n stripped, so nw should be nw 
        # so we know we're ngramming and so it's not empty.
        for index, val in enumerate(show):
            if val == 'n' or val == 'nw':
                show[index] = 'nw'
            elif val == 'b' or val == 'bw':
                show[index] = 'bw'
            elif val.endswith('pl'):
                show[index] = val.replace('pl', 'x')
            else:
                if len(val) == 2 and val.endswith('w'):
                    show[index] = val[0]
        return show

    def is_multiquery(corpus, search, query, just_speakers, outname):
        """determine if multiprocessing is needed
        do some retyping if need be as well"""
        is_mul = False
        from collections import OrderedDict
        #if hasattr(corpus, '__iter__'):
        #    is_mul = True
        # so we can do search = 't', query = ['NP', 'VP']:
        from corpkit.dictionaries.process_types import Wordlist
        
        #if isinstance(search, dict) and query in ['any', False, None]:
        #    if not all(k.islower() and k.isalpha() and len(k) < 4 for k in search.keys()):
        #        is_mul = 'namedqueriesmultiple'
        if isinstance(query, Wordlist):
            query = list(query)

        # what on earth is this?
        #if isinstance(query, list):
        #    if query != list(search.values())[0] or len(list(search.keys())) > 1:
        #        query = {c.title(): c for c in query}
        
        if isinstance(query, (dict, OrderedDict)):
            is_mul = 'namedqueriessingle'
        if just_speakers:
            if just_speakers == 'each':
                is_mul = 'eachspeaker'
                just_speakers = ['each']
            if just_speakers == ['each']:
                is_mul = 'eachspeaker'
            elif isinstance(just_speakers, STRINGTYPE):
                is_mul = False
                just_speakers = [just_speakers]
            #import re
            #if isinstance(just_speakers, re._pattern_type):
            #    is_mul = False
            if isinstance(just_speakers, list):
                if len(just_speakers) > 1:
                    'multiplespeaker'
        if isinstance(search, dict):
            if all(isinstance(i, dict) for i in list(search.values())):
                is_mul = 'namedqueriesmultiple'
        # cannot recursive multiquery
        if outname:
            is_mul = False
        return is_mul, corpus, search, query, just_speakers

    def slow_tregex(sents, **dummy_args):
        """do the speaker-specific version of tregex queries"""
        speakr = dummy_args.get('speaker', '')
        import os
        from corpkit.process import tregex_engine
        # first, put the relevant trees into temp file
        to_open = '\n'.join(sent.parse_string.strip() for sent in sents \
                              if sent.parse_string is not None)
        q = list(search.values())[0]
        ops = ['-o', '-%s' % translated_option]
        concs = []
        res = tregex_engine(query=q, 
                            options=ops, 
                            corpus=to_open,
                            root=root,
                            preserve_case=True
                           )
        if not no_conc:
            ops += ['-w', '-f']
            whole_res = tregex_engine(query=q, 
                                      options=ops, 
                                      corpus=to_open,
                                      root=root,
                                      preserve_case=True
                                     )
            for line in whole_res:
                line.insert(1, speakr) 

            res = format_tregex(res)
            whole_res = format_tregex(whole_res, whole=True)
            concs = make_conc_lines_from_whole_mid(whole_res, res)

        if root:
            root.update()
        if countmode:
            if isinstance(res, int):
                return res, False
            else:
                return len(res), False
        else:
            return res, concs

    def get_stats(sents, **dummy_args):
        """get a bunch of frequencies on interpersonal phenomena"""
        from collections import Counter
        statsmode_results = Counter()  
        # first, put the relevant trees into temp file

        for sent in sents:
            statsmode_results['Sentences'] += 1
            deps = get_deps(sent, dep_type)
            numpass = len([x for x in deps.links if x.type.endswith('pass')])
            statsmode_results['Passives'] += numpass
            statsmode_results['Tokens'] += len(sent.tokens)
            words = [w.word for w in sent.tokens if w.word is not None and w.word.isalnum()]
            statsmode_results['Words'] += len(words)
            statsmode_results['Characters'] += len(''.join(words))

        to_open = '\n'.join(s.parse_string.strip() for s in sents)

        from corpkit.dictionaries.process_types import processes
        from corpkit.other import as_regex
        tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                     'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                     'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Open class': r'/^(NN|JJ|VB|RB)/ < __',
                     'Closed class': r'__ !< __ !> /^(NN|JJ|VB|RB)/',
                     'Clauses': r'/^S/ < __',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Mental processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % \
                         as_regex(processes.mental, boundaries='w'),
                     'Verbal processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % \
                         as_regex(processes.verbal, boundaries='w'),
                     'Relational processes': r'VP > /^(S|ROOT)/ <+(VP) (VP <<# /%s/)' % \
                         as_regex(processes.relational, boundaries='w'),
                     'Verbless clause': r'/^S/ !<< /^VB.?/'}

        for name, q in sorted(tregex_qs.items()):
            res = tregex_engine(query=q, 
                                options=['-o', '-C'], 
                                corpus=to_open,  
                                root=root
                               )
            statsmode_results[name] += int(res)
            if root:
                root.update()
        return statsmode_results, []

    def make_conc_lines_from_whole_mid(wholes,
                                       middle_column_result
                                      ):
        """
        Create concordance line output from tregex output
        """
        import re
        import os
        if not wholes and not middle_column_result:
            return []

        conc_lines = []
        # remove duplicates from results
        unique_wholes = []
        unique_middle_column_result = []
        duplicates = []
        for (f, sk, whole), mid in zip(wholes, middle_column_result):
            joined = '-join-'.join([f, sk, whole, mid])
            if joined not in duplicates:
                duplicates.append(joined)
                unique_wholes.append([f, sk, whole])
                unique_middle_column_result.append(mid)

        # split into start, middle and end, dealing with multiple occurrences
        for (f, sk, whole), mid in zip(unique_wholes, unique_middle_column_result):
            reg = re.compile(r'([^a-zA-Z0-9-]|^)(' + re.escape(mid) + r')([^a-zA-Z0-9-]|$)', \
                             re.IGNORECASE | re.UNICODE)
            offsets = [(m.start(), m.end()) for m in re.finditer(reg, whole)]
            for offstart, offend in offsets:
                start, middle, end = whole[0:offstart].strip(), whole[offstart:offend].strip(), \
                                     whole[offend:].strip()
                conc_lines.append([os.path.basename(f), sk, start, middle, end])
        return conc_lines

    def uniquify(conc_lines):
        """get unique concordance lines"""
        from collections import OrderedDict
        unique_lines = []
        checking = []
        for index, (_, speakr, start, middle, end) in enumerate(conc_lines):
            joined = ' '.join([speakr, start, 'MIDDLEHERE:', middle, ':MIDDLEHERE', end])
            if joined not in checking:
                unique_lines.append(conc_lines[index])
            checking.append(joined)
        return unique_lines

    def lemmatiser(list_of_words, tag):
        """
        Take a list of unicode words and a tag and return a lemmatised list
        """
        output = []
        for word in list_of_words:
            if translated_option.startswith('u'):
                word = taglemma.get(word.lower(), 'Other')
            else:
                word = wordlist.get(word, lmtzr.lemmatize(word, tag))
            if not preserve_case:
                word = word.lower()
            output.append(word)
        return output

    def tgrep_searcher(sents, search, show, conc, **kwargs):
        """
        Use tgrep for constituency grammar search
        """
        f = kwargs.get('filename')
        from corpkit.process import show_tree_as_per_option, tgrep
        out = []
        conc_output = []
        conc_out = []
        for sent in sents:
            sk = get_speakername(sent)
            results = tgrep(sent, search['t'])
            for res in results:
                out.append(show_tree_as_per_option(show, res, sent))
                if conc:
                    lin = [f, sk, show_tree_as_per_option(show + ['whole'], res, sent)]
                    conc_out.append(lin)

        if conc:
            conc_output = make_conc_lines_from_whole_mid(conc_out, out)
        return out, conc_output

    def gettag(query, lemmatag=False):
        """
        Find tag for WordNet lemmatisation
        """
        if lemmatag:
            return lemmatag

        tagdict = {'N': 'n',
                   'J': 'a',
                   'V': 'v',
                   'A': 'r',
                   'None': False,
                   '': False,
                   'Off': False}

        # in case someone compiles the tregex query
        try:
            query = query.pattern
        except AttributeError:
            query = query
        

        qr = query.replace(r'\w', '').replace(r'\s', '').replace(r'\b', '')
        firstletter = next((c for c in qr if c.isalpha()), 'n')
        return tagdict.get(firstletter.upper(), 'n')

    def format_tregex(results, whole=False):
        """format tregex by show list"""
        import re

        if countmode:
            return results

        if not results:
            return

        done = []
        if whole:
            fnames, snames, results = zip(*results)

        if 'l' in show or 'x' in show:
            lemmata = lemmatiser(results, gettag(search.get('t'), lemmatag))
        else:
            lemmata = [None for i in results]
        for word, lemma in zip(results, lemmata):
            bits = []
            if exclude and exclude.get('w'):
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('w'), word):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('l'), lemma):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('p'), word):
                        continue
                if len(list(exclude.keys())) == 1 or excludemode == 'any':
                    if re.search(exclude.get('x'), lemma):
                        continue
            if exclude and excludemode == 'all':
                num_to_cause_exclude = len(list(exclude.keys()))
                current_num = 0
                if exclude.get('w'):
                    if re.search(exclude.get('w'), word):
                        current_num += 1
                if exclude.get('l'):
                    if re.search(exclude.get('l'), lemma):
                        current_num += 1
                if exclude.get('p'):
                    if re.search(exclude.get('p'), word):
                        current_num += 1
                if exclude.get('x'):
                    if re.search(exclude.get('x'), lemma):
                        current_num += 1   
                if current_num == num_to_cause_exclude:
                    continue                 

            for i in show:
                if i == 't':
                    bits.append(word)
                if i == 'l':
                    bits.append(lemma)
                elif i == 'w':
                    bits.append(word)
                elif i == 'p':
                    bits.append(word)
                elif i == 'x':
                    bits.append(lemma)
            joined = '/'.join(bits)
            done.append(joined)
        if whole:
            done = zip(fnames, snames, done)
        return done

    def tok_by_list(pattern, list_of_toks, concordancing=False, **kwargs):
        """search for regex in plaintext corpora"""
        import re
        if isinstance(pattern, STRINGTYPE):
            pattern = [pattern]
        if not case_sensitive:
            pattern = [p.lower() for p in pattern]
        if not concordancing:
            if case_sensitive:
                matches = [m for m in list_of_toks if m in pattern]
            else:
                matches = [m for m in list_of_toks if m.lower() in pattern]
        else:
            matches = []
            for index, token in enumerate(list_of_toks):
                if token in pattern:
                    if not split_contractions:
                        match = [' '.join(t for t in unsplitter(list_of_toks[:index]))[-140:]]
                    else:
                        match = [' '.join(t for t in list_of_toks[:index])[-140:]]
                    match.append(token)
                    if not split_contractions:
                        match.append(' '.join(t for t in unsplitter(list_of_toks[index + 1:]))[:140])
                    else:
                        match.append(' '.join(t for t in list_of_toks[index + 1:])[:140])

                    matches.append(match)
        if countmode:
            return len(matches)
        else:
            return matches

    def tok_ngrams(pattern, list_of_toks, concordancing=False, split_contractions=True):
        import re
        result = []
        list_of_toks = [x for x in list_of_toks if re.search(regex_nonword_filter, x)]

        if not split_contractions:
            list_of_toks = unsplitter(list_of_toks)
            
        for i in range(len(list_of_toks)):
            try:
                the_gram = [list_of_toks[i+x] for x in range(gramsize)]
                if any(re.search(pattern, x) for x in the_gram):
                    result.append(' '.join(the_gram))
            except IndexError:
                pass

        if countmode:
            return len(result)

        else:
            result = [i for i in result if result.count(i) > 1]
            return result

    def compiler(pattern):
        """compile regex or fail gracefully"""
        if hasattr(pattern, 'pattern'):
            return pattern
        import re
        try:
            if case_sensitive:
                comped = re.compile(pattern)
            else:
                comped = re.compile(pattern, re.IGNORECASE)
            return comped
        except:
            import traceback
            import sys
            from time import localtime, strftime
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Query %s' % (thetime, error_message))
            if root:
                return 'Bad query'
            else:
                raise ValueError('%s: Query %s' % (thetime, error_message))

    def tok_by_reg(pattern, list_of_toks, concordancing = False, **kwargs):
        """search for regex in plaintext corpora"""
        import re
        comped = compiler(pattern)
        if comped == 'Bad query':
            return 'Bad query'
        if not concordancing:
            matches = [m for m in list_of_toks if re.search(comped, m)]
        else:
            matches = []
            for index, token in enumerate(list_of_toks):
                if re.search(comped, token):
                    if not split_contractions:
                        match = [' '.join(t for t in unsplitter(list_of_toks[:index]))[-140:]]
                    else:
                        match = [' '.join(t for t in list_of_toks[:index])[-140:]]
                    match.append(re.search(comped, token).group(0))
                    if not split_contractions:
                        match.append(' '.join(t for t in unsplitter(list_of_toks[index + 1:]))[:140])
                    else:
                        match.append(' '.join(t for t in list_of_toks[index + 1:])[:140])
                    matches.append(match)
        if countmode:
            return len(matches)
        else:
            return matches

    def determine_search_func(show):
        """Figure out what search function we're using"""

        simple_tregex_mode = False
        statsmode = False
        tree_to_text = False

        if search.get('t') and not just_speakers and not kwargs.get('tgrep'):
            if have_java:
                simple_tregex_mode = True
                searcher = None
            else:
                searcher = tgrep_searcher
            optiontext = 'Searching parse trees'
        else:
            if datatype == 'plaintext':
                if any(i.endswith('n') for i in search.keys()):
                    optiontext = 'n-grams via plaintext'
                    raise NotImplementedError('Use a tokenised or parsed corpus for n-gramming.')
                    #searcher = plaintext_ngram
                elif any(i.endswith('w') for i in search.keys()):
                    if kwargs.get('regex', True):
                        searcher = plaintext_regex_search
                    else:
                        searcher = plaintext_simple_search
                    optiontext = 'Searching plaintext'
                else:
                    raise ValueError("Plaintext search must be 'w' or 'n'.")

            elif datatype == 'tokens':
                if any(i.endswith('n') for i in search.keys()):
                    searcher = tok_ngrams
                    optiontext = 'n-grams via tokens'
                elif any(i.endswith('w') for i in search.keys()):
                    if kwargs.get('regex', True):
                        searcher = tok_by_reg
                    else:
                        searcher = tok_by_list
                    if isinstance(search.get('w'), (list, Wordlist)):
                        searcher = tok_by_list
                    optiontext = 'Searching tokens'
            only_parse = ['r', 'd', 'g', 'dl', 'gl', 'df', 'gf',
                          'dp', 'gp', 'f', 'd2', 'd2f', 'd2p', 'd2l']
            
            if datatype != 'parse' and any(i in only_parse for i in list(search.keys())):
                form = ', '.join(i for i in list(search.keys()) if i in only_parse)
                raise ValueError('Need parsed corpus to search with "%s" option(s).' % form)

            elif datatype == 'parse':
                if any(i.endswith('n') for i in search.keys()):
                    search['w'] = search.pop('n')
                    if not show_ngram:
                        show = ['n']
                if any(i.endswith('t') for i in search.keys()):
                    if have_java and not kwargs.get('tgrep'):
                        searcher = slow_tregex
                    else:
                        searcher = tgrep_searcher
                    optiontext = 'Searching parse trees'
                elif any(i.endswith('s') for i in search.keys()):
                    searcher = get_stats
                    statsmode = True
                    optiontext = 'General statistics'
                elif any(i.endswith('r') for i in search.keys()):
                    from corpkit.depsearch import dep_searcher
                    searcher = dep_searcher
                    optiontext = 'Distance from root'
                else:
                    from corpkit.depsearch import dep_searcher
                    searcher = dep_searcher
                    optiontext = 'Dependency querying'
                
                # ngram mode for parsed data
                if show_ngram:
                    optiontext = 'N-grams from parsed data'
                    searcher = dep_searcher

        return searcher, optiontext, simple_tregex_mode, statsmode, tree_to_text

    def get_tregex_values():
        """If using Tregex, set appropriate values

        - Check for valid query
        - Make 'any' query
        - Make list query
        """

        translated_option = 't'
        if isinstance(search['t'], Wordlist):
            search['t'] = list(search['t'])
        q = tregex_engine(corpus=False,
                          query=search.get('t'),
                          options=['-t'],
                          check_query=True,
                          root=root,
                          preserve_case=preserve_case
                         )
        if q is False:
            if root:
                return 'Bad query', None
            else:
                return 'Bad query', None

        if isinstance(search['t'], list):
            regex = as_regex(search['t'], boundaries='line', case_sensitive=case_sensitive)
        else:
            regex = ''

        # listquery, anyquery, translated_option
        treg_dict = {'p': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'pl': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'x': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     't': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'o'],
                     'w': [r'/%s/ !< __' % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'c': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'C'],
                     'l': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 't']
                    }

        listq, anyq, translated_option = treg_dict.get(show[0].lower())
        if isinstance(search['t'], list):
            search['t'] = listq
        elif search['t'] == 'any':   
            search['t'] = anyq
        return search['t'], translated_option

    def plaintext_regex_search(pattern, plaintext_data, concordancing=False, **kwargs):
        """search for regex in plaintext corpora

        it searches over lines, so the user needs to be careful.
        """
        import re
        if concordancing:
            pattern = r'(.{,140})\b(' + pattern + r')\b(.{,140})'
        compiled_pattern = compiler(pattern)
        if compiled_pattern == 'Bad query':
            return 'Bad query'
        matches = re.findall(compiled_pattern, plaintext_data)
        if concordancing:
            matches = [list(m) for m in matches]
        if not concordancing:
            for index, i in enumerate(matches):
                if isinstance(i, tuple):
                    matches[index] = i[0]
        if countmode:
            return len(matches)
        else:
            return matches

    def correct_spelling(a_string):
        """correct spelling within a string"""
        if not spelling:
            return a_string
        from corpkit.dictionaries.word_transforms import usa_convert
        if spelling.lower() == 'uk':
            usa_convert = {v: k for k, v in list(usa_convert.items())}
        bits = a_string.split('/')
        for index, i in enumerate(bits):
            converted = usa_convert.get(i.lower(), i)
            if i.islower() or preserve_case is False:
                converted = converted.lower()
            elif i.isupper() and preserve_case:
                converted = converted.upper()
            elif i.istitle() and preserve_case:
                converted = converted.title()
            bits[index] = converted
        r = '/'.join(bits)
        return r

    def plaintext_simple_search(pattern, plaintext_data, concordancing=False, **kwargs):
        """search for tokens in plaintext corpora"""
        import re
        result = []
        if isinstance(pattern, STRINGTYPE):
            pattern = [pattern]
        for p in pattern:
            if concordancing:
                pat = r'(.{0,140})\b(' + re.escape(p) + r')\b(.{0,140})'
            pat = compiler(pat)
            if pat == 'Bad query':
                return 'Bad query'
            matches = re.findall(pat, plaintext_data)
            if concordancing:
                matches = [list(m) for m in matches]
                for i in matches:
                    result.append(i)
            else:   
                for m in range(len(matches)):
                    result.append(p)
        return result

    def make_search_iterable(corpus):
        """determine how to structure the corpus for interrogation"""
        
        # skip file definitions if they are not needed
        if simple_tregex_mode:
            if corpus.level in ['s', 'f']:
                return {(corpus.name, corpus.path): False}
            else:
                return {(os.path.basename(i), os.path.join(corpus.path, i)): False
                    for i in os.listdir(corpus.path)
                    if os.path.isdir(os.path.join(corpus.path, i))}

        if isinstance(corpus, Datalist):
            to_iterate_over = {}
            # it could be files or subcorpus objects
            if corpus[0].level == 's':
                if files_as_subcorpora:
                    for subc in corpus:
                        for f in subc.files:
                            to_iterate_over[(f.name, f.path)] = [f]
                else:
                    for subc in corpus:
                        to_iterate_over[(subc.name, subc.path)] = subc.files
            elif corpus[0].level == 'f':
                for f in corpus:
                    to_iterate_over[(f.name, f.path)] = [f]
        elif corpus.singlefile:
            to_iterate_over = {(corpus.name, corpus.path): [corpus]}
        elif not hasattr(corpus, 'subcorpora') or not corpus.subcorpora:
            # just files in a directory
            if files_as_subcorpora:
                to_iterate_over = {}
                for f in corpus.files:
                    to_iterate_over[(f.name, f.path)] = [f]
            else:
                to_iterate_over = {(corpus.name, corpus.path): corpus.files}
        else:
            to_iterate_over = {}
            if files_as_subcorpora:
                # don't know if possible: has subcorpora but also .files
                if hasattr(corpus, 'files') and corpus.files is not None:
                    for f in corpus.files:
                        to_iterate_over[(f.name, f.path)] = [f]
                # has subcorpora with files in those
                elif hasattr(corpus, 'files') and corpus.files is None:
                    for subc in corpus.subcorpora:
                        for f in subc.files:
                            to_iterate_over[(f.name, f.path)] = [f]
            else:
                if corpus[0].level == 's':
                    for subcorpus in corpus:
                        to_iterate_over[(subcorpus.name, subcorpus.path)] = subcorpus.files
                elif corpus[0].level == 'f':
                    for f in corpus:
                        to_iterate_over[(f.name, f.path)] = [f]
                else:
                    for subcorpus in corpus.subcorpora:
                        to_iterate_over[(subcorpus.name, subcorpus.path)] = subcorpus.files
        return to_iterate_over

    def welcome_printer(return_it=False):
        """Print welcome message"""
        if no_conc:
            message = 'Interrogating'
        else:
            message = 'Interrogating and concordancing'
        if only_conc:
            message = 'Concordancing'
        if kwargs.get('printstatus', True):
            thetime = strftime("%H:%M:%S", localtime())
            from corpkit.process import dictformat
            sformat = dictformat(search)
            welcome = ('\n%s: %s %s ...\n          %s\n          ' \
                        'Query: %s\n          %s corpus ... \n' % \
                      (thetime, message, cname, optiontext, sformat, message))
            if return_it:
                return welcome
            else:
                print(welcome)

    def goodbye_printer(return_it=False, only_conc=False):
        """Say goodbye before exiting"""
        if not kwargs.get('printstatus', True):
            return
        thetime = strftime("%H:%M:%S", localtime())
        if only_conc:
            
            show_me = (thetime, len(conc_df))
            finalstring = '\n\n%s: Concordancing finished! %d results.' % show_me
        else:
            finalstring = '\n\n%s: Interrogation finished!' % thetime
            if countmode:
                finalstring += ' %d matches.' % tot
            else:
                dat = (numentries, total_total)
                finalstring += ' %d unique results, %d total occurrences.' % dat
        if return_it:
            return finalstring
        else:
            print(finalstring)


    def make_conc_obj_from_conclines(conc_results):
        """
        Turn conclines into DataFrame
        """
        from corpkit.interrogation import Concordance
        all_conc_lines = []
        for sc_name, resu in sorted(conc_results.items()):
            if only_unique:
                unique_results = uniquify(resu)
            else:
                unique_results = resu
            #make into series
            if PYTHON_VERSION == 2:
                pindex = 'c f s l m r'.encode('utf-8').split()
            else:
                pindex = 'c f s l m r'.split()
            for fname, spkr, start, word, end in unique_results:
                #spkr = str(spkr, errors = 'ignore')
                fname = os.path.basename(fname)
                ser = [sc_name, fname, spkr, start, word, end]
                all_conc_lines.append(Series(ser, index=pindex))

        if random:
            from random import shuffle
            shuffle(all_conc_lines)

        try:
            conc_df = pd.concat(all_conc_lines, axis=1).T
            if all(x == '' for x in list(conc_df['s'].values)):
                conc_df.drop('s', axis=1, inplace=True)
            
            if show_ngram or show_collocates:
                if not language_model:
                    counted = Counter(conc_df['m'])
                    indices = [l for l in list(conc_df.index) if counted[conc_df.ix[l]['m']] > 1] 
                    conc_df = conc_df.ix[indices]
                    conc_df = conc_df.reset_index(drop=True)

            locs['corpus'] = corpus.name
            conc_df = Concordance(conc_df)
            try:
                conc_df.query = locs
            except AttributeError:
                pass
            return conc_df

        except ValueError:
            return

    def make_progress_bar():
        """generate a progress bar"""

        if simple_tregex_mode:
            total_files = len(list(to_iterate_over.keys()))
        else:
            total_files = sum(len(x) for x in list(to_iterate_over.values()))

        par_args = {'printstatus': kwargs.get('printstatus', True),
                    'root': root, 
                    'note': note,
                    'length': total_files,
                    'startnum': kwargs.get('startnum'),
                    'denom': kwargs.get('denominator', 1)}

        term = None
        if kwargs.get('paralleling', None) is not None:
            from blessings import Terminal
            term = Terminal()
            par_args['terminal'] = term
            par_args['linenum'] = kwargs.get('paralleling')

        if in_notebook:
            par_args['welcome_message'] = welcome_message

        outn = kwargs.get('outname', '')
        if outn:
            outn = getattr(outn, 'name', outn)
            outn = outn + ': '

        tstr = '%s%d/%d' % (outn, current_iter, total_files)
        p = animator(None, None, init=True, tot_string=tstr, **par_args)
        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
        animator(p, current_iter, tstr, **par_args)
        return p, outn, total_files, par_args

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')
    language_model = kwargs.get('language_model')

    # set up pause method
    original_sigint = signal.getsignal(signal.SIGINT)
    if kwargs.get('paralleling', None) is None:
        if not root:
            original_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal_handler)

    # find out about concordancing
    only_conc = False
    no_conc = False
    if conc is False:
        no_conc = True
    if isinstance(conc, str) and conc.lower() == 'only':
        only_conc = True
        no_conc = False
    numconc = 0

    # wipe non essential class attributes to not bloat query attrib
    if isinstance(corpus, Corpus):
        import copy
        corpus = copy.copy(corpus)
        for k, v in corpus.__dict__.items():
            if isinstance(v, (Interrogation, Interrodict)):
                corpus.__dict__.pop(k, None)

    # convert path to corpus object
    if not isinstance(corpus, (Corpus, Corpora, Subcorpus, File, Datalist)):
        if not multiprocess and not kwargs.get('outname'):
            corpus = Corpus(corpus, print_info=False)

    # figure out how the user has entered the query and show, and normalise
    from corpkit.process import searchfixer
    search = searchfixer(search, query)
    show = fix_show(show)
    
    show_ngram = any(x.startswith('n') for x in show)
    show_collocates = any(x.startswith('b') for x in show)

    # instantiate lemmatiser if need be
    if 'l' in show and isinstance(search, dict) and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr = WordNetLemmatizer()

    # do multiprocessing if need be
    im, corpus, search, query, just_speakers = is_multiquery(corpus, search, query, 
                                                just_speakers, kwargs.get('outname', False))

    # figure out if we can multiprocess the corpus
    if hasattr(corpus, '__iter__') and im:
        corpus = Corpus(corpus, print_info=False)
    if hasattr(corpus, '__iter__') and not im:
        im = 'datalist'
    if isinstance(corpus, Corpora):
        im = 'multiplecorpora'

    # split corpus if the user wants multiprocessing but no other iterable
    if not im and multiprocess:
        im = 'datalist'
        corpus = corpus[:]

    search = fix_search(search, case_sensitive=case_sensitive, root=root)
    exclude = fix_search(exclude, case_sensitive=case_sensitive, root=root)

    # if it's already been through pmultiquery, don't do it again
    locs['search'] = search
    locs['exclude'] = exclude
    locs['query'] = query
    locs['just_speakers'] = just_speakers
    locs['corpus'] = corpus
    locs['multiprocess'] = multiprocess
    locs['print_info'] = kwargs.get('printstatus', True)
    locs['multiple'] = im

    # send to multiprocess function
    if im:
        signal.signal(signal.SIGINT, original_sigint)
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)

    # get corpus metadata
    cname = corpus.name
    if isinstance(save, STRINGTYPE):
        savename = corpus.name + '-' + save
    if save is True:
        raise ValueError('save must be str, not bool.')


    datatype = getattr(corpus, 'datatype', 'parse')
    singlefile = getattr(corpus, 'singlefile', False)
    level = getattr(corpus, 'level', 'c')
        
    # store all results in here
    results = {}
    count_results = {}
    conc_results = {}

    # check if just counting, turn off conc if so
    countmode = 'c' in show
    if countmode:
        no_conc = True
        only_conc = False
    # where we are at in interrogation
    current_iter = 0

    # multiprocessing progress bar
    denom = kwargs.get('denominator', 1)
    startnum = kwargs.get('startnum', 0)

    # Determine the search function to be used #
    searcher, optiontext, simple_tregex_mode, statsmode, tree_to_text = determine_search_func(show)
    
    # no conc for statsmode
    if statsmode:
        no_conc = True
        only_conc = False
        conc = False

    # Set some Tregex-related values
    if search.get('t'):
        if show_ngram:
            raise ValueError("Can't search trees for n-grams---use a dependency search.")
        query, translated_option = get_tregex_values()
        if query == 'Bad query' and translated_option is None:
            if root:
                return 'Bad query'
            else:
                return
    # more tregex options
    if tree_to_text:
        treg_q = r'ROOT << __'
        op = ['-o', '-t', '-w']
    elif simple_tregex_mode:
        treg_q = search['t']
        op = ['-o', '-' + translated_option]

    # make iterable object for corpus interrogation
    to_iterate_over = make_search_iterable(corpus)

    from traitlets import TraitError
    try:
        from ipywidgets import IntProgress

        _ = IntProgress(min=0, max=10, value=1)
        in_notebook = True
    except TraitError:
        in_notebook = False
    except ImportError:
        in_notebook = False

    # print welcome message
    welcome_message = welcome_printer(return_it=in_notebook)

    # create a progress bar
    p, outn, total_files, par_args = make_progress_bar()

    # Iterate over data, doing interrogations
    for (subcorpus_name, subcorpus_path), files in sorted(to_iterate_over.items()):

        # results for subcorpus go here
        conc_results[subcorpus_name] = []
        count_results[subcorpus_name] = []
        results[subcorpus_name] = Counter()

        # get either everything (tree_to_text) or the search['t'] query
        if tree_to_text or simple_tregex_mode:
            result = tregex_engine(query=treg_q,
                                   options=op,
                                   corpus=subcorpus_path,
                                   root=root,
                                   preserve_case=preserve_case
                                  )

            # format search results with slashes etc
            if not countmode and not tree_to_text:
                result = format_tregex(result)

            # if concordancing, do the query again with 'whole' sent and fname
            if not no_conc:
                ops = ['-w', '-f'] + op
                whole_result = tregex_engine(query=search['t'],
                                             options=ops,
                                             corpus=subcorpus_path,
                                             root=root,
                                             preserve_case=preserve_case
                                            )
                for line in whole_result:
                    line.insert(1, '') 

                # format match too depending on option
                if not only_format_match:
                    whole_result = format_tregex(whole_result, whole=True)

                # make conc lines from conc results
                conc_result = make_conc_lines_from_whole_mid(whole_result, result)
                for lin in conc_result:
                    if numconc < maxconc or not maxconc:
                        conc_results[subcorpus_name].append(lin)
                    numconc += 1

            # add matches to ongoing counts
            if countmode:
                count_results[subcorpus_name] += [result]            
            else:
                result = Counter(result)
                results[subcorpus_name] += result

            # update progress bar
            current_iter += 1
            tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
            animator(p, current_iter, tstr, **par_args)

        # dependencies, plaintext, tokens, slow_tregex and tree_to_text
        if not simple_tregex_mode:
            for f in files:
                slow_treg_speaker_guess = kwargs.get('outname', False)
                if datatype == 'parse' and not tree_to_text:
                    # right now, this is not using the File class's read() or document
                    # methods. the reason is that there seem to be memory leaks. these
                    # may have been fixed already though.
                    try:
                        from corenlp_xml import Document
                    except ImportError:
                        from corenlp_xml.document import Document
                    with codecs.open(f.path, 'rb') as fo:
                        data = fo.read()
                    corenlp_xml = Document(data)
                    #corenlp_xml = f.document
                    if just_speakers:
                        import re
                        if isinstance(just_speakers, re._pattern_type):
                            sents = [s for s in corenlp_xml.sentences if \
                                     re.search(just_speakers, get_speakername(s))]
                        else:
                            sents = [s for s in corenlp_xml.sentences if get_speakername(s) in just_speakers]
                            if len(just_speakers) == 1:
                                slow_treg_speaker_guess = just_speakers[0]
                    else:
                        sents = corenlp_xml.sentences

                    # get coreferences
                    if kwargs.get('coref') or any(x.startswith('h') for x in show):
                        if just_speakers:
                            corefs = [i for i in corenlp_xml.coreferences if any(x == i.sentence for x in sents)]
                        else:
                            corefs = corenlp_xml.coreferences
                    else:
                        corefs = []
                        
                    corenlp_xml = None

                    res, conc_res = searcher(sents, search=search, show=show,
                                             dep_type=dep_type,
                                             exclude=exclude,
                                             excludemode=excludemode,
                                             searchmode=searchmode,
                                             case_sensitive=case_sensitive,
                                             conc=conc,
                                             only_format_match=only_format_match,
                                             speaker=slow_treg_speaker_guess,
                                             gramsize=gramsize,
                                             no_punct=no_punct,
                                             no_closed=no_closed,
                                             whitelist=whitelist,
                                             split_contractions=split_contractions,
                                             window=window,
                                             filename=f.name,
                                             language_model=language_model,
                                             corefs=corefs,
                                             is_a_word=is_a_word,
                                             **kwargs
                                            )

                    # garbage collection needed?
                    sents = None
                    corefs = None
                        
                    if res == 'Bad query':
                        return 'Bad query'

                if datatype == 'tokens':
                    import pickle
                    with codecs.open(f.path, "rb") as fo:
                        data = pickle.load(fo)
                elif datatype == 'plaintext' or tree_to_text:
                    if tree_to_text:
                        data = '\n'.join(result)
                        if not split_contractions:
                            data = unsplitter(data)
                    else:
                        with codecs.open(f.path, 'rb', encoding='utf-8') as data:
                            data = data.read()

                if datatype == 'tokens' or datatype == 'plaintext':

                    query = list(search.values())[0]

                    if not only_conc:
                        res = searcher(query,
                                       data,
                                       split_contractions=split_contractions, 
                                       concordancing=False
                                      )
                        if res == 'Bad query':
                            if root:
                                return 'Bad query'
                    if not no_conc:
                        conc_res = searcher(query,
                                            data,
                                            split_contractions=split_contractions, 
                                            concordancing=True
                                           )
                        if conc_res == 'Bad query':
                            if root:
                                return 'Bad query'
                        for line in conc_res:
                            line.insert(0, '')

                if countmode:
                    count_results[subcorpus_name] += [res]

                else:
                    # add filename and do lowercasing for conc
                    if not no_conc:
                        for line in conc_res:
                            if searcher != slow_tregex and searcher != tgrep_searcher:
                                line.insert(0, f.name)
                            else:
                                line[0] = f.name
                            if not preserve_case:
                                line[3:] = [x.lower() for x in line[3:]]
                            if spelling:
                                line = [correct_spelling(b) for b in line]
                            if numconc < maxconc or not maxconc:
                                conc_results[subcorpus_name].append(line)
                                numconc += 1

                    # do lowercasing and spelling
                    if not only_conc:
                        if not preserve_case:
                            if not statsmode:
                                res = [i.lower() for i in res]

                        if spelling:
                            if not statsmode:
                                res = [correct_spelling(r) for r in res]
                        #if not statsmode:
                        results[subcorpus_name] += Counter(res)
                        #else:
                        #results[subcorpus_name] += res

                # update progress bar
                current_iter += 1
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
                animator(p, current_iter, tstr, **par_args)

    # Get concordances into DataFrame, return if just conc
    if not no_conc:
        # fail on this line with typeerror if no results?
        conc_df = make_conc_obj_from_conclines(conc_results)

        if only_conc:
            locs = sanitise_dict(locs)
            try:
                conc_df.query = locs
            except AttributeError:
                return conc_df
            if save and not kwargs.get('outname'):
                print('\n')
                conc_df.save(savename)
            goodbye_printer(only_conc=True)
            if not root:
                signal.signal(signal.SIGINT, original_sigint)            
            return conc_df
    else:
        conc_df = None

    # Get interrogation into DataFrame
    if countmode:
        df = Series({k: sum(v) for k, v in sorted(count_results.items())})
        tot = df.sum()
    else:
        the_big_dict = {}
        unique_results = set(item for sublist in list(results.values()) for item in sublist)
        sortres = sorted(results.items(), key=lambda x: x[0])
        for word in unique_results:
            the_big_dict[word] = [subcorp_result[word] for _, subcorp_result in sortres]
        # turn master dict into dataframe, sorted
        df = DataFrame(the_big_dict, index=sorted(results.keys()))

        # for ngrams, remove hapaxes
        if show_ngram or show_collocates:
            if not language_model:
                df = df[[i for i in list(df.columns) if df[i].sum() > 1]]

        numentries = len(df.columns)
        tot = df.sum(axis=1)
        total_total = df.sum().sum()

    # turn df into series if all conditions met
    if not countmode:
        if level == 's' or singlefile:
            if not files_as_subcorpora:
                if not kwargs.get('df1_always_df'):
                    df = Series(df.ix[0])
                    df.sort_values(ascending=False, inplace=True)
                    tot = df.sum()
                    numentries = len(df.index)
                    total_total = tot

    # turn data into DF for GUI if need be
    if isinstance(df, Series) and kwargs.get('df1_always_df'):
        total_total = df.sum()
        df = DataFrame(df)
        tot = Series(total_total, index=['Total'])

    # if we're doing files as subcorpora,  we can remove the .txt.xml etc
    if isinstance(df, DataFrame) and files_as_subcorpora:
        cname = corpus.name.replace('-stripped', '').replace('-parsed', '')
        edits = [(r'(-[0-9][0-9][0-9])?\.txt\.xml', ''),
                 (r'-%s(-stripped)?(-parsed)?' % cname, '')]
        from corpkit.editor import editor
        df = editor(df, replace_subcorpus_names=edits).results
        tot = df.sum(axis=1)
        total_total = df.sum().sum()

    # sort by total
    if isinstance(df, DataFrame):
        if not df.empty:   
            df = df[list(df.sum().sort_values(ascending=False).index)]

    # make interrogation object
    locs['corpus'] = corpus.path
    locs = sanitise_dict(locs)
    interro = Interrogation(results=df, totals=tot, query=locs, concordance=conc_df)

    # save it
    if save and not kwargs.get('outname'):
        print('\n')
        interro.save(savename)
    
    goodbye = goodbye_printer(return_it=in_notebook)
    if in_notebook:
        try:
            p.children[2].value = goodbye.replace('\n', '')
        except AttributeError:
            pass
    if not root:
        signal.signal(signal.SIGINT, original_sigint)
    return interro
