class Interrogation:
    """
    Stores results of a corpus interrogation, before or after editing.

    .. py:attribute:: results: DataFrame containing counts for each subcorpus
    .. py:attribute:: totals: Series containing summed results DataFrame
    .. py:attribute:: query: dict containing values that generated the result
    .. py:method:: edit(*args, **kwargs)
    .. py:method:: plot(title, **kwargs)
    """

    def __init__(self, results = None, totals = None, query = None):
        """initialise the class"""
        self.results = results
        self.totals = totals
        self.query = query

    def __str__(self):
        st = 'Corpus interrogation: %s\n\n' % (self.query['path'])
        return st

    def __repr__(self):
        return "<corpkit.interrogation.Interrogation instance: %d total results>" % (self.totals.sum())

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        branch = 'results'
        if 'branch' in kwargs.keys():
            branch = kwargs['branch']
            del kwargs['branch']
        if branch.lower().startswith('r'):
            return editor(self.results, *args, **kwargs)
        elif branch.lower().startswith('t'):
            return editor(self.totals, *args, **kwargs)

    def plot(self, title, *args, **kwargs):
        """calls corpkit.plotter.plotter()"""
        from corpkit import plotter
        branch = 'results'
        if 'branch' in kwargs.keys():
            branch = kwargs['branch']
            del kwargs['branch']
        if branch.lower().startswith('r'):
            plotter(title, self.results, *args, **kwargs)
        elif branch.lower().startswith('t'):
            plotter(title, self.totals, *args, **kwargs)

    def save(self, savename, *args, **kwargs):
        """Save data to pickle file"""
        from corpkit import save
        save(self, savename, *args, **kwargs)

    def quickview(self, n = 25):
        """Print top results from an interrogation or edit"""
        from corpkit import quickview
        quickview(self, n = n)

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
    formatting and editing
    """
    
    def __init__(self, data):
        pd.core.frame.DataFrame.__init__(self, data)

    #def __repr__(self):
        #return 'corpkit.interrogation.Concordance instance: %d lines' % (len(self))

    def save(self, savename, *args, **kwargs):
        """Save data to pickle file"""
        from corpkit import save
        save(self, savename, *args, **kwargs)

    def format(self, *args, **kwargs):
        """format concordance lines"""
        from corpkit.other import concprinter
        concprinter(self, *args, **kwargs)

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        return editor(self, *args, **kwargs)

