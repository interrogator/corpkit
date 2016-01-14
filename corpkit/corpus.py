
class Corpus:
    """A class representing a linguistic text corpus, which contains files,
       optionally within subcorpus folders.

       Methods for concordancing, interrogating, getting general stats"""

    def __init__(self, path, **kwargs):


        import os
        import re
        import operator
        from corpkit.process import determine_datatype

        if 'level' in kwargs.keys():
            level = kwargs['level']
        else:
            level = 'c'

        print_info = True
        if 'print_info' in kwargs.keys() and kwargs['print_info'] is False:
            print_info = False

        self.path = path
        self.name = os.path.basename(path)
        self.abspath = os.path.abspath(path)

        # this messy code figures out as quickly as possible what the datatype and singlefile
        # status of the path is. it's messy because it shortcuts full checking where possible
        # some of the shortcutting could maybe be moved into the determine_datatype() funct.

        if os.path.isfile(self.abspath):
            if self.abspath.endswith('.xml'):
                self.datatype = 'parse'
            self.singlefile = True
        elif path.endswith('-parsed'):
            self.datatype = 'parse'
            if len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]) > 0:
                self.singlefile = False
            else:
                self.singlefile = True
                if len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))\
                          and not f.startswith('.')]) > 0:
                    self.singlefile = False
                else:
                    self.singlefile = True
        else:
            if os.path.split(path.rstrip('/'))[0].endswith('-parsed'):
                self.datatype = 'parse'
                if len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))\
                      and not f.startswith('.')]) > 0:
                    self.singlefile = False
                else:
                    self.singlefile = True
            else:
                self.datatype, self.singlefile = determine_datatype(path)
        self.structure = None
        self.subcorpora = None
        self.files = None
        struct = {}
        all_files = []
        if level == 'c':
            print '\nCorpus at: %s\n' % self.abspath
            subcorpora = Datalist(sorted([Subcorpus(os.path.join(self.path, d)) \
                                               for d in os.listdir(self.path) \
                                               if os.path.isdir(os.path.join(self.path, d))], \
                                               key=operator.attrgetter('name')))
            self.subcorpora = subcorpora
            for subcorpus in subcorpora:
                file_list = Datalist(sorted([File(f, subcorpus.path) for f in os.listdir(subcorpus.path) \
                                             if not f.startswith('.')], key=operator.attrgetter('name')))
                struct[subcorpus] = file_list
                if print_info:
                    print 'Subcorpus: %s\n\t%s\n' % (subcorpus.name, \
                                                     '\n\t'.join([f.name for f in file_list[:10]]))
                    if len(file_list) > 10:
                        print '... and %s more' % str(len(file_list) - 10)
                for f in file_list:
                    all_files.append(f)
        
            self.structure = struct

        elif level == 's':
            all_files = sorted([File(f, self.path) for f in os.listdir(self.path) \
                                if not f.startswith('.')], key=operator.attrgetter('name'))

        if level != 'f':
            self.files = Datalist(all_files)

        self.features = False

        # set accessible attribute names for subcorpora and files
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

    def __repr__(self):
        return "<corpkit.corpus.Corpus instance: %s; %d subcorpora; %d files>" % (self.name, len(self.subcorpora), len(self.files))

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
        return Corpus(make_corpus(self.path, *args, **kwargs))

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using corpkit.conc.conc()"""
        from corpkit import conc
        return conc(self.path, *args, **kwargs)

    def interroplot(self, search, *args, **kwargs):
        """interrogate, then plot, with very little customisability"""
        if type(search) == str:
            search = {'t': search}
        quickstart = self.interrogate(search = search, **kwargs)
        edited = quickstart.edit('%', 'self', print_info = False)
        edited.plot(str(self.path), **kwargs)

    def save(self, savename = False, **kwargs):
        """Save data to pickle file"""
        from corpkit import save
        if not savename:
            savename = self.name
        save(self, savename, savedir = 'data', **kwargs)

from corpkit.corpus import Corpus
class Subcorpus(Corpus):
    """Model a subcorpus, so that it can be interrogated and concordanced"""
    
    def __init__(self, path):
        self.path = path
        kwargs = {'print_info': False, 'level': 's'}
        Corpus.__init__(self, self.path, **kwargs)

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s; %d files>" % (self.name, len(self.files))

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s>" % self.name

class File(Corpus):
    """Models a corpus file, for reading, interrogating, concordancing"""
    
    def __init__(self, path, dirname):
        import os
        self.path = os.path.join(dirname, path)
        kwargs = {'print_info': False, 'level': 'f'}
        Corpus.__init__(self, self.path, **kwargs)

    def __repr__(self):
        return "<corpkit.corpus.File instance: %s>" % self.name

    def __str__(self):
        return self.path

    def read(self, *args, **kwargs):
        with open(self.abspath, 'r') as fo:
            data = fo.read()
            return data

class Datalist(object):
    """
    A list-like object containing subcorpora or corpus files that can be accessed
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
            try:
                return self.__getattribute__(key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
        if key.startswith('c'):
            self.__setattr__(key.lstrip('c'), value)

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


from corpkit.corpus import Datalist
class Corpora(Datalist):

    def __init__(self, data):
        Datalist.__init__(self, data)

    def __repr__(self):
        return "<corpkit.corpus.Corpora instance: %d items>" % len(self)

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using corpkit.interrogator.interrogator"""
        from corpkit import interrogator
        return interrogator([s.path for s in self], *args, **kwargs)