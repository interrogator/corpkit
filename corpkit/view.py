#!/usr/bin/python

#   Interrogating parsed corpora and plotting the results: plotter()
#   Author: Daniel McDonald

def old_plotter(title, 
            results, 
            sort_by = False, 
            fract_of = False, 
            num_to_plot = 7, 
            significance_level = 0.05, 
            revert_year = True,
            multiplier = 100, 
            yearspan = False, 
            proj63 = 5,
            justyears = False, 
            csvmake = False, 
            x_label = False, 
            y_label = False, 
            legend_p = False,
            legend_totals = False, 
            log = False, 
            figsize = 11, 
            save = False, 
            only_below_p = False, 
            skip63 = False, 
            projection = True,
            just_totals = False,
            threshold = 'relative',
            style = 'ggplot'):
    """
    Visualise interrogator() results, optionally generating a csv as well.

    Basically, give your figure a title an a list of results and they will be plotted. 
    Results can also be plotted as fractions of another list, using the fract_of argument.

    If fract_of is simply a list of totals, every plotted entry will be plotted as a fraction of the total.
    If the fract_of list is another results list, it should probably be a superordinate one. 
    plotter() will plot the main entry as a fraction of the same word in the fract_of list.

    Another key feature is the ability to sort results by total, or by trajectory: increasing, decreasing or static. 
    When using the trajectory options, p values are also calculated, and can be printed in the legend.

    Most of the other options are for easy customisation of the look of the image, saving it, etc.

    Parameters
    ----------

    title : string
        Chart title
    results : list
        interrogator() results or totals (deaults to results)
    sort_by : string / Boolean
        'total': sort by most frequent
        'infreq': sort by least frequent
        'name': sort alphabetically
        'increase': calculate linear regression, sort by steepest up slope
        'decrease': calculate linear regression, sort by steepest down slope 
        'static': calculate linear regression, sort by least slope
        False: do no sorting
        True: do 'total'
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
    num_to_plot : int/'all'
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
    figsize : int
        Size of image
    save : True/False/string
        Generate save image with string as filename
        If True, 'title' string is used for name
    style : str
        visualisation style sheets. pick from:
        'dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight'

    NYT-only parameters
    -----
    skip63 : boolean
        Skip 1963 results (for NYT investigation)
    projection : boolean
        Project 1963/2014 results (for NYT investigation)
    proj63 : int
        The amount to project 1963 results by

    Examples
    -----
    from corpkit import interrogator, plotter
    corpus = 'path/to/corpus'
    adjectives = interrogator(corpus, 'words', r'/JJ.?/ < __', lemmatise = True)
    adjectives_as_subject_head = interrogator(corpus, 'words', r'/JJ.?/ >># @NP < __', lemmatise = True)
    allwords = interrogator(corpus, 'count', 'any_word')
    
    # absolute frequency of adjectives
    plotter('Most common adjectives', adjectives.results)

    # plot common adjectives as a percentage of all adjectives
    plotter('Most common adjectives', adjectives.results, fract_of = adjectives.totals)

    # plot adjectives as percentage of all words in the corpus
    plotter('Most common adjectives', adjectives.results, fract_of = allwords.totals)

    # plot common adjectives in subject position as percentage of all subject adjectives:
    plotter('Most common adjectives in subject position', 
             adjectives_as_subject_head.results, fract_of = adjectives_as_subject_head.totals)

    # determine the percentage of the time each adjective is used in subject position:
    plotter('Most common adjectives in subject position',
             adjectives_as_subject_head.results, fract_of = adjectives.results, 
             y_label = 'Percentage of the time each word is the subject')

    """

    import os
    import warnings
    import copy
    from time import localtime, strftime
    import numpy as np
    import matplotlib
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
    from corpkit.tests import check_dit, check_pytex, check_tex
    from corpkit.edit import resorter, mather, percenter

    # setup:

    # size:
    rcParams['figure.figsize'] = figsize, figsize/2
    
    #font
    rcParams.update({'font.size': (figsize / 2) + 7}) # half your size plus seven

    # nicer looks for plots
    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight']
    if style not in styles:
        raise ValueError('Style %s not found. Use %s' % (style, ', '.join(styles)))
    
    #matplotlib.style.use(style)
    
    # check what we're doing here.
    have_python_tex = check_pytex()
    on_cloud = check_dit()
    have_tex = check_tex(have_ipython = have_ipython)

    def keep_only_totaller(interrogator_list):
        return [interrogator_list[0], interrogator_list[-1]]

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
        for item in interrogator_list[1:-1]:
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
                    if item [0] <= yearspan[-1]:
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
    
    # True sort default to total
    if sort_by is True:
        sort_by = 'total'
    
    # are we doing stats?
    lin_reg = ['static', 'increase', 'decrease']
    if sort_by:
        if sort_by in lin_reg:
            do_stats = True
        else:
            do_stats = False
    else:
        do_stats = False

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
        if not do_stats:
            warnings.warn("\nP value has not been calculated. No entries will be excluded") 
    
    # convert plot all to length of results list
    if num_to_plot == 'all':
        num_to_plot = len(results)

    # cut short to save time if later results aren't useful
    if sort_by != 'total' and sort_by is not False:
        cutoff = len(results)
    else:
        cutoff = num_to_plot
    if csvmake:
        cutoff = len(results)
    csvdata = []
    csvalldata = []
    
    # if plotting one entry/a totals list, wrap it in another list
    if type(results[0]) == unicode or type(results[0]) == str:
        legend = False
        alldata = [results]
        num_to_plot = 1
    
    # if not, shorten list if possible
    else:
        legend = True
        alldata = []
        for entry in results[:cutoff]:
            alldata.append(entry)

    # determing if barchart
    barchart = False

    if just_totals:
        barchart = True
        barchart_one_datapoint = True
        legend = False

    if len(results[0]) == 3:
        barchart = True
        barchart_one_datapoint = True
        legend = False

    if len(results[0]) == 4:
        barchart = True
        barchart_one_datapoint = False
        legend = True
    
    if justyears: 
        if type(justyears) == list:
            if len(justyears) == 2:
                barchart_one_datapoint = False
                barchart = True
            elif len(justyears) == 1:
                barchart_one_datapoint = True
                barchart = True
        elif type(justyears) == str or type(justyears) == unicode:
            justyears = [justyears]
            barchart_one_datapoint = True
            barchart = True            
        elif type(justyears) == int:
            justyears = [justyears]
            barchart_one_datapoint = True
            barchart = True

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

    # select totals if no branch of fract_of selected
    if fract_of:
        if isinstance(fract_of, tuple) is True:
            fract_of = fract_of.totals
            warnings.warn('\nNo branch of fract_of selected. Using .totals ... ')

        if type(fract_of[0]) == list:
            use_percenter = True
            #warnings.warn('\nfract_of is a .results branch. Every entry in results being plotted will divided by the entry with the same name in the fract_of list. This takes longer.')
        else:
            use_percenter = False

        # do fraction maths
        if not use_percenter:
            mathed_data = []
            for entry in alldata:
                mathed_data.append(mather(entry, '%', fract_of, multiplier = multiplier))
            alldata = mathed_data
        
        # if using use_percenter
        else:
            from corpkit.edit import percenter
            alldata = percenter(alldata, fract_of, 
                         threshold = threshold, 
                         sort_by = 'most', 
                         print_threshold = False,
                         just_totals = just_totals)

    if num_to_plot > len(alldata):
        warnings.warn("There are not %d entries to show.\nPlotting all %d results..." % (num_to_plot, len(alldata)))
    
    # cut again now if possible
    if not csvmake:
        cutoff = num_to_plot
    
    # if more than 10 plots, use colormap
    if cutoff > 10:
        the_range = np.linspace(0, 1, cutoff)
        colours = [plt.cm.Dark2(n) for n in the_range]
    
    # if 10 or less plots, use custom color palette
    else:
        colours = ["#1f78b4", "#33a02c", "#e31a1c", "#ff7f00", "#6a3d9a", "#a6cee3", "#b2df8a", "#fb9a99", "#fdbf6f", "#cab2d6"]

    # skip subcorpora, project totals, etc
    processed_data = []
    for index, full_entry in enumerate(alldata):
        # remove totals
        entry = full_entry[:-1]
        if skip63:
            entry = skipper(entry)
        if yearspan:
            entry = yearspanner(entry, yearspan)
        if justyears:
            entry = yearskipper(entry, justyears)
        if projection:
            if not fract_of:
                entry = projector(entry)
        # add total
        entry.append([u'Total', sum([w[1] for w in entry[1:]])])
        processed_data.append(entry)

    # check if the above processes turned it into barchart length
    if len(processed_data[0]) == 3:
        barchart_one_datapoint = True
        barchart = True
    if len(processed_data[0]) == 4:
        barchart_one_datapoint = False
        barchart = True    

    # if just_totals, remove everything else from each entry
    if just_totals:
        fixed_entries = []
        for entry in processed_data:
            fixed_entries.append(keep_only_totaller(entry))
        processed_data = fixed_entries

    # sort processed results
    if sort_by:
        if not just_totals:
            alldata = resorter(processed_data,
                               sort_by = sort_by, 
                               revert_year = revert_year,
                               keep_stats = True,
                               only_below_p = only_below_p, 
                               significance_level = significance_level)
        elif just_totals:
            if do_stats:
                raise ValueError('just_totals cannot be used with sort_by = %s,\n'
                                 'because the linear regression needed to sort relies on multiple integer x-axes.' % sort_by)
            else:
                alldata = resorter(processed_data,
                               sort_by = sort_by, 
                               revert_year = revert_year,
                               keep_stats = True,
                               only_below_p = only_below_p, 
                               significance_level = significance_level)
        #elif barchart_one_datapoint:
            #raise ValueError('sort_by = %s cannot be used when there is only one subcorpus\n'
                                 #'because the linear regression needed to sort relies on multiple integer x-axes.' % sort_by)

    else:
        alldata = processed_data[:cutoff]

    rotate = False

    # make line chart
    if not barchart:

        # line types
        dotted = '--'
        undotted = '-'
        dot = '.'
        markertype = '_'

        for index, entry in enumerate(alldata):
            # get word
            word = entry[0]
            if do_stats:
                import decimal
                from decimal import Decimal
                decimal.getcontext().prec = 6
                pval = Decimal(entry[-1][3])
                p_short = "%.4f" % pval
                p_string = ' (p=%s)' % p_short   
                # remove stats, we're done with them.
                entry.pop() 
            # get totals ... horrible code
            total = 0
            if fract_of:
                if entry[-1][0].startswith('Total'):
                    num = entry[-1][1]
                    total = "%.2f" % num
                totalstring = ' (' + str(total) + '\%)'
            else:
                if entry[-1][0].startswith('Total'):
                    total = entry[-1][1]
                totalstring = ' (n=%d)' % total
    
            entry.pop() # get rid of total. good or bad?
            csvalldata.append(entry) 

            if index < num_to_plot:
                csvdata.append(entry)
                corpus_names = [e[0] for e in entry[1:]]
                
                # for now, convert non int corpus names to range ints
                if type(corpus_names[0]) != int:
                    corpus_names = range(len(corpus_names))

                tot = [e[1] for e in entry[1:]]

                #expected difference between subcorpus name ints
                good_diff = 1

                for i in range(1, len(corpus_names)):
                    # add totals to word if need be
                    if legend_totals:
                        # these wacky try statements are because word is soon turned to none
                        try:
                            word = word + totalstring
                        except:
                            pass
                    if legend_p:
                        if do_stats:
                            # these wacky try statements are because word is soon turned to none
                            try:
                                word = word + p_string
                            except:
                                pass
                        else:
                            warnings.warn("\np-value has not been calculated, so it can't be printed.")
                    # only plot the word the first time around
                    if i != 1:
                        word = None
                        markertype = None

                    # determine dotted or undotted line
                    if corpus_names[i] - corpus_names[i-1] != good_diff:
                        linetype = dotted
                    else:
                        linetype = undotted

                    with plt.style.context((style)):
                        plt.plot([corpus_names[i-1], corpus_names[i]], [tot[i-1], tot[i]], linetype, label=word, color=colours[index])
                        plt.plot([corpus_names[i-1], corpus_names[i]], [tot[i-1], tot[i]], dot, color=colours[index]) 

        #make legend
        if legend:
            with plt.style.context((style)):
                lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., framealpha=0.5)
    
    elif barchart:
        labels = [entry[0] for entry in alldata[:cutoff]]
        # make barchart
        rcParams['figure.figsize'] = figsize, figsize/2
        import numpy as np
        scores = [entry[1][1] for entry in alldata[:cutoff]]
        ind = np.arange(cutoff)  # the x locations for the groups
        width = 0.35       # the width of the bars

        fig, ax = plt.subplots()

        #adjusting dimensions ...
        if legend:
            plt.subplots_adjust(right=0.75)
            if legend_p or legend_totals:
                plt.subplots_adjust(right=0.65)

        fig.patch.set_alpha(0.0)
        
        plt.subplots_adjust(left=0.08)
        
        # more room for x label
        plt.subplots_adjust(bottom=0.18)

        rects1 = ax.bar(ind, scores, width, color="#1f78b4")
        ax.set_xticks(ind)

        longest = len(max(labels, key=len))
        if longest > 7:
            if figsize < 20:
                if num_to_plot > 6:
                    rotate = True
                    ax.set_xticklabels(labels, rotation=45)
        if not rotate:
            ax.set_xticklabels(labels)

        if not barchart_one_datapoint:
            ax.set_xlim(-width,len(ind))
            compscores = [entry[2][1] for entry in alldata[:cutoff]]
            rects2 = ax.bar(ind+width, compscores, width, color="#33a02c")
            # position of x labels
            ax.set_xticks(ind+width)
        else:
            ax.set_xlim(-width,len(ind)-width)
            #ax.set_xticks(ind)

        #else:
            #ax.set_xticklabels(labels)

        #def autolabel(rects):
            # attach some text labels
            #for rect in rects:
                #height = rect.get_height()
                #ax.text(rect.get_x()+rect.get_width()/2., 1.0*height, '%d'%int(height),
                        #ha='center', va='bottom')
        
        #autolabel(rects1)
        #if len(results[0]) == 4:
            #autolabel(rects2)
        if not barchart_one_datapoint:
            legend_labels = [alldata[0][1][0], alldata[0][2][0]]
            ax.legend( (rects1[0], rects2[0]), legend_labels )
        #else:
            #ax.legend()          
    
    # make axis labels
    if x_lab:
        plt.xlabel(x_lab)

    if not y_label:
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
    
    if legend:
        plt.subplots_adjust(right=0.80)
        if legend_p or legend_totals:
            plt.subplots_adjust(right=0.75)
    
    plt.subplots_adjust(left=0.08)
        
    # more room for x label
    plt.subplots_adjust(bottom=0.15)


    #plt.grid()
    fig1 = plt.gcf()
    if not have_python_tex:
        with plt.style.context((style)):
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
                fig1.savefig(savename, bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=150)
        else:
            fig1.savefig(savename, dpi=150)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)
    if csvmake:
        if type(csvmake) == bool:
            csvmake = urlify(title) + '.csv'    
        csvmaker(csvdata, csvalldata, csvmake)

