from __future__ import print_function
import corpkit

class Corpus:
    """
    A class representing a linguistic text corpus, which contains files,
    optionally within subcorpus folders.

    Methods for concordancing, interrogating, getting general stats.
    """

    def __init__(self, path, **kwargs):
        import os
        from os.path import join, isfile, isdir
        import re
        import operator
        from process import determine_datatype

        # levels are 'c' for corpus, 's' for subcorpus and 'f' for file. Which 
        # one is determined automatically below, and processed accordingly. We 
        # assume it is a full corpus to begin with.

        level = kwargs.pop('level', 'c')
        print_info = kwargs.get('print_info', True)

        path = os.path.abspath(path)

        self.path = os.path.relpath(path)
        self.name = os.path.basename(path)
        self.abspath = path

        # this messy code figures out as quickly as possible what the datatype 
        # and singlefile status of the path is. it's messy because it shortcuts 
        # full checking where possible some of the shortcutting could maybe be 
        # moved into the determine_datatype() funct.

        self.singlefile = False
        if os.path.isfile(self.abspath):
            if self.abspath.endswith('.xml'):
                self.datatype = 'parse'
            self.singlefile = True
        elif path.endswith('-parsed'):
            self.datatype = 'parse'
            if len([d for d in os.listdir(path) if isdir(join(path, d))]) > 0:
                self.singlefile = False
        else:
            self.datatype, self.singlefile = determine_datatype(path)
            if len([d for d in os.listdir(path) if isdir(join(path, d))]) == 0:
                level = 's'

        self.structure = None
        self.subcorpora = None
        self.files = None

        # these two will become .structure and .files if they exist
        struct = {}
        all_files = []
        
        # if initialised on a file, process as file
        if self.singlefile and level == 'c':
            level = 'f'

        # For corpora, make Datalist of subcorpora, make structure dict, make a
        # Datalist of files, and print useful information
        if level == 'c':
            if print_info:
                print('\nCorpus at: %s\n' % self.abspath)
            subcorpora = Datalist(sorted([Subcorpus(join(self.path, d)) \
                                               for d in os.listdir(self.path) \
                                               if isdir(join(self.path, d))], \
                                               key=operator.attrgetter('name')))
            self.subcorpora = subcorpora
            for sbc in subcorpora:
                
                file_list = [File(f, sbc.path) for f in os.listdir(sbc.path) \
                    if not f.startswith('.')]
                file_list = sorted(file_list, key=operator.attrgetter('name'))
                file_list = Datalist(file_list)
                struct[sbc] = file_list
                if print_info:
                    print('Subcorpus: %s\n\t%s\n' % (sbc.name, \
                        '\n\t'.join([f.name for f in file_list[:10]])))
                    if len(file_list) > 10:
                        print('... and %s more ... \n' % str(len(file_list) - 10))
                for f in file_list:
                    all_files.append(f)
        
            self.structure = struct

        # for subcorpora, we only need the filelist and a simple structure dict
        elif level == 's':
            all_files = sorted([File(f, self.path) for f in os.listdir(self.path) \
                                if not f.startswith('.')], key=operator.attrgetter('name'))
            self.files = Datalist(all_files)
            self.structure = {'.': self.files}
            if print_info:
                print('\nCorpus created with %d files:\n\t%s\n' % (len(self.files), '\n\t'.join([i.name for i in self.files][:10])))
                if len(self.files) > 10:
                    print('... and %s more ... \n' % str(len(self.files) - 10))

        # for non File, we will add files attribute
        if level != 'f':
            self.files = Datalist(all_files)

        # this is the future home of the output of .get_stats()
        self.features = False

        # set accessible attribute names for subcorpora and files
        variable_safe_r = re.compile('[\W0-9_]+', re.UNICODE)
        if self.subcorpora is not None:
            if self.subcorpora and len(self.subcorpora) > 0:
                for subcorpus in self.subcorpora:
                    variable_safe = re.sub(variable_safe_r, '', \
                        subcorpus.name.lower().split(',')[0])
                    setattr(self, variable_safe, subcorpus)
        if self.files is not None:
            if self.files and len(self.files) > 0:
                for f in self.files:
                    variable_safe = re.sub(variable_safe_r, '', f.name.lower().split('.')[0])
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
        """object representation of corpus"""
        if not self.files:
            sfiles = ''
        else:
            sfiles = self.files
        if not self.subcorpora:
            ssubcorpora = ''
        else:
            ssubcorpora = self.subcorpora
        return "<corpkit.corpus.Corpus instance: %s; %d subcorpora; %d files>" % (self.name, len(ssubcorpora), len(sfiles))

    # METHODS
    def get_stats(self, *args):
        """
        Get some basic stats from the corpus, and store as :py:attr:`~corpkit.corpus.Corpus.features`

           >>> corpus.get_stats()

        :returns: None
        """  
        from interrogator import interrogator
        self.features = interrogator(self.path, 's', 'any').results
        print('\nFeatures defined. See .features attribute ...') 

    def interrogate(self, search, *args, **kwargs):
        """Interrogate a corpus of texts for a lexicogrammatical phenomenon

            >>> # show lemma form of nouns ending in 'ing'
            >>> q = {'w': r'ing$', 'p': r'^N'}
            >>> data = corpus.interrogate(q, show = 'l')
        
        :param search: What query should be matching
           - t/tregex
           - w/word
           - l/lemma
           - f/function
           - g/governor
           - d/dependent
           - p/pos
           - i/index
           - n/ngrams
           - s/general stats
        :type search: str, or, for dependencies, a dict like ``{'w': 'help', 'p': r'^V'}``

        :param searchmode: Return results matching any/all criteria
        :type searchmode: str ('any'/'all')

        :param exclude: The inverse of `search`, removing results from search
        :type exclude: dict -- ``{'l': 'be'}``

        :param excludemode: Exclude results matching any/all criteria
        :type excludemode: str ('any'/'all')
        
        :param query: A search query for the interrogation
        :type query: str -- regex/Tregex pattern; dict -- ``{name: pattern}``; list -- word list to match
        
        :param show: What to output. If multiple strings are passed, results will be colon-separated, in order
           - t/tree
           - w/word
           - l/lemma
           - g/governor
           - d/dependent
           - f/function
           - p/pos
           - i/index
           - a/distance from root
        :type show: list of strings

        :param lemmatise: Force lemmatisation on results
        :type lemmatise: bool
           
        :param lemmatag: Explicitly pass a pos to lemmatiser (generally when data is unparsed)
        :type lemmatag: False/'n'/'v'/'a'/'r'
        
        :param spelling: Convert all to U.S. or U.K. English
        :type spelling: False/'US'/'UK'
           
        :param dep_type: The kind of Stanford CoreNLP dependency parses you want to use
        :type dep_type: str -- 'basic-dependencies'/'a', 'collapsed-dependencies'/'b', 'collapsed-ccprocessed-dependencies'/'c'
        
        :param quicksave: Save result as pickle to ```saved_interrogations/str``` on completion
        :type quicksave: str
        
        :param gramsize: size of ngrams (default 2)
        :type gramsize: int

        :param split_contractions: make ``"don't"`` et al into two tokens
        :type split_contractions: bool

        :param multiprocess: how many parallel processes to run
        :type multiprocess: int / bool (to determine automatically)

        :param files_as_subcorpora: treat each file as a subcorpus
        :type files_as_subcorpora: bool

        :returns: A :class:`corpkit.interrogation.Interrogation` object, with ``.query``, ``.results``, ``.totals`` attributes. If multiprocessing is \
        invoked, result may be a :class:`corpkit.interrogation.Interrodict` containing corpus names, queries or speakers as keys.
        """
        from interrogator import interrogator
        par = kwargs.pop('multiprocess', None)
        if par and self.subcorpora:
            if type(par) == int:
                kwargs['multiprocess'] = par
            return interrogator(self.subcorpora, search, *args, **kwargs)
        else:
            return interrogator(self, search, *args, **kwargs)

    def parse(self, corenlppath = False, operations = False, copula_head = True,
              speaker_segmentation = False, memory_mb = False, *args, **kwargs):
        """
        Parse an unparsed corpus, saving to disk

           >>> parsed = corpus.parse(speaker_segmentation = True)

        :param corenlppath: folder containing corenlp jar files
        :type corenlppath: str
                
        :param operations: which kinds of annotations to do
        :type operations: str
        
        :param speaker_segmentation: add speaker name to parser output if your corpus is script-like:
        :type speaker_segmentation: bool

        :param memory_mb: Amount of memory in MB for parser
        :type memory_mb: int

        :param copula_head: Make copula head in dependency parse
        :type copula_head: bool

        :returns: The newly created :class:`corpkit.corpus.Corpus`
        """
        from make import make_corpus
        from corpus import Corpus
        #from process import determine_datatype
        #dtype, singlefile = determine_datatype(self.path)
        if self.datatype != 'plaintext':
            raise ValueError('parse method can only be used on plaintext corpora.')
        kwargs.pop('parse', None)
        kwargs.pop('tokenise', None)
        return Corpus(make_corpus(self.path, parse = True, tokenise = False, 
              corenlppath = corenlppath, operations = operations, copula_head = copula_head,
              speaker_segmentation = speaker_segmentation, memory_mb = memory_mb, *args, **kwargs))

    def tokenise(self, *args, **kwargs):
        """
        Tokenise a plaintext corpus, saving to disk

           >>> tok = corpus.tokenise()

        :param nltk_data_path: path to tokeniser if not found automatically
        :type nltk_data_path: str

        :returns: The newly created :class:`corpkit.corpus.Corpus`
        """
        
        from corpkit import make_corpus
        from corpus import Corpus
        #from process import determine_datatype
        #dtype, singlefile = determine_datatype(self.path)
        if self.datatype != 'plaintext':
            raise ValueError('parse method can only be used on plaintext corpora.')
        kwargs.pop('parse', None)
        kwargs.pop('tokenise', None)

        return Corpus(make_corpus(self.path, parse = False, tokenise = True, *args, **kwargs))

    def concordance(self, *args, **kwargs): 
        """
        A concordance method for Tregex queries, CoreNLP dependencies, 
        tokenised data or plaintext.

           >>> wv = ['want', 'need', 'feel', 'desire']
           >>> corpus.concordance({'l': wv, 'f': 'root'})

        Arguments are the same as :func:`~corpkit.interrogation.Interrogation.interrogate`, plus:

        :param only_format_match: if True, left and right window will just be words, regardless of what is in 'show'
        :type only_format_match: bool

        :param random: randomise lines
        :type random: bool

        :param only_unique: only unique lines
        :type only_unique: bool

        :returns: A :class:`corpkit.interrogation.Concordance` instance

        """

        from interrogator import interrogator
        kwargs.pop('do_concordancing', None)
        kwargs.pop('conc', None)
        return interrogator(self, do_concordancing = 'only', *args, **kwargs)

    def interroplot(self, search, **kwargs):
        """Interrogate, relativise, then plot, with very little customisability. A demo function.

           >>> corpus.interroplot(r'/NN.?/ >># NP')

        :param search: search as per :func:`~corpkit.corpus.Corpus.interrogate`
        :type search: dict
        :param kwargs: extra arguments to pass to :func:`~corpkit.corpus.Corpus.interrogate`/:func:`~corpkit.corpus.Corpus.plot`
        :type kwargs: keyword arguments

        :returns: None (but show a plot)
        """
        if type(search) == str:
            search = {'t': search}
        quickstart = self.interrogate(search = search, **kwargs)
        edited = quickstart.edit('%', 'self', print_info = False)
        edited.plot(str(self.path), **kwargs)

    def save(self, savename = False, **kwargs):
        """Save corpus class to file

           >>> corpus.save()

        :param savename: name for the file
        :type savename: str

        :returns: None
        """
        from corpkit import save
        if not savename:
            savename = self.name
        save(self, savename, savedir = 'data', **kwargs)

