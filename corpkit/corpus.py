
class Corpus:
    """A class representing a linguistic text corpus, which contains files,
       optionally within subcorpus folders.

       Methods for concordancing, interrogating, getting general stats"""

    def __init__(self, path, **kwargs):

        import os
        from corpkit.process import determine_datatype
        
        def get_structure(print_info = True):
            """print structure of corpus and build .subcorpora, .files and .structure"""
            import os
            from corpkit.corpus import Subcorpus, File, Datalist
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
            if print_info:
                for k, v in structdict.items():
                    del structdict[k]
                    structdict[Subcorpus(k)] = v
                return structdict, Datalist(subcs), Datalist(sorted(filelist))
            else:
                return structdict, subcs, sorted(filelist)

        self.path = path
        self.name = os.path.basename(path)
        self.abspath = os.path.abspath(path)
        self.datatype, self.singlefile = determine_datatype(path)
        self.structure, self.subcorpora, self.files = get_structure(**kwargs)
        self.features = False

        import re
        variable_safe_r = re.compile('[\W0-9_]+', re.UNICODE)
        if self.subcorpora is not None:
            if self.subcorpora and len(self.subcorpora) > 0:
                for subcorpus in self.subcorpora:
                    variable_safe = re.sub(variable_safe_r, '', os.path.splitext(subcorpus.name.lower())[0])
                    setattr(self, variable_safe, subcorpus)
        if self.files is not None:
            if self.files and len(self.files) > 0:
                for f in self.files:
                    variable_safe = re.sub(variable_safe_r, '', f.name)
                    setattr(self, variable_safe, f)



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
        self.features = interrogator(self.path, 's', 'any').results
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
    """Model a subcorpus, so that it can be interrogated and concordanced"""
    
    def __init__(self, path):
        self.path = path
        kwargs = {'print_info': False}
        Corpus.__init__(self, self.path, **kwargs)

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s>" % self.name

class File(Corpus):
    
    def __init__(self, path, dirname):
        import os
        self.path = os.path.join(dirname, path)
        kwargs = {'print_info': False}
        Corpus.__init__(self, self.path, **kwargs)

    #def __repr__(self):
        #return self.path
    def __repr__(self):
        return "<corpkit.corpus.File instance: %s>" % self.name

    def __str__(self):
        return self.path

    def read(self, *args, **kwargs):
        with open(self.abspath, 'r') as fo:
            data = fo.read()
            return data

class Datalist(object):
    """a list of subcorpora or corpus files that can be accessed
       with indexing, slicing, etc."""

    def __init__(self, data):

        def makesafe(variabletext):
            import re
            from corpkit.process import is_number
            variable_safe_r = re.compile('[\W_]+', re.UNICODE)
            variable_safe = re.sub(variable_safe_r, '', variabletext.name.lower().split('.')[0])
            if is_number(variable_safe):
                variable_safe = 'c' + variable_safe
            return variable_safe

        import re
        import os
        self.current = 0
        if data:
            self.high = len(data)
        else:
            self.high = 0
        self.data = data
        if data and len(data) > 0:
            for subcorpus in data:
                safe_var = makesafe(subcorpus)
                setattr(self, safe_var, subcorpus)

    def __str__(self):
        st = []
        for i in self.data:
            st.append(i.name)
        return '\n'.join(st)

    def __repr__(self):
        return "<corpkit.corpus.Datalist instance: %d items>" % len(self)

    def __delitem__(self, key):
        self.__delattr__(key)

    def __getitem__(self, key):

        def makesafe(variabletext):
            import re
            from corpkit.process import is_number
            variable_safe_r = re.compile('[\W_]+', re.UNICODE)
            variable_safe = re.sub(variable_safe_r, '', variabletext.name.lower().split('.')[0])
            if is_number(variable_safe):
                variable_safe = 'c' + variable_safe
            return variable_safe

        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return [self[ii] for ii in xrange(*key.indices(len(self)))]
        elif type(key) == int:
            return self.__getitem__(makesafe(self.data[key]))
        else:
            return self.__getattribute__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __iter__(self):
        for datum in self.data:
            yield datum

    def __len__(self):
        return len(self.data)

    def next(self): # Python 3: def __next__(self)
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1
