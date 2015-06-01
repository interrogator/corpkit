
def plotter(title,
            df,
            x_label = False,
            y_label = False,
            style = 'ggplot',
            figsize = (13, 6),
            save = False,
            legend = 'best',
            num_to_plot = 7,
            tex = 'try',
            subplots = False,
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

    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight', 'matplotlib']
    if style not in styles:
        raise ValueError('Style %s not found. Use %s' % (style, ', '.join(styles)))


    if tex == 'try' or tex is True:
        try:
            rc('text', usetex=True)
            rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
        except:
            rc('text', usetex=False)
    else:
        rc('text', usetex=False)   

    dataframe = df.copy()

    if type(dataframe) == pandas.core.series.Series:
        dataframe = DataFrame(dataframe)

    # attempt to convert x axis to ints:
    try:
        dataframe.index = [int(i) for i in list(dataframe.index)]
    except:
        pass

    try:
        dataframe = dataframe.drop('Total', axis = 0)
    except:
        pass
    #try:
        #dataframe = dataframe.drop('Total', axis = 1)
    #except:
        #pass
    #plt.figure()
    if num_to_plot == 'all':
        num_to_plot = len(list(dataframe.columns))
    
    # no title for subplots because ugly
    if subplots:
        title_to_show = ''
        figsize = (figsize[0], figsize[1] * 2.5)
    else:
        title_to_show = title

    if style != 'matplotlib' and style is not False:
        with plt.style.context((style)):

            if type(legend) == bool:
                a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title_to_show, figsize = figsize, subplots = subplots, legend = legend, **kwargs)
            else:
                a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title_to_show, figsize = figsize, subplots = subplots, **kwargs)
    else:    
        if type(legend) == bool:
            a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title_to_show, figsize = figsize, subplots = subplots, legend = legend, **kwargs)
        else:
            a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title_to_show, figsize = figsize, subplots = subplots, **kwargs)

    # make and set x label:
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
        if not subplots:
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
        if not subplots:
            plt.ylabel(y_label)

    # hacky: turn legend into subplot titles :)
    if subplots:
        for index, f in enumerate(a_plot):
            titletext = list(dataframe.columns)[index]
            f.legend_.remove()
            f.set_title(titletext)

    # legend values
    possible = {'best': 0, 'upper right': 1, 'upper left': 2, 'lower left': 3, 'lower right': 4, 
                'right': 5, 'center left': 6, 'center right': 7, 'lower center': 8, 
                'upper center': 9, 'center': 10}

    if not legend.startswith('outside'):
        
        if type(legend) == int:
            the_loc = legend
        elif type(legend) == str:
            try:
                the_loc = possible[legend]
            except KeyError:
                raise KeyError('legend value must be one of:\n%s\n or an int between 0-10.' %', '.join(possible.keys()))
        else:
            raise KeyError('legend value must be one of:\n%s' %', '.join(possible.keys()))
        plt.legend(loc=the_loc)
    if legend.startswith('outside'):
        os, plc = legend.split(' ', 1)
        try:
            if plc == 'upper right':
            #the_loc = possible[plc]
                plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=1)
            if plc == 'center right':
                plt.legend(bbox_to_anchor=(1, 0.5), loc='center left', borderaxespad=1)
            if plc == 'lower right':
                plt.legend(bbox_to_anchor=(1, 0), loc='lower left', borderaxespad=1)
            #if plc == 'upper left':
                #plt.legend(bbox_to_anchor=(1, 0), loc=1, borderaxespad=1)
        except KeyError:
            raise KeyError('legend value must be one of:\n%s\n or an int between 0-10.' %', '.join(possible.keys()))
    else:
        raise KeyError('legend value must be one of:\n%s' %', '.join(possible.keys()))        
        
    #if legend == 'upper center':
        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True)

    # make figure
    plt.subplots_adjust(bottom=0.20)
    if not subplots:
        fig1 = a_plot.get_figure()
        if not have_python_tex:
            fig1.show()
    else:
        if not have_python_tex:
            plt.show()

    if not save:
        return

    if save:
        if have_python_tex:
            imagefolder = '../images'
        else:
            imagefolder = 'images'

        savename = get_savename(imagefolder, save = save, title = title)

        if not os.path.isdir(imagefolder):
            os.makedirs(imagefolder)

        # save image and get on with our lives
        fig1.savefig(savename, dpi=150, transparent=True)
        time = strftime("%H:%M:%S", localtime())
        if os.path.isfile(savename):
            print '\n' + time + ": " + savename + " created."
        else:
            raise ValueError("Error making %s." % savename)


    def get_savename(imagefolder, save = False, title = False):
        """Come up with the savename for the image."""

        def urlify(s):
            "Turn title into filename"
            import re
            s = s.lower()
            s = re.sub(r"[^\w\s]", '', s)
            s = re.sub(r"\s+", '-', s)
            return s     

        # name as 
        if type(save) == str:
            savename = os.path.join(imagefolder, urlify(save) + '.png')
        else:
            if title:
                savename = os.path.join(imagefolder, urlify(title) + '.png')
            # generic sequential naming
            else:
                list_images = [i for i in sorted(os.listdir(imagefolder)) if i.startswith('image-')]
                if len(list_images) > 0:
                    num = int(list_images[-1].split('-')[1].split('.')[0]) + 1
                    autoname = 'image-' + str(num).zfill(3)
                    savename = os.path.join(imagefolder, autoname + '.png')
                else:
                    savename = os.path.join(imagefolder, 'image-001.png')
        if savename.endswith('.png.png'):
            savename = savename[:-4]
        return savename