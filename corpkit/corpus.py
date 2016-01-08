
class Corpus:
    """A class representing a linguistic text corpus"""

    def __init__(self, path):    
        import os
        from corpkit.build import get_filepaths
        from corpkit.process import determine_datatype
        
        def get_subcorpora():
            """get names of subfolders"""
            import os
            subcorpora = []
            for root, dirs, fs in os.walk(self.path):
                if root not in subcorpora and root != self.path:
                    subcorpora.append(root)
            return subcorpora

        self.path = path
        self.abspath = os.path.abspath(path)
        self.files = get_filepaths(path, ext = False)
        self.datatype, self.singlefile = determine_datatype(path)
        self.subcorpora = get_subcorpora()
        self.features = False

    def __str__(self):
        """string representation of corpus"""
        st = 'Corpus at %s:\n\nData type: %s\nNumber of subcorpora: %d\n' \
             'Number of files: %d\n' % (self.abspath, self.datatype, len(self.subcorpora), len(self.files))
        if self.features is not False:
            cols = list(self.features.columns)[:10]
            st = st + '\nFeatures:\n\n' + self.features.head(10).to_string(columns = cols)
        return st

    # METHODS
    def get_stats(self, *args):
        """get some basic stats"""
        from corpkit import interrogator
        self.features = interrogator(c.path, 's', 'any').results
        print 'Features defined. See .features attribute ...'

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using corpkit.interrogator.interrogator"""
        from corpkit import interrogator
        return interrogator(self.path, *args, **kwargs)
