"""
corpkit: `Int`errogation and Interrogation-like classes
"""

from __future__ import print_function

from collections import OrderedDict
import pandas as pd
from corpkit.process import classname

class Interrogation(object):
    """
    Stores results of a corpus interrogation, before or after editing. The main 
    attribute, :py:attr:`~corpkit.interrogation.Interrogation.results`, is a 
    Pandas object, which can be edited or plotted.
    """

    def __init__(self, results=None, totals=None, query=None, concordance=None):
        """Initialise the class"""
        self.results = results
        """pandas `DataFrame` containing counts for each subcorpus"""
        self.totals = totals
        """pandas `Series` containing summed results"""
        self.query = query
        """`dict` containing values that generated the result"""
        self.concordance = concordance
        """pandas `DataFrame` containing concordance lines, if concordance lines were requested."""

    def __str__(self):
        if self.query.get('corpus'):
            prst = getattr(self.query['corpus'], 'name', self.query['corpus'])
        else:
            try:
                prst = self.query['interrogation'].query['corpus'].name
            except:
                prst = 'edited'
        st = 'Corpus interrogation: %s\n\n' % (prst)
        return st

    def __repr__(self):
        try:
            return "<%s instance: %d total>" % (classname(self), self.totals.sum())
        except AttributeError:
            return "<%s instance: %d total>" % (classname(self), self.totals)

    def edit(self, *args, **kwargs):
        """
        Manipulate results of interrogations.

        There are a few overall kinds of edit, most of which can be combined 
        into a single function call. It's useful to keep in mind that many are 
        basic wrappers around `pandas` operations---if you're comfortable with 
        `pandas` syntax, it may be faster at times to use its syntax instead.

        :Basic mathematical operations:

        First, you can do basic maths on results, optionally passing in some 
        data to serve as the denominator. Very commonly, you'll want to get 
        relative frequencies:

        :Example: 

        >>> data = corpus.interrogate({W: r'^t'})
        >>> rel = data.edit('%', SELF)
        >>> rel.results
            ..    to  that   the  then ...   toilet  tolerant  tolerate  ton
            01 18.50 14.65 14.44  6.20 ...     0.00      0.00      0.11 0.00
            02 24.10 14.34 13.73  8.80 ...     0.00      0.00      0.00 0.00
            03 17.31 18.01  9.97  7.62 ...     0.00      0.00      0.00 0.00

        For the operation, there are a number of possible values, each of 
        which is to be passed in as a `str`:

           `+`, `-`, `/`, `*`, `%`: self explanatory

           `k`: calculate keywords

           `a`: get distance metric
        
        `SELF` is a very useful shorthand denominator. When used, all editing 
        is performed on the data. The totals are then extracted from the edited 
        data, and used as denominator. If this is not the desired behaviour, 
        however, a more specific `interrogation.results` or 
        `interrogation.totals` attribute can be used.

        In the example above, `SELF` (or `'self'`) is equivalent to:

        :Example:

        >>> rel = data.edit('%', data.totals)

        :Keeping and skipping data:

        There are four keyword arguments that can be used to keep or skip rows 
        or columns in the data:

        * `just_entries`
        * `just_subcorpora`
        * `skip_entries`
        * `skip_subcorpora`

        Each can accept different input types:

        * `str`: treated as regular expression to match
        * `list`: 

          * of integers: indices to match
          * of strings: entries/subcorpora to match

        :Example:

        >>> data.edit(just_entries=r'^fr', 
        ...           skip_entries=['free','freedom'],
        ...           skip_subcorpora=r'[0-9]')

        :Merging data:

        There are also keyword arguments for merging entries and subcorpora:

        * `merge_entries`
        * `merge_subcorpora`

        These take a `dict`, with the new name as key and the criteria as 
        value. The criteria can be a str (regex) or wordlist.

        :Example:
        
        >>> from dictionaries.wordlists import wordlists
        >>> mer = {'Articles': ['the', 'an', 'a'], 'Modals': wordlists.modals}
        >>> data.edit(merge_entries=mer)

        :Sorting:

        The `sort_by` keyword argument takes a `str`, which represents the way 
        the result columns should be ordered.

        * `increase`: highest to lowest slope value
        * `decrease`: lowest to highest slope value
        * `turbulent`: most change in y axis values
        * `static`: least change in y axis values
        * `total/most`: largest number first
        * `infreq/least`: smallest number first
        * `name`: alphabetically

        :Example:

        >>> data.edit(sort_by='increase')

        :Editing text:
        
        Column labels, corresponding to individual interrogation results, can 
        also be edited with `replace_names`.

        :param replace_names: Edit result names, then merge duplicate entries
        :type replace_names: `str`/`list of tuples`/`dict`

        If `replace_names` is a string, it is treated as a regex to delete from 
        each name. If `replace_names` is a dict, the value is the regex, and 
        the key is the replacement text. Using a list of tuples in the form 
        `(find, replacement)` allows duplicate substitution values.

        :Example:

        >>> data.edit(replace_names={r'object': r'[di]obj'})

        :param replace_subcorpus_names: Edit subcorpus names, then merge duplicates.
                                        The same as `replace_names`, but on the other axis.
        :type replace_subcorpus_names: `str`/`list of tuples`/`dict`

        :Other options:

        There are many other miscellaneous options.

        :param keep_stats: Keep/drop stats values from dataframe after sorting
        :type keep_stats: `bool`
        
        :param keep_top: After sorting, remove all but the top *keep_top* results
        :type keep_top: `int`
        
        :param just_totals: Sum each column and work with sums
        :type just_totals: `bool`
        
        :param threshold: When using results list as dataframe 2, drop values 
                          occurring fewer than n times. If not keywording, you 
                          can use:
                                
           `'high'`: `denominator total / 2500`
           
           `'medium'`: `denominator total / 5000`
           
           `'low'`: `denominator total / 10000`
                            
           If keywording, there are smaller default thresholds

        :type threshold: `int`/`bool`

        :param span_subcorpora: If subcorpora are numerically named, span all 
                                from *int* to *int2*, inclusive
        :type span_subcorpora: `tuple` -- `(int, int2)`

        :param projection: multiply results in subcorpus by n
        :type projection: tuple -- `(subcorpus_name, n)`
        :param remove_above_p: Delete any result over `p`
        :type remove_above_p: `bool`

        :param p: set the p value
        :type p: `float`
        
        :param revert_year: When doing linear regression on years, turn annual 
                            subcorpora into 1, 2 ...
        :type revert_year: `bool`
        
        :param print_info: Print stuff to console showing what's being edited
        :type print_info: `bool`
        
        :param spelling: Convert/normalise spelling:
        :type spelling: `str` -- `'US'`/`'UK'`

        :Keywording options:

        If the operation is `k`, you're calculating keywords. In this case,
        some other keyword arguments have an effect:

        :param keyword_measure: what measure to use to calculate keywords:

           `ll`: log-likelihood
           `pd': percentage difference

        type keyword_measure: `str`
        
        :param selfdrop: When keywording, try to remove target corpus from 
                         reference corpus
        :type selfdrop: `bool`
        
        :param calc_all: When keywording, calculate words that appear in either 
                         corpus
        :type calc_all: `bool`

        :returns: :class:`corpkit.interrogation.Interrogation`
        """
        from corpkit.editor import editor
        return editor(self, *args, **kwargs)

    def sort(self, way, **kwargs):
        from corpkit.editor import editor
        return editor(self, sort_by=way, **kwargs)

    def visualise(self,
                  title='',
                  x_label=None,
                  y_label=None,
                  style='ggplot',
                  figsize=(8, 4),
                  save=False,
                  legend_pos='best',
                  reverse_legend='guess',
                  num_to_plot=7,
                  tex='try',
                  colours='Accent',
                  cumulative=False,
                  pie_legend=True,
                  rot=False,
                  partial_pie=False,
                  show_totals=False,
                  transparent=False,
                  output_format='png',
                  interactive=False,
                  black_and_white=False,
                  show_p_val=False,
                  indices=False,
                  transpose=False,
                  **kwargs
                 ):
        """Visualise corpus interrogations using `matplotlib`.

        :Example:

        >>> data.visualise('An example plot', kind='bar', save=True)
        <matplotlib figure>

        :param title: A title for the plot
        :type title: `str`
        :param x_label: A label for the x axis
        :type x_label: `str`
        :param y_label: A label for the y axis
        :type y_label: `str`
        :param kind: The kind of chart to make
        :type kind: `str` (`'line'`/`'bar'`/`'barh'`/`'pie'`/`'area'`/`'heatmap'`)
        :param style: Visual theme of plot
        :type style: `str` ('ggplot'/'bmh'/'fivethirtyeight'/'seaborn-talk'/etc)
        :param figsize: Size of plot
        :type figsize: `tuple` -- `(int, int)`
        :param save: If `bool`, save with *title* as name; if `str`, use `str` as name
        :type save: `bool`/`str`
        :param legend_pos: Where to place legend
        :type legend_pos: `str` ('upper right'/'outside right'/etc)
        :param reverse_legend: Reverse the order of the legend
        :type reverse_legend: `bool`
        :param num_to_plot: How many columns to plot
        :type num_to_plot: `int`/'all'
        :param tex: Use TeX to draw plot text
        :type tex: `bool`
        :param colours: Colourmap for lines/bars/slices
        :type colours: `str`
        :param cumulative: Plot values cumulatively
        :type cumulative: `bool`
        :param pie_legend: Show a legend for pie chart
        :type pie_legend: `bool`
        :param partial_pie: Allow plotting of pie slices only
        :type partial_pie: `bool`
        :param show_totals: Print sums in plot where possible
        :type show_totals: `str` -- 'legend'/'plot'/'both'
        :param transparent: Transparent .png background
        :type transparent: `bool`
        :param output_format: File format for saved image
        :type output_format: `str` -- 'png'/'pdf'
        :param black_and_white: Create black and white line styles
        :type black_and_white: `bool`
        :param show_p_val: Attempt to print p values in legend if contained in df
        :type show_p_val: `bool`
        :param indices: To use when plotting "distance from root"
        :type indices: `bool`
        :param stacked: When making bar chart, stack bars on top of one another
        :type stacked: `str`
        :param filled: For area and bar charts, make every column sum to 100
        :type filled: `str`
        :param legend: Show a legend
        :type legend: `bool`
        :param rot: Rotate x axis ticks by *rot* degrees
        :type rot: `int`
        :param subplots: Plot each column separately
        :type subplots: `bool`
        :param layout: Grid shape to use when *subplots* is True
        :type layout: `tuple` -- `(int, int)`
        :param interactive: Experimental interactive options
        :type interactive: `list` -- `[1, 2, 3]`
        :returns: matplotlib figure
        """
        from corpkit.plotter import plotter
        branch = kwargs.pop('branch', 'results')
        if branch.lower().startswith('r'):
            to_plot = self.results
        elif branch.lower().startswith('t'):
            to_plot = self.totals
        return plotter(to_plot,
                       title=title,
                       x_label=x_label,
                       y_label=y_label,
                       style=style,
                       figsize=figsize,
                       save=save,
                       legend_pos=legend_pos,
                       reverse_legend=reverse_legend,
                       num_to_plot=num_to_plot,
                       tex=tex,
                       rot=rot,
                       colours=colours,
                       cumulative=cumulative,
                       pie_legend=pie_legend,
                       partial_pie=partial_pie,
                       show_totals=show_totals,
                       transparent=transparent,
                       output_format=output_format,
                       interactive=interactive,
                       black_and_white=black_and_white,
                       show_p_val=show_p_val,
                       indices=indices,
                       transpose=transpose,
                       **kwargs
                      )

    def multiplot(self, leftdict={}, rightdict={}, **kwargs):
        from corpkit.plotter import multiplotter
        return multiplotter(self, leftdict=leftdict, rightdict=rightdict, **kwargs)

    def language_model(self, name, *args, **kwargs):
        """
        Make a language model from an Interrogation. This is usually done 
        directly on a :class:`corpkit.corpus.Corpus` object with the 
        :func:`~corpkit.corpus.Corpus.make_language_model` method.
        """
        from corpkit.model import _make_model_from_interro
        multi = self.multiindex()
        order = len(self.query['show'])
        return _make_model_from_interro(multi, name, order=order, *args, **kwargs)

    def save(self, savename, savedir='saved_interrogations', **kwargs):
        """
        Save an interrogation as pickle to ``savedir``.

        :Example:
        
        >>> o = corpus.interrogate(W, 'any')
        ### create ./saved_interrogations/savename.p
        >>> o.save('savename')
        
        :param savename: A name for the saved file
        :type savename: `str`
        
        :param savedir: Relative path to directory in which to save file
        :type savedir: `str`
        
        :param print_info: Show/hide stdout
        :type print_info: `bool`
        
        :returns: None
        """
        from corpkit.other import save
        save(self, savename, savedir=savedir, **kwargs)

    def quickview(self, n=25):
        """view top n results as painlessly as possible.

        :Example:
        
        >>> data.quickview(n=5)
            0: to    (n=2227)
            1: that  (n=2026)
            2: the   (n=1302)
            3: then  (n=857)
            4: think (n=676)

        :param n: Show top *n* results
        :type n: `int`
        :returns: `None`
        """
        from corpkit.other import quickview
        quickview(self, n=n)

    def tabview(self, **kwargs):
        import tabview
        tabview.view(self.results, **kwargs)

    def asciiplot(self,
                  row_or_col_name,
                  axis=0,
                  colours=True,
                  num_to_plot=100,
                  line_length=120,
                  min_graph_length=50,
                  separator_length=4,
                  multivalue=False,
                  human_readable='si',
                  graphsymbol='*',
                  float_format='{:,.2f}',
                  **kwargs):
        """
        A very quick ascii chart for result
        """
        from ascii_graph import Pyasciigraph
        from ascii_graph.colors import Gre, Yel, Red, Blu
        from ascii_graph.colordata import vcolor
        from ascii_graph.colordata import hcolor
        import pydoc

        graph = Pyasciigraph(
                            line_length=line_length,
                            min_graph_length=min_graph_length,
                            separator_length=separator_length,
                            multivalue=multivalue,
                            human_readable=human_readable,
                            graphsymbol=graphsymbol
                            )
        if axis == 0:
            dat = self.results.T[row_or_col_name]
        else:
            dat = self.results[row_or_col_name]
        data = list(zip(dat.index, dat.values))[:num_to_plot]
        if colours:
            pattern = [Gre, Yel, Red]
            data = vcolor(data, pattern)

        out = []
        for line in graph.graph(label=None, data=data, float_format=float_format):
            out.append(line)
        pydoc.pipepager('\n'.join(out), cmd='less -X -R -S')

    def rel(self, denominator='self', **kwargs):
        return self.edit('%', denominator, **kwargs)

    def keyness(self, measure='ll', denominator='self', **kwargs):
        return self.edit('k', denominator, **kwargs)

    def multiindex(self, indexnames=None):
        """Create a `pandas.MultiIndex` object from slash-separated results.

        :Example:

        >>> data = corpus.interrogate({W: 'st$'}, show=[L, F])
        >>> data.results
            ..  just/advmod  almost/advmod  last/amod 
            01           79             12          6 
            02          105              6          7 
            03           86             10          1 
        >>> data.multiindex().results
            Lemma       just almost last first   most 
            Function  advmod advmod amod  amod advmod 
            0             79     12    6     2      3 
            1            105      6    7     1      3 
            2             86     10    1     3      0                                   

        :param indexnames: provide custom names for the new index, or leave blank to guess.
        :type indexnames: `list` of strings

        :returns: :class:`corpkit.interrogation.Interrogation`, with 
                  `pandas.MultiIndex` as 
        :py:attr:`~corpkit.interrogation.Interrogation.results` attribute
        """

        from corpkit.other import make_multi
        return make_multi(self, indexnames=indexnames)

    def topwords(self, datatype='n', n=10, df=False, sort=True, precision=2):
        """Show top n results in each corpus alongside absolute or relative frequencies.

        :param datatype: show abs/rel frequencies, or keyness
        :type datatype: `str` (n/k/%)
        :param n: number of result to show
        :type n: `int`
        :param df: return a DataFrame
        :type df: `bool`
        :param sort: Sort results, or show as is
        :type sort: `bool`
        :param precision: float precision to show
        :type precision: `int`

        :Example:

        >>> data.topwords(n=5)
            1987           %   1988           %   1989           %   1990           %
            health     25.70   health     15.25   health     19.64   credit      9.22
            security    6.48   cancer     10.85   security    7.91   health      8.31
            cancer      6.19   heart       6.31   cancer      6.55   downside    5.46
            flight      4.45   breast      4.29   credit      4.08   inflation   3.37
            safety      3.49   security    3.94   safety      3.26   cancer      3.12

        :returns: None
        """
        from corpkit.other import topwords
        if df:
            return topwords(self, datatype=datatype, n=n, df=True,
                            sort=sort, precision=precision)
        else:
            topwords(self, datatype=datatype, n=n,
                     sort=sort, precision=precision)



    def perplexity(self):
        """
        Pythonification of the formal definition of perplexity.

        input:  a sequence of chances (any iterable will do)
        output: perplexity value.

        from https://github.com/zeffii/NLP_class_notes
        """

        def _perplex(chances):
            import math
            chances = [i for i in chances if i] 
            N = len(chances)
            product = 1
            for chance in chances:
                product *= chance
            return math.pow(product, -1/N)

        return self.results.apply(_perplex, axis=1)

    def entropy(self):
        """
        entropy(pos.edit(merge_entries=mergetags, sort_by='total').results.T
        """
        from scipy.stats import entropy
        import pandas as pd
        escores = entropy(self.rel().results.T)
        ser = pd.Series(escores, index=self.results.index)
        ser.name = 'Entropy'
        return ser

    def shannon(self):
        from corpkit.stats import shannon
        return shannon(self)

