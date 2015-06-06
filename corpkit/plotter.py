
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
            **kwargs):
    """plot interrogator() or editor() output.

    **kwargs are for pandas first, which can then send them through to matplotlib.plot():

    http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.plot.html
    http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot

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

  # pie chart requires subplots
    piemode = False
    if 'kind' in kwargs:
        if kwargs['kind'] == 'pie':
            piemode = True
            sbplt = True

    kwargs['subplots'] = sbplt
    # copy data, make series into df
    dataframe = df.copy()
    was_series = False
    if type(dataframe) == pandas.core.series.Series:
        was_series = True
        dataframe = DataFrame(dataframe)
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
    
    if cumulative:
        dataframe = DataFrame(dataframe.cumsum())

    if num_to_plot == 'all':
        if was_series:
            num_to_plot = len(dataframe)
        else:
            num_to_plot = len(list(dataframe.columns))

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
    
    #rotate automatically
    #if len(max(list(dataframe.columns), key=len)) > 6:
        #kwargs['rot'] = 45

    # no title for subplots because ugly
    if sbplt and not piemode:
        title_to_show = ''
        figsize = (figsize[0], figsize[1] * 2.5)
    else:
        title_to_show = title
    if piemode:
        title_to_show = ''
        figsize = (figsize[0], figsize[0])
        legend = False

    # this gets tid of the y_label thing showing up for pie mode...
    if piemode:
        if len(dataframe.columns) == 1:
            dataframe.columns = ['']

    if legend is False:
        kwargs['legend'] = False

    # use styles and plot
    with plt.style.context((style)):
        a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title_to_show, figsize = figsize, **kwargs)
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
            plt.xlabel(x_label)

    # make and set y label
    if y_label is False:
        try:
            if type(dataframe[list(dataframe.columns)[0]][list(dataframe.index)[0]]) == numpy.float64:
                y_label = 'Percentage'
            else:
                y_label = 'Absolute frequency'
        except:
            if type(dataframe['Total'][list(dataframe.index)[0]]) == numpy.float64:
                y_label = 'Percentage'
            else:
                y_label = 'Absolute frequency'
    
    if y_label is not None:
        if not sbplt:
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

        with plt.style.context((style)):
            ax = plt.subplot(111)
            box = ax.get_position()
            #ax.set_position([box.x0, box.y0, box.width, box.height])

            # Put a legend to the right of the current axis
            if not rev_leg:
                ax.legend(**leg_options)
            else:
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles[::-1], labels[::-1], **leg_options)










    # make room at the bottom for label?
    plt.subplots_adjust(bottom=0.20)

    # make figure
    if not sbplt:
        fig1 = a_plot.get_figure()
        if not have_python_tex:
            fig1.show()
    else:
        if not have_python_tex:
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
            fig1.savefig(savename, dpi=150, transparent=True)
        else:
            plt.savefig(savename, dpi=150, transparent=True)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print '\n' + time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)