from corpus import Corpus
class Subcorpus(Corpus):
    """Model a subcorpus, containing files but no subdirectories.

    Methods for interrogating, concordancing are the same as 
    :class:`corpkit.corpus.Corpus`."""
    
    def __init__(self, path):
        self.path = path
        kwargs = {'print_info': False, 'level': 's'}
        Corpus.__init__(self, self.path, **kwargs)

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s; %d files>" % (self.name, \
            len(self.files))

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s>" % self.name

class File(Corpus):
    """Models a corpus file for reading, interrogating, concordancing"""
    
    def __init__(self, path, dirname):
        import os
        from os.path import join, isfile, isdir
        self.path = join(dirname, path)
        kwargs = {'print_info': False, 'level': 'f'}
        Corpus.__init__(self, self.path, **kwargs)
        if self.path.endswith('.p'):
            self.datatype = 'tokens'
        elif self.path.endswith('.xml'):
            self.datatype = 'parse'
        else:
            self.datatype = 'plaintext'

    def __repr__(self):
        return "<corpkit.corpus.File instance: %s>" % self.name

    def __str__(self):
        return self.path

    def read(self, *args, **kwargs):
        """Read file data. If data is pickled, unpickle first

        :returns: str/unpickled data
        """

        if self.datatype == 'tokens':
            import pickle
            with open(self.abspath, "rb") as fo:
                data = pickle.load(fo)
                return data
        else:
            with open(self.abspath, 'r') as fo:
                data = fo.read()
                return data