class Concordance(pd.core.frame.DataFrame):
    """
    A class for concordance lines, with methods for saving, formatting and editing.
    """
    
    def __init__(self, data):

        super(Concordance, self).__init__(data)
        self.concordance = data

    def format(self, kind='string', n=100, window=35,
               print_it=True, columns='all', **kwargs):
        """
        Print concordance lines nicely, to string, LaTeX or CSV

        :param kind: output format: `string`/`latex`/`csv`
        :type kind: `str`
        :param n: Print first `n` lines only
        :type n: `int`/`'all'`
        :param window: how many characters to show to left and right
        :type window: `int`
        :param columns: which columns to show
        :type columns: `list`

        :Example:

        >>> lines = corpus.concordance({T: r'/NN.?/ >># NP'}, show=L)
        ### show 25 characters either side, 4 lines, just text columns
        >>> lines.format(window=25, n=4, columns=[L,M,R])
            0                  we 're in  tucson     , then up north to flagst
            1  e 're in tucson , then up  north      to flagstaff , then we we
            2  tucson , then up north to  flagstaff  , then we went through th
            3   through the grand canyon  area       and then phoenix and i sp

        :returns: None
        """
        from corpkit.other import concprinter
        if print_it:
            print(concprinter(self, kind=kind, n=n, window=window,
                           columns=columns, return_it=True, **kwargs))
        else:
            return concprinter(self, kind=kind, n=n, window=window,
                           columns=columns, return_it=True, **kwargs)

    def calculate(self):
        """Make new Interrogation object from (modified) concordance lines"""
        from corpkit.process import interrogation_from_conclines
        return interrogation_from_conclines(self)

    def shuffle(self, inplace=False):
        """Shuffle concordance lines

        :param inplace: Modify current object, or create a new one
        :type inplace: `bool`

        :Example:

        >>> lines[:4].shuffle()
            3  01  1-01.txt.conll   through the grand canyon  area       and then phoenix and i sp
            1  01  1-01.txt.conll  e 're in tucson , then up  north      to flagstaff , then we we
            0  01  1-01.txt.conll                  we 're in  tucson     , then up north to flagst
            2  01  1-01.txt.conll  tucson , then up north to  flagstaff  , then we went through th

        """
        import random
        index = list(self.index)
        random.shuffle(index)
        shuffled = self.ix[index]
        shuffled.reset_index()
        if inplace:
            self = shuffled
        else:
            return shuffled

    def edit(self, *args, **kwargs):
        """
        Delete or keep rows by subcorpus or by middle column text.

        >>> skipped = conc.edit(skip_entries=r'to_?match')
        """

        from corpkit.editor import editor
        return editor(self, *args, **kwargs)

    def __str__(self):
        return self.format(print_it=False)

    def __repr__(self):
        return self.format(print_it=False)

    def less(self, **kwargs):
        import pydoc
        pydoc.pipepager(self.format(print_it=False, **kwargs), cmd='less -X -R -S')

