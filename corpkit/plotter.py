
def plotter(title,
            df,
            x_label = None,
            y_label = None,
            style = 'ggplot',
            figsize = (8, 4),
            save = False,
            legend_pos = 'best',
            reverse_legend = 'guess',
            num_to_plot = 7,
            tex = 'try',
            colours = 'Paired',
            cumulative = False,
            pie_legend = True,
            partial_pie = False,
            show_totals = False,
            transparent = False,
            output_format = 'png',
            **kwargs):
    """plot interrogator() or editor() output.

    **kwargs are for pandas first, which can then send them through to matplotlib.plot():

    http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.plot.html
    http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot

    pie_legend: False to label slices rather than give legend
    show_totals: where to show percent/abs frequencies: False, 'plot', 'legend', or 'both'

    """

    import os
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc
    import pandas
    import pandas as pd
    from pandas import DataFrame

    import numpy
    from time import localtime, strftime
    from corpkit.tests import check_pytex

    have_python_tex = check_pytex()

    def get_savename(imagefolder, save = False, title = False, ext = 'png'):
        """Come up with the savename for the image."""
        import os
        def urlify(s):
            "Turn title into filename"
            import re
            s = s.lower()
            s = re.sub(r"[^\w\s]", '', s)
            s = re.sub(r"\s+", '-', s)
            return s     
        # name as 
        if not ext.startswith('.'):
            ext = '.' + ext
        if type(save) == str:
            savename = os.path.join(imagefolder, (urlify(save) + ext))
        #this 'else' is redundant now that title is obligatory
        else:
            if title:
                filename = urlify(title) + ext
                savename = os.path.join(imagefolder, filename)

        #    # generic sequential naming
        #    else:
        #        list_images = [i for i in sorted(os.listdir(imagefolder)) if i.startswith('image-')]
        #        if len(list_images) > 0:
        #            num = int(list_images[-1].split('-')[1].split('.')[0]) + 1
        #            autoname = 'image-' + str(num).zfill(3)
        #            savename = os.path.join(imagefolder, autoname + '.png')
        #        else:
        #            savename = os.path.join(imagefolder, 'image-001.png')
        
        # remove duplicated ext
        if savename.endswith('%s%s' % (ext, ext)):
            savename = savename.replace('%s%s' % (ext, ext), ext, 1)
        return savename

    def rename_data_with_total(dataframe, was_series = False, using_tex = False, absolutes = True):
        if was_series:
            where_the_words_are = dataframe.index
        else:
            where_the_words_are = dataframe.columns
        the_labs = []
        for w in list(where_the_words_are):
            if not absolutes:
                if was_series:
                    perc = dataframe.T[w][0]
                else:
                    the_labs.append(w)
                    continue
                if using_tex:
                    the_labs.append('%s (%.2f\%%)' % (w, perc))
                else:
                    the_labs.append('%s (%.2f %%)' % (w, perc))
            else:
                if was_series:
                    score = dataframe.T[w].sum()
                else:
                    score = dataframe[w].sum()
                if using_tex:
                    the_labs.append('%s (n=%d)' % (w, score))
                else:
                    the_labs.append('%s (n=%d)' % (w, score))
        if not was_series:
            dataframe.columns = the_labs
        else:
            vals = list(dataframe[list(dataframe.columns)[0]].values)
            dataframe = pd.DataFrame(vals, index = the_labs)
            dataframe.columns = ['Total']
        return dataframe

    def auto_explode(dataframe, input, was_series = False, num_to_plot = 7):
        """give me a list of strings and i'll output explode option"""
        output = [0 for s in range(num_to_plot)]
        if was_series:
            l = list(dataframe.index)
        else:
            l = list(dataframe.columns)

        if type(input) == str or type(input) == int:
            input = [input]
        if type(input) == list:
            for i in input:
                if type(i) == str:
                    index = l.index(i)
                else:
                    index = i
                output[index] = 0.1
        return output

    # are we doing subplots?
    # redundant ish now
    sbplt = False
    if 'subplots' in kwargs:
        if kwargs['subplots'] is True:
            sbplt = True

    if colours is True:
        colours = 'Paired'

    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight', 'matplotlib']
    if style not in styles:
        raise ValueError('Style %s not found. Use %s' % (style, ', '.join(styles)))

    # try to use tex
    using_tex = False
    if tex == 'try' or tex is True:
        try:
            rc('text', usetex=True)
            rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
            using_tex = True
        except:
            rc('text', usetex=False)
    else:
        rc('text', usetex=False)   

    if show_totals is False:
        show_totals = 'none'

    # find out if pie mode, add autopct format
    piemode = False
    if 'kind' in kwargs:
        if kwargs['kind'] == 'pie':
            piemode = True
            # always the best spot for pie
            if legend_pos == 'best':
                legend_pos = 'lower left'
            if show_totals.endswith('plot') or show_totals.endswith('both'):
                #kwargs['pctdistance'] = 0.65
                if using_tex:
                    kwargs['autopct'] = r'%1.1f\%%'
                else:
                    kwargs['autopct'] = '%1.1f%%'

    
    #if piemode:
        #if partial_pie:
            #kwargs['startangle'] = 180

    kwargs['subplots'] = sbplt

    # copy data, make series into df
    dataframe = df.copy()
    was_series = False
    if type(dataframe) == pandas.core.series.Series:
        was_series = True
        if not cumulative:
            dataframe = DataFrame(dataframe)
        else:
            dataframe = DataFrame(dataframe.cumsum())
    else:
        # don't know if this is much good.
        if cumulative:
            dataframe = DataFrame(dataframe.cumsum())
    
    # attempt to convert x axis to ints:
    try:
        dataframe.index = [int(i) for i in list(dataframe.index)]
    except:
        pass

    # remove totals if there ... maybe redundant
    try:
        dataframe = dataframe.drop('Total', axis = 0)
    except:
        pass

    # set backend?
    output_formats = ['svgz', 'ps', 'emf', 'rgba', 'raw', 'pdf', 'svg', 'eps', 'png', 'pgf']
    if output_format not in output_formats:
        raise ValueError('%s output format not recognised. Must be: %s' % (output_format, ', '.join(output_formats)))
    
    # don't know if these are necessary
    if 'pdf' in output_format:
        plt.switch_backend(output_format) 
    if 'pgf' in output_format:
        plt.switch_backend(output_format)

    if num_to_plot == 'all':
        if was_series:
            if not piemode:
                num_to_plot = len(dataframe)
            else:
                num_to_plot = len(dataframe)
        else:
            if not piemode:
                num_to_plot = len(list(dataframe.columns))
            else:
                num_to_plot = len(dataframe.index)

    # explode pie, or remove if not piemode
    if 'explode' in kwargs:
        if not piemode:
            del kwargs['explode']
    if piemode:
        if 'explode' in kwargs:
            kwargs['explode'] = auto_explode(dataframe, 
                                             kwargs['explode'], 
                                             was_series = was_series, 
                                             num_to_plot = num_to_plot)

    #cut data short
    plotting_a_totals_column = False
    if was_series:
        if list(dataframe.columns)[0] != 'Total':
            dataframe = dataframe[:num_to_plot]
        else:
            plotting_a_totals_column = True
            if not 'legend' in kwargs:
                legend = False
            num_to_plot = len(dataframe)

    else:
        dataframe = dataframe.T.head(num_to_plot).T

    # make and set y label
    absolutes = True
    if type(dataframe[list(dataframe.columns)[0]][list(dataframe.index)[0]]) == numpy.float64:
        absolutes = False

    #  use colormap if need be:
    if num_to_plot > 7:
        if not was_series:
            if 'kind' in kwargs:
                if kwargs['kind'] in ['pie', 'line', 'area']:
                    if colours:
                        if not plotting_a_totals_column:
                            kwargs['colormap'] = colours
        #else:
            if colours:
                kwargs['colormap'] = colours

    if piemode:
        if num_to_plot > 7:
            kwargs['colormap'] = colours
        else:
            if num_to_plot > 7:
                kwargs['colormap'] = colours
        #else:
            #if len(dataframe.T.columns) < 8:
                #try:
                    #del kwargs['colormap']
                #except:
                    #pass
    
    # multicoloured bar charts
    if 'kind' in kwargs:
        if colours:
            if kwargs['kind'].startswith('bar'):
                if len(list(dataframe.columns)) == 1:
                    import numpy as np
                    the_range = np.linspace(0, 1, num_to_plot)
                    cmap = plt.get_cmap(colours)
                    kwargs['colors'] = [cmap(n) for n in the_range]

    # reversing legend option
    if reverse_legend is True:
        rev_leg = True
    elif reverse_legend is False:
        rev_leg = False


    # show legend or don't, guess whether to reverse based on kind
    if not 'legend' in locals():
        legend = True
    if 'kind' in kwargs:
        if kwargs['kind'] in ['bar', 'barh', 'area', 'line', 'pie']:
            if was_series:
                legend = False
            if kwargs['kind'] == 'pie':
                if pie_legend:
                    legend = True
                else:
                    legend = False
        if kwargs['kind'] in ['barh', 'area']:
            if reverse_legend == 'guess':
                rev_leg = True
    if not 'rev_leg' in locals():
        rev_leg = False

    # the default legend placement
    if legend_pos is True:
        legend_pos = 'best'

    # cut dataframe if just_totals
    try:
        tst = dataframe['Combined total']
        dataframe = dataframe.head(num_to_plot)
    except:
        pass
    
    # rotate automatically
    if 'rot' not in kwargs:
        if not was_series:
            xvals = [str(i) for i in list(dataframe.index)[:num_to_plot]]
            #if 'kind' in kwargs:
                #if kwargs['kind'] in ['barh', 'area']:
                    #xvals = [str(i) for i in list(dataframe.columns)[:num_to_plot]]
        else:
            xvals = [str(i) for i in list(dataframe.index)[:num_to_plot]]
        if len(max(xvals, key=len)) > 6:
            kwargs['rot'] = 45

    # no title for subplots because ugly
    if sbplt:
        if 'title' in kwargs:
            del kwargs['title'] 
    else:
        kwargs['title'] = title
        
    # not using pandas for labels or legend anymore.
    #kwargs['labels'] = None
    #kwargs['legend'] = False

    # make legend
    if legend:
        # temporary, this makes legend in an acceptable spot at least
        if piemode:
            if sbplt:
                legend_pos = 'outside right'

        # kwarg optiosn go in leg_options
        leg_options = {'framealpha': .8}
        # determine legend position based on this dict
        if legend_pos:
            possible = {'best': 0, 'upper right': 1, 'upper left': 2, 'lower left': 3, 'lower right': 4, 
                        'right': 5, 'center left': 6, 'center right': 7, 'lower center': 8, 'upper center': 9, 
                        'center': 10, 'o r': 2, 'outside right': 2, 'outside upper right': 2, 
                        'outside center right': 'center left', 'outside lower right': 'lower left'}

            if type(legend_pos) == int:
                the_loc = legend_pos
            elif type(legend_pos) == str:
                try:
                    the_loc = possible[legend_pos]
                except KeyError:
                    raise KeyError('legend_pos value must be one of:\n%s\n or an int between 0-10.' %', '.join(possible.keys()))
            leg_options['loc'] = the_loc
            #weirdness needed for outside plot
            if legend_pos in ['o r', 'outside right', 'outside upper right']:
                leg_options['bbox_to_anchor'] = (1.02, 1)
            if legend_pos == 'outside center right':
                leg_options['bbox_to_anchor'] = (1.02, 0.5)
            if legend_pos == 'outside lower right':
                leg_options['bbox_to_anchor'] = (1.02, 0)
        
        # a bit of distance between legend and plot for outside legends
        if legend_pos.startswith('o'):
            leg_options['borderaxespad'] = 1

    if not piemode:
        if show_totals.endswith('both') or show_totals.endswith('legend'):
            dataframe = rename_data_with_total(dataframe, 
                                           was_series = was_series, 
                                           using_tex = using_tex, 
                                           absolutes = absolutes)
    else:
        if pie_legend:
            if show_totals.endswith('both') or show_totals.endswith('legend'):
                dataframe = rename_data_with_total(dataframe, 
                                           was_series = was_series, 
                                           using_tex = using_tex, 
                                           absolutes = absolutes)

    if piemode:
        if partial_pie:
            dataframe = dataframe / 100.0

    # some pie things
    if piemode:
        if not sbplt:
            kwargs['y'] = list(dataframe.columns)[0]
            if pie_legend:
                kwargs['labels'] = None
                if was_series:
                    leg_options['labels'] = list(dataframe.index)
                else:
                    leg_options['labels'] = list(dataframe.columns)
        else:
            if pie_legend:
                kwargs['labels'] = None
                if was_series:
                    leg_options['labels'] = list(dataframe.index)
                else:
                    leg_options['labels'] = list(dataframe.index)           

    if legend is False:
        kwargs['legend'] = False

    # cumulative grab first col
    if cumulative:
        kwargs['y'] = list(dataframe.columns)[0]

    # use styles and plot
    with plt.style.context((style)):

        if not sbplt:
            dataframe.plot(figsize = figsize, **kwargs)
        else:
            ax = dataframe.plot(figsize = figsize, **kwargs)
        if legend:
            if not rev_leg:
                lgd = plt.legend(**leg_options)
            else:
                handles, labels = plt.gca().get_legend_handles_labels()
                lgd = plt.legend(handles[::-1], labels[::-1], **leg_options)

        if not sbplt:
            if 'layout' not in kwargs:
                plt.tight_layout()


    if piemode:
        if not sbplt:
            plt.tight_layout()
            plt.axis('equal')

    # add x label  
    if x_label is not False:
        if type(x_label) == str:
            plt.xlabel(x_label)
        else:
            check_x_axis = list(dataframe.index)[0] # get first entry# get second entry of first entry (year, count)
            try:
                check_x_axis = int(check_x_axis)
                if 1500 < check_x_axis < 2050:
                    x_label = 'Year'
                else:
                    x_label = 'Group'
            except:
                x_label = 'Group'

        if not sbplt:
            if not piemode:
                plt.xlabel(x_label)

    # no weird scalar results:
    plt.ticklabel_format(useOffset = False)

    y_l = False
    if not absolutes:
        y_l = 'Percentage'
    else:
        y_l = 'Absolute frequency'
    
    if y_label is not False:
        if not sbplt:
            if not piemode:
                if type(y_label) == str:
                    plt.ylabel(y_label)
                else:
                    plt.ylabel(y_l)

    # hacky: turn legend into subplot titles :)
    if sbplt:
        # title the big plot
        #plt.suptitle(title, fontsize = 16)
        # get all axes
        if 'layout' not in kwargs:
            axes = [l for index, l in enumerate(ax)]
        else:
            axes = []
            cols = [l for index, l in enumerate(ax)]
            for col in cols:
                for bit in col:
                    axes.append(bit)
    
        # set subplot titles
    
        for index, a in enumerate(axes):
            try:
                titletext = list(dataframe.columns)[index]
            except:
                pass
            a.set_title(titletext)
            # remove axis labels for pie plots
            if piemode:
                a.axes.get_xaxis().set_visible(False)
                a.axes.get_yaxis().set_visible(False)
                a.axis('equal')

    
    # add sums to bar graphs and pie graphs
    # doubled right now, no matter
    if was_series:
        the_y_limit = plt.ylim()[1]
        if show_totals.endswith('plot') or show_totals.endswith('both'):
            for i, label in enumerate(list(dataframe.index)):
                if len(dataframe.ix[label]) == 1:
                    score = dataframe.ix[label][0]
                else:
                    if absolutes:
                        score = dataframe.ix[label].sum()
                    else:
                        #import warnings
                        #warnings.warn("It's not possible to determine total percentage from individual percentages.")
                        continue
                if not absolutes:
                    plt.annotate('%.2f' % score, (i - (num_to_plot / 100.0), score + (the_y_limit / 100)))
                else:
                    plt.annotate(score, (i - (num_to_plot / 100.0), score + (the_y_limit / 100)))
    else:
        the_y_limit = plt.ylim()[1]
        if show_totals.endswith('plot') or show_totals.endswith('both'):
            for i, label in enumerate(list(dataframe.columns)):
                if len(dataframe[label]) == 1:
                    score = dataframe[label][0]
                else:
                    if absolutes:
                        score = dataframe[label].sum()
                    else:
                        #import warnings
                        #warnings.warn("It's not possible to determine total percentage from individual percentages.")
                        continue
                if not absolutes:
                    plt.annotate('%.2f' % score, (i - (num_to_plot / 100.0), score + (the_y_limit / 100)))
                else:
                    plt.annotate(score, (i - (num_to_plot / 100.0), score + (the_y_limit / 100)))        

    #if not have_python_tex:
        #plt.gcf().show()

    plt.subplots_adjust(left=0.1)
    if 'layout' not in kwargs:
        plt.tight_layout()

    if save:
        import os
        if have_python_tex:
            imagefolder = '../images'
        else:
            imagefolder = 'images'

        savename = get_savename(imagefolder, save = save, title = title, ext = output_format)

        if not os.path.isdir(imagefolder):
            os.makedirs(imagefolder)

        # save image and get on with our lives
        if legend_pos.startswith('o'):
            plt.gcf().savefig(savename, dpi=150, transparent=transparent, bbox_extra_artists=(lgd,), bbox_inches='tight', format = output_format)
        else:
            plt.gcf().savefig(savename, dpi=150, transparent=transparent, format = output_format)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print '\n' + time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)
