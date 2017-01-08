import os
from corpkit.lazyprop import lazyprop
from corpkit.process import classname

class Corpus(list):

    """Model a corpus with arbitrary depth of subfolders"""

    def __init__(self, path_or_list, **kwargs):

        self.mainpath = kwargs.get('mainpath', False)
        if isinstance(path_or_list, list):
            self.singlefile = False
            self.path = kwargs.pop('root')
            self.name = os.path.basename(self.path)
            self.data = path_or_list
        else:
            # init file here?
            if os.path.isfile(path_or_list):
                self.singlefile = True
                self.path = path_or_list
            elif not os.path.isdir(path_or_list):
                path_or_list = os.path.join('data', path_or_list.strip('/'))
                self.singlefile = False
            else:
                self.singlefile = False
            self.path = os.path.abspath(path_or_list)
            self.name = os.path.basename(path_or_list)
            self.data = False
            if not self.mainpath:
                self.mainpath = path_or_list
            
        self._sliced = kwargs.pop('sliced', False)
        self.just = kwargs.pop('just', False)
        self.skip = kwargs.pop('skip', False)
        self.datatype = 'conll' if self.name.endswith('-parsed') else 'plaintext'

        # do not init a file!
        if self.singlefile:
            return

        if self.data:
            to_init = list(self.data)
        else:
            to_init = self.all_files

        # make a list of either subcorpora or files
        super(Corpus, self).__init__(to_init)

    @lazyprop
    def _data_paths(self):
        """
        Lazy load data paths in a corpus
        """ 
        from corpkit.process import make_filelist
        
        all_files = make_filelist(self.path)
        all_dirs = sorted(list(set(os.path.split(i)[0] for i in all_files 
                       if os.path.isdir(os.path.join(self.path, os.path.split(i)[0])))))

        # now, get just current files and current subcorpora
        immediate = os.listdir(self.path)
        files = [f for f in all_files if os.path.split(f)[1] in immediate]
        dirs = [d for d in all_dirs if os.path.basename(d.rstrip('/')) in immediate]
        
        return all_files, all_dirs, files, dirs, len(all_files)

    @lazyprop
    def subcorpora(self):
        ds = self._data_paths[3]
        return Subcorpus([Subcorpus(d, mainpath=self.mainpath) for d in ds], root=self.path, mainpath=self.mainpath)

    @lazyprop
    def _ndirs(self):
        all_files, all_dirs, files, dirs, l = self._data_paths
        return len(dirs)

    @lazyprop
    def _nfiles(self):
        if self._sliced:
            return len(self.data)
        all_files, all_dirs, files, dirs, l = self._data_paths
        return len(files)

    @lazyprop
    def files(self):
        fs = self._data_paths[2]
        return Subcorpus([File(f, mainpath=self.mainpath) for f in fs], root=self.path, mainpath=self.mainpath)

    @lazyprop
    def all_subcorpora(self):
        ds = self._data_paths[1]
        return Subcorpus([Subcorpus(d, mainpath=self.mainpath) for d in ds], root=self.path, mainpath=self.mainpath)

    @lazyprop
    def all_files(self):
        if self._sliced:
            return list(self.data)
        ds = self._data_paths[0]
        return Subcorpus([File(d, mainpath=self.mainpath) for d in ds], root=self.path, mainpath=self.mainpath)

    @lazyprop
    def _length(self):
        return self._data_paths[4]

    def search(self, search, exclude=False, searchmode='all', excludemode='any', **kwargs):
        from corpkit.interrogator import interrogator
        from corpkit.process import timestring
        kwargs.pop('skip', None)
        kwargs.pop('just', None)
        res = interrogator(self, search, exclude=exclude, just=self.just, skip=self.skip, **kwargs)
        bf = 1 if kwargs.get('multiprocess') else 2
        timestring("Finished! %s total results." % format(len(res), ','), blankfirst=bf)
        return res

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
        if isinstance(key, int):
            return super(Corpus, self).__getitem__(key)
        else:
            return Files(super(Corpus, self).__getitem__(key), root=self.path, sliced=True)

    def sample(self, n, level='f'):
        """
        Get a sample of the corpus

        :param n: amount of data in the the sample. If an ``int``, get n files.
                  if a ``float``, get float * 100 as a percentage of the corpus
        :type n: ``int``/``float``
        :param level: sample subcorpora (``s``) or files (``f``)
        :type level: ``str``
        :returns: a Corpus object
        """
        import random

        if isinstance(n, int):
            if level.lower().startswith('s'):
                rs = random.sample(list(self.subcorpora), n)
                rs = sorted(rs, key=lambda x: x.name)
                return Corpus(Datalist(rs),
                              print_info=False, datatype='conll')
            else:
                fps = list(self.all_files)
                dl = Datalist(random.sample(fps, n))
                return Corpus(dl, level='d',
                              print_info=False, datatype='conll')
        elif isinstance(n, float):
            if level.lower().startswith('s'):
                fps = list(self.subcorpora)
                n = len(fps) / n
                return Corpus(Datalist(random.sample(fps, n)),
                              print_info=False, datatype='conll')
            else:
                fps = list(self.all_files)
                n = len(fps) / n
                return Corpus(Datalist(random.sample(fps, n)), level='d',
                              print_info=False, datatype='conll')

    def delete_metadata(self):
        """
        Delete metadata for corpus. May be needed if corpus is changed
        """
        import os
        os.remove(os.path.join('data', '.%s.json' % self.name))

    @lazyprop
    def metadata(self):
        """
        Get metadata for a corpus
        """
        if isinstance(self, (Subcorpus, File)):
            self = self.mainpath
        from corpkit.process import get_corpus_metadata
        return get_corpus_metadata(self, generate=True)

    def parse(self,
              corenlppath=False,
              operations=False,
              copula_head=True,
              speaker_segmentation=False,
              memory_mb=False,
              multiprocess=False,
              split_texts=400,
              outname=False,
              metadata=False,
              coref=True,
              *args,
              **kwargs
             ):
        """
        Parse an unparsed corpus, saving to disk

        :param corenlppath: Folder containing corenlp jar files (use if *corpkit* can't find
                            it automatically)
        :type corenlppath: `str`

        :param operations: Which kinds of annotations to do
        :type operations: `str`

        :param speaker_segmentation: Add speaker name to parser output if your
                                     corpus is script-like
        :type speaker_segmentation: `bool`

        :param memory_mb: Amount of memory in MB for parser
        :type memory_mb: `int`

        :param copula_head: Make copula head in dependency parse
        :type copula_head: `bool`

        :param split_texts: Split texts longer than `n` lines for parser memory
        :type split_text: `int`

        :param multiprocess: Split parsing across n cores (for high-performance 
                             computers)
        :type multiprocess: `int`

        :param folderise: If corpus is just files, move each into own folder
        :type folderise: `bool`

        :param output_format: Save parser output as `xml`, `json`, `conll` 
        :type output_format: `str`

        :param outname: Specify a name for the parsed corpus
        :type outname: `str`

        :param metadata: Use if you have XML tags at the end of lines contaning metadata
        :type metadata: `bool`

        :Example:

        >>> parsed = corpus.parse(speaker_segmentation=True)
        >>> parsed
        <corpkit.corpus.Corpus instance: speeches-parsed; 9 subcorpora>

        :returns: The newly created :class:`corpkit.corpus.Corpus`
        """
        import os
        if outname:
            outpath = os.path.join('data', outname)
            if os.path.exists(outpath):
                raise ValueError('Path exists: %s' % outpath)

        from corpkit.make import make_corpus
        #from corpkit.process import determine_datatype
        #dtype, singlefile = determine_datatype(self.path)
        if self.datatype != 'plaintext':
            raise ValueError(
                'parse method can only be used on plaintext corpora.')
        kwargs.pop('parse', None)
        kwargs.pop('tokenise', None)
        kwargs['output_format'] = kwargs.pop('output_format', 'conll')
        corp = make_corpus(unparsed_corpus_path=self.path,
                           parse=True,
                           tokenise=False,
                           corenlppath=corenlppath,
                           operations=operations,
                           copula_head=copula_head,
                           speaker_segmentation=speaker_segmentation,
                           memory_mb=memory_mb,
                           multiprocess=multiprocess,
                           split_texts=split_texts,
                           outname=outname,
                           metadata=metadata,
                           coref=coref,
                           *args,
                           **kwargs)
        if not corp:
            return

        if os.path.isfile(corp):
            return File(corp)
        else:
            return Corpus(corp)

    def tokenise(self, postag=True, lemmatise=True, *args, **kwargs):
        """
        Tokenise a plaintext corpus, saving to disk

        :param nltk_data_path: Path to tokeniser if not found automatically
        :type nltk_data_path: `str`

        :Example:

        >>> tok = corpus.tokenise()
        >>> tok
        <corpkit.corpus.Corpus instance: speeches-tokenised; 9 subcorpora>

        :returns: The newly created :class:`corpkit.corpus.Corpus`
        """

        from corpkit.make import make_corpus
        #from corpkit.process import determine_datatype
        #dtype, singlefile = determine_datatype(self.path)
        if self.datatype != 'plaintext':
            raise ValueError(
                'parse method can only be used on plaintext corpora.')
        kwargs.pop('parse', None)
        kwargs.pop('tokenise', None)

        c = make_corpus(self.path,
                        parse=False,
                        tokenise=True,
                        postag=postag,
                        lemmatise=lemmatise,
                        *args,
                        **kwargs)
        return Corpus(c)

    def annotate(self, conclines, annotation, dry_run=True):
        """
        Annotate a corpus

        :param conclines: a Concordance or DataFrame containing matches to annotate
        :type annotation: Concordance/DataFrame

        :param annotation: a tag or field and value
        :type annotation: ``str``/``dict``
        
        :param dry_run: Show the annotations to be made, but don't do them
        :type dry_run: ``bool``

        :returns: ``None``
        """
        from corpkit.interrogation import Interrogation
        if isinstance(conclines, Interrogation):
            conclines = getattr(conclines, 'concordance', conclines)
        from corpkit.annotate import annotator
        annotator(conclines, annotation, dry_run=dry_run)
        # regenerate metadata afterward---could be a bit slow?
        if not dry_run:
            self.delete_metadata()
            from corpkit.process import make_dotfile
            make_dotfile(self)

    def unannotate(annotation, dry_run=True):
        """
        Delete annotation from a corpus

        :param annotation: a tag or field and value
        :type annotation: ``str``/``dict``

        :returns: ``None``
        """
        from corpkit.annotate import annotator
        annotator(self, annotation, dry_run=dry_run, deletemode=True)


class Files(Corpus):

    def __init__(self, data, **kwargs):

        super(Files, self).__init__(data, **kwargs)
        self.data = data

    def __getitem__(self, key):
        return list.__getitem__(self.data, key)

    def __repr__(self):
        path = ' -> '.join(os.path.relpath(self.path).split('/')[1:])
        return '<%s: %s (n=%s)>' % (self.__class__.__name__, path, format(self._nfiles, ','))

class Subcorpus(Corpus):

    def __init__(self, data, **kwargs):

        super(Subcorpus, self).__init__(data, **kwargs)

    def __getitem__(self, key):
        return list.__getitem__(self, key)

class File(Corpus):
    """
    Models a corpus file for reading, interrogating, concordancing.

    Methods for interrogating, concordancing and configurations are the same as
    :class:`corpkit.corpus.Corpus`, plus methods for accessing the file contents 
    directly as a `str`, or as a Pandas DataFrame.
    """

    def __init__(self, path, **kwargs):
        import os
        super(File, self).__init__(path, isfile=True)
        if self.path.endswith('.conll') or self.path.endswith('.conllu'):
            self.datatype = 'conll'
        else:
            self.datatype = 'plaintext'
        self.mainpath = kwargs.get('mainpath', False)

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
