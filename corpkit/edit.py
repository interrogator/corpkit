
def merger(lst, criteria, 
           newname = False, 
           printmerge = True, 
           sort_by = 'total'):
    """Merges result items by their index

    lst: list to work on
    criteria: list of result indexes
    newname = if str, this becomes the new name
                        if int, the item indexed with that int becomes newname
                        if False, most common item becomes newname"""
    import re
    import collections
    import warnings
    import copy
    from corpkit.edit import combiner, combiner
    if isinstance(lst, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results
    tomerge = []
    oldlist_copy = copy.deepcopy(lst)
    # if regex, get list of indices for mwatches
    if type(criteria) == str:
        forwards_index = []
        regex = re.compile(criteria, re.UNICODE)
        for entry in oldlist_copy:
            if re.search(regex, unicode(entry[0])):
                forwards_index.append(oldlist_copy.index(entry))
        backward_indices = sorted(forwards_index, reverse = True)
    #if indices, ensure results are sorted
    if type(criteria) == list:
        forwards_index = copy.deepcopy(criteria)
        backward_indices = sorted(criteria, reverse = True)
    # remove old entries
    for index in backward_indices:
        oldlist_copy.remove(oldlist_copy[index])
    # add matching entries to tomerge
    for index in forwards_index:
        tomerge.append(lst[index])
    # get the new word or use the first entry
    if type(newname) == int:
        getnewname= lst[newname]
        the_newname = getnewname[0]
    elif type(newname) == str:
        the_newname = unicode(newname)
    elif type(newname) == unicode:
        the_newname = newname
    else:
        the_newname = tomerge[0][0]

    merged = combiner(tomerge, the_newname, printmerge = printmerge)
    
    # put the merged entry back in the list
    # this is a bit redundant now that there's sorting
    output = []
    if type(criteria) == list:
        forwards_index = sorted(criteria)
    first_index = forwards_index[0]
    for entry in oldlist_copy[:first_index]:
        output.append(entry)
    output.append(merged)
    for entry in oldlist_copy[first_index:]:
         output.append(entry)
    if not sort_by:
        output = resorter(output, sort_by = sort_by)
    # generate totals:
    totals = combiner(output, 'Totals', printmerge = False)
    # make into name tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [str(criteria), the_newname]
    #main_totals.append([u'Total', total])
    output = outputnames(query_options, output, totals)
    return output

# depreciated searchtree and quicktree because not .py compatible



def surgeon(lst, criteria, remove = False, **kwargs):
    """Add or remove from results by regex or index.

    criteria: if string, it is a regular expression to keep/remove by.
                 if list, a list of indices to keep/remove by
    """
    import re
    import collections
    import warnings
    import copy

    from corpkit.edit import resorter, combiner

    # should we print info about what was removed and kept?
    if isinstance(lst, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results
    if remove:
        remove_string = 'remove = True'
    else:
        remove_string = 'remove = False'
    newlist = []
    if type(criteria) == str:
        regexp = re.compile(criteria)
        for item in lst:
            if remove is True:
                if type(item) == str:
                    if not re.search(regexp, item):
                        newlist.append(item)
                else:
                    if not re.search(regexp, item[0]):
                        newlist.append(item)                        
            if remove is False:
                if type(item) == str:
                    if re.search(regexp, item):
                        newlist.append(item)
                else:
                    if re.search(regexp, item[0]):
                        newlist.append(item)     
    if type(criteria) == list:
        if remove is True:
            newlist = copy.deepcopy(lst)
            backward_indices = sorted(criteria, reverse = True)
            for index in backward_indices:
                newlist.remove(newlist[index])
        if remove is False:
            for index in criteria:
                newlist.append(lst[index])
    if 'sort_by' in kwargs:
        newlist = resorter(newlist, **kwargs)        
    totals = combiner(newlist, 'Totals', printmerge = False)
    # make into name tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [str(criteria), remove_string]
    #main_totals.append([u'Total', total])
    output = outputnames(query_options, newlist, totals)
    return output


def datareader(data, on_cloud = False):
    """
    Returns a string of plain text from a number of kinds of data.

    The kinds of data currently accepted are:

    path to corpus : all trees are flattened
    path to subcorpus : all trees are flattened
    conc() output (list of concordance lines)
    csv file generated with conc()
    a string of text
    """
    import os
    from corpkit.query import query_test, check_pytex, check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    
    # if unicode, make it a string
    if type(data) == unicode:
        if not os.path.isdir(data):
            if not os.path.isfile(data):
                good = data.encode('utf-8', errors = 'ignore')

    elif type(data) == str:
        # if it's a file, assume csv and get the big part
        if os.path.isfile(data):
            f = open(data)
            raw = f.read()
            if data.endswith('csv'):
                bad, good = re.compile(r'Entire sentences \(n=[0-9]+\):').split(raw)
            else:
                good = raw
        # if it's a dir, conc()
        elif os.path.isdir(data):
            # why did root appear as key???
            if have_ipython:
                if on_cloud:
                    tregex_command = 'sh tregex.sh -o -w -t \'__ !> __\' %s 2>/dev/null' % data
                else:
                    tregex_command = 'tregex.sh -o -w -t \'__ !> __\' %s 2>/dev/null' % data
                trees_with_blank = get_ipython().getoutput(tregex_command)
                trees = [tree for tree in trees_with_blank if tree]
            else:
                if on_cloud:
                    tregex_command = ["sh", "tregex.sh", "-o", "-w", "-t", "__ !> __" % data]
                else:
                    tregex_command = ["tregex.sh", "-o", "-w", "-t", "__ !> __" % data]
                FNULL = open(os.devnull, 'w')
                trees = subprocess.check_output(tregex_command, stderr=FNULL)
                trees = os.linesep.join([s for s in trees.splitlines() if s]).split()
            good = '\n'.join(trees)
            if len(trees) == 0:
                # assuming data isn't trees, so 
                # read plain text out of files ...
                list_of_texts = []
                for f in os.listdir(data):
                    raw = open(os.path.join(data, f))
                    list_of_texts.append(raw)
                good = '\n'.join(list_of_texts)
        # if a string of text, just keyword that
        else:
            good = data
    # if conc results, turn into string...
    if type(data) == list:
        good = '\n'.join(data)
    return good

def resorter(lst, 
             sort_by = 'total', 
             keep_stats = False, 
             only_below_p = False, 
             significance_level = 0.05, 
             revert_year = False):
    """Re-sort interrogation results in a number of ways."""
    from operator import itemgetter # for more complex sorting ... is it used?
    import copy

    options = ['total', 'name', 'infreq', 'increase', 'decrease', 'static', 'none']
    if sort_by not in options:
        raise ValueError("sort_by parameter error: '%s' not recognised. Must be 'total', 'name', 'infreq', 'increase', 'decrease' or 'static'." % sort_by)
    to_reorder = copy.deepcopy(lst)


    if sort_by == 'total':
        to_reorder.sort(key=lambda x: x[-1], reverse = True)
    elif sort_by == 'name':
        # case insensitive!
        to_reorder.sort(key=lambda x: x[0].lower())
    elif sort_by == 'none':
        return to_reorder
    else:
        from scipy.stats import linregress
        yearlist = [int(y[0]) for y in to_reorder[0][1:-1]]
        if revert_year:
            first_year = yearlist[0]
            yearlist = [y - first_year for y in yearlist]
        processed_list = []
        for datum in to_reorder:
            counts = [int(y[1]) for y in datum[1:-1]]
            stats = linregress(yearlist, counts)
            if only_below_p:
            # if not significant, discard here
                if stats[3] >= significance_level:
                    continue
            datum.append(stats)
            processed_list.append(datum)
            # removing insignificant items ... bad idea?
            #if view != 'static':
                #if stats[4] <= significance_level:
                    #datum.append(stats)
            #else:
        if sort_by == 'infreq':
            processed_list.sort(key=lambda x: x[-2][1], reverse = True)
        elif sort_by == 'increase':
            processed_list.sort(key=lambda x: x[-1][0], reverse = True) # largest first
        elif sort_by == 'decrease':
            processed_list.sort(key=lambda x: x[-1][0], reverse = False) # smallest first
        elif sort_by == 'static':
            processed_list.sort(key=lambda x: abs(x[-1][0]), reverse = False)
        # remove all the stats we just added unless coming from plotter
        to_reorder = processed_list
        if not keep_stats:
            for datum in to_reorder:
                datum.pop()
    return to_reorder

def combiner(tomerge, newname, printmerge = True):
    """the main engine for merging entries, making totals"""
    if printmerge is True:
        toprint = []
        for index, entry in enumerate(tomerge):
            if index < 21:
                toprint.append(unicode(entry[0]))
            if index == 21:
                remaining = len(tomerge) - 20
                toprint.append(unicode('( ... and %d others ...)' % remaining))
        string_to_print = '\n'.join(toprint)
        print "Merging the following entries as '%s':\n%s" % (newname, string_to_print)
    combined = zip(*[l for l in tomerge])
    merged = [newname]
    for tup in combined[1:]: # for each tuple of combined years and counts
        getyearfrom = tup[0]
        year = getyearfrom[0]
        counts = []
        for bit in tup:
            counts.append(bit[1])
        total = sum(counts)
        goodtup = [year, total]
        merged.append(goodtup)
    return merged


def mather(oldlist, operation, newlist, multiplier = 100):
    """does maths on two lists of results/totals"""
    import operator
    import copy
    the_oldlist = copy.deepcopy(oldlist)
    the_newlist = copy.deepcopy(newlist)
    if type(the_oldlist) != type(the_newlist):
        raise ValueError('Different list types: %s and %s' % (type(the_oldlist), type(the_newlist)))
    # implement when everything is definitely in unicode, maybe:
    #if type(the_oldlist[0]) != type(the_newlist[0]):
        #raise ValueError('Different list depths.' 
    if len(the_oldlist) != len(the_newlist):
        print the_oldlist
        print the_newlist
        raise ValueError('Different list lengths: %d and %d' % (len(the_oldlist), len(the_newlist)))
    ops = {"+": operator.add,
           "-": operator.sub,
           "*": operator.mul,
           "/": operator.div}
    try:
        op_func = ops[operation]
    except KeyError:
        if operation != '%':
            raise ValueError("Operator not recognised. Must be '+', '-', '*', '/' or '%'.")
    # put word into a newly declared list
    mathedlist = [the_oldlist[0]]
    for index, entry in enumerate(the_oldlist[1:]):
        x_axis = entry[0]
        oldnum = entry[1]
        newtup = the_newlist[index + 1]
        if newtup[0] == x_axis:
            newnum = the_newlist[index + 1][1]
            if operation != '%':
                result = op_func(oldnum, float(newnum))
                # one day there will probably be a divide by zero error here. sorry!
            else:
                if newnum == 0:
                    result = 0
                else:
                    result = oldnum * multiplier / float(newnum)

            mathedlist.append([x_axis, result])
        else:
            raise ValueError('Different list labels: %s and %s' % (str(x_axis), str(newtup[0])))
    return mathedlist


def save_result(interrogation, savename, savedir = 'data/saved_interrogations'):
    """Save an interrogation as pickle to savedir"""
    from collections import namedtuple
    import pickle
    import os
    
    # currently, allow overwrite. if that's not ok:
    #if os.path.isfile(csvmake):
        #raise ValueError("Save error: %s already exists in %s. \
                    #Pick a new name." % (savename, savedir))
            
    try:
        temp_list = [interrogation.query, interrogation.results, interrogation.totals]
    except AttributeError:
        temp_list = [interrogation.query, interrogation.totals]
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    if not savename.endswith('.p'):
        savename = savename + '.p'
    f = open('%s/%s' % (savedir, savename), 'w')
    pickle.dump(temp_list, f)
    f.close()

def load_result(savename, loaddir = 'data/saved_interrogations'):
    """Reloads a save_result as namedtuple"""
    import collections
    import pickle
    if not savename.endswith('.p'):
        savename = savename + '.p'
    unpickled = pickle.load(open('%s/%s' % (loaddir, savename), 'rb'))
    if len(unpickled) == 3:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
        output = outputnames(unpickled[0], unpickled[1], unpickled[2])
    elif len(unpickled) == 2:
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        output = outputnames(unpickled[0], unpickled[1])
    return output

def subcorpus_remover(interrogator_list, just_subcorpora, remove = True, **kwargs):
    """Takes a list and returns only results from the years listed in just_subcorpora"""
    import collections
    import copy
    import warnings

    from corpkit.edit import combiner, combiner
    
    # default to results branch
    if isinstance(interrogator_list, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        interrogator_list = interrogator_list.results
    # copy and wrap list if need be
    if type(interrogator_list[0]) == unicode or type(interrogator_list[0]) == str:
        alldata = [copy.deepcopy(interrogator_list)]
    else:
        alldata = copy.deepcopy(interrogator_list)
    output = []
    if type(just_subcorpora) == int or type(just_subcorpora) == str or type(just_subcorpora) == unicode:
        just_subcorpora = [just_subcorpora]
    for entry in alldata:
        # new list with just word
        skipped = [entry[0]]
        for item in entry[1:]:
            # make sure it's a list ... weird way to do it
            if type(item) != unicode and type(item) != str:
                for subcorpus in just_subcorpora:
                    if remove:
                        if item[0] != subcorpus and item[0] != u'Total':
                            skipped.append(item)
                    elif not remove:
                        if item[0] == subcorpus and item[0] != u'Total':
                            skipped.append(item)
        total = sum([i[1] for i in skipped[1:]])
        skipped.append([u'Total', total])
        output.append(skipped)
    output = resorter(output, **kwargs)
    # generate totals:
    totals = combiner(output, 'Totals', printmerge = False)
    # make into name tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    try:
        query_options = interrogator_list.query
    except AttributeError:
        query_options = ['subcorpus_remover used to generate this']
    #main_totals.append([u'Total', total])
    output = outputnames(query_options, output, totals)
    return output