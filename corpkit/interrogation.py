
class Interrogation:
    """
    Stores results of a corpus interrogation, before or after editing.
    """

    def __init__(self, results = None, totals = None, query = None):
        """initialise the class"""
        self.results = results
        """pandas `DataFrame` containing counts for each subcorpus"""
        self.totals = totals
        """pandas `Series` containing summed results"""
        self.query = query
        """`dict` containing values that generated the result"""

    def __str__(self):
        st = 'Corpus interrogation: %s\n\n' % (self.query['path'])
        return st

    def __repr__(self):
        return "<corpkit.interrogation.Interrogation instance: %d total results>" % (self.totals.sum())

    def edit(self, *args, **kwargs):
        """Edit results of interrogations, do keywording, sort, etc.

        ``just/skip_entries`` and ``just/skip_subcorpora`` can take a few different kinds of input:

        * str: treated as regular expression to match
        * list: 

          * of integers: indices to match
          * of strings: entries/subcorpora to match

        ``merge_entries`` and ``merge_subcorpora``, however, are best entered as dicts:

        ``{newname: criteria, newname2: criteria2}```

        where criteria is a string, list, etc.

        :param operation: Kind of maths to do on inputted lists:

            '+', '-', '/', '*', '%': self explanatory

            'k': log likelihood (keywords)

            'a': get distance metric (for use with interrogator 'a' option)

            'd': get percent difference (alternative approach to keywording)

        :type operation: str
        
        :param dataframe2: List of results or totals.

            If list of results, for each entry in dataframe 1, locate
            entry with same name in dataframe 2, and do maths there
            if 'self', do all merging/keeping operations, then use
            edited dataframe1 as dataframe2

        :type dataframe2: pandas.core.series.Series/pandas.core.frame.DataFrame/dict/'self'

        :param sort_by: Calculate slope, stderr, r, p values, then sort by.

            increase: highest to lowest slope value
            decrease: lowest to highest slope value
            turbulent: most change in y axis values
            static: least change in y axis values
            total/most: largest number first
            infreq/least: smallest number first
            name: alphabetically

        :type sort_by: str

        :param keep_stats: Keep/drop stats values from dataframe after sorting
        :type keep_stats: bool
        
        :param keep_top: After sorting, remove all but the top *keep_top* results
        :type keep_top: int
        
        :param just_totals: Sum each column and work with sums
        :type just_totals: bool
        
        :param threshold: When using results list as dataframe 2, drop values occurring
                            fewer than n times. If not keywording, you can use:
                                
                                ``'high'``: dataframe2 total / 2500
                                
                                ``'medium'``: dataframe2 total / 5000
                                
                                ``'low'``: dataframe2 total / 10000
                            
                                If keywording, there are smaller default thresholds

        :type threshold: int/bool
        :param just_entries: Keep matching entries
        :type just_entries: see above
        :param skip_entries: Skip matching entries
        :type skip_entries: see above
        :param merge_entries: Merge matching entries
        :type merge_entries: see above
        :param newname: New name for merged entries
        :type newname: str/'combine'
        :param just_subcorpora: Keep matching subcorpora
        :type just_subcorpora: see above
        :param skip_subcorpora: Skip matching subcorpora
        :type skip_subcorpora: see above
        :param span_subcorpora: If subcorpora are numerically named, span all from *int* to *int2*, inclusive
        :type span_subcorpora: tuple -- ``(int, int2)``
        :param merge_subcorpora: Merge matching subcorpora
        :type merge_subcorpora: see above
        :param new_subcorpus_name: Name for merged subcorpora
        :type new_subcorpus_name: str/``'combine'``

        :param replace_names: Edit result names and then merge duplicate names.
        :type replace_names: dict -- ``{criteria: replacement_text}``; str -- a regex to delete from names
        :param projection:         a  to multiply results in subcorpus by n
        :type projection: tuple -- ``(subcorpus_name, n)``
        :param remove_above_p: Delete any result over p
        :type remove_above_p: bool
        :param p:                  set the p value
        :type p: float
        
        :param revert_year: When doing linear regression on years, turn annual subcorpora into 1, 2 ...
        :type revert_year: bool
        
        :param print_info: Print stuff to console showing what's being edited
        :type print_info: bool
        
        :param spelling: Convert/normalise spelling:
        :type spelling: str -- ``'US'``/``'UK'``
        
        :param selfdrop: When keywording, try to remove target corpus from reference corpus
        :type selfdrop: bool
        
        :param calc_all: When keywording, calculate words that appear in either corpus
        :type calc_all: bool

        :returns: :class:`corpkit.interrogation.Interrogation`
        """
        from corpkit import editor
        branch = kwargs.pop('branch', 'results')
        if branch.lower().startswith('r'):
            return editor(self.results, *args, **kwargs)
        elif branch.lower().startswith('t'):
            return editor(self.totals, *args, **kwargs)

    def plot(title,
            x_label = None,
            y_label = None,
            style = 'ggplot',
            figsize = (8, 4),
            save = False,
            legend_pos = 'best',
            reverse_legend = 'guess',
            num_to_plot = 7,
            tex = 'try',
            colours = 'Accent',
            cumulative = False,
            pie_legend = True,
            partial_pie = False,
            show_totals = False,
            transparent = False,
            output_format = 'png',
            interactive = False,
            black_and_white = False,
            show_p_val = False,
            indices = False,
            **kwargs):
        """Visualise corpus interrogations.

        :param title: A title for the plot
        :type title: str
        :param x_label: A label for the x axis
        :type x_label: str
        :param y_label: A label for the y axis
        :type y_label: str
        :param kind: The kind of chart to make
        :type kind: str ('line'/'bar'/'barh'/'pie'/'area')
        :param style: Visual theme of plot
        :type style: str ('ggplot'/'bmh'/'fivethirtyeight'/'seaborn-talk'/etc)
        :param figsize: Size of plot
        :type figsize: tuple (int, int)
        :param save: If bool, save with *title* as name; if str, use str as name
        :type save: bool/str
        :param legend_pos: Where to place legend
        :type legend_pos: str ('upper right'/'outside right'/etc)
        :param reverse_legend: Reverse the order of the legend
        :type reverse_legend: bool
        :param num_to_plot: How many columns to plot
        :type num_to_plot: int/'all'
        :param tex: Use TeX to draw plot text
        :type tex: bool
        :param colours: Colourmap for lines/bars/slices
        :type colours: str
        :param cumulative: Plot values cumulatively
        :type cumulative: bool
        :param pie_legend: Show a legend for pie chart
        :type pie_legend: bool
        :param partial_pie: Allow plotting of pie slices only
        :type partial_pie: bool
        :param show_totals: Print sums in plot where possible
        :type show_totals: str -- 'legend'/'plot'/'both'
        :param transparent: Transparent .png background
        :type transparent: bool
        :param output_format: File format for saved image
        :type output_format: str -- 'png'/'pdf'
        :param black_and_white: Create black and white line styles
        :type black_and_white: bool
        :param show_p_val: Attempt to print p values in legend if contained in df
        :type show_p_val: bool
        :param indices: To use when plotting "distance from root"
        :type indices: bool
        :param stacked: When making bar chart, stack bars on top of one another
        :type stacked: str
        :param filled: For area and bar charts, make every column sum to 100
        :type filled: str
        :param legend: Show a legend
        :type legend: bool
        :param rot: Rotate x axis ticks by *rot* degrees
        :type rot: int
        :param subplots: Plot each column separately
        :type subplots: bool
        :param layout: Grid shape to use when *subplots* is True
        :type layout: tuple -- (int, int)
        :param interactive: Experimental interactive options
        :type interactive: list -- [1, 2, 3]
        :returns: matplotlib figure
        """
        from corpkit import plotter
        branch = kwargs.pop('branch', 'results')
        if branch.lower().startswith('r'):
            plotter(title, self.results, *args, **kwargs)
        elif branch.lower().startswith('t'):
            plotter(title, self.totals, *args, **kwargs)

    def save(self, savename, savedir = 'saved_interrogations', print_info = True):
        """
        Save an interrogation as pickle to *savedir*.

           >>> o = corpus.interrogate('w', 'any')
           >>> save(o, 'savename')

        will create saved_interrogations/savename.p
        
        :param savename: A name for the saved file
        :type savename: str
        
        :param savedir: Relative path to directory in which to save file
        :type savedir: str
        
        :param print_info: Show/hide stdout
        :type print_info: bool
        
        :returns: None
        """
        from corpkit import save
        save(self, savename, *args, **kwargs)

    def quickview(self, n = 25):
        """view top n results as painlessly as possible.

        :param n: Show top *n* results
        :type n: int
        :returns: None
        """
        from corpkit import quickview
        quickview(self, n = n)

    def multiindex(self, indexnames = False):
        """Create a `pd.MultiIndex` object from slash-separated results.

        :param indexnames: provide custom names for the new index
        :type indexnames: list of strings
        """

        from corpkit.other import make_multi
        return make_multi(self, indexnames = indexnames)

