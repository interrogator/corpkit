
def merger(lst, criteria, newname = False, printmerge = True, sort_by = 'totals'):
    """Merges result items by their index

    lst: list to work on
    criteria: list of result indexes
    newname = if str, this becomes the new name
                        if int, the item indexed with that int becomes newname
                        if False, most common item becomes newname"""
    import re
    import collections
    import warnings
    if isinstance(lst, tuple) is True:
        warnings.warn('No branch of results selected. Using .results ... ')
        lst = lst.results
    tomerge = []
    oldlist_copy = list(lst)
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
        forwards_index = list(criteria)
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
    if sort_by is not False:
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
    # should we print info about what was removed and kept?
    if isinstance(lst, tuple) is True:
        warnings.warn('No branch of results selected. Using .results ... ')
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
            newlist = list(lst)
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


def datareader(data):
    """Figures out what kind of thing you're parsing
    and returns a big string of text"""
    import os
    if type(data) == str:
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
                tregex_command = 'tregex.sh -o -w -t %s \'__ !> __\' %s 2>/dev/null | grep -vP \'^\s*$\'' % data
                trees = get_ipython().getoutput(tregex_command)
            else:
                tregex_command = ["tregex.sh", "-o", "-w", "-t", "__ !> __" % options, '%s' % query, "%s" % data]
                FNULL = open(os.devnull, 'w')
                trees = subprocess.check_output(tregex_command, stderr=FNULL)
                trees = os.linesep.join([s for s in trees.splitlines() if s]).split()
            #tregex_command = "tregex.sh -o -w -t '__ !> __' %s 2>/dev/null | grep -vP '^\s*$'" % data
            #trees = !$tregex_command
            #remove root!?
            #trees = [tree for tree in trees if tree is not 'root']
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
            good = str(data)
    # if conc results, turn into string...
    if type(data) == list:
        good = '\n'.join(data)
        #type(data) == str:
        # assume it's text
    return good

def resorter(lst, sort_by = 'total'):
    """Re-sort interrogation results in a number of ways."""
    # should we output a named tuple?
    from operator import itemgetter # for more complex sorting ... is it used?
    options = ['total', 'name', 'infreq', 'increase', 'decrease', 'static']
    if sort_by not in options:
        raise ValueError("View parameter error: %s not recognised. Must be 'total', 'name', 'infreq', 'increase', 'decrease' or 'static'." % sort_by)
    to_reorder = list(lst)
    if sort_by == 'total':
        #for item in to_reorder:
            #print item[0]
            # wait, are totals not already calculated?!
            #total = sum([t[-1] for t in item[1:]])
            #item.append([u'Total', total])
        to_reorder.sort(key=lambda x: x[-1], reverse = True)
        #for item in to_reorder:
            #item.pop()
    elif sort_by == 'name':
        # case insensitive!
        to_reorder.sort(key=lambda x: x[0].lower())
    else:
        from scipy.stats import linregress
        significance_level = 0.05
        yearlist = [int(y[0]) for y in to_reorder[0][1:-1]]
        for datum in to_reorder:
            counts = [int(y[1]) for y in datum[1:-1]]
            stats = linregress(yearlist, counts)
            # removing insignificant items ... bad idea?
            #if view != 'static':
                #if stats[4] <= significance_level:
                    #datum.append(stats)
            #else:
            datum.append(stats)
        if sort_by == 'infreq':
            to_reorder.sort(key=lambda x: x[-2][1], reverse = True)
        elif sort_by == 'increase':
            to_reorder.sort(key=lambda x: x[-1][0], reverse = True) # largest first
        elif sort_by == 'decrease':
            to_reorder.sort(key=lambda x: x[-1][0], reverse = False) # smallest first
        elif sort_by == 'static':
            to_reorder.sort(key=lambda x: abs(x[-1][0]), reverse = False)
        # remove all the stats we just added ...
        #for datum in to_reorder:
            #datum.pop()
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
    """does simple maths on two lists of results/totals"""
    import operator
    the_oldlist = list(oldlist)
    the_newlist = list(newlist)
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
