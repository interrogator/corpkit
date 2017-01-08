import os
from corpkit.lazyprop import lazyprop
from corpkit.corpus import File
from corpkit.process import classname

class RecursiveCorpus(list):

    """Model a corpus with arbitrary depth of subfolders"""

    def __init__(self, path_or_list, **kwargs):

        if isinstance(path_or_list, list):
            self.singlefile = False
            self.path = kwargs.pop('root')
            self.name = os.path.basename(self.path)
        else:
            self.path = os.path.abspath(path_or_list)
            self.name = os.path.basename(path_or_list)
            self.singlefile = os.path.isfile(path_or_list)

        self.parent = kwargs.pop('parent', None)

        self.level = 0 if self.singlefile else False
        self.just = kwargs.pop('just', False)
        self.skip = kwargs.pop('skip', False)

        self._subs = [RecursiveCorpus(os.path.abspath(os.path.join(self.path, d)))
                      for d in os.listdir(self.path)
                      if os.path.isdir(os.path.join(self.path, d))]
        
        super(RecursiveCorpus, self).__init__(self._subs)

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
        return Corpus([Corpus(d) for d in ds], root=self.path, flist=False)

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
        print(fs)
        return Corpus([File(f) for f in fs], root=self.path, flist=True)

    @lazyprop
    def all_subcorpora(self):
        ds = self._data_paths[1]
        return Corpus([Corpus(d) for d in ds], root=self.path)

    @lazyprop
    def all_files(self):
        ds = self._data_paths[0]
        return Corpus([File(d) for d in ds], root=self.path)

    @lazyprop
    def _length(self):
        return self._data_paths[4]

    def search(self, search, exclude=False, searchmode='all', excludemode='any'):
        from corpkit.interrogator import interrogate
        return interrogate(search, exclude=exclude, just=self.just, skip=self.skip)

    def __str__(self):
        from corpkit.process import make_tree
        return make_tree(self.path)

    def __repr__(self):
        name = [self.name]
        while True:
            self = self.parent
            if not self:
                break
            name.append(self.name)
        name = '-->'.join(name)

        return '<%s: %s --- %ss/%sf>' % (self.__class__.__name__, name, format(self._ndirs, ','), format(self._nfiles, ','))

    #def __len__(self):
    #    return self._length

class Corpus(RecursiveCorpus):

    def __init__(self, data, **kwargs):

        super(Corpus, self).__init__(data, **kwargs)
        self.data = data

    def __getitem__(self, key):
        return list.__getitem__(self.data, key)