import pandas as pd
class Results(pd.core.frame.DataFrame):
    """
    A class for interrogation results, with methods for editing, plotting,
    saving and quickviewing
    """

    def __init__(self, data):
        pd.core.frame.DataFrame.__init__(self, data)

    #def __repr__(self):
        #return "<corpkit.interrogation.Results instance: %d unique results>" % len(self.columns)

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        return editor(self, *args, **kwargs)

    def plot(self, title, *args, **kwargs):
        """calls corpkit.plotter.plotter()"""
        from corpkit import plotter
        plotter(title, self, *args, **kwargs)

    def save(self, savename, *args, **kwargs):
        """Save data to pickle file"""
        from corpkit import save
        save(self, savename, *args, **kwargs)

    def quickview(self, n = 25):
        """Print top results from an interrogation or edit"""
        from corpkit import quickview
        quickview(self, n = n)
    
class Totals(pd.core.series.Series):
    """
    A class for interrogation totals, with methods for editing, plotting,
    saving and quickviewing
    """
    def __init__(self, data):
        pd.core.series.Series.__init__(self, data)

    #def __repr__(self):
        #return "<corpkit.interrogation.Totals instance: %d unique results>" % self.sum()

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        return editor(self, *args, **kwargs)

    def plot(self, title, *args, **kwargs):
        """calls corpkit.plotter.plotter()"""
        from corpkit import plotter
        plotter(title, self, *args, **kwargs)

    def save(self, savename, *args, **kwargs):
        """Save data to pickle file"""
        from corpkit import save
        save(self, savename, *args, **kwargs)

    def quickview(self, n = 25):
        """Print top results from an interrogation or edit"""
        from corpkit import quickview
        quickview(self, n = n)
    
