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
                **kwargs
               ):
    """
    - Parallel process multiple queries or corpora.
    - This function is used by corpkit.interrogator.interrogator()
    - for multiprocessing.
    - There's no reason to call this function yourself."""
    import os
    from pandas import DataFrame, Series
    import pandas as pd
    import collections
    from collections import namedtuple, OrderedDict
    from time import strftime, localtime
    import corpkit
    from corpkit.interrogator import interrogator
    from corpkit.interrogation import Interrogation
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
    multiple_option = False
    multiple_queries = False
    multiple_speakers = False
    multiple_corpora = False
    multiple_search = False
    mult_corp_are_subs = False
    denom = 1

    if hasattr(corpus, '__iter__'):
        multiple_corpora = True
        num_cores = best_num_parallel(num_cores, len(corpus))
        denom = len(corpus)
        if all(c.__class__ == corpkit.corpus.Subcorpus for c in corpus):
            mult_corp_are_subs = True
    elif (isinstance(query, list) or isinstance(query, dict)) and not hasattr(search, '__iter__'):
            multiple_queries = True
            num_cores = best_num_parallel(num_cores, len(query))
            denom = len(query)
    elif hasattr(search, '__iter__') and all(isinstance(i, dict) for i in list(search.values())):
        multiple_search = True
        num_cores = best_num_parallel(num_cores, len(list(search.keys())))
        denom = len(list(search.keys()))

    elif just_speakers:
        from build import get_speaker_names_from_xml_corpus
        multiple_speakers = True
        if just_speakers == 'each' or just_speakers == ['each']:
            just_speakers = get_speaker_names_from_xml_corpus(corpus.path)
        if len(just_speakers) == 0:
            print('No speaker name data found.')
            return
        num_cores = best_num_parallel(num_cores, len(just_speakers))
        denom = len(just_speakers)

    if multiple_corpora and any(x is True for x in [multiple_speakers, multiple_queries, 
                                                    multiple_search, multiple_option]):
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
    
    # the options that don't change
    d = {'function': 'interrogator',
         'root': root,
         'note': note,
         'denominator': denom}
    
    # add kwargs to query
    for k, v in list(kwargs.items()):
        d[k] = v

    # make a list of dicts to pass to interrogator,
    # with the iterable unique in every one
    ds = []
    if multiple_corpora:
        for index, p in enumerate(corpus):
            name = p.name
            a_dict = dict(d)
            a_dict['corpus'] = p
            a_dict['search'] = search
            a_dict['query'] = query
            a_dict['show'] = show
            a_dict['outname'] = name.replace('-parsed', '')
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_queries:
        for index, (name, q) in enumerate(query.items()):
            a_dict = dict(d)
            a_dict['corpus'] = corpus
            a_dict['search'] = search
            a_dict['query'] = q
            a_dict['show'] = show
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_speakers:
        for index, name in enumerate(just_speakers):
            a_dict = dict(d)
            a_dict['corpus'] = corpus
            a_dict['search'] = search
            a_dict['query'] = query
            a_dict['show'] = show
            a_dict['outname'] = name
            a_dict['just_speakers'] = [name]
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_search:
        for index, (name, val) in enumerate(search.items()):
            a_dict = dict(d)
            a_dict['corpus'] = corpus
            a_dict['search'] = val
            a_dict['query'] = query
            a_dict['show'] = show
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)

    if kwargs.get('do_concordancing') is False:
        message = 'Interrogating'
    elif kwargs.get('do_concordancing') is True:
        message = 'Interrogating and concordancing'
    elif kwargs.get('do_concordancing').lower() == 'only':
        message = 'Concordancing'
    time = strftime("%H:%M:%S", localtime())
    sformat = ''
    if multiple_queries:
        to_it_over = query
    else:
        to_it_over = search
    for i, (k, v) in enumerate(list(to_it_over.items())):
        if type(v) == list:
            vformat = ', '.join(v[:5])
            if len(v) > 5:
                vformat += ' ...'
        elif type(v) == dict:
            vformat = ''
            for kk, vv in v.items():
                if type(vv) == list:
                    vv = ', '.join(vv[:5])

                vformat += '\n                     %s: %s' % (kk, vv)
                if len(vv) > 5:
                    vformat += ' ...'
        else:
            vformat = v
        sformat += '%s: %s' %(k, vformat)
        if i < len(to_it_over.keys()) - 1:
            sformat += '\n                   '

    if print_info:
        # proper printing for plurals
        # in truth this needs to be revised, it's horrible.
        if num_cores == 1:
            add_es = ''
        else:
            add_es = 'es'
        if multiple_corpora and not multiple_option:
            corplist = "\n              ".join([i.name for i in corpus[:20]])
            if len(corpus) > 20:
                corplist += '\n ... and %d more ...\n' % (len(corpus) - 20)
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s):\n              %s" \
               "\n          Query: %s\n          %s corpus ... \n"  % (time, len(corpus), num_cores, add_es, corplist, sformat, message)))

        elif multiple_queries:
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s): %s" \
               "\n          Queries: %s\n          %s corpus ... \n" % (time, len(query), num_cores,  add_es, corpus.name, sformat, message) ))

        elif multiple_search:
            print(("\n%s: Beginning %d corpus interrogations (in %d parallel process%s): %s" \
               "\n          Queries: %s\n          %s corpus ... \n" % (time, len(list(search.keys())), num_cores, add_es, corpus.name, sformat, message)))

        elif multiple_option:
            print(("\n%s: Beginning %d parallel corpus interrogation%s (multiple options): %s" \
               "\n          Query: %s\n          %s corpus ... \n" % (time, num_cores, add_es.lstrip('e'), corpus.name, sformat,  message) ))

        elif multiple_speakers:
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
            res = sorted(res)
        except:
            pass

    # remove unpicklable bits from query
    from types import ModuleType, FunctionType, BuiltinMethodType, BuiltinFunctionType
    qlocs = {k: v for k, v in locs.items() if not isinstance(v, ModuleType) \
            and not isinstance(v, FunctionType) \
            and not isinstance(v, BuiltinFunctionType) \
            and not isinstance(v, BuiltinMethodType)}

    if hasattr(qlocs['corpus'], 'name'):
        qlocs['corpus'] = qlocs['corpus'].path
    else:
        qlocs['corpus'] = list([i.path for i in qlocs['corpus']])

    from corpkit.interrogation import Concordance
    if kwargs.get('do_concordancing') == 'only':
        concs = pd.concat([x for x in res])
        thetime = strftime("%H:%M:%S", localtime())
        lines = Concordance(concs)
        
        if save:
            lines.save(save, print_info=print_info)

        if print_info:
            print('\n\n%s: Finished! %d results.\n\n' % (thetime, len(concs.index)))

        return lines

    if not all(isinstance(i.results, Series) for i in res):
        out = OrderedDict()
        for interrog, d in zip(res, ds):
            for unpicklable in ['note', 'root']:
                interrog.query.pop(unpicklable, None)
            try:
                out[interrog.query['outname']] = interrog
            except KeyError:
                out[d['outname']] = interrog

        from corpkit.interrogation import Interrodict
        idict = Interrodict(out)
        
        if print_info:
            time = strftime("%H:%M:%S", localtime())
            print("\n\n%s: Finished! Output is a dictionary with keys:\n\n         '%s'\n" % \
                (time, "'\n         '".join(sorted(out.keys()))))

        idict.query = qlocs

        if save:
            idict.save(save, print_info = print_info)

        return idict
    

    # make query and total branch, save, return
    # todo: standardise this so we don't have to guess transposes
    else:
        if multiple_corpora and not mult_corp_are_subs:
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
            if not mult_corp_are_subs:
                out = out.T
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
        if kwargs.get('do_concordancing') is True:
            concs = pd.concat([x.concordance for x in res], ignore_index = True)
            concs = concs.sort_values(by='c')
            concs = concs.reset_index(drop=True)
            out.concordance = Concordance(concs)
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
