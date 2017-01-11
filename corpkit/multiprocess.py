"""
corpkit: multiprocessing of interrogations
"""

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
                show=['mw'],
                subcorpora=False,
                mainpath=False,
                countmode=False,
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
    from corpkit.interrogator import interrogator, welcome_printer
    from corpkit.interrogation import Interrogation
    from corpkit.process import canpickle
    from corpkit.corpus import Corpus
    try:
        from joblib import Parallel, delayed
    except ImportError:
        pass
    import multiprocessing

    #if isinstance(corpus, Datalist):
    #    corpus = Corpus(corpus, level='d', print_info=False)

    locs = locals()
    for k, v in kwargs.items():
        locs[k] = v
    in_notebook = locs.get('in_notebook')
    #cname = kwargs.pop('cname')
    optiontext = kwargs.pop('optiontext')

    if not isinstance(multiprocess, int):
        multiprocess = multiprocessing.cpu_count()

    if getattr(corpus, 'all_files', False):
        files = corpus.all_files
    else:
        files = corpus

    num_files = len(files)

    def partition(lst, n):
        q, r = divmod(len(lst), n)
        indices = [q*i + min(i, r) for i in range(n+1)]
        chunks = [lst[indices[i]:indices[i+1]] for i in range(n)]
        return [i for i in chunks if i]

    chunks = partition(files, multiprocess)

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
                        'mp': True,
                        'countmode': countmode}

    # make a new dict for every iteration
    ds = [dict(**basic_multi_dict) for i in range(multiprocess)]

    for index, (d, bit) in enumerate(zip(ds, chunks)):
        d['paralleling'] = index
        d['corpus'] = list(bit)
    
    welcome_message = welcome_printer(search, 'corpus', optiontext, return_it=in_notebook, printstatus=print_info)

    # run in parallel, get either a list of tuples (non-c option)
    # or a dataframe (c option)
    #import sys
    #reload(sys)
    #stdout=sys.stdout
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
        res = Parallel(n_jobs=multiprocess)(delayed(interrogator)(**x) for x in ds)
    else:
        res = []
        for index, d in enumerate(ds):
            d['startnum'] = (100 / denom) * index
            res.append(interrogator(**d))
        try:
            res = sorted([i for i in res if i])
        except:
            pass

    merged_res = [item for sublist in res for item in sublist]
    subc = subcorpora if kwargs.get('subcorpora') else 'default'

    querybits = {'search': search,
                  'exclude': exclude,
                  'show': show,
                  'subcorpora': subcorpora}

    interro = Interrogation(data=merged_res, corpus=corpus, query=querybits, path=mainpath, count=countmode)

    if print_info:
        if terminal:
            print(terminal.move(terminal.height-1, 0))

    return interro
