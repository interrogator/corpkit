import os
from corpkit.lazyprop import lazyprop
from corpkit.process import classname

class Corpus(list):

    """Model a corpus with arbitrary depth of subfolders"""

    def __init__(self, path_or_list, **kwargs):

        if isinstance(path_or_list, list):
            self.singlefile = False
            self.path = kwargs.pop('root')
            self.name = os.path.basename(self.path)
        else:
            if not os.path.isdir(path_or_list):
                path_or_list = os.path.join('data', path_or_list.strip('/'))
            self.path = os.path.abspath(path_or_list)
            self.name = os.path.basename(path_or_list)
            self.singlefile = os.path.isfile(path_or_list)

        self.level = 0 if self.singlefile else False
        self.just = kwargs.pop('just', False)
        self.skip = kwargs.pop('skip', False)
        self._countable = False

        self._slicetype = kwargs.pop('slicetype', None)
        self._fromslice = False

        if self._slicetype:
            self._countable = path_or_list
            self._fromslice = True

        _subs = [Corpus(os.path.abspath(d))
                      for d in os.listdir(self.path)
                      if os.path.isdir(d)]
        if _subs:
            self._countable = _subs
            self._slicetype = 's'
        else:
            self._countable = [File(os.path.abspath(f))
                          for f in os.listdir(self.path)
                          if os.path.isfile(os.path.join(self.path, f))]
            self._slicetype = 'f'
        
        super(Corpus, self).__init__(self._countable)

    @lazyprop
    def _data_paths(self):
        """
        Lazy load data paths in a corpus
        """
        all_files = list()

        for root, ds, fs in os.walk(self.path):
            for f in fs:
                if not f.endswith('.txt') and not f.endswith('.conll'):
                    continue
                fp = os.path.join(root, f)
                all_files.append(fp)

        all_dirs = sorted(list(set(os.path.split(i)[0] for i in all_files 
                       if os.path.isdir(os.path.join(self.path, os.path.split(i)[0])))))

        immediate = os.listdir(self.path)
        files = [f for f in all_files if os.path.split(f)[1] in immediate]
        dirs = [d for d in all_dirs if os.path.basename(d.rstrip('/')) in immediate]
        return all_files, all_dirs, files, dirs, len(all_files)

    @lazyprop
    def subcorpora(self):
        ds = self._data_paths[3]
        return Subcorpus([Subcorpus(d) for d in ds], root=self.path)

    @lazyprop
    def _ndirs(self):
        all_files, all_dirs, files, dirs, l = self._data_paths
        return len(dirs)

    @lazyprop
    def _nfiles(self):
        all_files, all_dirs, files, dirs, l = self._data_paths
        return len(files)

    @lazyprop
    def files(self):
        fs = self._data_paths[2]
        return Subcorpus([File(f) for f in fs], root=self.path)

    @lazyprop
    def all_subcorpora(self):
        ds = self._data_paths[1]
        return Subcorpus([Subcorpus(d) for d in ds], root=self.path)

    @lazyprop
    def all_files(self):
        if self._fromslice and self._slicetype == 'f':
            return Subcorpus([File(d) for d in self._countable], root=self.path)
        ds = self._data_paths[0]
        return Subcorpus([File(d) for d in ds], root=self.path)

    @lazyprop
    def _length(self):
        return self._data_paths[4]

    def search(self, search, exclude=False, searchmode='all', excludemode='any'):
        from corpkit.interrogator import interrogator
        return interrogator(self, search, exclude=exclude, just=self.just, skip=self.skip)

    # alias for search
    def interrogate(self, search, **kwargs):
        return self.search(search=search, **kwargs)

    def __str__(self):
        from corpkit.process import make_tree
        return make_tree(self.path)

    def __repr__(self):
        path = ' -> '.join(os.path.relpath(self.path).split('/')[1:])
        return '<%s: %s --- %ss/%sf>' % (self.__class__.__name__, path, format(self._ndirs, ','), format(self._nfiles, ','))

    def __getitem__(self, key):
        return Subcorpus(super(Corpus, self).__getitem__(key), root=self.path, slicetype=self._slicetype)

class Subcorpus(Corpus):

    def __init__(self, data, **kwargs):

        super(Subcorpus, self).__init__(data, **kwargs)
        self.data = data

    def __getitem__(self, key):
        return list.__getitem__(self.data, key)



class File(Corpus):
    """
    Models a corpus file for reading, interrogating, concordancing.

    Methods for interrogating, concordancing and configurations are the same as
    :class:`corpkit.corpus.Corpus`, plus methods for accessing the file contents 
    directly as a `str`, or as a Pandas DataFrame.
    """

    def __init__(self, path, dirname=False, datatype=False, **kwa):
        import os
        from os.path import join, isfile, isdir
        if dirname:
            self.path = join(dirname, path)
        else:
            self.path = path
        kwargs = {'print_info': False, 'level': 'f', 'datatype': datatype}
        kwargs.update(kwa)
        Corpus.__init__(self, self.path, **kwargs)
        if self.path.endswith('.conll') or self.path.endswith('.conllu'):
            self.datatype = 'conll'
        else:
            self.datatype = 'plaintext'

    def __repr__(self):
        return "<%s instance: %s>" % (classname(self), self.name)

    def __str__(self):
        return self.path
 
    def read(self, **kwargs):
        """
        Read file data. If data is pickled, unpickle first

        :returns: `str`/unpickled data
        """
        from corpkit.constants import OPENER
        with OPENER(self.path, 'r', **kwargs) as fo:
            return fo.read()

    @lazyprop
    def document(self):
        """
        Return a version of the file that can be manipulated

        * For conll, this is a DataFrame
        * For tokens, this is a list of tokens
        * For plaintext, this is a string
        """
        if self.datatype == 'conll':
            from corpkit.conll import parse_conll
            return parse_conll(self.path)
        else:
            from corpkit.process import saferead
            return saferead(self.path)[0]
    
    @lazyprop
    def trees(self):
        """
        Get an OrderedDict of Tree objects in a File
        """
        if self.datatype == 'conll':
            from nltk import Tree
            from collections import OrderedDict
            return OrderedDict({k: Tree.fromstring(v['parse']) \
                                for k, v in sorted(self.document._metadata.items())})
        else:
            raise AttributeError('Data must be parsed to get trees.')

    @lazyprop
    def plain(self):
        """
        Show the sentences in a File as plaintext
        """
        text = []
        if self.datatype == 'conll':
            doc = self.document
            for sent in list(doc.index.levels[0]):
                text.append('%d: ' % sent + ' '.join(list(doc.loc[sent]['w'])))
        else:
            self.read()
        return '\n'.join(text)