class Interrodict(OrderedDict):
    """
    A class for interrogations that do not fit in a single-indexed DataFrame.

    Individual interrogations can be looked up via dict keys, indexes or attributes:

    :Example:

    >>> out_data['WSJ'].results
    >>> out_data.WSJ.results
    >>> out_data[3].results

    Methods for saving, editing, etc. are similar to 
    :class:`corpkit.corpus.Interrogation`. Additional methods are available for 
    collapsing into single (multi-indexed) DataFrames.

    This class is now deprecated, in favour of a multiindexed DataFrame.
    """
    
    def __init__(self, data):
        from corpkit.process import makesafe
        if isinstance(data, list):
            data = OrderedDict(data)
        # attribute access
        for k, v in data.items():
            setattr(self, makesafe(k), v)
        self.query = None
        super(Interrodict, self).__init__(data)

    def __getitem__(self, key):
        """allow slicing, indexing"""
        from corpkit.process import makesafe
        # allow slicing
        if isinstance(key, slice):
            n = OrderedDict()
            for ii in range(*key.indices(len(self))):
                n[self.keys()[ii]] = self[ii]
            return Interrodict(n)
        # allow integer index
        elif isinstance(key, int):
            return next(v for i, (k, v) in enumerate(self.items()) if i == key)
            #return self.subcorpora.__getitem__(makesafe(self.subcorpora[key]))
        # dict key access
        else:
            try:
                return OrderedDict.__getitem__(self, key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    def __setitem__(self, key, value):
        from corpkit.process import makesafe
        setattr(self, makesafe(key), value)
        super(Interrodict, self).__setitem__(key, value)
        
    def __repr__(self):
        return "<%s instance: %d items>" % (classname(self), len(self))

    def __str__(self):
        return "<%s instance: %d items>" % (classname(self), len(self))

    def edit(self, *args, **kwargs):
        """Edit each value with :func:`~corpkit.interrogation.Interrogation.edit`.

        See :func:`~corpkit.interrogation.Interrogation.edit` for possible arguments.

        :returns: A :class:`corpkit.interrogation.Interrodict`
        """

        from corpkit.editor import editor
        return editor(self, *args, **kwargs)

    def multiindex(self):

        """Create a `pandas.MultiIndex` version of results.

        :Example:

        >>> d = corpora.interrogate({F: 'compound', GL: '^risk'}, show=L)
        >>> d.keys()
            ['CHT', 'WAP', 'WSJ']
        >>> d['CHT'].results
            ....  health  cancer  security  credit  flight  safety  heart
            1987      87      25        28      13       7       6      4
            1988      72      24        20      15       7       4      9
            1989     137      61        23      10       5       5      6
        >>> d.multiindex().results
            ...               health  cancer  credit  security  downside  
            Corpus Subcorpus                                             
            CHT    1987           87      25      13        28        20 
                   1988           72      24      15        20        12 
                   1989          137      61      10        23        10                                                      
            WAP    1987           83      44       8        44        10 
                   1988           83      27      13        40         6 
                   1989           95      77      18        25        12 
            WSJ    1987           52      27      33         4        21 
                   1988           39      11      37         9        22 
                   1989           55      47      43         9        24 

        :returns: A :class:`corpkit.interrogation.Interrogation`
        """

        import pandas as pd
        import numpy as np
        from itertools import product
        from corpkit.interrogation import Interrodict, Interrogation

        query = self.query

        def trav(dct, parents={}, level=0, colset=set(),
                 results=list(), myparname=[]):
            from collections import defaultdict

            columns = False
            if hasattr(dct, 'items'):
                parents[level] = list(dct.keys())
                level += 1
                for k, v in list(dct.items()):
                    pars = myparname + [k]
                    # the below is only for python3
                    #pars = [*myparname, k]
                    trav(v, parents=parents, level=level,
                         results=results, myparname=pars)
            else:
                if parents.get(level):
                    parents[level] |= set(dct.results.index)
                else:
                    parents[level] = set(dct.results.index)
                if not dct.results.empty:
                    for n, ser in dct.results.iterrows():
                        ser.name = tuple(myparname + [ser.name])
                        #ser.name = (*myparname, ser.name)
                        results.append(ser)
                    for c in list(dct.results.columns):
                        colset.add(c)
                    level += 1
            return results

        data = trav(self)
        index = [i.name for i in data]

        # todo: better default for speakers?
        if self.query['subcorpora']:
            nms = {'names': self.query['subcorpora']}
        else:
            nms = {} 
        ix = pd.MultiIndex.from_tuples(index, **nms)
        df = pd.DataFrame(data, index=ix)
        df = df.fillna(0).astype(int)
        df = df[df.sum().sort_values(ascending=False).index]
        totals = df.sum(axis=1)
        return Interrogation(results=df, totals=totals, query=query)

    def save(self, savename, savedir='saved_interrogations', **kwargs):
        """
        Save an interrogation as pickle to `savedir`.

        :param savename: A name for the saved file
        :type savename: `str`
        
        :param savedir: Relative path to directory in which to save file
        :type savedir: `str`
        
        :param print_info: Show/hide stdout
        :type print_info: `bool`
        
        :Example: 

        >>> o = corpus.interrogate(W, 'any')
        ### create ``saved_interrogations/savename.p``
        >>> o.save('savename')

        :returns: None
        """
        from corpkit.other import save
        save(self, savename, savedir=savedir, **kwargs)

    def collapse(self, axis='y'):
        """
        Collapse Interrodict on an axis or along interrogation name.

        :param axis: collapse along x, y or name axis
        :type axis: `str`: x/y/n

        :Example:

        .. code-block:: python

           >>> d = corpora.interrogate({F: 'compound', GL: r'^risk'}, show=L)
           
           >>> d.keys()
               ['CHT', 'WAP', 'WSJ']
           
           >>> d['CHT'].results
               ....  health  cancer  security  credit  flight  safety  heart
               1987      87      25        28      13       7       6      4
               1988      72      24        20      15       7       4      9
               1989     137      61        23      10       5       5      6
           
           >>> d.collapse().results
               ...  health  cancer  credit  security
               CHT    3174    1156     566       697
               WAP    2799     933     582      1127
               WSJ    1812     680    2009       537
           
           >>> d.collapse(axis='x').results
               ...  1987  1988  1989
               CHT   384   328   464
               WAP   389   355   435
               WSJ   428   410   473
           
           >>> d.collapse(axis='key').results
               ...   health  cancer  credit  security
               1987     282     127      65        93
               1988     277     100      70       107
               1989     379     253      83        91
               
        :returns: A :class:`corpkit.interrogation.Interrogation`
        """
        # join on keys ... probably shouldn't transpose like this though!
        if axis.lower()[0] not in ['x', 'y']:
            df = self.values()[0].results
            others = [i.results.T for i in list(self.values())[1:]]
            try:
                df = df.T.join(others).T
            except ValueError:
                for i in self.values()[1:]:
                    df = df.add(i.results, fill_value=0)

            df = df.fillna(0)
        else:
            out = []
            for corpus_name, interro in self.items():
                if axis.lower().startswith('y'):
                    ax = 0
                elif axis.lower().startswith('x'):
                    ax = 1
                data = interro.results.sum(axis=ax)
                data.name = corpus_name
                out.append(data)
            # concatenate and transpose
            df = pd.concat(out, axis=1).T
            # turn NaN to 0, sort
            df = df.fillna(0)
        
        #make interrogation object from df
        if not axis.lower().startswith('x'):
            df = df.edit(sort_by='total', print_info=False)
        else:
            df = df.edit(print_info=False)
        # make sure everything is int, not float
        for col in list(df.results.columns):
            df.results[col] = df.results[col].astype(int)
        return df

    def topwords(self, datatype='n', n=10, df=False, sort=True, precision=2):
        """Show top n results in each corpus alongside absolute or relative frequencies.

        :param datatype: show abs/rel frequencies, or keyness
        :type datatype: `str` (n/k/%)
        :param n: number of result to show
        :type n: `int`
        :param df: return a DataFrame
        :type df: `bool`
        :param sort: Sort results, or show as is
        :type sort: `bool`
        :param precision: float precision to show
        :type precision: `int`
        :Example:

        >>> data.topwords(n=5)
            TBT            %   UST            %   WAP            %   WSJ            %
            health     25.70   health     15.25   health     19.64   credit      9.22
            security    6.48   cancer     10.85   security    7.91   health      8.31
            cancer      6.19   heart       6.31   cancer      6.55   downside    5.46
            flight      4.45   breast      4.29   credit      4.08   inflation   3.37
            safety      3.49   security    3.94   safety      3.26   cancer      3.12

        :returns: None
        """
        from corpkit.other import topwords
        if df:
            return topwords(self, datatype=datatype, n=n, df=True,
                            sort=sort, precision=precision)
        else:
            topwords(self, datatype=datatype, n=n,
                     sort=sort, precision=precision)

    def visualise(self, shape='auto', truncate=8, **kwargs):
        """
        Attempt to visualise Interrodict by using subplots

        :param shape: Layout for the subplots (e.g. `(2, 2)`)
        :type shape: tuple

        :param truncate: Only process the first `n` items in the 
                         class:`corpkit.interrogation.Interrodict`
        :type truncate: `int`

        :param kwargs: specifications to pass to :func:`~corpkit.plotter.plotter`
        :type kwargs: keyword arguments
        """
        import matplotlib.pyplot as plt
        if shape == 'auto':
            shape = (int(len(self) / 2), 2)
        if truncate:
            self = self[:truncate]
        f, axes = plt.subplots(*shape)
        for (name, interro), ax in zip(self.items(), axes.flatten()):
            if kwargs.get('name_format'):
                name = name_format.format(name)
            interro.visualise(name, ax=ax, **kwargs)
        return plt

    def copy(self):
        from corpkit.interrogation import Interrodict
        copied = {}
        for k, v in self.items():
            copied[k] = v
        return Interrodict(copied)

    def flip(self, truncate=30, transpose=True, repeat=False, *args, **kwargs):
        """
        Change the dimensions of :class:`corpkit.interrogation.Interrodict`,
        making column names into keys.

        :param truncate: Get first `n` columns
        :type truncate: `int`/`'all'`

        :param transpose: Flip rows and columns:
        :type transpose: `bool`

        :param repeat: Flip twice, to move columns into key position
        :type repeat: `bool`

        :param kwargs: Arguments to pass to the 
                       :func:`~corpkit.interrogation.Interrogation.edit`
                       method

        :returns: :class:`corpkit.interrogation.Interrodict`
        """
        import pandas as pd
        from corpkit.interrogation import Interrodict

        # copy interrodict
        copied = self.copy()

        # first, flip x axis and keys
        words = list(copied.collapse().results.columns)
        if truncate != 'all':
            words = words[:truncate]

        data = {}
        for word in words:
            wordata = []
            for k, v in copied.items():
                try:
                    point = v.results[word]
                except KeyError:
                    ser = [0] * len(v.results.index)
                    point = pd.Series(ser, index=v.results.index)
                point.name = k
                wordata.append(point)
            df = pd.concat(wordata, axis=1)
            if transpose:
                df = df.T
            df = df.edit(*args, **kwargs)
            # divide each newspaper separately
            data[word] = df
        idi = Interrodict(data)
        if repeat:
            return idi.flip(truncate=truncate, transpose=False, repeat=False)
        else:
            return idi

    def get_totals(self):
        """
        Helper function to concatenate all totals
        """
        lst = []
        # for each interrogation name and data
        for k, v in self.items():
            # get the totals
            tot = v.totals
            # name the totals with the corpus name
            tot.name = k
            # add to a list
            lst.append(tot)
        # turn the list into a dataframe
        return pd.concat(lst, axis=1)