class Datalist(object):
    """
    A list-like object containing subcorpora or corpus files.

    Objects can be accessed as attributes, dict keys or by indexing/slicing.

    Methods for interrogating and concordancing are available.
    """

    def __init__(self, data):
        import re
        import os
        from os.path import join, isfile, isdir
        from process import makesafe
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

        from process import makesafe

        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return Datalist([self[ii] for ii in range(*key.indices(len(self)))])
        elif type(key) == int:
            return self.__getitem__(makesafe(self.data[key]))
        else:
            try:
                return self.__getattribute__(key)
            except:
                from process import is_number
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

    def __next__(self): # Python 3: def __next__(self)
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

    def interrogate(self, *args, **kwargs):
        """interrogate the corpus using :func:`~corpkit.corpus.Corpus.interrogate`"""
        from interrogator import interrogator
        return interrogator([s for s in self], *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """interrogate the corpus using :func:`~corpkit.corpus.Corpus.concordance`"""
        from interrogator import interrogator
        return interrogator([s for s in self], do_concordancing = 'only', *args, **kwargs)

from corpus import Datalist
class Corpora(Datalist):
    """
    Models a collection of corpora. Methods are available for interrogating and plotting the entire collection.

    :param data: Corpora to model
    :type data: str (path containing corpora), list (of corpus paths/:class:`corpkit.corpus.Corpus` objects)
    """

    def __init__(self, data):
        from corpus import Corpus
        # handle a folder containing corpora
        if type(data) == str or type(data) == str:
            import os
            from os.path import join, isfile, isdir
            if not os.path.isdir(data):
                raise ValueError('Corpora(str) needs to point to a directory.')
            data = sorted([join(data, d) for d in os.listdir(data) \
                          if isdir(join(data, d))])
        # otherwise, make a list of Corpus objects
        for index, i in enumerate(data):
            if type(i) == str:
                data[index] = Corpus(i)

        # now turn it into a Datalist
        Datalist.__init__(self, data)

    def __repr__(self):
        return "<corpkit.corpus.Corpora instance: %d items>" % len(self)

    def __getitem__(self, key):
        """allow slicing, indexing"""
        from process import makesafe
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return Corpora([self[ii] for ii in range(*key.indices(len(self)))])
        elif type(key) == int:
            return self.__getitem__(makesafe(self.data[key]))
        else:
            try:
                return self.__getattribute__(key)
            except:
                from process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

