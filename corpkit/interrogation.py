def _edit(*args, **kwargs):
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

def _plot(title, *args, **kwargs):
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

class Interrogation(object):
    """
    Stores results of a corpus interrogation, before or after editing.

    .. py:attribute:: results: DataFrame containing counts for each subcorpus
    .. py:attribute:: totals: Series containing summed results DataFrame
    .. py:attribute:: query: dict containing values that generated the result
    .. py:method:: edit(*args, **kwargs)
    .. py:method:: plot(title, **kwargs)
    """
    from corpkit.interrogation import _edit, _plot

    def __init__(self, results = None, totals = None, query = None):

        self.results = results
        self.totals = totals
        self.query = query
        self.edit = _edit
        self.plot = _plot
