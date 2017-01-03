"""corpkit: multiprocessing of interrogations"""

from __future__ import print_function

def pmultiquery(corpus, 
                search,
                exclude=False,
                sort_by='total', 
                save=False,
                multiprocess='default', 
                root=False,
                note=False,
                print_info=True,
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
    from corpkit.interrogator import interrogator
    from corpkit.interrogation import Interrogation, Interrodict
    from corpkit.process import canpickle
    from corpkit.corpus import Corpus, Corpora, Datalist
    from corpkit.matches import Matches
    try:
        from joblib import Parallel, delayed
    except ImportError:
        pass
    import multiprocessing

    locs = locals()
    for k, v in kwargs.items():
        locs[k] = v
    in_notebook = locs.get('in_notebook')

    if not isinstance(multiprocess, int):
        multiprocess = multiprocessing.cpu_count()

    num_files = len(corpus.all_files)

    def partition(lst, n):
        q, r = divmod(len(lst), n)
        indices = [q*i + min(i, r) for i in range(n+1)]
        chunks = [lst[indices[i]:indices[i+1]] for i in range(n)]
        return [i for i in chunks if i]

    chunks = partition(corpus.all_files, multiprocess)

    if len(chunks) < multiprocess:
        multiprocess = len(chunks)

    # make sure saves are right type
    if save is True:
        raise ValueError('save argument must be string when multiprocessing.')

    # make a list of dicts to pass to interrogator,
    # with the iterable unique in every one
    basic_multi_dict = {'search': search,
                        'exclude': exclude,
                        #'just_metadata' = just_metadata,
                        'printstatus': False,
                        'multiprocess': False,
                        'df1_always_df': False,
                        'files_as_subcorpora': False}

    # make a new dict for every iteration
    ds = [dict(**basic_multi_dict) for i in range(multiprocess)]

    for index, (d, bit) in enumerate(zip(ds, chunks)):
        d['paralleling'] = index
        d['corpus'] = list(bit)
    #print(ds)

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
        print('starting')

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    #import sys
    #reload(sys)
    #stdout=sys.stdout
    failed = False
    terminal = False
    used_joblib = False
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
        try:
            res = Parallel(n_jobs=multiprocess)(delayed(interrogator)(**x) for x in ds)
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

    merged_res = { k: v for d in res for k, v in d.items() }
    matches = Matches(merged_res, corpus)
    subc = subcorpora if kwargs.get('subcorpora') else 'default'
    resbranch = matches.table(subcorpora=subc, show=show)
    try:
        totals = resbranch.sum(axis=1)
    except:
        totals = resbranch.sum()

    interro = Interrogation(data=matches, corpus=corpus)

    return interro

    # remove unpicklable bits from query
    from types import ModuleType, FunctionType, BuiltinMethodType, BuiltinFunctionType
    badtypes = (ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType)
    qlocs = {k: v for k, v in locs.items() if not isinstance(v, badtypes)}

    if hasattr(qlocs.get('corpus', False), 'name'):
        qlocs['corpus'] = qlocs['corpus'].path
    else:
        qlocs['corpus'] = list([i.path for i in qlocs.get('corpus', [])])

    # return just a concordance
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
            print('\n\n%s: Finished! %d results.\n\n' % (thetime, format(len(concs.index), ',')))

        return lines

    # return interrodict (to become multiindex)
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
    # 
    else:
        if multiple_corpora:
            sers = [i.results for i in res]
            out = DataFrame(sers, index=[i.query['outname'] for i in res])
            out = out.reindex_axis(sorted(out.columns), axis=1) # sort cols
            out = out.fillna(0) # nan to zero
            out = out.astype(int) # float to int
            out = out.T            
        else:
            # make a series from counts
            if all(len(i.results) == 1 for i in res):
                out = pd.concat([r.results for r in res])
                out = out.sort_index()
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
            or all(x.endswith('.txt') for x in list(out.columns)) \
            or all(x.endswith('.conll') for x in list(out.columns)):
                out = out.T
                
            if kwargs.get('nosubmode'):
                out = out.sum()
    
        from corpkit.interrogation import Interrogation
        tt = out.sum(axis=1) if isinstance(out, DataFrame) else out.sum()
        out = Interrogation(results=out, totals=tt, query=qlocs)

        if hasattr(out, 'columns') and len(out.columns) == 1:
            out = out.sort_index()   

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
        if terminal:
            print(terminal.move(terminal.height-1, 0))
        if print_info:
            if terminal:
                print(terminal.move(terminal.height-1, 0))
            if hasattr(out.results, 'columns'):
                print('%s: Interrogation finished! %s unique results, %s total.' % (thetime, format(len(out.results.columns), ','), format(out.totals.sum(), ',')))
            else:
                print('%s: Interrogation finished! %s matches.' % (thetime, format(tt, ',')))
        if save:
            out.save(save, print_info = print_info)

        if list(out.results.index) == ['0'] and not kwargs.get('df1_always_df'):
            out.results = out.results.ix[0].sort_index()
        return out
