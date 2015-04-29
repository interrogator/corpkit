#!/usr/bin/python

#   Interrogating parsed corpora and plotting the results: plotter()
#   Author: Daniel McDonald


def plotter(title, 
            results, 
            sort_by = 'total', 
            fract_of = False, 
            y_label = False, 
            num_to_plot = 7, 
            significance_level = 0.05, 
            revert_year = False,
            multiplier = 100, 
            yearspan = False, 
            proj63 = 5,
            justyears = False, 
            csvmake = False, 
            x_label = False, 
            legend_p = False,
            legend_totals = False, 
            log = False, 
            figsize = 11, 
            save = False, 
            only_below_p = False, 
            skip63 = False, 
            projection = True):
    """
    Visualise interrogator() results, optionally generating a csv as well.

    Parameters
    ----------

    title : string
        Chart title
    results : list
        interrogator() results or totals (deaults to results)
    sort_by : string
        'total': sort by most frequent
        'increase': calculate linear regression, sort by steepest up slope
        'decrease': calculate linear regression, sort by steepest down slope 
        'static': calculate linear regression, sort by least slope
    fract_of : list
        measure results as a fraction (default: as a percentage) of this list.
        usually, use interrogator() totals
    multiplier : int
        mutliply results list before dividing by fract_of list
        Default is 100 (for percentage), can use 1 for ratios
    y_label : string
        text for y-axis label (default is 'Absolute frequency'/'Percentage') 
    X_label : string
        text for x-axis label (default is 'Group'/'Year')
    num_to_plot : int
        How many top entries to show
    significance_level : float
        If using sort_by, set the p threshold (default 0.05)
    only_below_p : Boolean
        Do not plot any results above p value
    yearspan : list with two ints
        Get only results between the specified ints
    justyears : list of ints
        Get only results from the listed subcorpora
    csvmake : True/False/string
        Generate a CSV of plotted and all results with string as filename
        If True, 'title' string is used
    legend_totals : Boolean
        Show total frequency of each result, or overall percentage if fract_of
    legend_p : Boolean
        Show p-value for slope when using sort_by
    log : False/'x'/'y'/'x, y'
        Use logarithmic axes
    figsize = int
        Size of image
    save = True/False/string
        Generate save image with string as filename
        If True, 'title' string is used for name

    NYT-only parameters
    -----
    skip63 : boolean
        Skip 1963 results (for NYT investigation)
    projection : boolean
        Project 1963/2014 results (for NYT investigation)
    proj63 : int
        The amount to project 1963 results by

    Example
    -----
    from corpkit import interrogator, plotter
    corpus = 'path/to/corpus'
    adjectives = interrogator(corpus, 'words', r'/JJ.?/ < __')
    plotter('Most common adjectives', adjectives.results, fract_of = adjectives.totals,
            csvmake = True, legend_totals = True)

    """

    import os
    import warnings
    import copy
    from time import localtime, strftime
    import numpy as np
    
    import matplotlib.pyplot as plt
    from matplotlib import rc
    from matplotlib.ticker import MaxNLocator, ScalarFormatter
    import pylab
    from pylab import rcParams
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    from corpkit.query import check_dit, check_pytex, check_tex
    from corpkit.edit import resorter, mather

    # setup:

    # size:
    rcParams['figure.figsize'] = figsize, figsize/2
    
    #font
    rcParams.update({'font.size': (figsize / 2) + 7}) # half your size plus seven
    
    # check what we're doing here.
    have_python_tex = check_pytex()
    on_cloud = check_dit()
    have_tex = check_tex(have_ipython = have_ipython)


    def skipper(interrogator_list):
        """Takes a list and returns a version without 1963"""
        skipped = []
        skipped.append(interrogator_list[0]) # append word
        for item in interrogator_list[1:]:
            if type(item) != unicode and type(item) != str and item[0] != 1963:
                skipped.append(item)
        return skipped

    def yearskipper(interrogator_list, justyears):
        """Takes a list and returns only results from the years listed in justyears"""
        skipped = []
        skipped.append(interrogator_list[0]) # append word
        for item in interrogator_list[1:]:
            if type(item) != unicode and type(item) != str:
                for year in justyears:
                    if item[0] == year:
                        skipped.append(item)
        return skipped

    def yearspanner(interrogator_list, yearspan):
        """Takes a list and returns results from between the first and last year in yearspan"""
        
        skipped = [interrogator_list[0]] # append word
        for item in interrogator_list[1:]:
            if type(item) != unicode and type(item) != str:
                if item[0] >= yearspan[0]:
                    if item [0] <= yearspan[-1] + 1:
                        skipped.append(item)
        return skipped

    def projector(interrogator_list):
        """Takes a list and returns a version with projections"""
        projected = []
        projected.append(interrogator_list[0]) # append word
        for item in interrogator_list[1:]:
            if type(item) != str and type(item) != str and item[0] == 1963:
                newtotal = item[1] * proj63
                datum = [item[0], newtotal]
                projected.append(datum)
            elif type(item) != str and type(item) != str and item[0] == 2014:
                newtotal = item[1] * 1.37
                datum = [item[0], newtotal]
                projected.append(datum)
            else:
                projected.append(item)
        return projected

    def csvmaker(csvdata, csvalldata, csvmake):
        """Takes whatever ended up getting plotted and puts it into a csv file"""
        # now that I know about Pandas, I could probably make this much less painful.
        csv = []
        yearlist = []
        # get list of years
        for entry in csvdata[0]:
            if type(entry) == list:
                yearlist.append(str(entry[0]))
        # make first line
        csv.append(title)
        # make the second line
        years = ',' + ','.join(yearlist)
        csv.append(years)
        # for each word
        for entry in csvdata:
            csvline = []
            csvcounts = []
            csvline.append(entry[0]) # append word
            for part in entry[1:]:
                csvcounts.append(str(part[1])) # append just the count
            counts = ','.join(csvcounts)
            csvline.append(counts)
            line = ','.join(csvline)
            csv.append(line)
        csv = '\n'.join(csv)
        # now do all data
        csvall = []
        yearlist = []
        # get list of years
        for entry in csvalldata[0]:
            if type(entry) == list:
                yearlist.append(str(entry[0]))
        # make first line
        csvall.append(title)
        # make the second line
        years = ',' + ','.join(yearlist)
        csvall.append(years)
        # for each word
        for entry in csvalldata:
            csvallline = []
            csvallcounts = []
            csvallline.append(entry[0]) # append word
            for part in entry[1:]:
                csvallcounts.append(str(part[1])) # append just the count
            counts = ','.join(csvallcounts)
            csvallline.append(counts)
            line = ','.join(csvallline)
            csvall.append(line)
        csvall = '\n'.join(csvall)
        # write the csvall file?
        if os.path.isfile(csvmake):
            raise ValueError("CSV error: %s already exists in current directory. \
                    Move it, delete it, or change the name of the new .csv file." % csvmake)
        try:
            fo=open(csvmake,"w")
        except IOError:
            print "Error writing CSV file."
        fo.write('Plotted results:\n'.encode("UTF-8"))
        fo.write(csv.encode("UTF-8"))
        fo.write('\n\nAll results:\n'.encode("UTF-8"))
        fo.write(csvall.encode("UTF-8"))
        fo.close()
        time = strftime("%H:%M:%S", localtime())
        print time + ": " + csvmake + " written to currect directory."

    ##################################################################

    # check for tex and use it if it's there
    if have_tex:
        rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
        rc('text', usetex=True)

    #image directory
    if have_python_tex:
        imagefolder = '../images'
    else:
        imagefolder = 'images'

    # Use .results branch if branch is unspecified
    if isinstance(results, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        results = results.results
    if only_below_p:
        if sort_by == 'static':
            warnings.warn('\nStatic trajectories will confirm the null hypothesis, so it might ' +
                              'not be helpful to use both the static and only_below_p options together.')
        if sort_by == 'total' or sort_by == 'name':
            warnings.warn("\nP value has not been calculated. No entries will be excluded") 
    
    # cut short to save time if later results aren't useful
    if csvmake or sort_by != 'total':
        cutoff = len(results)
    else:
        cutoff = num_to_plot
    
    # if plotting one entry/a totals list, wrap it in another list
    if type(results[0]) == unicode or type(results[0]) == str:
        legend = False
        alldata = [copy.deepcopy(results)][:cutoff]
        num_to_plot = 1
    else:
        legend = True
        alldata = copy.deepcopy(results[:cutoff])

    # determine if no subcorpora and thus barchart
    if len(results[0]) == 3 or len(results[0]) == 4:
        barchart = True
    else:
        barchart = False

    # if no x_label, guess 'year' or 'group'
    if x_label:
        x_lab = x_label
    else:
        if not barchart:
            check_x_axis = alldata[0] # get first entry
            check_x_axis = check_x_axis[1] # get second entry of first entry (year, count)
            if 1500 < check_x_axis[0] < 2050:
                x_lab = 'Year'
            else:
                x_lab = 'Group'
        else:
            x_lab = False


    # select totals if no branch selected
    if fract_of:
        if isinstance(fract_of, tuple) is True:
            fract_of = fract_of.totals
            warnings.warn('\nNo branch of fract_of selected. Using .totals ... ')
        # copy this, to be safe!
        if fract_of[0] != u'Totals':
            raise ValueError('Results branch selected for fract_of. Change to .totals and try again.')
        totals = copy.deepcopy(fract_of)

        #use mather to make percentage results
        fractdata = []
        for entry in alldata:
            fractdata.append(mather(entry, '%', totals, multiplier = multiplier))
        alldata = copy.deepcopy(fractdata)
    

    csvdata = []
    csvalldata = []
    final = []
    
    if num_to_plot > len(alldata):
        warnings.warn("There are not %d entries to show.\nPlotting all %d results..." % (num_to_plot, len(alldata)))
    
    if not csvmake:
        cutoff = num_to_plot
    
    
    # if more than 10 plots, use colormap
    if cutoff > 10:
        the_range = np.linspace(0, 1, cutoff)
        colours = [plt.cm.Dark2(n) for n in the_range]
    # if 10 or less plots, use custom color palette
    else:
        colours = ["#1f78b4", "#33a02c", "#e31a1c", "#ff7f00", "#6a3d9a", "#a6cee3", "#b2df8a", "#fb9a99", "#fdbf6f", "#cab2d6"]


    # process all the data according to options

    processed_data = []
    if not barchart:
        for index, entry in enumerate(alldata):
            # run called processes
            if skip63:
                entry = skipper(entry)
            if yearspan:
                entry = yearspanner(entry, yearspan)
            if justyears:
                entry = yearskipper(entry, justyears)
            if projection:
                if not fract_of:
                    entry = projector(entry)
            processed_data.append(entry)

        # do stats if needed
        if sort_by != 'total':
            do_stats = True
            from decimal import Decimal
            getcontext().prec = 6
            alldata = resorter(processed_data,
                               sort_by = sort_by, 
                               revert_year = revert_year,
                               keep_stats = True,
                               only_below_p = only_below_p, 
                               significance_level = significance_level)
        else:
            do_stats = False

        # if not barchart, format data for plotting and plot
        for index, entry in enumerate(alldata[:cutoff]):
            # get word
            word = entry[0]
            
            if do_stats:
                pval = Decimal(entry[-1][3])
                p_short = "%.4f" % pval
                p_string = ' (p=%s)' % p_short   
                # remove stats, we're done with them.
                entry.pop() 
            # get totals ... horrible code
            total = 0
            if fract_of:
                if entry[-1][0] == 'Total':
                    num = entry[-1][1]
                    total = "%.2f" % num
                    #total = str(float(entry[-1][1]))[:5]
                totalstring = ' (' + str(total) + '\%)'     
            else:
                if entry[-1][0] == 'Total':
                    total = entry[-1][1]
                totalstring = ' (n=%d)' % total
    
            entry.pop() # get rid of total. good or bad?
            csvalldata.append(entry) 
    
            # this bad code attempts to draw dotted lines when bits are missing. 
            # it's no good.

            if index < num_to_plot:
                csvdata.append(entry)
                toplot = []
                xvalsbelow = []
                yvalsbelow = []
                xvalsabove = []
                yvalsabove = []
                d = 1 # first tuple, maybe not very stable
                tups = len(entry) - 2 # all tuples minus 2 (to skip totals tuple)
                for _ in range(tups):
                    firstpart = entry[d] # first tuple
                    firstyear = firstpart[0]
                    nextpart = entry[d + 1]
                    nextyear = nextpart[0]
                    diff = nextyear - firstyear
                    if nextyear - firstyear > 1:
                        xvalsbelow.append(firstpart[0])
                        yvalsbelow.append(firstpart[1])
                        xvalsbelow.append(nextpart[0])
                        yvalsbelow.append(nextpart[1])
                    else:
                        xvalsabove.append(firstpart[0])
                        yvalsabove.append(firstpart[1])
                        xvalsabove.append(nextpart[0])
                        yvalsabove.append(nextpart[1])
                    d += 1

                # do actual plotting
                if on_cloud:
                    plt.plot(xvalsbelow, yvalsbelow, '--', color=colours[index])
                    plt.plot(xvalsabove, yvalsabove, '-', label=word, color=colours[index])
                    plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])
                else:
                    plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])
                    plt.plot(xvalsbelow, yvalsbelow, '--', color=colours[index])
                    if legend_totals:
                        thelabel = word + totalstring
                        plt.plot(xvalsabove, yvalsabove, '-', label=thelabel, color=colours[index])
                        plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])
                    elif legend_p:
                        if sort_by == 'total' or sort_by == 'name':
                            warnings.warn("\nP value has not been calculated, so it can't be printed.", color=colours[index])
                            plt.plot(xvalsabove, yvalsabove, '-', label=word, color=colours[index])
                            plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])              
                        else:
                            thelabel = word + p_string
                            plt.plot(xvalsabove, yvalsabove, '-', label=thelabel, color=colours[index])
                            plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])               
                    else:
                        plt.plot(xvalsabove, yvalsabove, '-', label=word, color=colours[index])
                        plt.plot(xvalsabove, yvalsabove, '.', color=colours[index])
            
            # old way to plot everything at once
            #plt.plot(*zip(*toplot), label=word) # this is other projects...
        
        #make legend
        if legend:
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fancybox=True, framealpha=0.5)

    elif barchart:
        rcParams['figure.figsize'] = figsize, figsize/2
        cutoff = len(alldata)
        import numpy as np
        scores = [entry[1][1] for entry in alldata[:cutoff]]
        ind = np.arange(cutoff)  # the x locations for the groups
        width = 0.35       # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, scores, width, color="#1f78b4")
        
        if len(results[0]) == 4:
            compscores = [entry[2][1] for entry in alldata[:cutoff]]
            rects2 = ax.bar(ind+width, compscores, width, color="#33a02c")
        
        # add some text for labels, title and axes ticks
        
        ax.set_xticks(ind+width)
        
        # get labels
        labels = [entry[0] for entry in alldata[:cutoff]]
        
        longest = len(max(labels, key=len))
        if longest > 7:
            if figsize < 20:
                if num_to_plot > 6:
                    ax.set_xticklabels(labels, rotation=45)
        else:
            ax.set_xticklabels(labels)

        # rotate the labels if they're long:

        
        #def autolabel(rects):
            # attach some text labels
            #for rect in rects:
                #height = rect.get_height()
                #ax.text(rect.get_x()+rect.get_width()/2., 1.0*height, '%d'%int(height),
                        #ha='center', va='bottom')
        
        #autolabel(rects1)
        #if len(results[0]) == 4:
            #autolabel(rects2)
        legend_labels = [alldata[0][1][0], alldata[0][2][0]]
        ax.legend( (rects1[0], rects2[0]), legend_labels )

    # make axis labels
    if x_lab:
        plt.xlabel(x_lab)

    if not y_label:
        #print "Warning: no name given for y-axis. Using default."
        if fract_of:
            y_label = 'Percentage'
        if not fract_of:
            y_label = 'Total frequency'
    plt.ylabel(y_label)
    pylab.title(title)

    if not barchart:
        plt.gca().get_xaxis().set_major_locator(MaxNLocator(integer=True))
        
        if log == 'x':
            plt.xscale('log')
            plt.gca().get_xaxis().set_major_formatter(ScalarFormatter())
        elif log == 'y':
            plt.yscale('log')
            plt.gca().get_yaxis().set_major_formatter(ScalarFormatter())
        elif log == 'x, y':
            plt.xscale('log')
            plt.gca().get_xaxis().set_major_formatter(ScalarFormatter())
            plt.yscale('log')
            plt.gca().get_yaxis().set_major_formatter(ScalarFormatter())
        else:
            plt.ticklabel_format(useOffset=False, axis='x', style = 'plain')
    plt.grid()
    fig1 = plt.gcf()
    if not have_python_tex:
        plt.show()

    def urlify(s):
            import re
            s = s.lower()
            s = re.sub(r"[^\w\s]", '', s)
            s = re.sub(r"\s+", '-', s)
            return s     
    
    if save:
        if not os.path.isdir(imagefolder):
            os.makedirs(imagefolder)
        if type(save) == str:
            savename = os.path.join(imagefolder, urlify(save) + '.png')
        else:
            savename = os.path.join(imagefolder, urlify(title) + '.png')
        if legend and not barchart:
                fig1.savefig(savename, bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=150, transparent=True)
        else:
            fig1.savefig(savename, dpi=150, transparent=True)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)
    if csvmake:
        if type(csvmake) == bool:
            csvmake = urlify(title) + '.csv'    
        csvmaker(csvdata, csvalldata, csvmake)