class Concordance(pd.core.frame.DataFrame):
    """
    A class for concordance lines, with methods for saving,
    formatting and editing.
    """
    
    def __init__(self, data):

        pd.core.frame.DataFrame.__init__(self, data)
        self.results = data

    #def __repr__(self):
        #return 'corpkit.interrogation.Concordance instance: %d lines' % (len(self))

    def format(self, kind = 'string', n = 100, window = 35, columns = 'all', **kwargs):
        """
        Print conc lines nicely, to string, latex or csv

        :param kind: output format
        :type kind: str ('string'/'latex'/'csv')
        :param n: Print first n lines only
        :type n: int/'all'
        :param window: how many characters to show to left and right
        :type window: int
        :param columns: which columns to show
        :type columns: list
        :returns: None
        """
        from corpkit.other import concprinter
        concprinter(self, kind = kind, n = n, window = window, columns = columns, **kwargs)

class Interrodict(dict):
    """
    A class for interrogations that do not fit in a single-indexed DataFrame.

    Methods for saving, editing, and generating multiindex DataFrame equivalent.
    """
    
    def __init__(self, data):
        from corpkit.process import makesafe
        for k, v in data.items():
            setattr(self, makesafe(k), v)
        dict.__init__(self, data)

    def edit(self, *args, **kwargs):
        from corpkit import editor
        return editor(self, *args, **kwargs)

    def multiindex(self, indexnames = False):
        from corpkit.other import make_multi
        return make_multi(self, indexnames = indexnames)
        
