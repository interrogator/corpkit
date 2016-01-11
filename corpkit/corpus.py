class Corpus:
    """A class representing a linguistic text corpus"""

    def __init__(self, path, **kwargs):

        import os
        from corpkit.process import determine_datatype
        
        def get_structure(print_info = True):
            """print structure of corpus and build .subcorpora, .files and .structure"""
            import os
            from corpkit.corpus import Subcorpus, File
            strep = '\nCorpus: %s\n' % os.path.abspath(self.path)
            structdict = {}
            for dirname, subdirlist, filelist in os.walk(self.path):
                filelist = [File(f, dirname) for f in filelist if not f.startswith('.')]
                if print_info:
                    if os.path.abspath(dirname) == os.path.abspath(self.path):
                        continue
                structdict[dirname] = filelist
                strep = strep + '\nSubcorpus: %s' % os.path.basename(dirname)
                for index, fname in enumerate(filelist):
                    strep = strep + '\n\t%s' % os.path.basename(fname.path)
                    if index > 9:
                        strep = strep + '\n\t... and %d others ...' % (len(filelist) - 10)
                        break
            if print_info:
                print strep
            filelist = []
            for fl in structdict.values():
                for f in fl:
                    filelist.append(f)
            if print_info:
                subcs = [Subcorpus(i) for i in sorted(structdict.keys())]
            else:
                subcs = None
            return structdict, subcs, sorted(filelist)

        self.path = path
        self.abspath = os.path.abspath(path)
        self.datatype, self.singlefile = determine_datatype(path)
        self.structure, self.subcorpora, self.files = get_structure(**kwargs)
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

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using corpkit.conc.conc()"""
        from corpkit import conc
        return conc(self.path, *args, **kwargs)

from corpkit.corpus import Corpus
class Subcorpus(Corpus):
    
    def __init__(self, path):
        self.path = path
        kwargs = {'print_info': False}
        Corpus.__init__(self, path, **kwargs)

    def __str__(self):
        return self.path

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using corpkit.interrogator.interrogator()"""
        from corpkit import interrogator
        return interrogator(self.path, *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using corpkit.conc.conc()"""
        from corpkit import conc
        return conc(self.path, *args, **kwargs)

class File(Corpus):
    
    def __init__(self, path, dirname):
        import os
        self.path = os.path.join(dirname, path)
        kwargs = {'print_info': False}
        Corpus.__init__(self, self.path, **kwargs)

    def __str__(self):
        return self.path

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using corpkit.interrogator.interrogator()"""
        from corpkit import interrogator
        return interrogator(self.path, *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using corpkit.conc.conc()"""
        from corpkit import conc
        return conc(self.path, *args, **kwargs)