def topix_plot(title, results, fract_of = False, **kwargs):
    """Plots results from subcorpus interrogation."""
    topic_subcorpora = ['economics', 'health', 'politics']
    for index, topic in enumerate(topic_subcorpora):
        newtitle = title + ' in ' + str(topic) + ' articles' # semi-automatic titles (!)
        if not fract_of: # if counting ratios/percentages, 
            plotter(newtitle, results[index], **kwargs)
        else:
            plotter(newtitle, results[index], 
                fract_of = fract_of[index], **kwargs)




def table(data_to_table, allresults = False, maxresults = 50):
    """Outputs a table from interrogator or CSV results.

    if allresults, show all results table, rather than just plotted results"""
    import pandas
    from pandas import DataFrame
    import re
    import os
    from StringIO import StringIO
    import copy
    if type(data_to_table) == str:
        f = open(data_to_table)
        raw = f.read()
        #raw = os.linesep.join([s for s in raw.splitlines() if s])
        plotted_results, all_results =  raw.split('All results:')
        if not allresults:
            lines = plotted_results.split('\n')
            print str(lines[1])
            data = '\n'.join([line for line in lines if line.strip()][2:])
        if allresults:
            lines = all_results.split('\n')
            print str(lines[1])
            lines = lines[:maxresults + 3]
            data = '\n'.join([line for line in lines if line.strip()][1:])
    elif type(data_to_table) == list:
        csv = []
        if type(data_to_table[0]) == str or type(data_to_table[0]) == unicode:
            wrapped = [copy.deepcopy(data_to_table)]
        else:
            wrapped = copy.deepcopy(data_to_table)
        regex = re.compile('(?i)total')
        if re.match(regex, wrapped[-1][0]):
            total_present = True
        else:
            total_present = False
        years = [str(year) for year, count in wrapped[0][1:]]
        # uncomment below to make total column
        topline = ',' + ','.join(years) # + ',total'
        csv.append(topline)
        data = []
        for entry in wrapped[:maxresults]:
            word = entry[0]
            total = sum([count for year, count in entry[1:]])
            counts = [str(count) for year, count in entry[1:]]
            # uncomment below to make total column
            dataline = str(word) + ',' + ','.join(counts) # + ',' + str(total)
            csv.append(dataline)
        # table it with pandas
        data = '\n'.join(csv)
    df = DataFrame(pandas.read_csv(StringIO(data), index_col = 0, engine='python'))
    pandas.options.display.float_format = '{:,.2f}'.format
    return df


