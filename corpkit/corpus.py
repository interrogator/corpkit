from __future__ import print_function
import corpkit
from functools import wraps
from lazyprop import lazyprop

class Corpus(object):
    """
    A class representing a linguistic text corpus, which contains files,
    optionally within subcorpus folders.

    Methods for concordancing, interrogating, getting general stats, getting behaviour of particular word, etc.
    """

    def __init__(self, path, **kwargs):
        import os
        from os.path import join, isfile, isdir, abspath, dirname, basename
        import re
        import operator
        import glob
        from process import determine_datatype
        from corpus import Datalist

        # levels are 'c' for corpus, 's' for subcorpus and 'f' for file. Which 
        # one is determined automatically below, and processed accordingly. We 
        # assume it is a full corpus to begin with.

        self.data = None

        level = kwargs.pop('level', 'c')
        self.datatype = kwargs.pop('datatype', None)
        print_info = kwargs.get('print_info', True)

        if path.__class__ == Datalist or type(path) == list:
            self.path = abspath(dirname(path[0].path.rstrip('/')))
            self.name = basename(self.path)
            self.data = path
        else:
            self.path = abspath(path)
            self.name = basename(path)

        # this messy code figures out as quickly as possible what the datatype 
        # and singlefile status of the path is. it's messy because it shortcuts 
        # full checking where possible some of the shortcutting could maybe be 
        # moved into the determine_datatype() funct.

        if print_info:
            print('Corpus: %s' % self.path)

        self.singlefile = False
        if os.path.isfile(self.path):
            if self.path.endswith('.xml'):
                self.datatype = 'parse'
            self.singlefile = True
        elif self.path.endswith('-parsed'):
            self.datatype = 'parse'
            if len([d for d in os.listdir(self.path) if isdir(join(self.path, d))]) > 0:
                self.singlefile = False
            if len([d for d in os.listdir(self.path) if isdir(join(self.path, d))]) == 0:
                level = 's'
        else:
            if level == 'c':
                if not self.datatype:
                    self.datatype, self.singlefile = determine_datatype(self.path)
            if len([d for d in os.listdir(self.path) if isdir(join(self.path, d))]) == 0:
                level = 's'
        
        # if initialised on a file, process as file
        if self.singlefile and level == 'c':
            level = 'f'

        self.level = level

        # load each interrogation as an attribute
        if kwargs.get('load_saved', False):
            from other import load
            from process import makesafe
            if os.path.isdir('saved_interrogations'):
                saved_files = glob.glob(r'saved_interrogations/*')
                for f in saved_files:
                    filename = os.path.basename(f)
                    if not filename.startswith(self.name):
                        continue
                    not_filename = filename.replace(self.name + '-', '')
                    not_filename = os.path.splitext(not_filename)[0]
                    if not_filename in ['features', 'wordclasses', 'postags']:
                        continue
                    variable_safe = makesafe(not_filename)
                    try:
                        setattr(self, variable_safe, load(filename))
                        if print_info:
                            print('\tLoaded %s as %s attribute.' % (filename, variable_safe))
                    except AttributeError:
                        if print_info:
                            print('\tFailed to load %s as %s attribute. Name conflict?' % (filename, variable_safe))

    @lazyprop
    def subcorpora(self):
        """A list-like object containing a corpus' subcorpora."""
        import re, os, operator
        from os.path import join, isdir
        if self.data.__class__ == Datalist or type(self.data) == list:
            return self.data
        if self.level == 'c':
            variable_safe_r = re.compile('[\W0-9_]+', re.UNICODE)
            sbs = Datalist(sorted([Subcorpus(join(self.path, d), self.datatype) \
                                       for d in os.listdir(self.path) \
                                       if isdir(join(self.path, d))], \
                                       key=operator.attrgetter('name')))
            for subcorpus in sbs:
                variable_safe = re.sub(variable_safe_r, '', \
                    subcorpus.name.lower().split(',')[0])
                setattr(self, variable_safe, subcorpus)
            return sbs

    @lazyprop
    def files(self):
        """A list-like object containing the files in a folder

        >>> corpus.subcorpora[0].files

        """
        import re, os, operator
        from os.path import join, isdir
        if self.level == 's':

            #variable_safe_r = re.compile('[\W0-9_]+', re.UNICODE)
            fs = sorted([File(f, self.path, self.datatype) for f in os.listdir(self.path) \
                        if not f.startswith('.')], key=operator.attrgetter('name'))
            fs = Datalist(fs)
            #for f in fs:
            #    variable_safe = re.sub(variable_safe_r, '', f.name.lower().split('.')[0])
            #    setattr(self, variable_safe, f)
            return fs

    def __str__(self):
        """String representation of corpus"""
        st = 'Corpus at %s:\n\nData type: %s\nNumber of subcorpora: %d\n' % (self.path, self.datatype, len(self.subcorpora))
        if self.singlefile:
            st = st + '\nCorpus is a single file.\n'
        if 'features' in self.__dict__.keys():
            if not self.singlefile:
                cols = list(self.features.columns)[:10]
                st = st + '\nFeatures:\n\n' + self.features.head(10).to_string(columns = cols)
            else:
                st = st + '\nFeatures:\n\n' + self.features.head(10).to_string()
        else:
            st = st + '\nFeatures not analysed yet. Use .features to calculate them.\n'
        return st

    def __repr__(self):
        """object representation of corpus"""
        import os
        if not self.subcorpora:
            ssubcorpora = ''
        else:
            ssubcorpora = self.subcorpora
        return "<corpkit.corpus.Corpus instance: %s; %d subcorpora>" % (os.path.basename(self.path), len(ssubcorpora))

    def __getitem__(self, key):
        from process import makesafe
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return Datalist([self[ii] for ii in range(*key.indices(len(self.subcorpora)))])
        elif type(key) == int:
            return self.subcorpora.__getitem__(makesafe(self.subcorpora[key]))
        else:
            try:
                return self.subcorpora.__getattribute__(key)
            except:
                from process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    # METHODS
    @lazyprop
    def features(self):
        """
        Generate and show basic stats from the corpus, including number of sentences, clauses, process types, etc.

        :Example:

        >>> corpus.features
            SB  Characters  Tokens  Words  Closed class words  Open class words  Clauses
            01       26873    8513   7308                4809              3704     2212   
            02       25844    7933   6920                4313              3620     2270   
            03       18376    5683   4877                3067              2616     1640   
            04       20066    6354   5366                3587              2767     1775

        """
        import os
        from os.path import isfile, isdir, join
        from interrogator import interrogator
        from other import load
        from dictionaries import mergetags

        savedir = 'saved_interrogations'
        if isfile(join(savedir, self.name + '-features.p')):
            try:
                return load(self.name + '-features').results
            except AttributeError:
                return load(self.name + '-features')
        else:
            feat = interrogator(self, 's', 'any').results
            if isdir(savedir):
                feat.save(self.name + '-features')
            return feat

    @lazyprop
    def wordclasses(self):
        """
        Generate and show basic stats from the corpus, including number of sentences, clauses, process types, etc.

        :Example:

        >>> corpus.wordclasses
            SB  Characters  Tokens  Words  Closed class words  Open class words  Clauses
            01       26873    8513   7308                4809              3704     2212   
            02       25844    7933   6920                4313              3620     2270   
            03       18376    5683   4877                3067              2616     1640   
            04       20066    6354   5366                3587              2767     1775

        """
        import os
        from os.path import isfile, isdir, join
        from interrogator import interrogator
        from other import load
        from dictionaries import mergetags

        savedir = 'saved_interrogations'
        if isfile(join(savedir, self.name + '-wordclasses.p')):
            try:
                return load(self.name + '-wordclasses').results
            except AttributeError:
                return load(self.name + '-wordclasses')
        elif isfile(join(savedir, self.name + '-postags.p')):
            try:
                posdata = load(self.name + '-postags').results
            except AttributeError:
                posdata = load(self.name + '-postags')  
            return posdata.edit(merge_entries = mergetags, sort_by = 'total').results
        else:
            feat = interrogator(self, 't', 'any', show = 'pl').results
            if isdir(savedir):
                feat.save(self.name + '-wordclasses')
            return feat

    @lazyprop
    def postags(self):
        """
        Generate and show basic stats from the corpus, including number of sentences, clauses, process types, etc.

        :Example:

        >>> corpus.postags
            SB  NN  VB  JJ  IN DT wo Open class words  Clauses
            01       26873    8513   7308                4809              3704     2212   
            02       25844    7933   6920                4313              3620     2270   
            03       18376    5683   4877                3067              2616     1640   
            04       20066    6354   5366                3587              2767     1775

        """
        import os
        from os.path import isfile, isdir, join
        from interrogator import interrogator
        from other import load
        from dictionaries import mergetags

        savedir = 'saved_interrogations'
        if isfile(join(savedir, self.name + '-postags.p')):
            try:
                return load(self.name + '-postags').results
            except AttributeError:
                return load(self.name + '-postags')
        else:
            feat = interrogator(self, 't', 'any', show = 'p').results
            if isdir(savedir):
                feat.save(self.name + '-postags')
                wc = feat.edit(merge_entries = mergetags, sort_by = 'total').results
                wc.save(self.name + '-wordclasses')
            return feat

    def configurations(self, search, **kwargs):
        """
        Get the overall behaviour of tokens or lemmas matching a regular expression. The search below makes DataFrames containing the most common subjects, objects, modifiers (etc.) of 'see':
        
        :param search: Similar to `search` in the `interrogate()` / `concordance() methods. `W`/`L keys match word or lemma; `F`: key specifies semantic role (`'participant'`, `'process'` or `'modifier'`. If `F` not specified, each role will be searched for. 
        :type search: dict

        :Example:
        
        >>> see = corpus.configurations({L: 'see', F: 'process'}, show = L)
        >>> see.has_subject.results.sum()
            i           452
            it          227
            you         162
            we          111
            he           94

        :returns: :class:`corpkit.interrogation.Interrodict`
        """

        from configurations import configurations
        return configurations(self, search, **kwargs)

    def interrogate(self, search, *args, **kwargs):
        """Interrogate a corpus of texts for a lexicogrammatical phenomenon

        :Example:

        >>> corpus = Corpus('data/conversations-parsed')
        ### show lemma form of nouns ending in 'ing'
        >>> q = {W: r'ing$', P: r'^N'}
        >>> data = corpus.interrogate(q, show = L)
        >>> data.results
            ..  something  anything  thing  feeling  everything  nothing  morning
            01         14        11     12        1           6        0        1   
            02         10        20      4        4           8        3        0   
            03         14         5      5        3           1        0        0
            ...                                                               ...   
        
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
        :type search: str, or, for dependencies, a dict like `{W: 'help', P: r'^V'}`

        :param searchmode: Return results matching any/all criteria
        :type searchmode: str -- `'any'`/`'all'`

        :param exclude: The inverse of `search`, removing results from search
        :type exclude: dict -- `{L: 'be'}`

        :param excludemode: Exclude results matching any/all criteria
        :type excludemode: str -- `'any'`/`'all'`
        
        :param query: A search query for the interrogation
        :type query: 
           - str -- regex/Tregex pattern
           - dict -- `{name: pattern}`
           - list -- word list to match
        
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
        
        :param save: Save result as pickle to `saved_interrogations/<save>` on completion
        :type save: str
        
        :param gramsize: size of ngrams (default 2)
        :type gramsize: int

        :param split_contractions: make `"don't"` et al into two tokens
        :type split_contractions: bool

        :param multiprocess: how many parallel processes to run
        :type multiprocess: int / bool (to determine automatically)

        :param files_as_subcorpora: treat each file as a subcorpus
        :type files_as_subcorpora: bool

        :param do_concordancing: Concordance while interrogating, store as `.concordance` attribute
        :type do_concordancing: bool/'only'

        :param maxconc: Maximum number of concordance lines
        :type maxcond: int

        :returns: A :class:`corpkit.interrogation.Interrogation` object, with `.query`, `.results`, `.totals` attributes. If multiprocessing is \
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
              speaker_segmentation = False, memory_mb = False, multiprocess = False, 
              *args, **kwargs):
        """
        Parse an unparsed corpus, saving to disk

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

        :param multiprocess: Split parsing across n cores (for high-performance computers)
        :type multiprocess: int

        :Example:

        >>> parsed = corpus.parse(speaker_segmentation = True)
        >>> parsed
        <corpkit.corpus.Corpus instance: speeches-parsed; 9 subcorpora>


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

        :param nltk_data_path: path to tokeniser if not found automatically
        :type nltk_data_path: str

        :Example:

        >>> tok = corpus.tokenise()
        >>> tok
        <corpkit.corpus.Corpus instance: speeches-tokenised; 9 subcorpora>

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

        :Example:

        >>> wv = ['want', 'need', 'feel', 'desire']
        >>> corpus.concordance({L: wv, F: 'root'})
           0   01  1-01.txt.xml                But , so I  feel     like i do that for w
           1   01  1-01.txt.xml                         I  felt     a little like oh , i
           2   01  1-01.txt.xml   he 's a difficult man I  feel     like his work ethic 
           3   01  1-01.txt.xml                      So I  felt     like i recognized li
           ...                                                                       ...


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

        :Example:

        >>> corpus.interroplot(r'/NN.?/ >># NP')
        <matplotlib figure>

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

           >>> corpus.save(filename)

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

    Methods for interrogating, concordancing and configurations are the same as 
    :class:`corpkit.corpus.Corpus`."""
    
    def __init__(self, path, datatype):
        self.path = path
        kwargs = {'print_info': False, 'level': 's', 'datatype': datatype}
        Corpus.__init__(self, self.path, **kwargs)

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s; %d files>" % (self.name, \
            len(self.files))

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<corpkit.corpus.Subcorpus instance: %s>" % self.name

    def __getitem__(self, key):

        from process import makesafe

        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return Datalist([self[ii] for ii in range(*key.indices(len(self.files)))])
        elif type(key) == int:
            return self.files.__getitem__(makesafe(self.files[key]))
        else:
            try:
                return self.files.__getattribute__(key)
            except:
                from process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

class File(Corpus):
    """Models a corpus file for reading, interrogating, concordancing"""
    
    def __init__(self, path, dirname, datatype):
        import os
        from os.path import join, isfile, isdir
        self.path = join(dirname, path)
        kwargs = {'print_info': False, 'level': 'f', 'datatype': datatype}
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

    @lazyprop
    def document(self):
        """Return the parsed XML of a parsed file"""
        from corenlp_xml.document import Document
        return Document(self.read())

    def __getitem__(self, key):
        from process import makesafe

        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return Datalist([self[ii] for ii in range(*key.indices(len(self.subcorpora)))])
        elif type(key) == int:
            return self.subcorpora.__getitem__(makesafe(self.subcorpora[key]))
        else:
            try:
                return self.subcorpora.__getattribute__(key)
            except:
                from process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    def read(self, *args, **kwargs):
        """Read file data. If data is pickled, unpickle first

        :returns: str/unpickled data
        """

        if self.datatype == 'tokens':
            import pickle
            with open(self.path, "rb") as fo:
                data = pickle.load(fo)
                return data
        else:
            with open(self.path, 'r') as fo:
                data = fo.read()
                return data

class Datalist(object):
    """
    A list-like object containing subcorpora or corpus files.

    Objects can be accessed as attributes, dict keys or by indexing/slicing.

    Methods for interrogating, concordancing and getting configurations are the same as for :class:`corpkit.corpus.Corpus`
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
        from process import makesafe, is_number
        if key.startswith('c') and len(key) > 1 and all(is_number(x) for x in key[1:]):
            self.__setattr__(key.lstrip('c'), value)
        else:
            self.__setattr__(key, value)

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
        """Interrogate the corpus using :func:`~corpkit.corpus.Corpus.interrogate`"""
        from interrogator import interrogator
        return interrogator(self, *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """Concordance the corpus using :func:`~corpkit.corpus.Corpus.concordance`"""
        from interrogator import interrogator
        return interrogator(self, do_concordancing = 'only', *args, **kwargs)

    def configurations(self, search, **kwargs):
        """Get a configuration using :func:`~corpkit.corpus.Corpus.configurations`"""
        from configurations import configurations
        return configurations(self, search, **kwargs)

from corpus import Datalist
class Corpora(Datalist):
    """
    Models a collection of Corpus objects. Methods are available for interrogating and plotting the entire collection. This is the highest level of abstraction available.

    :param data: Corpora to model
    :type data: str (path containing corpora), list (of corpus paths/:class:`corpkit.corpus.Corpus` objects)
    """

    def __init__(self, data, **kwargs):
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
                data[index] = Corpus(i, **kwargs)

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

    @lazyprop
    def features(self):
        for corpus in self:
            corpus.features

    @lazyprop
    def postags(self):
        for corpus in self:
            corpus.postags

    @lazyprop
    def wordclasses(self):
        for corpus in self:
            corpus.wordclasses
