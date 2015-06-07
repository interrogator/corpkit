
def plotter(title,
            df,
            x_label = False,
            y_label = False,
            style = 'ggplot',
            figsize = (13, 6),
            save = False,
            legend_pos = 'best',
            reverse_legend = 'guess',
            num_to_plot = 7,
            tex = 'try',
            colours = 'Paired',
            cumulative = False,
            pie_legend = True,
            show_total = 'plot',
            **kwargs):
    """plot interrogator() or editor() output.

    **kwargs are for pandas first, which can then send them through to matplotlib.plot():

    http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.plot.html
    http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot

    pie_legend: show legend for pie charts instead of ticks
    show_total: where to show percent: False, 'plot', 'legend', or 'both'

    """

    import os
    import matplotlib.pyplot as plt
    from matplotlib import rc
    import pandas
    import pandas as pd
    from pandas import DataFrame

    import numpy
    from time import localtime, strftime
    from corpkit.tests import check_pytex

    have_python_tex = check_pytex()

    def get_savename(imagefolder, save = False, title = False):
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
        if type(save) == str:
            savename = os.path.join(imagefolder, (urlify(save) + '.png'))
        #this 'else' is redundant now that title is obligatory
        else:
            if title:
                filename = urlify(title) + '.png'
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
        #if savename.endswith('.png.png'):
        #    savename = savename[:-4]
        return savename

    # are we doing subplots?
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


    if show_total is False:
        show_total = 'none'

    piemode = False
    if 'kind' in kwargs:
        if kwargs['kind'] == 'pie':
            piemode = True
            if show_total.endswith('plot') or show_total.endswith('both'):
                if using_tex:
                    kwargs['autopct'] = r'%1.1f\%%'
                else:
                    kwargs['autopct'] = '%1.1f%%'

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
    
    if num_to_plot == 'all':
        if was_series:
            num_to_plot = len(dataframe)
        else:
            num_to_plot = len(list(dataframe.columns))


    #if num_to_plot > len(list(dataframe.columns)):
        #num_to_plot = len(list(dataframe.columns))

    #  use colormap if need be:
    colormap = False
    if num_to_plot > 7:
        if 'kind' in kwargs:
            if kwargs['kind'] in ['pie', 'line', 'area']:
                if colours:
                    kwargs['colormap'] = colours
        else:
            if colours:
                kwargs['colormap'] = colours
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
    
    # rotate automatically?
    if 'rot' not in kwargs:
        if max(list(dataframe.columns)[:num_to_plot], key=len) > 6:
            kwargs['rot'] = 45

    # no title for subplots because ugly
    if sbplt:
        figsize = (figsize[0], figsize[1] * 2.5)
    else:
        kwargs['title'] = title
    
    # not using pandas for labels anymore.
    
    if piemode:
        if pie_legend:
            legend = True
            kwargs['labels'] = None
        else:
            legend = False            
        figsize = (figsize[0] * 1.5, figsize[1] * 1.5)

        # this gets tid of the y_label thing showing up for pie mode...
        if len(dataframe.columns) == 1:
            dataframe.columns = ['']

        if not sbplt:
            kwargs['y'] = list(dataframe.columns)[0]

    # no legend option
    if legend is False:
        kwargs['legend'] = False

    # cumulative grab first col
    if cumulative:
        kwargs['y'] = list(dataframe.columns)[0]

    # use styles and plot
    with plt.style.context((style)):

        a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(figsize = figsize, **kwargs)

        # this would limit percent charts y axis to 100 :)
        # if not absolutes:
        #     a_plot.set_ylim(0, 100)

        if piemode:
            a_plot.set_aspect('equal')
    if x_label is False:
        check_x_axis = list(dataframe.index)[0] # get first entry# get second entry of first entry (year, count)
        try:
            check_x_axis = int(check_x_axis)
            if 1500 < check_x_axis < 2050:
                x_label = 'Year'
            else:
                x_label = 'Group'
        except:
            x_label = 'Group'

    if x_label is not None:
        if not sbplt:
            if not piemode:
                plt.xlabel(x_label)

    # make and set y label
    absolutes = True
    if y_label is False:
        try:
            if type(dataframe[list(dataframe.columns)[0]][list(dataframe.index)[0]]) == numpy.float64:
                y_label = 'Percentage'
                absolutes = False
            else:
                y_label = 'Absolute frequency'
        except:
            if type(dataframe['Total'][list(dataframe.index)[0]]) == numpy.float64:
                y_label = 'Percentage'
                absolutes = False
            else:
                y_label = 'Absolute frequency'
    
    if y_label is not None:
        if not sbplt:
            if not piemode:
                plt.ylabel(y_label)

    # hacky: turn legend into subplot titles :)
    if sbplt:
        for index, f in enumerate(a_plot):
            titletext = list(dataframe.columns)[index]
            if not piemode:
                f.legend_.remove()        
            f.set_title(titletext)

    # MAKE LEGEND OPTIONS
    if legend:
        leg_options = {'framealpha': .8}
        if legend_pos:
            possible = {'best': 0,
                        'upper right': 1,
                        'upper left': 2,
                        'lower left': 3,
                        'lower right': 4,  
                        'right': 5,
                        'center left': 6,
                        'center right': 7,
                        'lower center': 8,
                        'upper center': 9,
                        'center': 10,
                        'o r': 2,
                        'outside right': 2,
                        'outside upper right': 2,
                        'outside center right': 'center left',
                        'outside lower right': 'lower left'}
            if type(legend_pos) == int:
                the_loc = legend_pos
            elif type(legend_pos) == str:
                try:
                    the_loc = possible[legend_pos]
                except KeyError:
                    raise KeyError('legend_pos value must be one of:\n%s\n or an int between 0-10.' %', '.join(possible.keys()))
            leg_options['loc'] = the_loc
            if legend_pos in ['o r', 'outside right', 'outside upper right']:
                leg_options['bbox_to_anchor'] = (1.02, 1)
            if legend_pos == 'outside center right':
                leg_options['bbox_to_anchor'] = (1.02, 0.5)
            if legend_pos == 'outside lower right':
                leg_options['bbox_to_anchor'] = (1.02, 0)
        if legend_pos.startswith('o'):
            leg_options['borderaxespad'] = 1

        if was_series:
            where_the_words_are = dataframe.index
        else:
            where_the_words_are = dataframe.columns

        if show_total.endswith('none') or show_total.endswith('plot'):
            the_labs = list(where_the_words_are)[:num_to_plot]
        else:
            the_labs = []
            for w in list(where_the_words_are)[:num_to_plot]:
                if not absolutes:
                    if was_series:
                        perc = dataframe.T[w][0]
                    else:
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

        leg_options['labels'] = the_labs

        with plt.style.context((style)):
            ax = plt.subplot(111)
            box = ax.get_position()
            #ax.set_position([box.x0, box.y0, box.width, box.height])

            # Put a legend to the right of the current axis
            if not rev_leg:
                lgd = ax.legend(**leg_options)
            else:
                handles, labels = ax.get_legend_handles_labels()
                lgd = ax.legend(handles[::-1], labels[::-1], **leg_options)

    if was_series:  
        if show_total.endswith('plot') or show_total.endswith('both'):
            for i, label in enumerate(list(dataframe.index)):
                if len(dataframe.ix[label]) == 1:
                    score = dataframe.ix[label][0]
                else:
                    if absolutes:
                        score = dataframe.ix[label].sum()
                    else:
                        raise ValueError("It's not possible to determine total percentage from individual percentages.")
                if not absolutes:
                    a_plot.annotate('%.2f' % score, (i - (num_to_plot / 60.0), score + 0.2))
                else:
                    a_plot.annotate(score, (i - (num_to_plot / 60.0), score + 0.2))
    else:
        if show_total.endswith('plot') or show_total.endswith('both'):
            for i, label in enumerate(list(dataframe.columns)):
                if len(dataframe[label]) == 1:
                    score = dataframe[label][0]
                else:
                    if absolutes:
                        score = dataframe[label].sum()
                    else:
                        raise ValueError("It's not possible to determine total percentage from individual percentages.")
                if not absolutes:
                    a_plot.annotate('%.2f' % score, (i - (num_to_plot / 60.0), score + 0.2))
                else:
                    a_plot.annotate(score, (i - (num_to_plot / 60.0), score + 0.2))        


    # make room at the bottom for label?
    plt.subplots_adjust(bottom=0.20)

    # make figure
    if not sbplt:
        fig1 = a_plot.get_figure()
        if not have_python_tex:
            fig1.show()
    else:
        if not have_python_tex:
            if piemode:
                plt.axis('equal')
            plt.show()

    if not save:
        return

    if save:
        import os
        if have_python_tex:
            imagefolder = '../images'
        else:
            imagefolder = 'images'

        savename = get_savename(imagefolder, save = save, title = title)

        if not os.path.isdir(imagefolder):
            os.makedirs(imagefolder)

        # save image and get on with our lives
        if not sbplt:
            if legend_pos.startswith('o'):
                fig1.savefig(savename, dpi=150, transparent=False, bbox_extra_artists=(lgd,), bbox_inches='tight')
            else:
                fig1.savefig(savename, dpi=150, transparent=False)
        else:
            if legend_pos.startswith('o'):
                plt.savefig(savename, dpi=150, transparent=False, bbox_extra_artists=(lgd,), bbox_inches='tight')
            else:
                plt.savefig(savename, dpi=150, transparent=False)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print '\n' + time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)