def tally(lst, indices):
    """Display total occurrences of a result"""

    # this tool doesn't do a whole lot, now that totals are found during interrogation.
    output = []
    if type(indices) == int:
        item_of_interest = lst[indices]
        word = item_of_interest[0]
        total = item_of_interest[-1][-1]
        string = str(indices) + ': ' + str(word) + ': ' + str(total) + ' total occurrences.'
        output.append(string)
    if type(indices) == list:
        for index in indices:
            item_of_interest = lst[index]
            word = item_of_interest[0]
            total = item_of_interest[-1][-1]
            string = str(index) + ': ' + str(word) + ': ' + str(total) + ' total occurrences.'
            output.append(string)
    if type(indices) == str:
        if indices == 'all':
            for item in lst:
                word = item[0]
                total = item[-1][-1]
                string = str(lst.index(item)) + ': ' + str(word) + ': ' + str(total) + ' total occurrences.'
                output.append(string)
        else: # if regex
            import re
            regex = re.compile(indices)    
            for item in lst:
                if re.search(regex, item[0]):
                    word = item[0]
                    total = item[-1][-1]
                    string = str(lst.index(item)) + ': ' + str(word) + ': ' + str(total) + ' total occurrences.'
                    output.append(string)
                #else:
                    #raise ValueError("No matches found. Sorry")
    return output


