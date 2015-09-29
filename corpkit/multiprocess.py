    
def pmultiquery(path, 
    option = 'c', 
    query = 'any', 
    sort_by = 'total', 
    quicksave = False,
    num_proc = 'default', 
    function_filter = False,
    just_speakers = False,
    root = False,
    note = False,
    print_info = True,
    **kwargs):
    """Parallel process multiple queries or corpora.

    This function is used by interrogator if:

        a) path is a list of paths
        b) query is a dict of named queries
        c) function_filter is iterable
        d) just speakers == 'each'
    
    This function needs joblib 0.8.4 or above in order to run properly."""
    
    import collections
    import os
    import pandas
    import pandas as pd
    import collections
    from collections import namedtuple
    from time import strftime, localtime
    from interrogator import interrogator
    from editor import editor
    from other import save_result
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
                return max([int(num_queries / n) for n in range(2, num_cores) if int(num_queries / n) <= num_cores])        
            else:
                import math
                if (float(math.sqrt(num_queries))).is_integer():
                    square_root = math.sqrt(num_queries)
                    if square_root <= num_queries / num_cores: 
                        return int(square_root)    
        return num_cores

    num_cores = multiprocessing.cpu_count()

    # are we processing multiple queries or corpora?
    # find out optimal number of cores to use.
    multiple_option = False
    multiple_queries = False
    multiple_speakers = False
    multiple_corpora = False

    denom = 1
    if hasattr(path, '__iter__'):
        multiple_corpora = True
        num_cores = best_num_parallel(num_cores, len(path))
        denom = len(path)
    elif hasattr(query, '__iter__'):
        multiple_queries = True
        num_cores = best_num_parallel(num_cores, len(query))
        denom = len(query)
    elif hasattr(function_filter, '__iter__'):
        multiple_option = True
        num_cores = best_num_parallel(num_cores, len(function_filter.keys()))
        denom = len(function_filter.keys())
    elif just_speakers:
        from corpkit.build import get_speaker_names_from_xml_corpus
        multiple_speakers = True
        if just_speakers == 'each':
            just_speakers = get_speaker_names_from_xml_corpus(path)
        if len(just_speakers) == 0:
            print 'No speaker name data found.'
            return
        num_cores = best_num_parallel(num_cores, len(just_speakers))
        denom = len(just_speakers)
        
    if num_proc != 'default':
        num_cores = num_proc

    # make sure quicksaves are right type
    if quicksave is True:
        raise ValueError('quicksave must be string when using pmultiquery.')
    
    # the options that don't change
    d = {'option': option,
         #'paralleling': True,
         'function': 'interrogator',
         'root': root,
         'note': note,
         'denominator': denom}
    # add kwargs to query
    for k, v in kwargs.items():
        d[k] = v

    # make a list of dicts to pass to interrogator,
    # with the iterable unique in every one
    ds = []
    if multiple_corpora:
        path = sorted(path)
        for index, p in enumerate(path):
            name = os.path.basename(p)
            a_dict = dict(d)
            a_dict['path'] = p
            a_dict['query'] = query
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_queries:
        for index, (name, q) in enumerate(query.items()):
            a_dict = dict(d)
            a_dict['path'] = path
            a_dict['query'] = q
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_option:
        for index, (name, q) in enumerate(function_filter.items()):
            a_dict = dict(d)
            a_dict['path'] = path
            a_dict['query'] = query
            a_dict['outname'] = name
            a_dict['just_speakers'] = just_speakers
            a_dict['paralleling'] = index
            a_dict['function_filter'] = q
            a_dict['printstatus'] = False
            ds.append(a_dict)
    elif multiple_speakers:
        for index, name in enumerate(just_speakers):
            a_dict = dict(d)
            a_dict['path'] = path
            a_dict['query'] = query
            a_dict['outname'] = name
            a_dict['just_speakers'] = [name]
            a_dict['function_filter'] = function_filter
            a_dict['paralleling'] = index
            a_dict['printstatus'] = False
            ds.append(a_dict)

    time = strftime("%H:%M:%S", localtime())
    if multiple_corpora and not multiple_option:
        print ("\n%s: Beginning %d parallel corpus interrogations:\n              %s" \
           "\n\n          Query: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, "\n              ".join(path), query) )

    elif multiple_queries:
        print ("\n%s: Beginning %d parallel corpus interrogations: %s" \
           "\n          Queries: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, os.path.basename(path), "', '".join(query.values())) )

    elif multiple_option:
        print ("\n%s: Beginning %d parallel corpus interrogations (multiple options): %s" \
           "\n\n          Query: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, os.path.basename(path), query) )

    elif multiple_speakers:
        print ("\n%s: Beginning %d parallel corpus interrogations: %s" \
           "\n\n          Query: '%s'" \
           "\n          Interrogating corpus ... \n" % (time, num_cores, os.path.basename(path), query) )

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    #import sys
    #reload(sys)
    #stdout=sys.stdout
    failed = False
    #ds = ds[::-1]
    if not root:
        from blessings import Terminal
        terminal = Terminal()
        print '\n' * (len(ds) - 2)
        for dobj in ds:
            linenum = dobj['paralleling']
            with terminal.location(0, terminal.height - (linenum + 1)):
                # this is a really bad idea.
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: [                      0%% (%s)                            ]' % (thetime, dobj['outname'])
        
        #res = Parallel(n_jobs=num_cores)(delayed(interrogator)(**x) for x in ds)
        try:
            #ds = sorted(ds, key=lambda k: k['paralleling'], reverse = True) 
            res = Parallel(n_jobs=num_cores)(delayed(interrogator)(**x) for x in ds)
            print '\n\n\n'
        except:
            failed = True
            print 'Multiprocessing failed.'
            raise
        try:
            res = sorted(res)
        except:
            failed = True
            pass
    elif root or failed:
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
    #from corpkit.interrogator import interrogator
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
    if not option.startswith('c'):
        out = {}
        #print ''
        for (name, data), d in zip(res, ds):
            for unpicklable in ['note', 'root']:
                try:
                    del d[unpicklable]
                except KeyError:
                    pass
            if not option.startswith('k'):
                outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
                try:
                    stotal = data.sum(axis = 1)
                    stotal.name = u'Total'
                except ValueError:
                    stotal = data.sum()
                output = outputnames(d, data, stotal)
            else:
                outputnames = collections.namedtuple('interrogation', ['query', 'results'])
                output = outputnames(d, data)
            out[name] = output
    
        # could be wrong for unstructured corpora?
        if quicksave:
            fullpath = os.path.join('saved_interrogations', quicksave)
            while os.path.isdir(fullpath):
                selection = raw_input("\nSave error: %s already exists in %s.\n\nType 'o' to overwrite, or enter a new name: " % (quicksave, 'saved_interrogations'))
                if selection == 'o' or selection == 'O':
                    import shutil
                    shutil.rmtree(fullpath)
                else:
                    import os
                    fullpath = os.path.join('saved_interrogations', selection)

            for k, v in out.items():
                save_result(v, k, savedir = fullpath, print_info = False)
        
            time = strftime("%H:%M:%S", localtime())
            print "\n%s: %d files saved to %s" % ( time, len(out.keys()), fullpath)

        time = strftime("%H:%M:%S", localtime())
        print "\n\n%s: Finished! Output is a dictionary with keys:\n\n         '%s'\n" % (time, "'\n         '".join(sorted(out.keys())))
        
        return out
    # make query and total branch, save, return
    else:
        out = pd.concat(res, axis = 1)
        out = editor(out, sort_by = sort_by, print_info = False, keep_stats = False)
        time = strftime("%H:%M:%S", localtime())
        print '\n\n%s: Finished! %d unique results, %d total.' % (time, len(out.results.columns), out.totals.sum())
        if quicksave:
            from other import save_result
            save_result(out, quicksave)
        return out

if __name__ == '__main__':
    pmultiquery(path, 
    option = False, 
    query = False, 
    sort_by = False, 
    quicksave = False,
    num_proc = False, 
    function_filter = False,
    just_speakers = False,
    root = False,
    note = False,
    print_info = True,
    **kwargs)