#interactive??


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
    import matplotlib.pyplot as plt, mpld3
    from matplotlib import rc
    import pandas
    import pandas as pd
    from pandas import DataFrame

    import numpy
    from time import localtime, strftime
    from corpkit.tests import check_pytex
    import signal

    if interactive:
        import collections
        from mpld3 import plugins, utils

        class HighlightLines(plugins.PluginBase):
            """A plugin to highlight lines on hover"""

            JAVASCRIPT = """
            mpld3.register_plugin("linehighlight", LineHighlightPlugin);
            LineHighlightPlugin.prototype = Object.create(mpld3.Plugin.prototype);
            LineHighlightPlugin.prototype.constructor = LineHighlightPlugin;
            LineHighlightPlugin.prototype.requiredProps = ["line_ids"];
            LineHighlightPlugin.prototype.defaultProps = {alpha_bg:0.0, alpha_fg:1.0}
            function LineHighlightPlugin(fig, props){
                mpld3.Plugin.call(this, fig, props);
            };

            LineHighlightPlugin.prototype.draw = function(){
              for(var i=0; i<this.props.line_ids.length; i++){
                 var obj = mpld3.get_element(this.props.line_ids[i], this.fig),
                     alpha_fg = this.props.alpha_fg;
                     alpha_bg = this.props.alpha_bg;
                 obj.elements()
                     .on("mouseover.highlight", function(d, i){
                                    d3.select(this).transition().duration(50)
                                      .style("stroke-opacity", alpha_fg); })
                     .on("mouseout.highlight", function(d, i){
                                    d3.select(this).transition().duration(200)
                                      .style("stroke-opacity", alpha_bg); });
              }
            };
            """

            def __init__(self, lines):
                self.lines = lines
                self.dict_ = {"type": "linehighlight",
                              "line_ids": [utils.get_id(line) for line in lines],
                              "alpha_bg": lines[0].get_alpha(),
                              "alpha_fg": 1.0}


        class InteractiveLegendPlugin(plugins.PluginBase):
            """A plugin for an interactive legends. 
            
            Inspired by http://bl.ocks.org/simzou/6439398
            
            Parameters
            ----------
            plot_elements : iterable of matplotliblib elements
                the elements to associate with a given legend items
            labels : iterable of strings
                The labels for each legend element
            css : str, optional
                css to be included, for styling if desired
            ax :  matplotlib axes instance, optional
                the ax to which the legend belongs. Default is the first
                axes
            alpha_sel : float, optional
                the alpha value to apply to the plot_element(s) associated 
                with the legend item when the legend item is selected. 
                Default is 1.0
            alpha_unsel : float, optional
                the alpha value to apply to the plot_element(s) associated 
                with the legend item when the legend item is unselected. 
                Default is 0.2
                
            Examples
            --------
            
            """
            
            JAVASCRIPT = """
            mpld3.register_plugin("interactive_legend", InteractiveLegend);
            InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
            InteractiveLegend.prototype.constructor = InteractiveLegend;
            InteractiveLegend.prototype.requiredProps = ["element_ids", "labels"];
            InteractiveLegend.prototype.defaultProps = {"ax":null, 
                                                        "alpha_sel":1.0,
                                                        "alpha_unsel":0}
            function InteractiveLegend(fig, props){
                mpld3.Plugin.call(this, fig, props);
            };

            InteractiveLegend.prototype.draw = function(){
                console.log(this)
                var alpha_sel = this.props.alpha_sel
                var alpha_unsel = this.props.alpha_unsel
            
                var legendItems = new Array();
                for(var i=0; i<this.props.labels.length; i++){
                    var obj = {}
                    obj.label = this.props.labels[i]
                    
                    var element_id = this.props.element_ids[i]
                    mpld3_elements = []
                    for(var j=0; j<element_id.length; j++){
                        var mpld3_element = mpld3.get_element(element_id[j], this.fig)
                        mpld3_elements.push(mpld3_element)
                    }
                    
                    obj.mpld3_elements = mpld3_elements
                    obj.visible = false; // must be setable from python side
                    legendItems.push(obj);
                }
                console.log(legendItems)
                
                // determine the axes with which this legend is associated
                var ax = this.props.ax
                if(!ax){
                    ax = this.fig.axes[0]
                } else{
                    ax = mpld3.get_element(ax, this.fig);
                }
                
                // add a legend group to the canvas of the figure
                var legend = this.fig.canvas.append("svg:g")
                                       .attr("class", "legend");
                
                // add the rectangles
                legend.selectAll("rect")
                        .data(legendItems)
                     .enter().append("rect")
                        .attr("height",10)
                        .attr("width", 25)
                        .attr("x",ax.width+10+ax.position[0])
                        .attr("y",function(d,i) {
                                    return ax.position[1]+ i * 25 - 10;})
                        .attr("stroke", get_color)
                        .attr("class", "legend-box")
                        .style("fill", function(d, i) {
                                    return d.visible ? get_color(d) : "white";}) 
                        .on("click", click)
                
                // add the labels
                legend.selectAll("text")
                        .data(legendItems)
                    .enter().append("text")
                      .attr("x", function (d) {
                                    return ax.width+10+ax.position[0] + 40})
                      .attr("y", function(d,i) { 
                                    return ax.position[1]+ i * 25})
                      .text(function(d) { return d.label })
                
                // specify the action on click
                function click(d,i){
                    d.visible = !d.visible;
                    d3.select(this)
                      .style("fill",function(d, i) {
                        return d.visible ? get_color(d) : "white";
                      })
                      
                    for(var i=0; i<d.mpld3_elements.length; i++){
                    
                        var type = d.mpld3_elements[i].constructor.name
                        if(type =="mpld3_Line"){
                            d3.select(d.mpld3_elements[i].path[0][0])
                                .style("stroke-opacity", 
                                        d.visible ? alpha_sel : alpha_unsel);
                        } else if(type=="mpld3_PathCollection"){
                            d3.selectAll(d.mpld3_elements[i].pathsobj[0])
                                .style("stroke-opacity", 
                                        d.visible ? alpha_sel : alpha_unsel)
                                .style("fill-opacity", 
                                        d.visible ? alpha_sel : alpha_unsel);
                        } else{
                            console.log(type + " not yet supported")
                        }
                    }
                };
                
                // helper function for determining the color of the rectangles
                function get_color(d){
                    var type = d.mpld3_elements[0].constructor.name
                    var color = "black";
                    if(type =="mpld3_Line"){
                        color = d.mpld3_elements[0].props.edgecolor;
                    } else if(type=="mpld3_PathCollection"){
                        color = d.mpld3_elements[0].props.facecolors[0];
                    } else{
                        console.log(type + " not yet supported")
                    }
                    return color
                };
            };
            """

            css_ = """
            .legend-box {
              cursor: pointer;  
            }
            """
            
            def __init__(self, plot_elements, labels, ax=None,
                         alpha_sel=1,alpha_unsel=0.2):
                
                self.ax = ax
                
                if ax:
                    ax = utils.get_id(ax)
                
                mpld3_element_ids = self._determine_mpld3ids(plot_elements)
                self.mpld3_element_ids = mpld3_element_ids
                
                self.dict_ = {"type": "interactive_legend",
                              "element_ids": mpld3_element_ids,
                              "labels":labels,
                              "ax":ax,
                              "alpha_sel":alpha_sel,
                              "alpha_unsel":alpha_unsel}
            
            def _determine_mpld3ids(self, plot_elements):
                """
                Helper function to get the mpld3_id for each
                of the specified elements.
                
                This is a convenience function. You can
                now do:
                
                lines = ax.plot(x,y)
                plugins.connect(fig, HighlightLines(lines, labels))
                
                rather than first having to wrap each entry in
                lines in a seperate list.
                
                """


                mpld3_element_ids = []
            
                for entry in plot_elements:
                    if isinstance(entry, collections.Iterable):
                        mpld3_element_ids.append([utils.get_id(element) for element in entry])
                    else:   
                        mpld3_element_ids.append([utils.get_id(entry)])

                return mpld3_element_ids


    def signal_handler(signal, frame):
        """exit on ctrl+c, rather than just stop loop"""
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

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

    styles = ['dark_background', 'bmh', 'grayscale', 'ggplot', 'fivethirtyeight']
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

    if interactive:
        using_tex = False 

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

    if 'legend' in kwargs:
        legend = kwargs['legend']
    else:
        legend = True

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
    if was_series:
        if dataframe.iloc[0].dtype == 'float64':
            absolutes = False
    else:
        if dataframe.iloc[0][0].dtype == 'float64':
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
                    # make a bar width ... ?
                    kwargs['width'] = figsize[0] / float(num_to_plot)

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
        if 'shadow' in kwargs:
            leg_options['shadow'] = True
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

    linemode = True
    if 'kind' in kwargs:
        if kwargs['kind'] != 'line':
            linemode = False       
    
    #areamode = False
    #if 'kind' in kwargs:
        #if kwargs['kind'] == 'area':
            #areamode = True        

    if legend is False:
        kwargs['legend'] = False

    # cumulative grab first col
    if cumulative:
        kwargs['y'] = list(dataframe.columns)[0]

    # line highlighting option for interactive!
    if interactive:
        if '2' in interactive:
            if linemode:
                kwargs['marker'] = ','
        if not piemode:
            kwargs['alpha'] = 0.1
        # convert dates --- works only in my current case!
        if plotting_a_totals_column or not was_series:
            try:
                n = pd.PeriodIndex([d for d in list(dataframe.index)], freq='A')
                dataframe = dataframe.set_index(n)
            except:
                pass

    
    # use styles and plot 
    with plt.style.context((style)):

        if not sbplt:
            dataframe.plot(figsize = figsize, **kwargs)
        else:
            ax = dataframe.plot(figsize = figsize, **kwargs)
        if legend:
            if '3' not in interactive:
                if not rev_leg:
                    lgd = plt.legend(**leg_options)
                else:
                    handles, labels = plt.gca().get_legend_handles_labels()
                    lgd = plt.legend(handles[::-1], labels[::-1], **leg_options)
        #if interactive:
            #if legend:
                #lgd.set_title("")
        #if not sbplt:
            #if 'layout' not in kwargs:
                #plt.tight_layout()

    if interactive:
        ax = plt.gca()
        # fails for piemode
        lines = ax.lines
        handles, labels = plt.gca().get_legend_handles_labels()
        if '1' in interactive:
            plugins.connect(plt.gcf(), HighlightLines(lines))

        if '3' in interactive:
            plugins.connect(plt.gcf(), InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0))

        for i, l in enumerate(lines):
            y_vals = l.get_ydata()
            if absolutes:
                ls = ['%s: %d' % (labels[i], y_val) for y_val in y_vals]
            else:
                ls = ['%s: %.2f%%' % (labels[i], y_val) for y_val in y_vals]
            if '2' in interactive:
                if 'kind' in kwargs:
                    if kwargs['kind'] == 'area':
                        tooltips = mpld3.plugins.LineLabelTooltip(ax.get_lines()[i], labels[i])
                        mpld3.plugins.connect(plt.gcf(), tooltips)
                    else:
                        tooltips = mpld3.plugins.PointLabelTooltip(l, labels = ls)
                mpld3.plugins.connect(plt.gcf(), tooltips)
        
            # works:
            #plugins.connect(plt.gcf(), plugins.LineLabelTooltip(l, labels[i]))


        #labels = ["Point {0}".format(i) for i in range(num_to_plot)]
        #tooltip = plugins.LineLabelTooltip(lines)
        #mpld3.plugins.connect(plt.gcf(), mpld3.plugins.PointLabelTooltip(lines))

    #if piemode:
        #if not sbplt:
            #plt.tight_layout()
            #plt.axis('equal')


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

    # no weird scalar results:
    try: 
        plt.ticklabel_format(useOffset = False)
    except:
        # if other kind of plot...
        pass

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
            a.legend_.remove()
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

    #if not have_python_tex:
        #plt.gcf().show()

    plt.subplots_adjust(left=0.1)
    #if 'layout' not in kwargs:
        #plt.tight_layout()

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
    
    if interactive:
        plt.subplots_adjust(right=.8)
        plt.subplots_adjust(left=.1)
        ax.legend_.remove()
        return mpld3.display()