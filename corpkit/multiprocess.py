"""corpkit: multiprocessing of interrogations"""

from __future__ import print_function

def pmultiquery(corpus, 
                search,
                show='words',
                query='any', 
                sort_by='total', 
                save=False,
                multiprocess='default', 
                just_speakers=False,
                root=False,
                note=False,
                print_info=True,
                subcorpora=False,
                **kwargs
               ):
    """
    - Parallel process multiple queries or corpora.
    - This function is used by corpkit.interrogator.interrogator()
    - for multiprocessing.
    - There's no reason to call this function yourself.
    """
    import os
    from pandas import DataFrame, Series
    import pandas as pd
    import collections
    from collections import namedtuple, OrderedDict
    from time import strftime, localtime
    import corpkit
    from corpkit.interrogator import interrogator
    from corpkit.interrogation import Interrogation
    from corpkit.process import canpickle
    try:
        from joblib import Parallel, delayed
    except ImportError:
        pass
    import multiprocessing

    locs = locals()
    for k, v in kwargs.items():
        locs[k] = v
    in_notebook = locs.get('in_notebook')

    def best_num_parallel(num_cores, num_queries):
        """decide how many parallel processes to run

        the idea, more or less, is to balance the load when possible"""
        import corpkit
        if num_queries <= num_cores:
            return num_queries
        if num_queries > num_cores:
            if (num_queries / num_cores) == num_cores:
                return int(num_cores)
            if num_queries % num_cores == 0:
                try:
                    return max([int(num_queries / n) for n in range(2, num_cores) \
                               if int(num_queries / n) <= num_cores])   
                except ValueError:
                    return num_cores
            else:
                import math
                if (float(math.sqrt(num_queries))).is_integer():
                    square_root = math.sqrt(num_queries)
                    if square_root <= num_queries / num_cores: 
                        return int(square_root)    
        return num_cores

    num_cores = multiprocessing.cpu_count()

    # what is our iterable? ...
    multiple = kwargs.get('multiple', False)
    mult_corp_are_subs = False
    if hasattr(corpus, '__iter__'):
        if all(getattr(x, 'level', False) == 's' for x in corpus):
            mult_corp_are_subs = True

    if just_speakers:
        if just_speakers is True:
            import re
            just_speakers = re.compile(r'.*')
        else:
            from corpkit.build import get_speaker_names_from_parsed_corpus
            if just_speakers == 'each' or just_speakers == ['each']:
                just_speakers = get_speaker_names_from_parsed_corpus(corpus)
            if len(just_speakers) == 0:
                print('No speaker name data found.')
                return

    non_first_sub = None
    if subcorpora:
        non_first_sub = subcorpora[1:] if isinstance(subcorpora, list) else None
        subval = subcorpora if not non_first_sub else subcorpora[0]
        #print(subcorpora, non_first_sub, subval)
        if subcorpora is True:
            import re
            subcorpora = re.compile(r'.*')
        else: 
            from corpkit.build import get_speaker_names_from_parsed_corpus
            subcorpora = get_speaker_names_from_parsed_corpus(corpus, feature=subval)
            if len(subcorpora) == 0:
                print('No %s metadata found.' % str(subval))
                return

    mapcores = {'datalist': [corpus, 'corpus'],
                'multiplecorpora': [corpus, 'corpus'],
                'namedqueriessingle': [query, 'query'],
                'eachspeaker': [just_speakers, 'just_speakers'],
                'multiplespeaker': [just_speakers, 'just_speakers'],
                'namedqueriesmultiple': [search, 'search'],
                'subcorpora': [subcorpora, 'subcorpora']}

    # a is a dummy, just to produce default one
    toiter, itsname = mapcores.get(multiple, [False, False])
    if isinstance(toiter, dict):
        toiter = toiter.items()
    denom = len(toiter)
    num_cores = best_num_parallel(num_cores, denom)

    vals = ['eachspeaker', 'multiplespeaker', 'namedqueriesmultiple']
    if multiple == 'multiplecorpora' and any(x is True for x in vals):
        from corpkit.corpus import Corpus, Corpora
        if isinstance(corpus, Corpora):
            multiprocess = False
        else:
            corpus = Corpus(corpus)

    if isinstance(multiprocess, int):
        num_cores = multiprocess
    if multiprocess is False:
        num_cores = 1

    # make sure saves are right type
    if save is True:
        raise ValueError('save must be string when multiprocessing.')

    # make a list of dicts to pass to interrogator,
    # with the iterable unique in every one
    locs['printstatus'] = False
    locs['multiprocess'] = False
    locs['df1_always_df'] = False
    locs['files_as_subcorpora'] = False
    locs['just_speakers'] = just_speakers
    locs['corpus'] = corpus

    if multiple == 'multiplespeaker':
        locs['multispeaker'] = True

    if isinstance(non_first_sub, list) and len(non_first_sub) == 1:
        non_first_sub = non_first_sub[0]

    # make the default query
    locs = {k: v for k, v in locs.items() if canpickle(v)}
    # make a new dict for every iteration
    ds = [dict(**locs) for i in range(denom)]
    for index, (d, bit) in enumerate(zip(ds, toiter)):
        d['paralleling'] = index
        if multiple in ['namedqueriessingle', 'namedqueriesmultiple']:
            d[itsname] = bit[1]
            d['outname'] = bit[0]
        elif multiple in ['multiplecorpora', 'datalist']:
            d['outname'] = bit.name.replace('-parsed', '')
            d[itsname] = bit
        elif multiple in ['eachspeaker', 'multiplespeaker']:
            d[itsname] = bit
            d['just_speakers'] = bit
            d['outname'] = bit
        elif multiple in ['subcorpora']:
            d[itsname] = bit
            jmd = {subval: bit}
            # put this earlier
            j2 = kwargs.get('just_metadata', False)
            if not j2:
                j2 = {}
            jmd.update(j2)
    
            d['just_metadata'] = jmd
            d['outname'] = bit
            d['by_metadata'] = False
            d['subcorpora'] = non_first_sub
            if non_first_sub:
                d['print_info'] = False

    # message printer should be a function...
    if kwargs.get('conc') is False:
        message = 'Interrogating'
    elif kwargs.get('conc') is True:
        message = 'Interrogating and concordancing'
    elif kwargs.get('conc').lower() == 'only':
        message = 'Concordancing'

    time = strftime("%H:%M:%S", localtime())
    from corpkit.process import dictformat
    
    if print_info:

        # proper printing for plurals
        # in truth this needs to be revised, it's horrible.
        sformat = dictformat(search, query)

        if num_cores == 1:
            add_es = ''
        else:
            add_es = 'es'
        if multiple in ['multiplecorpora', 'datalist']:
            corplist = "\n              ".join([i.name for i in list(corpus)[:20]])
            if len(corpus) > 20:
                corplist += '\n ... and %d more ...\n' % (len(corpus) - 20)
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s):\n              %s" \
               "\n          Query: %s\n          %s corpus ... \n"  % (time, len(corpus), num_cores, add_es, corplist, sformat, message)))

        elif multiple == 'namedqueriessingle':
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s): %s" \
               "\n          Queries: %s\n          %s corpus ... \n" % (time, len(query), num_cores,  add_es, corpus.name, sformat, message) ))

        elif multiple == 'namedqueriesmultiple':
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s): %s" \
               "\n          Queries: %s\n          %s corpus ... \n" % (time, len(list(search.keys())), num_cores, add_es, corpus.name, sformat, message)))

        elif multiple in ['eachspeaker', 'multiplespeaker']:
            print(("\n%s: Beginning %d parallel corpus interrogation%s: %s" \
               "\n          Query: %s\n          %s corpus ... \n" % (time, num_cores, add_es.lstrip('e'), corpus.name, sformat, message) ))
        elif multiple in ['subcorpora']:
            print(("\n%s: Beginning %d parallel corpus interrogation%s: %s" \
               "\n          Query: %s\n          %s corpus ... \n" % (time, num_cores, add_es.lstrip('e'), corpus.name, sformat, message) ))

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    #import sys
    #reload(sys)
    #stdout=sys.stdout
    failed = False
    terminal = False
    used_joblib = False
    #ds = ds[::-1]
    #todo: the number of blank lines to print can be way wrong
    if not root and print_info:
        from blessings import Terminal
        terminal = Terminal()
        print('\n' * (len(ds) - 2))
        for dobj in ds:
            linenum = dobj['paralleling']
            # this try handles nosetest problems in sublime text
            try:
                with terminal.location(0, terminal.height - (linenum + 1)):
                    # this is a really bad idea.
                    thetime = strftime("%H:%M:%S", localtime())
                    num_spaces = 26 - len(dobj['outname'])
                    print('%s: QUEUED: %s' % (thetime, dobj['outname']))
            except:
                pass

    if not root and multiprocess:
        #res = Parallel(n_jobs=num_cores)(delayed(interrogator)(**x) for x in ds)
        try:
            #ds = sorted(ds, key=lambda k: k['paralleling'], reverse = True) 
            res = Parallel(n_jobs=num_cores)(delayed(interrogator)(**x) for x in ds)
            used_joblib = True
        except:
            failed = True
            print('Multiprocessing failed.')
            raise
        if not res:
            failed = True
    else:
        res = []
        for index, d in enumerate(ds):
            d['startnum'] = (100 / denom) * index
            res.append(interrogator(**d))
        try:
            res = sorted([i for i in res if i])
        except:
            pass

    # remove unpicklable bits from query
    from types import ModuleType, FunctionType, BuiltinMethodType, BuiltinFunctionType
    badtypes = (ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType)
    qlocs = {k: v for k, v in locs.items() if not isinstance(v, badtypes)}

    if hasattr(qlocs['corpus'], 'name'):
        qlocs['corpus'] = qlocs['corpus'].path
    else:
        qlocs['corpus'] = list([i.path for i in qlocs['corpus']])

    from corpkit.interrogation import Concordance
    if kwargs.get('conc') == 'only':
        concs = pd.concat([x for x in res])
        thetime = strftime("%H:%M:%S", localtime())
        concs = concs.reset_index(drop=True)
        if kwargs.get('maxconc'):
            concs = concs[:kwargs.get('maxconc')]
        lines = Concordance(concs)
        
        if save:
            lines.save(save, print_info=print_info)

        if print_info:
            print('\n\n%s: Finished! %d results.\n\n' % (thetime, len(concs.index)))

        return lines

    from corpkit.interrogation import Interrodict

    if isinstance(res[0], Interrodict) or not all(isinstance(i.results, Series) for i in res):
        out = OrderedDict()
        for interrog, d in zip(res, ds):
            for unpicklable in ['note', 'root']:
                interrog.query.pop(unpicklable, None)
            try:
                out[interrog.query['outname']] = interrog
            except KeyError:
                out[d['outname']] = interrog

        idict = Interrodict(out)
        
        if print_info:
            thetime = strftime("%H:%M:%S", localtime())
            print("\n\n%s: Finished! Output is multi-indexed." % thetime)
        idict.query = qlocs

        if save:
            idict.save(save, print_info=print_info)

        return idict

    # make query and total branch, save, return
    # todo: standardise this so we don't have to guess transposes
    else:
        if multiple == 'multiplecorpora' and not mult_corp_are_subs:
            sers = [i.results for i in res]
            out = DataFrame(sers, index=[i.query['outname'] for i in res])
            out = out.reindex_axis(sorted(out.columns), axis=1) # sort cols
            out = out.fillna(0) # nan to zero
            out = out.astype(int) # float to int
            out = out.T            
        else:
            try:
                out = pd.concat([r.results for r in res], axis=1)
                out = out.T
                out.index = [i.query['outname'] for i in res]
            except ValueError:
                return None
            # format like normal
            # this sorts subcorpora, which are cls
            out = out[sorted(list(out.columns))]
            # puts subcorpora in the right place
            if not mult_corp_are_subs and multiple != 'subcorpora':
                out = out.T
            if multiple == 'subcorpora':
                out = out.sort_index()
            out = out.fillna(0) # nan to zero
            out = out.astype(int)
            if 'c' in show and mult_corp_are_subs:
                out = out.sum()
                out.index = sorted(list(out.index))

        # sort by total
        if isinstance(out, DataFrame):
            out = out[list(out.sum().sort_values(ascending=False).index)]

            # really need to figure out the deal with tranposing!
            if all(x.endswith('.xml') for x in list(out.columns)) \
            or all(x.endswith('.txt') for x in list(out.columns)):
                out = out.T
        out = out.edit(sort_by=sort_by, print_info=False, keep_stats=False, \
                      df1_always_df=kwargs.get('df1_always_df'))
        out.query = qlocs

        if len(out.results.columns) == 1:
            out.results = out.results.sort_index()   
        if kwargs.get('conc') is True:
            try:
                concs = pd.concat([x.concordance for x in res], ignore_index=True)
                concs = concs.sort_values(by='c')
                concs = concs.reset_index(drop=True)
                if kwargs.get('maxconc'):
                    concs = concs[:kwargs.get('maxconc')]
                out.concordance = Concordance(concs)
            except ValueError:
                out.concordance = None

        thetime = strftime("%H:%M:%S", localtime())
        if terminal and print_info:
            with terminal.location(0, terminal.height):
                print('\n\n%s: Finished! %d unique results, %d total.%s' % (thetime, len(out.results.columns), out.totals.sum(), '\n'))
        else:
            if print_info:
                print('\n\n%s: Finished! %d unique results, %d total.%s' % (thetime, len(out.results.columns), out.totals.sum(), '\n'))
        if save:
            out.save(save, print_info = print_info)
        return out