def quickview(lst, n = 50, topics = False, sort_by = 'total'):
    """See first n words of an interrogation.
    lst: interrogator() list
    n: number of results to view
    topics: for investigation of topic subcorpora"""
    if sort_by != 'total':
        from corpkit.edit import resorter
    if isinstance(lst, tuple) is True:
        import warnings
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results
    import copy
    safe_copy = copy.deepcopy(lst)
    if sort_by != 'total':
        safe_copy = resorter(safe_copy, sort_by = sort_by)
    if type(safe_copy[0]) == str or type(safe_copy[0]) == unicode:
        return '0: %s: %d' % (safe_copy[0], safe_copy[-1][1])
    if not topics:
        out = []
        for index, item in enumerate(safe_copy[:n]):
            # if it's interrogator result
            if type(item) == list:
                word = str(item[0])
                index_and_word = ['% 4d' % index, word]
                as_string = ': '.join(index_and_word)
                out.append(as_string)
            else:
                out.append(item)
        return out
    if topics:
        topics = [d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path,d))
        and d != 'years']
        out = []
        for corpus in topics:
            subout = []
            out.append(corpus.upper())
            sublist = safe_copy[topics.index(corpus)]
            subout = []
            for item in sublist[:n]:
                indexnum = sublist.index(item)
                word = item[0]
                index_and_word = [str(indexnum), word]
                as_string = ': '.join(index_and_word)
                subout.append(as_string)
            out.append(subout)
    # should this change to just printing?
    return out