def old_quickview(lst, 
              n = 50, 
              sort_by = False, 
              showtotals = True,
              selection = False,
              topics = False):
    """
    View interrogator() or conc() output

    lst: the interrogator() or conc() output
    n = max to show
    sort_by = temporarily resort
    showtotals = toggle totals for each result
    selection = show only things matching this. it can be:
        int: index of item to show
        list of ints: indices to show
        str: regex, show matches
        list of strs: 
            for interrogator results, keep entries matching anything in list
            for concordance lines, keep lines containing anything in list
        topics: obsolete, unmaintained option for quickviewing a number of corpora
        """
    if sort_by is not False:
        from corpkit.edit import resorter
    if isinstance(lst, tuple) is True:
        import warnings
        warnings.warn('\nNo branch of results selected. Using .results ... ')
        lst = lst.results

    # if quickview totals, do it very simply:
    if lst[0] == u'Totals':
        return '0: %s (%d)' % (lst[0], lst[-1][1])

    conclines = True
    if type(lst[0]) == list:
        conclines = False

    output = []
    to_show = []

    if selection == 'all':
        selection = range(len(lst))

    # if selection is int, wrap
    if type(selection) == int:
        selection = [selection]

    if selection:
        if type(selection) == list:
            if type(selection[0]) == int:
                to_show = [i for index, i in enumerate(lst) if index in selection]
            elif type(selection[0]) == str:
                if conclines:
                    to_show = []
                    for w in selection:
                        for e in lst:
                            if w in e:
                                to_show.append(e)
                else:
                    to_show = [e for e in lst if e[0] in selection]
        else:
            # if regex
            import re
            regex = re.compile(selection)
            if conclines:
                to_show = [e for e in lst if re.search(regex, e)]
            else:
                to_show = [e for e in lst if re.search(regex, e[0])]
                
    else:
        to_show = [i for i in lst]

    if sort_by:
        sorted_lst = resorter(to_show, sort_by = sort_by)
    else:
        sorted_lst = [i for i in to_show]

    if not topics:
        out = []
        for index, item in enumerate(sorted_lst[:n]):
            # if it's interrogator result
            if type(item) == list:
                word = str(item[0])
                total = ' (%d)' % item[-1][1]
                if not showtotals:
                    index_and_word = ['% 4d' % index, word]
                    as_string = ': '.join(index_and_word)
                else:
                    index_and_word = ['% 4d' % index, word]
                    as_string = ': '.join(index_and_word)
                    as_string = as_string + total
                out.append(as_string)
            else:
                out.append(': '.join(['% 4d' % index, item]))
        return out
    # below is unmaintained
    if topics:
        topics = [d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path,d))
        and d != 'years']
        out = []
        for corpus in topics:
            subout = []
            out.append(corpus.upper())
            sublist = sorted_lst[topics.index(corpus)]
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
