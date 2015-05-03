
def merger(lst, criteria, 
           newname = False, 
           printmerge = True, 
           sort_by = 'total'):
    """Merges result items by their index

    lst: list to work on
    criteria: list of result indexes, list of words, or a regular expression
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
    
    to_merge = []
    not_merging = []

    # if regex, get list of indices for matches
    if type(criteria) == str:
        regex = re.compile(criteria, re.UNICODE)
        for e in lst:
            if re.search(regex, e[0]):
                to_merge.append(e)
            else:
                not_merging.append(e)

    #if indices or list of words
    if type(criteria) == list:
        if type(criteria[0]) == int:
            for index, e in enumerate(lst):
                if index in criteria:
                    to_merge.append(e)
                else:
                    not_merging.append(e)
        else:
            for e in lst:
                if e[0] in criteria:
                    to_merge.append(e)
                else:
                    not_merging.append(e)

    # figure out the newname for the merged item
    if type(newname) == int:
        the_newname = lst[newname][0]
    elif type(newname) == str:
        the_newname = unicode(newname)
    elif type(newname) == unicode:
        the_newname = newname
    # if false, make the_newname the top result
    else:
        the_newname = to_merge[0][0]
    
    # create the merged entry
    merged = combiner(to_merge, the_newname, printmerge = printmerge)
    
    # add it to the main list
    not_merging.append(merged)

    # sort this list
    output = resorter(output, sort_by = sort_by)

    # generate totals:
    totals = combiner(output, 'Totals', printmerge = False)

    # make into named tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [criteria, the_newname]
    output = outputnames(query_options, output, totals)
    return output

# depreciated searchtree and quicktree because not .py compatible



def surgeon(lst, criteria, 
            remove = False, 
            printsurgery = True, 
            sort_by = False):

    """Make a new interrogation tuple by keeping/removing certain items from another list.

    a .totals branch will be generated.
    a .query branch will contain the criteria and remove boolean
    The .results branchcan be sorted with sort_by.

    Parameters
    ----------
    lst: an interrogator() results list
    criteria: if string, it is a regular expression to keep/remove by.
              if list of ints, a list of indices to keep/remove by.
              if list of strings, a list of entries to keep/remove
    remove: keep or remove the items matched by criteria
    printsurgery: print info for the user. Can be turned off if used in other functions.
    sort_by: 'total', 'name', 'increase', 'decrease', 'static' (see edit.resorter() for info)

    """
    import re
    import collections
    import warnings
    import copy

    from corpkit.edit import resorter, combiner

    if isinstance(lst, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results
    if remove:
        remove_string = 'remove = True'
    else:
        remove_string = 'remove = False'

    # if keep/remove by regex
    if type(criteria) == str:
        regexp = re.compile(criteria)
        if remove:
            newlist = [e for e in lst if not re.search(regexp, e[0])]
            removed = [e for e in lst if re.search(regexp, e[0])]
        else:
            newlist = [e for e in lst if re.search(regexp, e[0])]
    # criteria can also be a list
    if type(criteria) == list:
        # if it's a list of indices
        if type(criteria[0]) == int:
            if remove:
                newlist = [e for index, e in enumerate(lst) if index not in criteria]
                removed = [e for index, e in enumerate(lst) if index in criteria]
            else:
                newlist = [e for index, e in enumerate(lst) if index in criteria]
        # if list of words
        else:
            if remove:
                newlist = [e for e in lst if e[0] not in criteria]
                removed = [e for e in lst if e[0] in criteria]
            else:
                newlist = [e for e in lst if e[0] in criteria]

    # print helpful info
    if printsurgery:
        if remove:
            print 'Removing the following %d entries:' % len(removed)
            for entry in removed[:25]:
                print '%s (total = %d)' % ( entry[0], entry[-1][1])
            if len(removed) > 25:
                num_more = len(removed) - 25
                print '... and %d more ... ' % num_more
        if not remove:
            print 'Making a new results list with following %d entries:' % len(newlist)
            for entry in newlist[:25]:
                print '%s (total = %d)' % ( entry[0], entry[-1][1])
            if len(newlist) > 25:
                num_more = len(newlist) - 25
                print '... and %d more ... ' % num_more
    
    # sort if we want
    if sort_by:
        newlist = resorter(newlist, sort_by = sort_by)        
    # generate totals info
    totals = combiner(newlist, 'Totals', printmerge = False)
    
    # make into name tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [criteria, remove_string]
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
            # these four versions of the same shell command will be the death of me.
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
            good = data.encode('utf-8', errors = 'ignore')
    # if conc results, turn into string...
    if type(data) == list:
        good = '\n'.join(data)
    # if list of tokens...?
    
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
    elif sort_by == 'infreq':
        to_reorder.sort(key=lambda x: x[-1])
    elif sort_by == 'name':
        # case insensitive!
        to_reorder.sort(key=lambda x: x[0].lower())
    elif sort_by == 'none' or sort_by is False:
        return to_reorder
    else:
        from scipy.stats import linregress
        
        # you can't do linear regression if your x axis is a string.

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
        if sort_by == 'increase':
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
    """the main engine for merging entries, making totals.

    tomerge: a list of interrogator results
    """
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

def percenter(small_list, big_list, 
              threshold = 'relative', 
              sort_by = 'most', 
              multiplier = 100,
              just_totals = False,
              print_threshold = True):
    """Figure out the percentage of times the word in big_list is in small_list

    small_list : interrogator results
    big_list : superordinate interrogator results list
    threshold : an integer or float, being minimum number of times the word must appear
              : a string: relative (total/10000), low (/20000), high (/5000)
    sort_by : show most or least frequent first
    multiplier : 100 for percentages, 1 for ratio

    """
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        have_ipython = False
    
    # translate threshold to denominator
    if type(threshold) == str:
        if threshold == 'low':
            denominator = 20000
        if threshold == 'relative':
            denominator = 10000
        if threshold == 'high':
            denominator = 5000
        
        # tally all totals in big_list
        totals = []
        for each_entry in big_list:
            totals.append(each_entry[-1][1])
        tot = sum(totals)

        # generate a threshold
        threshold = tot / float(denominator)
    
    # some info for the user
    if threshold:
        if print_threshold:
            print 'Using %d as threshold ... ' % threshold
        
    # if big_list is .totals, just do totalling
    if just_totals:
        dictionary = {}
        for entry in small_list:
            # get word
            word = entry[0]
            # get total for word
            subj_total = entry[-1][1]
            # get entry in big_list
            try:
                matching_entry = next(e for e in big_list if e[0] == word)
            except StopIteration:
                continue
            # get total from this entry
            matching_total = matching_entry[-1][1]
            # this if allows threshold to be zero with 'threshold = None/False'
            if threshold:
                if matching_total >= threshold:
                    try:
                        perc = float(subj_total) * float(multiplier) / float(matching_total)
                    except ZeroDivisionError:
                        perc = 0
                    dictionary[word] = perc
            else:
                try:
                    perc = float(subj_total) * float(multiplier) / float(matching_total)
                except ZeroDivisionError:
                    perc = 0
                dictionary[word] = perc
        # sort by most or leat percent
        if sort_by == 'most':
            list_of_tups = [(k, dictionary[k]) for k in sorted(dictionary, key=dictionary.get, reverse=True)]
        elif sort_by == 'least':
            list_of_tups = [(k, dictionary[k]) for k in sorted(dictionary, key=dictionary.get)]
        output = []
        if multiplier == 100:
            subcorpus_name = u'Percentage'
        elif multiplier == 1:
            subcorpus_name = u'Ratio'
        else:
            subcorpus_name = u'Score'
        # rather than a dict, i should go straight to list, and
        # i should print total frequency, so that plotter can use a threshold
        for word, score in list_of_tups:
            new_entry = [word]
            new_entry.append([subcorpus_name, score])
            new_entry.append([u'Total', score])
            output.append(new_entry)
            if have_ipython:
                clear_output()
        return output
    
    # if big_list is .results, 
    else:
        fixed_list = []
        for entry in small_list:
            word = entry[0]
            years_counts = [e for e in entry[1:]]
            #years = [e[0] for e in years_counts]
            #counts = [e[1] for e in years_counts]
            try:
                matching_entry = next(e for e in big_list if e[0] == word)[1:]
            except StopIteration:
                continue
            #matching_entry = matching_entry[1:]
            matching_total = matching_entry[-1][1]
            if threshold:
                if matching_total >= threshold:
                    mathed = [word]
                    for year_count, matching_year_count in zip(years_counts, matching_entry):
                        year = year_count[0]
                        count = year_count[1]
                        matching_count = matching_year_count[1]
                        try:
                            perc = float(count) * float(multiplier) / float(matching_count)
                        except ZeroDivisionError:
                            perc = 0
                        mathed.append([year, perc])
                    fixed_list.append(mathed)
            if sort_by != 'most' and sort_by != 'least':
                fixed_list = resorter(fixed_list, sort_by = sort_by, revert_year = True)
            elif sort_by == 'most':
                fixed_list = resorter(fixed_list, sort_by = 'total', revert_year = True)
            elif sort_by == 'least':
                fixed_list = resorter(fixed_list, sort_by = 'total', revert_year = True)
                fixed_list = sorted(fixed_list, reverse = True)
        if have_ipython:
            clear_output()
        return fixed_list
