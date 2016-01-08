class Corpus:
    """A class representing a linguistic text corpus"""

    def __init__(self, path):

        import os
        from corpkit.process import determine_datatype
        
        def get_structure():
            """print structure of corpus and build .subcorpora, .files and .structure"""
            import os
            from corpkit.corpus import Subcorpus
            strep = '\nCorpus: %s\n' % self.abspath
            structdict = {}
            for dirname, subdirlist, filelist in os.walk(self.path):
                if os.path.abspath(dirname) == os.path.abspath(self.path):
                    continue
                structdict[dirname] = filelist
                strep = strep + '\nSubcorpus: %s' % os.path.basename(dirname)
                for fname in filelist:
                    strep = strep + '\n\t%s' % fname
            print strep
            filelist = []
            for fl in structdict.values():
                for f in fl:
                    filelist.append(f)
            subcs = [Subcorpus(i) for i in structdict.keys()]
            return structdict, subcs, filelist

        self.path = path
        self.abspath = os.path.abspath(path)
        self.datatype, self.singlefile = determine_datatype(path)
        self.structure, self.subcorpora, self.files = get_structure()
        self.features = False

    def __str__(self):
        """string representation of corpus"""
        st = 'Corpus at %s:\n\nData type: %s\nNumber of subcorpora: %d\n' \
             'Number of files: %d\n' % (self.abspath, self.datatype, len(self.subcorpora), len(self.files))
        if self.singlefile:
            st = st + '\nCorpus is a single file.\n'
        if self.features is not False:
            if not self.singlefile:
                cols = list(self.features.columns)[:10]
                st = st + '\nFeatures:\n\n' + self.features.head(10).to_string(columns = cols)
            else:
                st = st + '\nFeatures:\n\n' + self.features.head(10).to_string()
        else:
            st = st + '\nFeatures not analysed yet. Use .get_stats() method.\n'
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

    def parse(self, *args, **kwargs):
        from corpkit import make_corpus
        from corpkit.corpus import Corpus
        outpaths = make_corpus(self.path)
        corpora = []
        for p in outpaths:
            corpora.append(Corpus(p))
        return corpora

class Subcorpus(str):
    
    def __init__(self, path):
        self.path = path

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using corpkit.interrogator.interrogator()"""
        from corpkit import interrogator
        return interrogator(self.path, *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using corpkit.conc.conc()"""
        from corpkit import conc
        return conc(self.path, *args, **kwargs)