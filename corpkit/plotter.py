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
            interactive = False,
            black_and_white = False,
            show_p_val = False,
            indices = 'guess',
            **kwargs):
    """plot interrogator() or editor() output.

    **kwargs are for pandas first, which can then send them through to matplotlib.plot():

    http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.plot.html
    http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot

    pie_legend: False to label slices rather than give legend
    show_totals: where to show percent/abs frequencies: False, 'plot', 'legend', or 'both'

    """

    import corpkit
    import os
    import matplotlib as mpl
    if interactive:
        import matplotlib.pyplot as plt, mpld3
    else:
        import matplotlib.pyplot as plt
    from matplotlib import rc
    import pandas
    import pandas as pd
    from pandas import DataFrame

    import numpy
    from time import localtime, strftime
    from corpkit.tests import check_pytex, check_spider, check_t_kinter

    if interactive:
        import mpld3
        import collections
        from mpld3 import plugins, utils
        from plugins import InteractiveLegendPlugin, HighlightLines

    tk = check_t_kinter()

    running_python_tex = check_pytex()
    # incorrect spelling of spider on purpose
    running_spider = check_spider()

    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
        """remove extreme values from colourmap --- no pure white"""
        import matplotlib.colors as colors
        import numpy as np
        new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
        return new_cmap

    def get_savename(imagefolder, save = False, title = False, ext = 'png'):
        """Come up with the savename for the image."""
        import os

        def urlify(s):
            "Turn title into filename"
            import re
            s = s.lower()
            s = re.sub(r"[^\w\s-]", '', s)
            s = re.sub(r"\s+", '-', s)
            s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
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

        # remove duplicated ext
        if savename.endswith('%s%s' % (ext, ext)):
            savename = savename.replace('%s%s' % (ext, ext), ext, 1)
        return savename

    def rename_data_with_total(dataframe, was_series = False, using_tex = False, absolutes = True):
        """adds totals (abs, rel, keyness) to entry name strings"""
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
    sbplt = False
    if 'subplots' in kwargs:
        if kwargs['subplots'] is True:
            sbplt = True

    if colours is True:
        colours = 'Paired'

    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight']
    if style not in styles:
        raise ValueError('Style %s not found. Use %s' % (style, ', '.join(styles)))

    if 'savepath' in kwargs.keys():
        mpl.rcParams['savefig.directory'] = kwargs['savepath']
        del kwargs['savepath']

    mpl.rcParams['savefig.bbox'] = 'tight'

    # try to use tex
    # TO DO:
    # make some font kwargs here
    using_tex = False
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['text.latex.unicode'] = True
    
    if tex == 'try' or tex is True:
        try:
            rc('text', usetex=True)
            rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
            using_tex = True
        except:
            matplotlib.rc('font', family='sans-serif') 
            matplotlib.rc('font', serif='Helvetica Neue') 
            matplotlib.rc('text', usetex='false') 
            rc('text', usetex=False)
    else:
        rc('text', usetex=False)  

    if interactive:
        using_tex = False 

    if show_totals is False:
        show_totals = 'none'

    # find out what kind of plot we're making, and enable
    # or disable interactive values if need be
    if 'kind' not in kwargs:
        kwargs['kind'] = 'line'

    if interactive:
        if kwargs['kind'].startswith('bar'):
            interactive_types = [3]
        elif kwargs['kind'] == 'area':
            interactive_types = [2, 3]
        elif kwargs['kind'] == 'line':
            interactive_types = [2, 3]
        elif kwargs['kind'] == 'pie':
            interactive_types = None
            warnings.warn('Interactive plotting not yet available for pie plots.')
        else:
            interactive_types = [None]
    if interactive is False:
        interactive_types = [None]

    # find out if pie mode, add autopct format
    piemode = False
    if 'kind' in kwargs:
        if kwargs['kind'] == 'pie':
            piemode = True
            # always the best spot for pie
            #if legend_pos == 'best':
                #legend_pos = 'lower left'
            if show_totals.endswith('plot') or show_totals.endswith('both'):
                kwargs['pctdistance'] = 0.6
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
        if len(list(dataframe.columns)) == 1:
            was_series = True
    
    # attempt to convert x axis to ints:
    try:
        dataframe.index = [int(i) for i in list(dataframe.index)]
    except:
        pass

    # remove totals and tkinter order
    if not was_series:
        for name, ax in zip(['Total'] * 2 + ['tkintertable-order'] * 2, [0, 1, 0, 1]):
            dataframe = dataframe.drop(name, axis = ax, errors = 'ignore')
    else:
        dataframe = dataframe.drop('tkintertable-order', errors = 'ignore')
        dataframe = dataframe.drop('tkintertable-order', axis = 1, errors = 'ignore')
            
    # look at columns to see if all can be ints, in which case, set up figure
    # for depnumming
    if not was_series:
        if indices == 'guess':
            def isint(x):
                try:
                    a = float(x)
                    b = int(a)
                except ValueError or OverflowError:
                    return False
                else:
                    return a == b

            if all([isint(x) is True for x in list(dataframe.columns)]):
                indices = True
            else:
                indices = False

        # if depnumming, plot all, transpose, and rename axes
        if indices is True:
            num_to_plot = 'all'
            dataframe = dataframe.T
            if y_label is None:
                y_label = 'Percentage of all matches'
            if x_label is None:
                x_label = ''

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
            if not sbplt:
                kwargs['explode'] = auto_explode(dataframe, 
                                             kwargs['explode'], 
                                             was_series = was_series, 
                                             num_to_plot = num_to_plot)

    if 'legend' in kwargs:
        legend = kwargs['legend']
    else:
        legend = True

    #cut data short
    plotting_a_totals_column = False
    if was_series:
        if list(dataframe.columns)[0] != 'Total':
            try:
                can_be_ints = [int(x) for x in list(dataframe.index)]
                num_to_plot = len(dataframe)
            except:
                dataframe = dataframe[:num_to_plot]
        elif list(dataframe.columns)[0] == 'Total':
            plotting_a_totals_column = True
            if not 'legend' in kwargs:
                legend = False
            num_to_plot = len(dataframe)
    else:
        dataframe = dataframe.T.head(num_to_plot).T

    # remove stats fields, put p in entry text, etc.
    statfields = ['slope', 'intercept', 'r', 'p', 'stderr']
    try:
        dataframe = dataframe.drop(statfields, axis = 1)
    except:
        pass    
    try:
        dataframe.ix['p']
        there_are_p_vals = True
    except:
        there_are_p_vals = False
    if show_p_val:
        if there_are_p_vals:
            newnames = []
            for col in list(dataframe.columns):
                pval = dataframe[col]['p']
                newname = '%s (p=%s)' % (col, format(pval, '.5f'))
                newnames.append(newname)
            dataframe.columns = newnames
            dataframe.drop(statfields, axis = 0, inplace = True)
        else:
            warnings.warn('No p-values calculated to show.\n\nUse sort_by and keep_stats in editor() to generate these values.')
    else:
        if there_are_p_vals:
            dataframe.drop(statfields, axis = 0, inplace = True)

    # make and set y label
    absolutes = True
    if type(dataframe) == pandas.core.frame.DataFrame:
        try:
            if not all([s.is_integer() for s in dataframe.iloc[0,:].values]):
                absolutes = False
        except:
            pass
    else:
        if not all([s.is_integer() for s in dataframe.values]):        
            absolutes = False

    #  use colormap if need be:
    if num_to_plot > 0:
        if not was_series:
            if 'kind' in kwargs:
                if kwargs['kind'] in ['pie', 'line', 'area']:
                    if colours:
                        if not plotting_a_totals_column:
                            if colours == 'Default':
                                colours = 'Paired'
                            kwargs['colormap'] = colours
        #else:
            if colours:
                if colours == 'Default':
                    colours = 'Paired'
                kwargs['colormap'] = colours

    if piemode:
        if num_to_plot > 0:
            if colours == 'Default':
                colours = 'Paired'
            kwargs['colormap'] = colours
        else:
            if num_to_plot > 0:
                if colours == 'Default':
                    colours = 'Paired'
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
                    if not black_and_white:
                        import numpy as np
                        the_range = np.linspace(0, 1, num_to_plot)
                        cmap = plt.get_cmap(colours)
                        kwargs['colors'] = [cmap(n) for n in the_range]
                    # make a bar width ... ?
                    #kwargs['width'] = (figsize[0] / float(num_to_plot)) / 1.5


    # reversing legend option
    if reverse_legend is True:
        rev_leg = True
    elif reverse_legend is False:
        rev_leg = False

    # show legend or don't, guess whether to reverse based on kind
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
            xvals = [str(i) for i in list(dataframe.columns)[:num_to_plot]]
        if len(max(xvals, key=len)) > 6:
            if not piemode:
                kwargs['rot'] = 45

    # no title for subplots because ugly,
    if sbplt:
        if 'title' in kwargs:
            del kwargs['title'] 
    else:
        kwargs['title'] = title
        
    # no interactive subplots yet:


    if sbplt and interactive:
        import warnings
        interactive = False
        warnings.warn('No interactive subplots yet, sorry.')
        return
        
    # not using pandas for labels or legend anymore.
    #kwargs['labels'] = None
    #kwargs['legend'] = False

    if legend:
        # kwarg options go in leg_options
        leg_options = {'framealpha': .8}
        if 'shadow' in kwargs:
            leg_options['shadow'] = True
        if 'ncol' in kwargs:
            leg_options['ncol'] = kwargs['ncol']
            del kwargs['ncol']
        else:
            if num_to_plot > 6:
                leg_options['ncol'] = num_to_plot / 7

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
                leg_options['loc'] == 'upper right'
                leg_options['bbox_to_anchor'] = (0.5, 0.5)
        
        # a bit of distance between legend and plot for outside legends
        if type(legend_pos) == str:
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
                kwargs['legend'] = False
                if was_series:
                    leg_options['labels'] = list(dataframe.index)
                else:
                    leg_options['labels'] = list(dataframe.columns)
        else:
            if pie_legend:
                kwargs['legend'] = False
                if was_series:
                    leg_options['labels'] = list(dataframe.index)
                else:
                    leg_options['labels'] = list(dataframe.index)   
    
    areamode = False
    if 'kind' in kwargs:
        if kwargs['kind'] == 'area':
            areamode = True        

    if legend is False:
        kwargs['legend'] = False

    # cumulative grab first col
    if cumulative:
        kwargs['y'] = list(dataframe.columns)[0]

    # line highlighting option for interactive!
    if interactive:
        if 2 in interactive_types:
            if kwargs['kind'] == 'line':
                kwargs['marker'] = ','
        if not piemode:
            kwargs['alpha'] = 0.1
    
    # convert dates --- works only in my current case!
    if plotting_a_totals_column or not was_series:
        try:
            can_it_be_int = int(list(dataframe.index)[0])
            can_be_int = True
        except:
            can_be_int = False
        if can_be_int:
            if 1500 < int(list(dataframe.index)[0]):
                if 2050 > int(list(dataframe.index)[0]):
                    n = pd.PeriodIndex([d for d in list(dataframe.index)], freq='A')
                    dataframe = dataframe.set_index(n)

    MARKERSIZE = 4
    COLORMAP = {
            0: {'marker': None, 'dash': (None,None)},
            1: {'marker': None, 'dash': [5,5]},
            2: {'marker': "o", 'dash': (None,None)},
            3: {'marker': None, 'dash': [1,3]},
            4: {'marker': "s", 'dash': [5,2,5,2,5,10]},
            5: {'marker': None, 'dash': [5,3,1,2,1,10]},
            6: {'marker': 'o', 'dash': (None,None)},
            7: {'marker': None, 'dash': [5,3,1,3]},
            8: {'marker': "1", 'dash': [1,3]},
            9: {'marker': "*", 'dash': [5,5]},
            10: {'marker': "2", 'dash': [5,2,5,2,5,10]},
            11: {'marker': "s", 'dash': (None,None)}
            }

    HATCHES = {
            0:  {'color': '#dfdfdf', 'hatch':"/"},
            1:  {'color': '#6f6f6f', 'hatch':"\\"},
            2:  {'color': 'b', 'hatch':"|"},
            3:  {'color': '#dfdfdf', 'hatch':"-"},
            4:  {'color': '#6f6f6f', 'hatch':"+"},
            5:  {'color': 'b', 'hatch':"x"}
            }

    if black_and_white:
        if kwargs['kind'] == 'line':
            kwargs['linewidth'] = 1

        cmap = plt.get_cmap('Greys')
        new_cmap = truncate_colormap(cmap, 0.25, 0.95)
        if kwargs['kind'] == 'bar':
            # darker if just one entry
            if len(dataframe.columns) == 1:
                new_cmap = truncate_colormap(cmap, 0.70, 0.90)
        kwargs['colormap'] = new_cmap

    # use styles and plot

    with plt.style.context((style)):

        if not sbplt:
            # check if negative values, no stacked if so
            if areamode:
                if dataframe.applymap(lambda x: x < 0.0).any().any():
                    kwargs['stacked'] = False
                    rev_leg = False
            ax = dataframe.plot(figsize = figsize, **kwargs)
        else:
            if not piemode and not sbplt:
                ax = dataframe.plot(figsize = figsize, **kwargs)
            else:
                ax = dataframe.plot(figsize = figsize, **kwargs)
                handles, labels = plt.gca().get_legend_handles_labels()
                plt.legend( handles, labels, loc = leg_options['loc'], bbox_to_anchor = (0,-0.1,1,1),
                bbox_transform = plt.gcf().transFigure )
                if not tk:
                    plt.show()
                    return
        if 'rot' in kwargs:
            if kwargs['rot'] != 0 and kwargs['rot'] != 90:
                labels = [item.get_text() for item in ax.get_xticklabels()]
                ax.set_xticklabels(labels, rotation = kwargs['rot'], ha='right')

        if transparent:
            plt.gcf().patch.set_facecolor('white')
            plt.gcf().patch.set_alpha(0)

        if black_and_white:
            #plt.grid()
            plt.gca().set_axis_bgcolor('w')
            if kwargs['kind'] == 'line':
                # white background

                # change everything to black and white with interesting dashes and markers
                c = 0
                for line in ax.get_lines():
                    line.set_color('black')
                    #line.set_width(1)
                    line.set_dashes(COLORMAP[c]['dash'])
                    line.set_marker(COLORMAP[c]['marker'])
                    line.set_markersize(MARKERSIZE)
                    c += 1
                    if c == len(COLORMAP.keys()):
                        c = 0

        if legend:
            if not piemode and not sbplt:
                if 3 not in interactive_types:
                    if not rev_leg:
                        lgd = plt.legend(**leg_options)
                    else:
                        handles, labels = plt.gca().get_legend_handles_labels()
                        lgd = plt.legend(handles[::-1], labels[::-1], **leg_options)

            #if black_and_white:
                #lgd.set_facecolor('w')

        #if interactive:
            #if legend:
                #lgd.set_title("")
        #if not sbplt:
            #if 'layout' not in kwargs:
                #plt.tight_layout()

    if interactive:
        # 1 = highlight lines
        # 2 = line labels
        # 3 = legend switches
        ax = plt.gca()
        # fails for piemode
        lines = ax.lines
        handles, labels = plt.gca().get_legend_handles_labels()
        if 1 in interactive_types:
            plugins.connect(plt.gcf(), HighlightLines(lines))

        if 3 in interactive_types:
            plugins.connect(plt.gcf(), InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0))

        for i, l in enumerate(lines):
            y_vals = l.get_ydata()
            x_vals = l.get_xdata()
            x_vals = [str(x) for x in x_vals]
            if absolutes:
                ls = ['%s (%s: %d)' % (labels[i], x_val, y_val) for x_val, y_val in zip(x_vals, y_vals)]
            else:
                ls = ['%s (%s: %.2f%%)' % (labels[i], x_val, y_val) for x_val, y_val in zip(x_vals, y_vals)]
            if 2 in interactive_types:
                #if 'kind' in kwargs and kwargs['kind'] == 'area':
                tooltip_line = mpld3.plugins.LineLabelTooltip(lines[i], labels[i])
                mpld3.plugins.connect(plt.gcf(), tooltip_line)
                #else:
                if kwargs['kind'] == 'line':
                    tooltip_point = mpld3.plugins.PointLabelTooltip(l, labels = ls)
                    mpld3.plugins.connect(plt.gcf(), tooltip_point)
        
            # works:
            #plugins.connect(plt.gcf(), plugins.LineLabelTooltip(l, labels[i]))


        #labels = ["Point {0}".format(i) for i in range(num_to_plot)]
        #tooltip = plugins.LineLabelTooltip(lines)
        #mpld3.plugins.connect(plt.gcf(), mpld3.plugins.PointLabelTooltip(lines))

    if piemode:
        if not sbplt:
            plt.axis('equal')
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)


    # add x label
    # this could be revised now!
    # if time series period, it's year for now
    if type(dataframe.index) == pandas.tseries.period.PeriodIndex:
        x_label = 'Year'

    if x_label is not False:
        if type(x_label) == str:
            plt.xlabel(x_label)
        else:
            check_x_axis = list(dataframe.index)[0] # get first entry# get second entry of first entry (year, count)
            try:
                if type(dataframe.index) == pandas.tseries.period.PeriodIndex:
                    x_label = 'Year'
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

    # no offsets for numerical x and y values
    if type(dataframe.index) != pandas.tseries.period.PeriodIndex:
        try:
            # check if x axis can be an int
            check_x_axis = list(dataframe.index)[0]
            can_it_be_int = int(check_x_axis)
            # if so, set these things
            from matplotlib.ticker import ScalarFormatter
            plt.gca().xaxis.set_major_formatter(ScalarFormatter()) 
        except:
            pass

    # same for y axis
    try:
        # check if x axis can be an int
        check_y_axis = list(dataframe.columns)[0]
        can_it_be_int = int(check_y_axis)
        # if so, set these things
        from matplotlib.ticker import ScalarFormatter
        plt.gca().yaxis.set_major_formatter(ScalarFormatter()) 
    except:
        pass

    # y labelling
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
            try:
                a.legend_.remove()
            except:
                pass
            # remove axis labels for pie plots
            if piemode:
                a.axes.get_xaxis().set_visible(False)
                a.axes.get_yaxis().set_visible(False)
                a.axis('equal')
    
    # add sums to bar graphs and pie graphs
    # doubled right now, no matter

    if not sbplt:
        if 'kind' in kwargs:
            if kwargs['kind'].startswith('bar'):
                width = ax.containers[0][0].get_width()

    if was_series:
        the_y_limit = plt.ylim()[1]
        if show_totals.endswith('plot') or show_totals.endswith('both'):
            # make plot a bit higher if putting these totals on it
            plt.ylim([0,the_y_limit * 1.05])
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
                    plt.annotate('%.2f' % score, (i, score), ha = 'center', va = 'bottom')
                else:
                    plt.annotate(score, (i, score), ha = 'center', va = 'bottom')
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
                    plt.annotate('%.2f' % score, (i, score), ha = 'center', va = 'bottom')
                else:
                    plt.annotate(score, (i, score), ha = 'center', va = 'bottom')        

    #if not running_python_tex:
        #plt.gcf().show()

    plt.subplots_adjust(left=0.1)
    plt.subplots_adjust(bottom=0.18)
    #if 'layout' not in kwargs:
        #plt.tight_layout()



    if save:
        import os
        if running_python_tex:
            imagefolder = '../images'
        else:
            imagefolder = 'images'

        savename = get_savename(imagefolder, save = save, title = title, ext = output_format)

        if not os.path.isdir(imagefolder):
            os.makedirs(imagefolder)

        # save image and get on with our lives
        if legend_pos.startswith('o'):
            plt.gcf().savefig(savename, dpi=150, bbox_extra_artists=(lgd,), bbox_inches='tight', format = output_format)
        else:
            plt.gcf().savefig(savename, dpi=150, format = output_format)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print '\n' + time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)

    if not interactive and not running_python_tex and not running_spider and not tk:
        plt.show()
        return
    if running_spider or tk or sbplt:
        return plt

    if interactive:
        plt.subplots_adjust(right=.8)
        plt.subplots_adjust(left=.1)
        try:
            ax.legend_.remove()
        except:
            pass
        return mpld3.display()



