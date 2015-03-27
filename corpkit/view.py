#!/usr/bin/python

#   Interrogating parsed corpora and plotting the results: plotter()
#   Author: Daniel McDonald


def plotter(title, results, sort_by = 'total', fract_of = False, y_label = False, 
    num_to_plot = 7, skip63 = False, significance_level = 0.05,
    multiplier = 100, projection = True, yearspan = False, proj63 = 5,
    justyears = False, csvmake = False, x_label = False, legend_p = False,
    legend_totals = False, log = False, figsize = 11, save = False, only_below_p = False):
    """
    Takes interrogator output and plots it with matplotlib, optionally generating a csv as well.

    Option documentation forthcoming.
    """

    import os
    import warnings
    import copy
    from time import localtime, strftime
    
    import matplotlib.pyplot as plt
    from matplotlib import rc
    from matplotlib.ticker import MaxNLocator, ScalarFormatter
    import pylab
    from pylab import rcParams
    
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.edit import resorter, mather

    # setup:

    # size:
    rcParams['figure.figsize'] = figsize, figsize/2
    
    #font
    rcParams.update({'font.size': (figsize / 2) + 7}) # half your size plus seven
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
    rc('text', usetex=True)

    #image directory
    imagefolder = 'images'


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
            warnings.warn('\nNo branch of fract_of selected. Using .totals ... ')
            fract_of = fract_of.totals
        # copy this, to be safe!
        totals = copy.deepcopy(fract_of)

        #use mather to make percentage results
        fractdata = []
        for entry in alldata:
            fractdata.append(mather(entry, '%', totals, multiplier = multiplier))
        alldata = copy.deepcopy(fractdata)
    
    # sort_by with resorter
    if sort_by != 'total':
        do_stats = True
        alldata = resorter(alldata, sort_by = sort_by, 
                           keep_stats = True, only_below_p = only_below_p, 
                           significance_level = significance_level, skip63 = skip63)
    else:
        do_stats = False
    csvdata = []
    csvalldata = []
    final = []
    colours = ["#1f78b4", "#33a02c", "#e31a1c", "#ff7f00", "#6a3d9a", "#a6cee3", "#b2df8a", "#fb9a99", "#fdbf6f", "#cab2d6"]
    c = 0
    
    if num_to_plot > len(alldata):
        warnings.warn("There are not %d entries to show.\nPlotting all %d results..." % (num_to_plot, len(alldata)))
    
    if not csvmake:
        cutoff = num_to_plot
    
    if not barchart:
        for index, entry in enumerate(alldata[:cutoff]):
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
            # get word
            word = entry[0]
            if do_stats:
                pval = entry[-1][3]
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
                # do these get written over!?
                plt.plot(xvalsabove, yvalsabove, '.', color=colours[c]) # delete for nyt
                plt.plot(xvalsbelow, yvalsbelow, '--', color=colours[c])
                if legend_totals:
                    thelabel = word + totalstring
                    plt.plot(xvalsabove, yvalsabove, '-', label=thelabel, color=colours[c])
                    plt.plot(xvalsabove, yvalsabove, '.', color=colours[c]) # delete for nyt
                elif legend_p:
                    if sort_by == 'total' or sort_by == 'name':
                        warnings.warn("\nP value has not been calculated, so it can't be printed.")
                        plt.plot(xvalsabove, yvalsabove, '-', label=word, color=colours[c])
                        plt.plot(xvalsabove, yvalsabove, '.', color=colours[c]) # delete for nyt              
                    else:
                        thelabel = word + p_string
                        plt.plot(xvalsabove, yvalsabove, '-', label=thelabel, color=colours[c])
                        plt.plot(xvalsabove, yvalsabove, '.', color=colours[c]) # delete for nyt               
                else:
                    plt.plot(xvalsabove, yvalsabove, '-', label=word, color=colours[c])
                    plt.plot(xvalsabove, yvalsabove, '.', color=colours[c]) # delete for nyt
                if c == 8:
                    c = 0 # unpythonic
                c += 1
            
            # old way to plot everything at once
            #plt.plot(*zip(*toplot), label=word) # this is other projects...
        
        #make legend
        if legend:
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    elif barchart:
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

        
        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.0*height, '%d'%int(height),
                        ha='center', va='bottom')
        
        autolabel(rects1)
        if len(results[0]) == 4:
            autolabel(rects2)
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
    plt.show()

    def urlify(s):
            import re
            s = s.lower()
            s = re.sub(r"[^\w\s]", '', s)
            s = re.sub(r"\s+", '-', s)
            return s     
    
    if save:
        if type(save) == str:
            savename = os.path.join(imagefolder, urlify(save) + '.png')
        else:
            savename = os.path.join(imagefolder, urlify(title) + '.png')
        if legend:
            fig1.savefig(savename, bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=150) 
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


def quickview(lst, n = 50, topics = False):
    """See first n words of an interrogation.

    lst: interrogator() list
    n: number of results to view
    topics: for investigation of topic subcorpora"""
    import warnings
    if isinstance(lst, tuple) is True:
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results
    if type(lst[0]) == str or type(lst[0]) == unicode:
        return '0: %s: %d' % (lst[0], lst[-1][1])
    if not topics:
        out = []
        for index, item in enumerate(lst[:n]):
            # if it's interrogator result
            if type(item) == list:
                word = item[0]
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
            sublist = lst[topics.index(corpus)]
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
