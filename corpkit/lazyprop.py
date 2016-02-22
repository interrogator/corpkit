# this file duplicates lazyprop many times because i can't work out how to
# automatically add the right docstring...

def lazyprop(fn):
    """Lazy loading class attributes, with hard-coded docstrings for now..."""
    attr_name = '_lazy_' + fn.__name__
    if fn.__name__ == 'subcorpora':
        @property
        def _lazyprop(self):
            """A list-like object containing a corpus' subcorpora.

            :Example:

            >>> corpus.subcorpora
            <corpkit.corpus.Datalist instance: 12 items>

            """
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'files':
        @property
        def _lazyprop(self):
            """A list-like object containing the files in a folder.

            :Example:

            >>> corpus.subcorpora[0].files
            <corpkit.corpus.Datalist instance: 240 items>

            """
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'features':
        @property
        def _lazyprop(self):
            """
            Generate and show basic stats from the corpus, including number of sentences, clauses, process types, etc.

            :Example:
    
            >>> corpus.features
                ..  Characters  Tokens  Words  Closed class words  Open class words  Clauses
                01       26873    8513   7308                4809              3704     2212   
                02       25844    7933   6920                4313              3620     2270   
                03       18376    5683   4877                3067              2616     1640   
                04       20066    6354   5366                3587              2767     1775
               
            """
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'document':
        @property
        def _lazyprop(self):
            """Return the parsed XML of a parsed file"""
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'relational':
        @property
        def _lazyprop(self):
            """List of relational processes"""
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'verbal':
        @property
        def _lazyprop(self):
            """List of verbal processes"""
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    elif fn.__name__ == 'mental':
        @property
        def _lazyprop(self):
            """List of mental processes"""
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    else:
        @property
        def _lazyprop(self):
            """Lazy-loaded data.
            """
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    return _lazyprop