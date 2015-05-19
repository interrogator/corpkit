
def plotter(dataframe,
            title = False,
            x_label = False,
            y_label = False,
            style = 'ggplot',
            figsize = (10, 4),
            save = False,
            legend = 'default',
            returns = False,
            num_to_plot = 7,
            subplots = False,
            **kwargs):
    """plot interrogator() or editor() output."""

    import os
    import matplotlib.pyplot as plt
    import pandas as pd
    from pandas import DataFrame
    import numpy
    from time import localtime, strftime
    from corpkit.query import check_pytex

    have_python_tex = check_pytex()

    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight']
    if style not in styles:
        raise ValueError('Style %s not found. Use %s' % (style, ', '.join(styles)))


    
    #plt.figure()
    if num_to_plot == 'all':
        num_to_plot = len(list(dataframe.columns))

    with plt.style.context((style)):
        a_plot = DataFrame(dataframe[list(dataframe.columns)[:num_to_plot]]).plot(title = title, figsize = figsize, subplots = subplots, **kwargs)

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
        plt.xlabel(x_label)

    # make and set y label
    if y_label is False:
        if type(dataframe[list(dataframe.columns)[0]][0]) == numpy.float64:
            y_label = 'Percentage'
        else:
            y_label = 'Absolute frequency'
    if y_label is not None:
        plt.ylabel(y_label)
    
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