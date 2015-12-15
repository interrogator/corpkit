class Interrogation(object):
	"""stores results of a corpus interrogation"""

	def __init__(self, results = None, totals = None, query = None):

		self.results = results
		self.totals = totals
		self.query = query

		def _edit(*args, **kwargs):
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
			from corpkit import plotter
			branch = 'results'
			if 'branch' in kwargs.keys():
				branch = kwargs['branch']
				del kwargs['branch']
			if branch.lower().startswith('r'):
				plotter(title, self.results, *args, **kwargs)
			elif branch.lower().startswith('t'):
				plotter(title, self.totals, *args, **kwargs)

		self.edit = _edit
		self.plot = _plot
