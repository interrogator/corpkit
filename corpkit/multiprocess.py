from __future__ import print_function

def pmultiquery(corpus, 
    search,
    show = 'words',
    query = 'any', 
    sort_by = 'total', 
    quicksave = False,
    multiprocess = 'default', 
    function_filter = False,
    just_speakers = False,
    root = False,
    note = False,
    print_info = True,
    **kwargs):
    """Parallel process multiple queries or corpora.

    This function is used by interrogator() if:

        a) path is a list of paths
        b) query is a dict of named queries
        c) just speakers == 'each', or a list of speakers with len(list) > 1
    
    This function needs joblib 0.8.4 or above in order to run properly.
    There's no reason to call it yourself."""
    
    import collections
    import os
    import pandas as pd
    import collections
    from collections import namedtuple
    from time import strftime, localtime
    import corpkit
    from interrogator import interrogator
    from editor import editor
    from other import save
    from interrogation import Interrogation
    try:
        from joblib import Parallel, delayed
    except:
        pass
        #raise ValueError('joblib, the module used for multiprocessing, cannot be found. ' \
        #                 'Install with:\n\n        pip install joblib')
    import multiprocessing

    def best_num_parallel(num_cores, num_queries):
        import corpkit
        """decide how many parallel processes to run

        the idea, more or less, is to balance the load when possible"""
        if num_queries <= num_cores:
            return num_queries
        if num_queries > num_cores:
            if (num_queries / num_cores) == num_cores:
                return int(num_cores)
            if num_queries % num_cores == 0:
                try:
                    return max([int(num_queries / n) for n in range(2, num_cores) if int(num_queries / n) <= num_cores])   
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
    elif type(query) == list or type(query) == dict:
        multiple_queries = True
        num_cores = best_num_parallel(num_cores, len(query))
        denom = len(query)
    elif hasattr(search, '__iter__') and type(search) != dict:
        multiple_search = True
        num_cores = best_num_parallel(num_cores, len(list(search.keys())))
        denom = len(list(search.keys()))
    elif hasattr(function_filter, '__iter__'):
        multiple_option = True
        num_cores = best_num_parallel(num_cores, len(list(function_filter.keys())))
        denom = len(list(function_filter.keys()))
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
        
    if type(multiprocess) == int:
        num_cores = multiprocess
    if multiprocess is False:
        num_cores = 1

    # make sure quicksaves are right type
    if quicksave is True:
        raise ValueError('quicksave must be string when using pmultiquery.')
    
    # the options that don't change
    d = {
         #'paralleling': True,
         'function': 'interrogator',
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
    elif multiple_option:
        for index, (name, q) in enumerate(function_filter.items()):
            a_dict = dict(d)
            a_dict['corpus'] = corpus
            a_dict['search'] = search
            a_dict['query'] = query
            a_dict['show'] = show
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['function_filter'] = q
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
            a_dict['function_filter'] = function_filter
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_search:
        for index, val in enumerate(search):
            a_dict = dict(d)
            a_dict['corpus'] = corpus
            a_dict['search'] = val
            a_dict['query'] = query
            a_dict['show'] = show
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['function_filter'] = function_filter
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)

    time = strftime("%H:%M:%S", localtime())
    sformat = '\n                 '.join(['%s: %s' % (k.rjust(3), v) for k, v in list(search.items())])
    if multiple_corpora and not multiple_option:
        print(("\n%s: Beginning %d corpus interrogations (in %d parallel processes):\n              %s" \
           "\n          Query: '%s'\n"  % (time, len(corpus), num_cores, "\n              ".join([i.name for i in corpus]), sformat)))

    elif multiple_queries:
        print(("\n%s: Beginning %d corpus interrogations (in %d parallel processes): %s" \
           "\n          Queries: '%s'\n" % (time, len(search), num_cores, corpus.name, "', '".join(list(search.values()))) ))

    elif multiple_search:
        print(("\n%s: Beginning %d corpus interrogations (in %d parallel processes): %s" \
           "\n          Queries: '%s'\n" % (time, len(list(search.keys())), num_cores, corpus.name, str(list(search.values())))))

    elif multiple_option:
        print(("\n%s: Beginning %d parallel corpus interrogations (multiple options): %s" \
           "\n          Query: '%s'\n" % (time, num_cores, corpus.name, sformat) ))

    elif multiple_speakers:
        print(("\n%s: Beginning %d parallel corpus interrogations: %s" \
           "\n          Query: '%s'\n" % (time, num_cores, corpus.name, sformat) ))

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    #import sys
    #reload(sys)
    #stdout=sys.stdout
    failed = False
    terminal = False
    used_joblib = False
    #ds = ds[::-1]
    if not root:
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

    # multiprocessing way
    #from multiprocessing import Process
    #from interrogator import interrogator
    #jobs = []
    ##for d in ds:
    ##    p = multiprocessing.Process(target=interrogator, kwargs=(**d,))
    ##    jobs.append(p)
    ##    p.start()
    ##    while p.is_alive():
    ##        import time
    ##        time.sleep(2)
    ##        if root:
    ##            root.update()
    #result_queue = multiprocessing.Queue()
    #
    #for d in ds:
    #funs = [interrogator(result_queue, **kwargs) for kwargs in ds]
    #jobs = [multiprocessing.Process(mc) for mc in funs]
    #for job in jobs: job.start()
    #for job in jobs: job.join()
    #results = [result_queue.get() for mc in funs]

    # turn list into dict of results, make query and total branches,
    # save and return
    if not all(type(i.results) == pd.core.series.Series for i in res):
        out = {}
        for interrog, d in zip(res, ds):
            interrog.query = d
            for unpicklable in ['note', 'root']:
                interrog.query.pop(unpicklable, None)
            out[interrog.query['outname']] = interrog
    
        # could be wrong for unstructured corpora?
        if quicksave:
            fullpath = os.path.join('saved_interrogations', quicksave)
            while os.path.isdir(fullpath):
                selection = input("\nSave error: %s already exists in %s.\n\nType 'o' to overwrite, or enter a new name: " % (quicksave, 'saved_interrogations'))
                if selection == 'o' or selection == 'O':
                    import shutil
                    shutil.rmtree(fullpath)
                else:
                    import os
                    fullpath = os.path.join('saved_interrogations', selection)

            for k, v in list(out.items()):
                save(v, k, savedir = fullpath, print_info = False)
        
            time = strftime("%H:%M:%S", localtime())
            print("\n%s: %d files saved to %s" % ( time, len(list(out.keys())), fullpath))

        time = strftime("%H:%M:%S", localtime())
        print("\n%s: Finished! Output is a dictionary with keys:\n\n         '%s'\n" % (time, "'\n         '".join(sorted(out.keys()))))
        from interrogation import Interrodict
        return Interrodict(out)
    # make query and total branch, save, return
    else:
        #print sers
        #print ds
        if multiple_corpora and not mult_corp_are_subs:
            sers = [i.results for i in res]
            out = pd.DataFrame(sers, index = [d['outname'] for d in ds])
            out = out.reindex_axis(sorted(out.columns), axis=1) # sort cols
            out = out.fillna(0) # nan to zero
            out = out.astype(int) # float to int
            out = out.T
        else:
            out = pd.concat([r.results for r in res], axis = 1)
            # format like normal
            out = out[sorted(list(out.columns))]
            out = out.T
            out = out.fillna(0) # nan to zero
            out = out.astype(int)

        # sort by total
        if type(out) == pd.core.frame.DataFrame:
            out.ix['Total-tmp'] = out.sum()
            tot = out.ix['Total-tmp']
            out = out[tot.argsort()[::-1]]
            out = out.drop('Total-tmp', axis = 0)

        out = out.edit(sort_by = sort_by, print_info = False, keep_stats = False)
        thetime = strftime("%H:%M:%S", localtime())
        if terminal:
            with terminal.location(0, terminal.height):
                print('\n\n%s: Finished! %d unique results, %d total.%s' % (thetime, len(out.results.columns), out.totals.sum(), '\n'))
        else:
            print('\n\n%s: Finished! %d unique results, %d total.%s' % (thetime, len(out.results.columns), out.totals.sum(), '\n'))
        if used_joblib:
            print('\n' * (len(ds) - 3))
        if quicksave:
            from other import save
            save(out, quicksave)
        return out

if __name__ == '__main__':
    pmultiquery(corpus,
    search,
    query = False,
    show = 'words', 
    sort_by = False, 
    quicksave = False,
    multiprocess = False, 
    function_filter = False,
    just_speakers = False,
    root = False,
    note = False,
    print_info = True,
    **kwargs)