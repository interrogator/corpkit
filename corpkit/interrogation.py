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

import pandas as pd
class Results(pd.core.frame.DataFrame):

    def __init__(self, data):
        pd.core.frame.DataFrame.__init__(self, data)

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        return editor(self, *args, **kwargs)

    def plot(self, title, *args, **kwargs):
        """calls corpkit.plotter.plotter()"""
        from corpkit import plotter
        plotter(title, self, *args, **kwargs)


class Totals(pd.core.series.Series):

    def __init__(self, data):
        pd.core.series.Series.__init__(self, data)

    def edit(self, *args, **kwargs):
        """calls corpkit.editor.editor()"""
        from corpkit import editor
        return editor(self, *args, **kwargs)

    def plot(self, title, *args, **kwargs):
        """calls corpkit.plotter.plotter()"""
        from corpkit import plotter
        plotter(title, self, *args, **kwargs)


