"""
corpkit: Interrogate a parsed corpus
"""

#!/usr/bin/python

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

def interrogator(corpus, 
    search='w', 
    query='any',
    show='w',
    exclude=False,
    excludemode='any',
    searchmode='all',
    case_sensitive=False,
    save=False,
    subcorpora=False,
    just_speakers=False,
    just_metadata=False,
    skip_metadata=False,
    preserve_case=False,
    lemmatag=False,
    files_as_subcorpora=False,
    only_unique=False,
    only_format_match=True,
    multiprocess=False,
    spelling=False,
    regex_nonword_filter=r'[A-Za-z0-9]',
    gramsize=2,
    split_contractions=False,
    conc=False,
    maxconc=9999,
    window=4,
    no_closed=False,
    no_punct=True,
    discard=False,
    **kwargs):
    """
    Interrogate corpus, corpora, subcorpus and file objects.
    See corpkit.interrogation.interrogate() for docstring
    """
    
    conc = kwargs.get('do_concordancing', conc)
    quiet = kwargs.get('quiet', False)
    coref = kwargs.pop('coref', False)
    show_conc_metadata = kwargs.pop('show_conc_metadata', False)
    fsi_index = kwargs.pop('fsi_index', True)
    dep_type = kwargs.pop('dep_type', 'collapsed-ccprocessed-dependencies')

    nosubmode = subcorpora is None
    #todo: temporary
    #if getattr(corpus, '_dlist', False):
    #    subcorpora = 'file'

    # store kwargs and locs
    locs = locals().copy()
    locs.update(kwargs)
    locs.pop('kwargs', None)

    # so you can do corpus.interrogate('features/postags/wordclasses')
    if search == 'features':
        search = 'v'
        query = 'any'
    if search in ['postags', 'wordclasses']:
        query = 'any'
        show = 'p' if search == 'postags' else 'x'
        search = 't'
        preserve_case = True

    if not kwargs.get('cql') and isinstance(search, STRINGTYPE) and len(search) > 3:
        raise ValueError('search argument not recognised.')

    import codecs
    import signal
    import os
    from time import localtime, strftime
    from collections import Counter

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

    from traitlets import TraitError
    
    have_java = check_jdk()

    # convert cql-style queries---pop for the sake of multiprocessing
    cql = kwargs.pop('cql', None)
    if cql:
        from corpkit.cql import to_corpkit
        search, exclude = to_corpkit(search)

    def signal_handler(signal, _):
        """
        Allow pausing and restarting whn not in GUI
        """
        if root:
            return  
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
        """
        Lowercase anything in show and turn into list
        """
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
        """
        Determine if multiprocessing is needed/possibe, and 
        do some retyping if need be as well
        """
        is_mul = False
        from collections import OrderedDict
        from corpkit.dictionaries.process_types import Wordlist
        
        if isinstance(query, Wordlist):
            query = list(query)

        if subcorpora and multiprocess:
            is_mul = 'subcorpora'

        if isinstance(subcorpora, (list, tuple)):
            is_mul = 'subcorpora'

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
        return is_mul, corpus, search, query, just_speakers

    def slow_tregex(sents, **kwargs):
        """
        Do the metadata specific version of tregex queries

        This has some duplicate code from conll.py, which would ideally be resolved.
        When there are subcorpora involved, this seems faster than the conll.py
        recursive method, because it does not need to search multiple times with tregex
        """
        speakr = kwargs.get('speaker', '')
        subcorpora = kwargs.get('subcorpora')
        just_metadata = kwargs.get('just_metadata')
        skip_metadata = kwargs.get('skip_metadata')
        search = kwargs.get('search')['t']
        translated_option = kwargs.get('translated_option')

        from corpkit.process import tregex_engine
        from corpkit.conll import parse_conll, pipeline, process_df_for_speakers

        from corpkit.conll import parse_conll, cut_df_by_meta
        df = parse_conll(sents)
        df = cut_df_by_meta(df, just_metadata, skip_metadata)
        if df is None or df.empty:
            return {}, {}
        speak_tree = [(x.get(subcorpora, 'none'), x['parse']) for x in df._metadata.values()]
            
        if speak_tree:
            speak, tree = list(zip(*speak_tree))
        else:
            speak, tree = [], []
        
        if all(not x for x in speak):
            speak = False

        to_open = '\n'.join(tree)
        concs = []

        if not to_open.strip('\n'):
            if subcorpora:
                return {}, {}

        ops = ['-%s' % i for i in translated_option] + ['-o', '-n']
        res = tregex_engine(query=search, 
                            options=ops, 
                            corpus=to_open,
                            root=root,
                            preserve_case=True,
                            speaker_data=speak)

        res = format_tregex(res, speaker_data=speak)
        if not res:
            if subcorpora:
                return {}, {}

        if not no_conc:
            ops += ['-w']
            whole_res = tregex_engine(query=q, 
                                      options=ops, 
                                      corpus=to_open,
                                      root=root,
                                      preserve_case=True,
                                      speaker_data=speak)

            # format match too depending on option
            if not only_format_match:
                whole_res = format_tregex(whole_res, whole=True, speaker_data=speak)

            # make conc lines from conc results
            concs = make_conc_lines_from_whole_mid(whole_res, res, filename=dummy_args.get('filename'))
        else:
            concs = [False for i in res]

        if root:
            root.update()

        if subcorpora:
            from collections import defaultdict
            outres = defaultdict(list)
            outconc = defaultdict(list)
            for (_, met, r), line in zip(res, concs):
                outres[met].append(r)
                outconc[met].append(line)
            if countmode:
                outres = {k: len(v) for k, v in outres.items()}
                outconc = {}
            if no_conc:
                outconc = {k: [] for k, v in outres.items()}
            return outres, outconc

        if countmode:
            if isinstance(res, int):
                return res, False
            else:
                return len(res), False
        else:
            return res, concs

    def ispunct(s):
        import string
        return all(c in string.punctuation for c in s)

    def get_stats_conll(fname, **kwargs):
        """
        Do the metadata specific version of tregex queries
        """

        #todo: this should be moved to conll.pys
        import re
        from corpkit.dictionaries.process_types import processes
        from collections import Counter, defaultdict
        from corpkit.process import tregex_engine
        from corpkit.conll import parse_conll, pipeline, process_df_for_speakers, cut_df_by_meta

        subcorpora = kwargs.get('subcorpora')
        just_metadata = kwargs.get('just_metadata')
        skip_metadata = kwargs.get('skip_metadata')

        sub_res = {}

        df = parse_conll(fname)
        df = cut_df_by_meta(df, just_metadata, skip_metadata)
        speak_tree = [(x.get(subcorpora, 'none'), x['parse']) for x in df._metadata.values()]
        
        if speak_tree:
            speak, tree = list(zip(*speak_tree))
        else:
            speak, tree = [], []
        if subcorpora:
            all_cats = set(speak)
        else:
            all_cats = ['none']

        tregex_qs = {'Imperative': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     'Open interrogative': r'ROOT < SBARQ <<- (/\?/ !< __)', 
                     'Closed interrogative': r'ROOT ( < (SQ < (NP $+ VP)) << (/\?/ !< __) | < (/(S|SBAR)/ < (VP $+ NP)) <<- (/\?/ !< __))',
                     'Unmodalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declarative': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Clauses': r'/^S/ < __',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Processes': r'/VB.?/ >># (VP !< VP >+(VP) /^(S|ROOT)/)'}

        for cat in all_cats:
            new_df = process_df_for_speakers(df, df._metadata, cat, feature=subcorpora)
            sub_res[cat] = Counter()
            for name in tregex_qs.keys():
                sub_res[cat][name] = 0
            sub_res[cat]['Sentences'] = len(set(new_df.index.labels[0]))
            sub_res[cat]['Passives'] = len(new_df[new_df['f'] == 'nsubjpass'])
            sub_res[cat]['Tokens'] = len(new_df)
            # the below has returned a float before. i assume actually a nan?
            sub_res[cat]['Words'] = len([w for w in list(new_df['w']) if w and not ispunct(str(w))])
            sub_res[cat]['Characters'] = sum([len(str(w)) for w in list(new_df['w']) if w])
            sub_res[cat]['Open class'] = sum([1 for x in list(new_df['p']) if x and x[0] in ['N', 'J', 'V', 'R']])
            sub_res[cat]['Punctuation'] = sub_res[cat]['Tokens'] - sub_res[cat]['Words']
            sub_res[cat]['Closed class'] = sub_res[cat]['Words'] - sub_res[cat]['Open class']

        if all(not x for x in speak):
            speak = False

        to_open = '\n'.join(tree)

        if not to_open.strip('\n'):
            if subcorpora:
                return {}, {}

        for name, q in sorted(tregex_qs.items()):
            options = ['-o', '-t', '-n'] if name == 'Processes' else ['-o', '-n']
            # c option removed, could cause memory problems
            #ops = ['-%s' % i for i in translated_option] + ['-o', '-n']
            res = tregex_engine(query=q, 
                                options=options,
                                corpus=to_open,  
                                root=root,
                                speaker_data=speak)

            res = format_tregex(res, speaker_data=speak)
            if not res:
                continue
            concs = [False for i in res]
            for (_, met, r), line in zip(res, concs):
                sub_res[met][name] = len(res)
            if name != 'Processes':
                continue
            non_mat = 0
            for ptype in ['mental', 'relational', 'verbal']:
                reg = getattr(processes, ptype).words.as_regex(boundaries='l')
                count = len([i for i in res if re.search(reg, i[-1])])
                nname = ptype.title() + ' processes'
                sub_res[met][nname] = count

        if not res:
            if subcorpora:
                return {}, {}
        
        if root:
            root.update()

        fake_conc = {k: [] for k in sub_res.keys()}

        if list(sub_res.keys()) == ['none']:
            sub_res = sub_res['none']
            fake_conc = fake_conc['none']

        return sub_res, fake_conc

    def make_conc_lines_from_whole_mid(wholes,
                                       middle_column_result,
                                       filename=False):
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

        word_index = show.index('w') if 'w' in show else 0

        for (f, sk, whole), mid in list(zip(wholes, middle_column_result)):
            mid = mid[-1]
            joined = '-join-'.join([f, sk, whole, mid])
            if joined not in duplicates:
                duplicates.append(joined)
                unique_wholes.append([f, sk, whole])
                unique_middle_column_result.append(mid)

        # split into start, middle and end, dealing with multiple occurrences
        # this fails when multiple show values are given, because they are slash separated...
        for (f, sk, whole), mid in list(zip(unique_wholes, unique_middle_column_result)):
            mid = mid.split('/')[word_index]
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
            if 'u' in translated_option:
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
        # todo: rewrite, allowing for metadata and removing bad code

        f = kwargs.get('filename')
        from corpkit.process import show_tree_as_per_option, tgrep
        out = []
        conc_output = []
        conc_out = []
        if datatype == 'parse':
            for sent in sents:
                sk = get_speakername(sent)
                results = tgrep(sent.parse_string, search['t'])
                for res in results:
                    out.append(show_tree_as_per_option(show, res, corpus.datatype, sent))
                    if conc:
                        lin = [f, sk, show_tree_as_per_option(show + ['whole'], res, sent)]
                        conc_out.append(lin)
        
        elif datatype == 'conll':
            from corpkit.conll import parse_conll
            df = parse_conll(sents)
            for i, sent in df._metadata.items():
                sk = sent['speaker']
                results = tgrep(sent['parse'], search['t'])
                for res in results:
                    out.append(show_tree_as_per_option(show, res, corpus.datatype, sent, df=df, sent_id=i))
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

    def format_tregex(results, whole=False, speaker_data=False):
        """
        Format tregex by show list
        """
        import re

        if countmode:
            return results

        if not results:
            return

        done = []

        fnames, snames, results = zip(*results)

        # this needs to be standardised!
        new_show = [x.lstrip('m') for x in show]
        new_show = ['w' if not x else x for x in new_show]

        if 'l' in new_show or 'x' in new_show:
            lemmata = lemmatiser(results, gettag(search.get('t'), lemmatag))
        else:
            lemmata = [None for i in results]
        for word, lemma in list(zip(results, lemmata)):
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

            for i in new_show:
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

        done = list(zip(fnames, snames, done))
        
        return done

    def compiler(pattern):
        """
        Compile regex or fail gracefully
        """
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

    def determine_search_func(show):
        """Figure out what search function we're using"""

        simple_tregex_mode = False
        statsmode = False
        tree_to_text = False

        if datatype == 'conll':
            from corpkit.conll import pipeline
            searcher = pipeline

        simp_crit = all(not i for i in [just_speakers,
                                        kwargs.get('tgrep'),
                                        files_as_subcorpora,
                                        subcorpora,
                                        just_metadata,
                                        skip_metadata])

        if search.get('t') and simp_crit:
            if have_java:
                simple_tregex_mode = True
                searcher = None
            else:
                searcher = tgrep_searcher
            optiontext = 'Searching parse trees'

        elif datatype == 'conll':
        
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
            elif any(i.endswith('v') for i in search.keys()):
                # either of these searchers now seems to work
                searcher = pipeline
                #seacher = get_stats_conll
                statsmode = True
                optiontext = 'General statistics'
            elif any(i.endswith('r') for i in search.keys()):
                searcher = pipeline
                optiontext = 'Distance from root'
            else:
                searcher = pipeline
                optiontext = 'Querying CONLL data'
            # ngram mode for parsed data
            if show_ngram:
                optiontext = 'N-grams from CONLL data'
                searcher = pipeline

        return searcher, optiontext, simple_tregex_mode, statsmode, tree_to_text

    def get_tregex_values(show):
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

        # so many of these bad fixing loops!
        nshow = []
        for i in show:
            if i == 'm':
                nshow.append('w')
            else:
                nshow.append(i.lstrip('m'))
        show = nshow

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
                     'l': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'u': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'v']
                    }

        newshow = []

        listq, anyq, translated_option = treg_dict.get(show[0][-1].lower())
        newshow.append(translated_option)
        for item in show[1:]:
            _, _, noption = treg_dict.get(item.lower())
            newshow.append(noption)

        if isinstance(search['t'], list):
            search['t'] = listq
        elif search['t'] == 'any':   
            search['t'] = anyq
        return search['t'], newshow

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

    def make_search_iterable(corpus):
        """determine how to structure the corpus for interrogation"""
        # skip file definitions if they are not needed
        if getattr(corpus, '_dlist', False):

            return {(i.name, i.path): [i] for i in list(corpus.files)}
            #return {('Sample', 'Sample'): list(corpus.files)}

        if simple_tregex_mode:
            if corpus.level in ['s', 'f', 'd']:
                return {(corpus.name, corpus.path): False}
            else:
                return {(os.path.basename(i), os.path.join(corpus.path, i)): False
                    for i in os.listdir(corpus.path)
                    if os.path.isdir(os.path.join(corpus.path, i))}

        if isinstance(corpus, Datalist):
            to_iterate_over = {}
            # it could be files or subcorpus objects
            if corpus[0].level in ['s', 'd']:
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

    def get_conc_colnames(corpus,
                          fsi_index=False,
                          simple_tregex_mode=False):
    
        fields = []
        base = 'c f s l m r'
        
        if simple_tregex_mode:
            base = base.replace('f ', '')

        if fsi_index and not simple_tregex_mode:
            base = 'i ' + base
        
        if PYTHON_VERSION == 2:
            base = base.encode('utf-8').split()
        else:
            base = base.split() 

        if show_conc_metadata:
            from corpkit.build import get_all_metadata_fields
            meta = get_all_metadata_fields(corpus.path)

            if isinstance(show_conc_metadata, list):
                meta = [i for i in meta if i in show_conc_metadata]
            #elif show_conc_metadata is True:
            #    pass
            for i in sorted(meta):
                if i in ['speaker', 'sent_id', 'parse']:
                    continue
                if PYTHON_VERSION == 2:
                    base.append(i.encode('utf-8'))
                else:
                    base.append(i)
        return base

    def make_conc_obj_from_conclines(conc_results, fsi_index=False):
        """
        Turn conclines into DataFrame
        """
        from corpkit.interrogation import Concordance
        #fsi_place = 2 if fsi_index else 0

        all_conc_lines = []
        for sc_name, resu in sorted(conc_results.items()):
            if only_unique:
                unique_results = uniquify(resu)
            else:
                unique_results = resu
            #make into series
            for lin in unique_results:
                #spkr = str(spkr, errors = 'ignore')
                #if not subcorpora:
                #    lin[fsi_place] = lin[fsi_place]
                #lin.insert(fsi_place, sc_name)

                if len(lin) < len(conc_col_names):
                    diff = len(conc_col_names) - len(lin)
                    lin.extend(['none'] * diff)


                all_conc_lines.append(Series(lin, index=conc_col_names))

        conc_df = pd.concat(all_conc_lines, axis=1).T

        if all(x == '' for x in list(conc_df['s'].values)) or \
           all(x == 'none' for x in list(conc_df['s'].values)):
            conc_df.drop('s', axis=1, inplace=True)
        
        if show_collocates and not language_model:
            counted = Counter(conc_df['m'])
            indices = [l for l in list(conc_df.index) if counted[conc_df.ix[l]['m']] > 1] 
            conc_df = conc_df.ix[indices]
            conc_df = conc_df.reset_index(drop=True)

        locs['corpus'] = corpus.name

        # there is an error in xml conc that duplicates results
        # i'm not maintaining it anymore, but i'll fix it with this
        if datatype == 'parse':
            conc_df = conc_df.drop_duplicates().reset_index()
        if maxconc:
            conc_df = Concordance(conc_df[:maxconc])
        else:
            conc_df = Concordance(conc_df)
        try:
            conc_df.query = locs
        except AttributeError:
            pass
        return conc_df

    def lowercase_result(res):
        """      
        Take any result and do spelling/lowercasing if need be
        """
        if not res or statsmode:
            return res
        if not preserve_case:
            if isinstance(res[0], tuple):
                newr = []
                for tup in res:
                    tup = list(tup)
                    tup[-1] = tup[-1].lower()
                    newr.append(tuple(tup))
                res = newr
            else:
                res = [i.lower() for i in res]
        if spelling:
            res = [correct_spelling(r) for r in res]
        return res

    def postprocess_concline(line, fsi_index=False):
        # todo: are these right?
        subc, star, en = 0, 2, 5
        if fsi_index:
            subc, star, en = 2, 4, 7
        #if searcher != slow_tregex and searcher != tgrep_searcher \
        #    and datatype != 'conll':
        #    line.insert(subc, f.name)
        #else:
        #    line[subc] = f.name
        if not preserve_case:
            line[star:en] = [str(x).lower() for x in line[star:en]]
        if spelling:
            line[star:en] = [correct_spelling(str(b)) for b in line[star:en]]
        return line

    def make_progress_bar():
        """generate a progress bar"""

        if simple_tregex_mode:
            total_files = len(list(to_iterate_over.keys()))
        else:
            total_files = sum(len(x) for x in list(to_iterate_over.values()))

        par_args = {'printstatus': kwargs.get('printstatus', True),
                    'root': root, 
                    'note': note,
                    'quiet': quiet,
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
    if any(i.endswith('l') for i in show) and isinstance(search, dict) and search.get('t'):
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
        if hasattr(corpus, 'subcorpora') and corpus.subcorpora:
            corpus = corpus[:]
        else:
            corpus = corpus.files

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
    locs['subcorpora'] = subcorpora

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
    from collections import defaultdict
    results = defaultdict(Counter)
    count_results = defaultdict(list)
    conc_results = defaultdict(list)

    # check if just counting, turn off conc if so
    countmode = 'c' in show or 'mc' in show
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
    translated_option = False
    if search.get('t'):
        if show_ngram:
            raise ValueError("Can't search trees for n-grams---use a dependency search.")
        query, translated_option = get_tregex_values(show)
        if query == 'Bad query' and translated_option is None:
            if root:
                return 'Bad query'
            else:
                return
    # more tregex options
    if tree_to_text:
        treg_q = r'ROOT << __'
        op = ['-o', '-t', '-w', '-f']
    elif simple_tregex_mode:
        treg_q = search['t']
        op = ['-%s' % i for i in translated_option] + ['-o', '-f']

    # make iterable object for corpus interrogation
    to_iterate_over = make_search_iterable(corpus)

    try:
        from ipywidgets import IntProgress
        _ = IntProgress(min=0, max=10, value=1)
        in_notebook = True
    except TraitError:
        in_notebook = False
    except ImportError:
        in_notebook = False
    # caused in newest ipython
    except AttributeError:
        in_notebook = False

    # print welcome message
    welcome_message = welcome_printer(return_it=in_notebook)

    # create a progress bar
    p, outn, total_files, par_args = make_progress_bar()

    if conc:
        conc_col_names = get_conc_colnames(corpus,
                                           fsi_index=fsi_index,
                                           simple_tregex_mode=simple_tregex_mode)
 

    # Iterate over data, doing interrogations
    for (subcorpus_name, subcorpus_path), files in sorted(to_iterate_over.items()):
        if nosubmode:
            subcorpus_name = '_nosubmode'

        # results for subcorpus go here
        #conc_results[subcorpus_name] = []
        #count_results[subcorpus_name] = []
        #results[subcorpus_name] = Counter()

        # get either everything (tree_to_text) or the search['t'] query
        if tree_to_text or simple_tregex_mode:
            result = tregex_engine(query=treg_q,
                                   options=op,
                                   corpus=subcorpus_path,
                                   root=root,
                                   preserve_case=preserve_case)

            # format search results with slashes etc
            if not countmode and not tree_to_text:
                result = format_tregex(result)

            # if concordancing, do the query again with 'whole' sent and fname
            if not no_conc:
                ops = ['-w'] + op
                #ops = [i for i in ops if i != '-n']
                whole_result = tregex_engine(query=search['t'],
                                             options=ops,
                                             corpus=subcorpus_path,
                                             root=root,
                                             preserve_case=preserve_case
                                            )

                # format match too depending on option
                if not only_format_match:
                    whole_result = format_tregex(whole_result, whole=True)

                # make conc lines from conc results
                conc_result = make_conc_lines_from_whole_mid(whole_result, result)
                for lin in conc_result:
                    if maxconc is False or numconc < maxconc:
                        conc_results[subcorpus_name].append(lin)
                    numconc += 1

            # add matches to ongoing counts
            if countmode:
                count_results[subcorpus_name] += [result]            
            else:
                if result:
                    results[subcorpus_name] += Counter([i[-1] for i in result])
                else:
                    results[subcorpus_name] += Counter()

            # update progress bar
            current_iter += 1
            tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
            animator(p, current_iter, tstr, **par_args)
            continue

        # todo: move this
        kwargs.pop('by_metadata', None)
        
        # conll querying goes by file, not subcorpus
        for f in files:
            from corpkit.process import parse_just_speakers
            slow_treg_speaker_guess = kwargs.get('outname', '') if kwargs.get('multispeaker') else ''
            just_speakers = parse_just_speakers(just_speakers, corpus)
            filepath, corefs = f.path, coref
            res, conc_res = searcher(filepath, search=search, show=show,
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
                                     just_speakers=just_speakers,
                                     split_contractions=split_contractions,
                                     window=window,
                                     filename=f.path,
                                     coref=corefs,
                                     countmode=countmode,
                                     maxconc=(maxconc, numconc),
                                     is_a_word=is_a_word,
                                     by_metadata=subcorpora,
                                     show_conc_metadata=show_conc_metadata,
                                     just_metadata=just_metadata,
                                     skip_metadata=skip_metadata,
                                     fsi_index=fsi_index,
                                     category=subcorpus_name,
                                     translated_option=translated_option,
                                     statsmode=statsmode,
                                     **kwargs
                                    )


            if res is None and conc_res is None:
                current_iter += 1
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
                animator(p, current_iter, tstr, **par_args)
                continue

            # deal with symbolic structures---that is, rather than adding
            # results by subcorpora, add them by metadata value
            # todo: sorting?
            if subcorpora:
                for (k, v), concl in zip(res.items(), conc_res.values()):                            
                    v = lowercase_result(v)
                    results[k] += Counter(v)
                    for line in concl:
                        if maxconc is False or numconc < maxconc:
                            line = postprocess_concline(line,
                                fsi_index=fsi_index)
                            conc_results[k].append(line)
                            numconc += 1
                
                current_iter += 1
                tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
                animator(p, current_iter, tstr, **par_args)
                continue

            # garbage collection needed?
            sents = None
            corefs = None
                
            if res == 'Bad query':
                return 'Bad query'

            if countmode:
                count_results[subcorpus_name] += [res]

            else:
                # add filename and do lowercasing for conc
                if not no_conc:
                    for line in conc_res:
                        line = postprocess_concline(line,
                            fsi_index=fsi_index)
                        if maxconc is False or numconc < maxconc:
                            conc_results[subcorpus_name].append(line)
                            numconc += 1

                # do lowercasing and spelling
                if not only_conc:
                    res = lowercase_result(res)
                    # discard removes low results, helping with 
                    # curse of dimensionality
                    countres = Counter(res)
                    if isinstance(discard, float):
                        countres.most_common()
                        nkeep = len(counter) - len(counter) * discard
                        countres = Counter({k: v for i, (k, v) in enumerate(countres.most_common()) if i <= nkeep})
                    elif isinstance(discard, int):
                        countres = Counter({k: v for k, v in countres.most_common() if v >= discard})
                    results[subcorpus_name] += countres
                    #else:
                    #results[subcorpus_name] += res

            # update progress bar
            current_iter += 1
            tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
            animator(p, current_iter, tstr, **par_args)

    # Get concordances into DataFrame, return if just conc
    if not no_conc:
        # fail on this line with typeerror if no results?
        conc_df = make_conc_obj_from_conclines(conc_results, fsi_index=fsi_index)

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
    conds = [countmode,
             files_as_subcorpora,
             subcorpora,
             kwargs.get('df1_always_df')]
    anyxs = [level == 's',
             singlefile,
             nosubmode]
    if all(not x for x in conds) and any(x for x in anyxs):
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
        edits = [(r'(-[0-9][0-9][0-9])?\.txt\.(xml|conll)', ''),
                 (r'-%s(-stripped)?(-parsed)?' % cname, '')]
        from corpkit.editor import editor
        df = editor(df, replace_subcorpus_names=edits).results
        tot = df.sum(axis=1)
        total_total = df.sum().sum()

    if conc_df is not None and conc_df is not False:
        # removed 'f' from here for now
        for col in ['c']:
            for pat in ['.txt', '.xml', '.conll']:
                conc_df[col] = conc_df[col].str.replace(pat, '')
            conc_df[col] = conc_df[col].str.replace(r'-[0-9][0-9][0-9]$', '')

        #df.index = df.index.str.replace('w', 'this')

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
