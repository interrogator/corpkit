"""
corpkit: Corpus and Corpus-like objects
"""

from __future__ import print_function

from lazyprop import lazyprop
from corpkit.process import classname
from corpkit.constants import STRINGTYPE, PYTHON_VERSION

class Corpus(object):
    """
    A class representing a linguistic text corpus, which contains files,
    optionally within subcorpus folders.

    Methods for concordancing, interrogating, getting general stats, getting
    behaviour of particular word, etc.

    Unparsed, tokenised and parsed corpora use the same class, though some
    methods are available only to one or the other. Only unparsed corpora 
    can be parsed, and only parsed/tokenised corpora can be interrogated.
    """

    def __init__(self, path, **kwargs):
        import re
        import operator
        import glob
        import os
        from os.path import join, isfile, isdir, abspath, dirname, basename
        from corpkit.process import determine_datatype

        # levels are 'c' for corpus, 's' for subcorpus and 'f' for file. Which
        # one is determined automatically below, and processed accordingly. We
        # assume it is a full corpus to begin with.

        def get_symbolics(self):
            return {'skip': self.skip,
                    'just': self.just,
                    'symbolic': self.symbolic}

        self.data = None
        self._dlist = None
        self.level = kwargs.pop('level', 'c')
        self.datatype = kwargs.pop('datatype', None)
        self.print_info = kwargs.pop('print_info', True)
        self.symbolic = kwargs.get('subcorpora', False)
        self.skip = kwargs.get('skip', False)
        self.just = kwargs.get('just', False)
        self.kwa = get_symbolics(self)

        if isinstance(path, (list, Datalist)):
            self.path = abspath(dirname(path[0].path.rstrip('/')))
            self.name = basename(self.path)
            self.data = path
            if self.level == 'd':
                self._dlist = path
        elif isinstance(path, STRINGTYPE):
            self.path = abspath(path)
            self.name = basename(path)
        elif hasattr(path, 'path') and path.path:
            self.path = abspath(path.path)
            self.name = basename(path.path)

        # this messy code figures out as quickly as possible what the datatype
        # and singlefile status of the path is. it's messy because it shortcuts
        # full checking where possible some of the shortcutting could maybe be
        # moved into the determine_datatype() funct.
        if self.level == 'd':
            self.singlefile = len(self._dlist) > 1
        else:
            self.singlefile = False
            if os.path.isfile(self.path):
                self.singlefile = True
            else:
                if not isdir(self.path):
                    if isdir(join('data', path)):
                        self.path = abspath(join('data', path))
            
            if self.path.endswith('-parsed') or self.path.endswith('-tokenised'):

                for r, d, f in os.walk(self.path):
                    if not f:
                        continue
                    if isinstance(f, str) and f.startswith('.'):
                        continue
                    if f[0].endswith('conll'):
                        self.datatype = 'conll'
                        break

                if len([d for d in os.listdir(self.path)
                        if isdir(join(self.path, d))]) > 0:
                    self.singlefile = False
                if len([d for d in os.listdir(self.path)
                        if isdir(join(self.path, d))]) == 0:
                    self.level = 's'
            else:
                if self.level == 'c':
                    if not self.datatype:
                        self.datatype, self.singlefile = determine_datatype(
                            self.path)
                if isdir(self.path):
                    if len([d for d in os.listdir(self.path)
                            if isdir(join(self.path, d))]) == 0:
                        self.level = 's'

            # if initialised on a file, process as file
            if self.singlefile and self.level == 'c':
                self.level = 'f'

            # load each interrogation as an attribute
            if kwargs.get('load_saved', False):
                from corpkit.other import load
                from corpkit.process import makesafe
                if os.path.isdir('saved_interrogations'):
                    saved_files = glob.glob(r'saved_interrogations/*')
                    for filepath in saved_files:
                        filename = os.path.basename(filepath)
                        if not filename.startswith(self.name):
                            continue
                        not_filename = filename.replace(self.name + '-', '')
                        not_filename = os.path.splitext(not_filename)[0]
                        if not_filename in ['features', 'wordclasses', 'postags']:
                            continue
                        variable_safe = makesafe(not_filename)
                        try:
                            setattr(self, variable_safe, load(filename))
                            if self.print_info:
                                print(
                                    '\tLoaded %s as %s attribute.' %
                                    (filename, variable_safe))
                        except AttributeError:
                            if self.print_info:
                                print(
                                    '\tFailed to load %s as %s attribute. Name conflict?' %
                                    (filename, variable_safe))

            if self.print_info:
                print('Corpus: %s' % self.path)

    @lazyprop
    def subcorpora(self):
        """A list-like object containing a corpus' subcorpora."""
        import re
        import os
        import operator
        from os.path import join, isdir
        if self.level == 'd':
            return
        if self.data.__class__ == Datalist or isinstance(self.data, (Datalist, list)):
            return self.data
        if self.level == 'c':
            variable_safe_r = re.compile(r'[\W0-9_]+', re.UNICODE)
            sbs = Datalist(sorted([Subcorpus(join(self.path, d), self.datatype, **self.kwa)
                                   for d in os.listdir(self.path)
                                   if isdir(join(self.path, d))],
                                  key=operator.attrgetter('name')), **self.kwa)
            for subcorpus in sbs:
                variable_safe = re.sub(variable_safe_r, '',
                                       subcorpus.name.lower().split(',')[0])
                setattr(self, variable_safe, subcorpus)
            return sbs

    @lazyprop
    def speakerlist(self):
        """A list of speakers in the corpus"""
        from corpkit.build import get_speaker_names_from_parsed_corpus
        return get_speaker_names_from_parsed_corpus(self)

    @lazyprop
    def files(self):
        """A list-like object containing the files in a folder

        >>> corpus.subcorpora[0].files

        """

        import re
        import os
        import operator
        from os.path import join, isdir
        if self.level == 's':
            fls = [f for f in os.listdir(self.path) if not f.startswith('.')]
            fls = [File(f, self.path, self.datatype, **self.kwa) for f in fls]
            fls = sorted(fls, key=operator.attrgetter('name'))
            return Datalist(fls, **self.kwa)
        elif self.level == 'd':
            return self._dlist

    @lazyprop
    def all_filepaths(self):
        """
        Lazy-load a list of all filepaths in a corpus
        """
        if self.level == 'f':
            return [self.path]
        if self.files:
            return [i.path for i in self.files]
        fs = []
        for sc in self.subcorpora:
            for f in sc.files:
                fs.append(f.path)
        return fs

    @lazyprop
    def all_files(self):
        """
        Lazy-load a list of all filepaths in a corpus
        """
        if self.level == 'f':
            return Datalist([self])
        if self.files:
            return self.files
        fs = []
        for sc in self.subcorpora:
            for f in sc.files:
                fs.append(f)
        return Datalist(fs)

    def tfidf(self, search={'w': 'any'}, show=['w'], **kwargs):
        """
        Generate TF-IDF vector representation of corpus
        using interrogate method. All args and kwargs go to 
        :func:`~corpkit.corpus.Corpus.interrogate`.

        :returns: Tuple: the vectoriser and matrix
        """

        from sklearn.feature_extraction.text import TfidfVectorizer
        vectoriser = TfidfVectorizer(input='content',
                                     tokenizer=lambda x: x.split())

        res = self.interrogate(search=search,
                               show=show,
                               **kwargs).results

        # there is also a string repeat method which could be better
        def dupe_string(line):
            """Duplicate line name by line count and return string"""
            return ''.join([(w + ' ') * line[w] for w in line.index])

        ser = res.apply(dupe_string, axis=1)
        vec = vectoriser.fit_transform(ser.values)
        #todo: subcorpora names are lost?
        return vectoriser, vec


    def __str__(self):
        """
        String representation of corpus
        """
        showing = 'subcorpora'
        if getattr(self, 'subcorpora', False):
            sclen = len(self.subcorpora)
        else:
            showing = 'files'
            sclen = len(self.files)

        show = 'Corpus at %s:\n\nData type: %s\nNumber of %s: %d\n' % (
            self.path, self.datatype, showing, sclen)
        val = self.symbolic if self.symbolic else 'default'
        show += 'Subcorpora: %s\n' % val
        if self.singlefile:
            show += '\nCorpus is a single file.\n'
        #if getattr(self, 'symbolic'):
        #    show += 'Symbolic subcorpora: %s\n' % str(self.symbolic)
        if getattr(self, 'skip'):
            show += 'Skip: %s\n' % str(self.skip)
        if getattr(self, 'just'):
            show += 'Just: %s\n' % str(self.just)
        return show

    def __repr__(self):
        """
        Object representation of corpus
        """
        import os
        if not self.subcorpora:
            ssubcorpora = ''
        else:
            ssubcorpora = self.subcorpora
        return "<%s instance: %s; %d subcorpora>" % (
            classname(self), os.path.basename(self.path), len(ssubcorpora))

    def __getitem__(self, key):
        """
        Get attributes from corpus
        todo: symbolic stuff for item selection
        """
        from corpkit.process import makesafe
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            if hasattr(self, 'subcorpora') and self.subcorpora:
                return Datalist([self[ii] for ii in range(
                    *key.indices(len(self.subcorpora)))], **self.kwa)
            elif hasattr(self, 'files') and self.files:
                return Datalist([self[ii] for ii in range(
                    *key.indices(len(self.files)))], **self.kwa)                
        elif isinstance(key, int):
            try:
                return self.subcorpora.__getitem__(makesafe(self.subcorpora[key]))
            except:
                try:
                    return self.subcorpora.__getitem__(self.subcorpora[key])
                except AttributeError:
                    return
        else:
            try:
                return self.subcorpora.__getattribute__(key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    @lazyprop
    def features(self):
        """
        Generate and show basic stats from the corpus, including number of 
        sentences, clauses, process types, etc.

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
        from corpkit.interrogator import interrogator
        from corpkit.other import load
        from corpkit.dictionaries.word_transforms import mergetags
        from corpkit.process import make_savename_for_features

        kwa = {'just_metadata': self.just, 'skip_metadata': self.skip}
        if self.symbolic:
            kwa['subcorpora'] = self.symbolic

        name = make_savename_for_features(obj='features',
                                          corpname=self.name,
                                          subcorpora=self.symbolic)

        savedir = 'saved_interrogations'
        if isfile(join(savedir, name + '.p')):
            try:
                return load(name).results
            except AttributeError:
                return load(name)
        else:
            feat = interrogator(self, 'features', **kwa)
            from corpkit.interrogation import Interrodict
            if isinstance(feat, Interrodict):
                feat = feat.multiindex()
            feat = feat.results
            if isdir(savedir):
                feat.save(name)
            return feat

    @lazyprop
    def wordclasses(self):
        """
        Generate and show basic stats from the corpus, including number of 
        sentences, clauses, process types, etc.

        :Example:

        >>> corpus.wordclasses
            SB   Verb  Noun  Preposition   Determiner ...
            01  26873  8513         7308         5508 ...
            02  25844  7933         6920         3323 ...
            03  18376  5683         4877         3137 ...
            04  20066  6354         5366         4336 ...
        """

        import os
        from os.path import isfile, isdir, join
        from corpkit.interrogator import interrogator
        from corpkit.other import load
        from corpkit.dictionaries.word_transforms import mergetags
        from corpkit.process import make_savename_for_features

        kwa = {'just_metadata': self.just, 'skip_metadata': self.skip}

        wcname = make_savename_for_features(obj='wordclasses',
                                            corpname=self.name,
                                            subcorpora=self.symbolic)

        psname = make_savename_for_features(obj='postags',
                                            corpname=self.name,
                                            subcorpora=self.symbolic)

        savedir = 'saved_interrogations'
        if isfile(join(savedir, wcname + '.p')):
            try:
                return load(wcname).results
            except AttributeError:
                return load(wcname)
        elif isfile(join(savedir, psname)):
            try:
                posdata = load(psname).results
            except AttributeError:
                posdata = load(psname)
            return posdata.edit(
                merge_entries=mergetags,
                sort_by='total').results
        else:
            feat = interrogator(self, show='x',
                subcorpora=self.symbolic, *kwa).results
            if isdir(savedir):
                feat.save(self.name + '-wordclasses')
            return feat

    @lazyprop
    def postags(self):
        """
        Generate and show basic stats from the corpus, including number of 
        sentences, clauses, process types, etc.

        :Example:

        >>> corpus.postags
            SB      NN     VB     JJ     IN     DT 
            01   26873   8513   7308   4809   3704  ...
            02   25844   7933   6920   4313   3620  ...
            03   18376   5683   4877   3067   2616  ...
            04   20066   6354   5366   3587   2767  ...

        """
        import os
        from os.path import isfile, isdir, join
        from corpkit.interrogator import interrogator
        from corpkit.other import load
        from corpkit.dictionaries.word_transforms import mergetags
        from corpkit.process import make_savename_for_features

        psname = make_savename_for_features(obj='postags',
                                    corpname=self.name,
                                    subcorpora=self.symbolic)

        kwa = {'just_metadata': self.just, 'skip_metadata': self.skip}

        savedir = 'saved_interrogations'
        if isfile(join(savedir, psname + '.p')):
            try:
                return load(psname).results
            except AttributeError:
                return load(psname)
        else:
            feat = interrogator(self,
                                show='p',
                                preserve_case=True,
                                subcorpora=self.symbolic,
                                **kwa).results
            if isdir(savedir):
                feat.save(psname)
                wordclss = feat.edit(
                    merge_entries=mergetags,
                    sort_by='total').results
                wordclss.save(self.name + '-wordclasses')
            return feat

    @lazyprop
    def lexicon(self, **kwargs):
        """
        Get a lexicon/frequency distribution from a corpus,
        and save to disk for next time.

        :param kwargs: Arguments to pass to the 
                       :func:`~corpkit.corpus.Corpus.interrogate` method
        :type kwargs: `keyword arguments`

        :returns: a `DataFrame` of tokens and counts
        """
        from os.path import join, isfile, isdir
        from corpkit.interrogator import interrogator
        from corpkit.other import load
        from corpkit.process import make_savename_for_features

        show = kwargs.get('show', ['w'])
        savedir = 'saved_interrogations'
        if isinstance(show, STRINGTYPE):
            show = [show]

        name = make_savename_for_features(obj='lexicon',
                                    corpname=self.name,
                                    subcorpora=self.symbolic)

        kwa = {'just_metadata': self.just, 'skip_metadata': self.skip}

        if isfile(join(savedir, name + '.p')):
            try:
                return load(name)
            except AttributeError:
                pass
        dat = self.interrogate('w', show=show,
                               subcorpora=self.symbolic, **kwa).results
        if isdir(savedir):
            dat.save(name)
        return dat

    def configurations(self, search, **kwargs):
        """
        Get the overall behaviour of tokens or lemmas matching a regular 
        expression. The search below makes DataFrames containing the most 
        common subjects, objects, modifiers (etc.) of 'see':

        :param search: Similar to `search` in the 
                       :func:`~corpkit.corpus.Corpus.interrogate` 
                       method.

                       Valid keys are:

                          - `W`/`L` match word or lemma
                          - `F`: match a semantic role (`'participant'`, `'process'` or 
                            `'modifier'`. If `F` not specified, each role will be 
                            searched for.
        :type search: `dict`

        :Example:

        >>> see = corpus.configurations({L: 'see', F: 'process'}, show=L)
        >>> see.has_subject.results.sum()
            i           452
            it          227
            you         162
            we          111
            he           94

        :returns: :class:`corpkit.interrogation.Interrodict`
        """
        if 'subcorpora' not in kwargs:
            kwargs['subcorpora'] = self.symbolic
        if 'just_metadata' not in kwargs:
            kwargs['just_metadata'] = self.just
        if 'skip_metadata' not in kwargs:
            kwargs['skip_metadata'] = self.skip
        from corpkit.configurations import configurations
        return configurations(self, search, **kwargs)

    def interrogate(self, search='w', *args, **kwargs):
        """
        Interrogate a corpus of texts for a lexicogrammatical phenomenon.

        This method iterates over the files/folders in a corpus, searching the
        texts, and returning a :class:`corpkit.interrogation.Interrogation`
        object containing the results. The main options are `search`, where you
        specify search criteria, and `show`, where you specify what you want to
        appear in the output.

        :Example:

        >>> corpus = Corpus('data/conversations-parsed')
        ### show lemma form of nouns ending in 'ing'
        >>> q = {W: r'ing$', P: r'^N'}
        >>> data = corpus.interrogate(q, show=L)
        >>> data.results
            ..  something  anything  thing  feeling  everything  nothing  morning
            01         14        11     12        1           6        0        1
            02         10        20      4        4           8        3        0
            03         14         5      5        3           1        0        0
            ...                                                               ...

        :param search: What part of the lexicogrammar to search, and what 
                       criteria to match. The `keys` are the thing to be 
                       searched, and values are the criteria. To search parse 
                       trees, use the `T` key, and a Tregex query as the value.
                       When searching dependencies, you can use any of:

                       +--------------------+-------+----------+-----------+-----------+
                       |                    | Match | Governor | Dependent | Head      |
                       +====================+=======+==========+===========+===========+
                       | Word               | `W`   | `G`      | `D`       | `H`       |
                       +--------------------+-------+----------+-----------+-----------+
                       | Lemma              | `L`   | `GL`     | `DL`      | `HL`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | Function           | `F`   | `GF`     | `DF`      | `HF`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | POS tag            | `P`   | `GP`     | `DP`      | `HP`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | Word class         | `X`   | `GX`     | `DX`      | `HX`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | Distance from root | `R`   | `GR`     | `DR`      | `HR`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | Index              | `I`   | `GI`     | `DI`      | `HI`      |
                       +--------------------+-------+----------+-----------+-----------+
                       | Sentence index     | `S`   | `SI`     | `SI`      | `SI`      |
                       +--------------------+-------+----------+-----------+-----------+

                       Values should be regular expressions or wordlists to 
                       match.

        :type search: `dict`

        :Example:

        >>> corpus.interrogate({T: r'/NN.?/' < /^t/'}) # T- nouns, via trees
        >>> corpus.interrogate({W: '^t': P: r'^v'}) # T- nouns, via dependencies

        :param searchmode: Return results matching any/all criteria
        :type searchmode: `str` -- `'any'`/`'all'`

        :param exclude: The inverse of `search`, removing results from search
        :type exclude: `dict` -- `{L: 'be'}`

        :param excludemode: Exclude results matching any/all criteria
        :type excludemode: `str` -- `'any'`/`'all'`

        :param query: A search query for the interrogation. This is only used
                      when `search` is a `str`, or when multiprocessing. When 
                      `search` If `search` is a str, the search criteria can be 
                      passed in as `query, in order to allow the simpler syntax:

                         >>> corpus.interrogate(GL, '(think|want|feel)')

                      When multiprocessing, the following is possible:

                         >>> {'Nouns': r'/NN.?/', 'Verbs': r'/VB.?/'}
                         ### return an :class:`corpkit.interrogation.Interrodict` object:
                         >>> corpus.interrogate(T, q)
                         ### return an :class:`corpkit.interrogation.Interrogation` object:
                         >>> corpus.interrogate(T, q, show=C)

        :type query: `str`, `dict` or `list`

        :param show: What to output. If multiple strings are passed in as a `list`, 
                     results will be colon-separated, in the suppled order. Possible 
                     values are the same as those for `search`, plus options 
                     n-gramming and getting collocates:

                     +------+-----------------------+------------------------+
                     | Show | Gloss                 | Example                |
                     +======+=======================+========================+
                     | N    |  N-gram word          | `The women were`       |
                     +------+-----------------------+------------------------+
                     | NL   |  N-gram lemma         | `The woman be`         |
                     +------+-----------------------+------------------------+
                     | NF   |  N-gram function      | `det nsubj root`       |
                     +------+-----------------------+------------------------+
                     | NP   |  N-gram POS tag       | `DT NNS VBN`           |
                     +------+-----------------------+------------------------+
                     | NX   |  N-gram word class    | `determiner noun verb` |
                     +------+-----------------------+------------------------+
                     | B    |  Collocate word       | `The_were`             |
                     +------+-----------------------+------------------------+
                     | BL   |  Collocate lemma      | `The_be`               |
                     +------+-----------------------+------------------------+
                     | BF   |  Collocate function   | `det_root`             |
                     +------+-----------------------+------------------------+
                     | BP   |  Collocate POS tag    | `DT_VBN`               |
                     +------+-----------------------+------------------------+
                     | BX   |  Collocate word class | `determiner_verb`      |
                     +------+-----------------------+------------------------+

        :type show: `str`/`list` of strings

        :param lemmatise: Force lemmatisation on results. **Deprecated:
                          instead, output a lemma form with the `show` argument**
        :type lemmatise: `bool`

        :param lemmatag: Explicitly pass a POS to lemmatiser (generally when data
                         is unparsed, or when tag cannot be recovered from Tregex query)
        :type lemmatag: `'n'`/`'v'`/`'a'`/`'r'`/`False`

        :param spelling: Convert all to U.S. or U.K. English
        :type spelling: `False`/`'US'`/`'UK'`

        :param dep_type: The kind of Stanford CoreNLP dependency parses you want
                         to use: `'basic-dependencies'`, `'collapsed-dependencies'`,
                         or `'collapsed-ccprocessed-dependencies'`.

        :param save: Save result as pickle to `saved_interrogations/<save>` on 
                     completion
        :type save: `str`

        :param gramsize: Size of n-grams (default 2)
        :type gramsize: `int`

        :param split_contractions: Make `"don't"` et al into two tokens
        :type split_contractions: `bool`

        :param multiprocess: How many parallel processes to run
        :type multiprocess: `int`/`bool` (`bool` determines automatically)

        :param files_as_subcorpora: (**Deprecated, use subcorpora=files**). Treat each file as a subcorpus, ignoring 
                                    actual subcorpora if present
        :type files_as_subcorpora: `bool`

        :param conc: Generate a concordance while interrogating, 
                                 store as `.concordance` attribute
        :type conc: `bool`/`'only'`

        :param coref: Allow counting of pronominal referents
        :type coref: `bool`

        :param representative: Allow copula coreference matching
        :type representative: `bool`

        :param representative: Allow non-copula coreference matching
        :type representative: `bool`        

        :param tgrep: Use `TGrep` for tree querying. TGrep is less expressive 
                      than Tregex, and is slower, but can work without Java.
        :type tgrep: `bool`

        :param just_speakers: Limit search to paricular speakers. If 'each',
                              generate :class:`corpkit.interrogation.Interrodict`
                              for each speaker. If a `list` of speaker names, 
                              generate :class:`corpkit.interrogation.Interrodict`
                              for each named speaker. If compiled regular expression,
                              generate :class:`corpkit.interrogation.Interrogation`
                              with each speaker matching the regex conflated.
        :type just_speakers: `str`/`each`/`list`/`regex`

        :param subcorpora: Use a metadata value as subcorpora. 
                           Passing a list will create a multiindex.
                           `'file'` and `'folder'`/`'default'` are also possible values.
        :type subcorpora: `str`/`list`

        :param just_metadata: A field and regex/list to filter sentences by.
                              Only those matching will be kept
        :type just_metadata: `dict`

        :param skip_metadata: A field and regex/list to filter sentences by.
                              Those matching will be skipped.
        :type skip_metadata: `dict`

        :param discard: When returning many (i.e. millions) of results, memory can be
                        a problem. Setting a discard value will ignore results occurring
                        infrequently in a subcorpus. An ``int`` will remove any result
                        occurring ``n`` times or fewer. A float will remove this proportion
                        of results (i.e. 0.1 will remove 10 per cent)
        :type discard: ``int``/``float``

        :returns: A :class:`corpkit.interrogation.Interrogation` object, with 
                  `.query`, `.results`, `.totals` attributes. If multiprocessing is 
                  invoked, result may be multiindexed.
        """
        from corpkit.interrogator import interrogator
        import pandas as pd
        par = kwargs.pop('multiprocess', None)
        kwargs.pop('corpus', None)

        if self.datatype != 'conll':
            raise ValueError('You need to parse or tokenise the corpus before searching.')
        
        # handle symbolic structures
        subcorpora = False
        if self.symbolic:
            subcorpora = self.symbolic
        if kwargs.get('subcorpora', False):
            subcorpora = kwargs.pop('subcorpora')
        if subcorpora in ['default', 'folder', 'folders']:
            subcorpora = False
        if subcorpora in ['file', 'files']:
            subcorpora = False
            kwargs['files_as_subcorpora'] = True

        if self.skip:
            if kwargs.get('skip_metadata'):
                kwargs['skip_metadata'].update(self.skip)
            else:
                kwargs['skip_metadata'] = self.skip

        if self.just:
            if kwargs.get('just_metadata'):
                kwargs['just_metadata'].update(self.just)
            else:
                kwargs['just_metadata'] = self.just

        kwargs.pop('subcorpora', False)

        if par and self.subcorpora:
            if isinstance(par, int):
                kwargs['multiprocess'] = par
            res = interrogator(self.subcorpora, search,
                                subcorpora=subcorpora, *args, **kwargs)
        else:
            kwargs['multiprocess'] = par
            res = interrogator(self, search,
                                subcorpora=subcorpora, *args, **kwargs)

        if kwargs.get('conc', False) == 'only':
            return res

        from corpkit.interrogation import Interrodict
        if isinstance(res, Interrodict) and kwargs.get('use_interrodict'):
            return res
        elif isinstance(res, Interrodict) and not kwargs.get('use_interrodict'):
            return res.multiindex()
        else:
            from corpkit.process import get_index_name
            js = kwargs.get('just_speakers', False)
            ixnames = get_index_name(self, subcorpora, js)
            if ixnames:
                res.results.index.name = ixnames

        # sort by total
        ind = list(res.results.index)
        if isinstance(res.results, pd.DataFrame):
            if not res.results.empty:
                res.results = res.results[list(res.results.sum().sort_values(ascending=False).index)]
                res.results = res.results.astype(int)

            if all(i == 'none' or str(i).isdigit() for i in ind):
                longest = max([len(str(i)) if str(i).isdigit() else 1 for i in ind])
                res.results.index = [str(i).zfill(longest) for i in ind]
                res.results = res.results.sort_index().astype(int)        
        return res

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
                           **kwargs
                          )
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

    def concordance(self, *args, **kwargs):
        """
        A concordance method for Tregex queries, CoreNLP dependencies,
        tokenised data or plaintext. 

        :Example:

        >>> wv = ['want', 'need', 'feel', 'desire']
        >>> corpus.concordance({L: wv, F: 'root'})
           0   01  1-01.txt.conll                But , so I  feel     like i do that for w
           1   01  1-01.txt.conll                         I  felt     a little like oh , i
           2   01  1-01.txt.conll   he 's a difficult man I  feel     like his work ethic
           3   01  1-01.txt.conll                      So I  felt     like i recognized li
           ...                                                                       ...

        Arguments are the same as :func:`~corpkit.corpus.Corpus.interrogate`, 
        plus a few extra parameters:

        :param only_format_match: If `True`, left and right window will just be
                                  words, regardless of what is in `show`
        :type only_format_match: `bool`

        :param only_unique: Return only unique lines
        :type only_unique: `bool`

        :param maxconc: Maximum number of concordance lines
        :type maxconc: `int`

        :returns: A :class:`corpkit.interrogation.Concordance` instance, with 
                  columns showing filename, subcorpus name, speaker name, left 
                  context, match and right context.
        """

        kwargs.pop('conc', None)
        kwargs.pop('conc', None)
        kwargs.pop('corpus', None)
        return self.interrogate(conc='only', *args, **kwargs)

    def interroplot(self, search, **kwargs):
        """
        Interrogate, relativise, then plot, with very little customisability.
        A demo function.

        :Example:

        >>> corpus.interroplot(r'/NN.?/ >># NP')
        <matplotlib figure>

        :param search: Search as per :func:`~corpkit.corpus.Corpus.interrogate`
        :type search: `dict`
        :param kwargs: Extra arguments to pass to :func:`~corpkit.corpus.Corpus.visualise`
        :type kwargs: `keyword arguments`

        :returns: `None` (but show a plot)
        """
        if isinstance(search, STRINGTYPE):
            search = {'t': search}
        interro = self.interrogate(search=search, show=kwargs.pop('show', 'w'))
        edited = interro.edit('%', 'self', print_info=False)
        edited.visualise(self.name, **kwargs).show()

    def save(self, savename=False, **kwargs):
        """
        Save corpus instance to file. There's not much reason to do this, really.

           >>> corpus.save(filename)

        :param savename: Name for the file
        :type savename: `str`

        :returns: `None`
        """
        from corpkit.other import save
        if not savename:
            savename = self.name
        save(self, savename, savedir=kwargs.pop('savedir', 'data'), **kwargs)

    def make_language_model(self,
                           name,
                           search={'w': 'any'},
                           exclude=False,
                           show=['w', '+1mw'],
                           **kwargs):
        """
        Make a language model for the corpus

        :param name: a name for the model
        :type name: `str`

        :param kwargs: keyword arguments for the interrogate() method
        :type kwargs: `keyword arguments`

        :returns: a :class:`corpkit.model.MultiModel`
        """
        import os
        from corpkit.other import load
        from corpkit.model import MultiModel
        if not name.endswith('.p'):
            namep = name + '.p'
        else:
            namep = name

        # handle symbolic structures
        subcorpora = False
        if self.symbolic:
            subcorpora = self.symbolic
        if kwargs.get('subcorpora', False):
            subcorpora = kwargs.pop('subcorpora')
        kwargs.pop('subcorpora', False)

        jst = kwargs.pop('just_metadata') if 'just_metadata' in kwargs else self.just
        skp = kwargs.pop('skip_metadata') if 'skip_metadata' in kwargs else self.skip
        
        pth = os.path.join('models', namep)
        if os.path.isfile(pth):
            print('Returning saved model: %s' % pth)
            return load(name, loaddir='models')

        # set some defaults if not passed in as kwargs
        #langmod = not any(i.startswith('n') for i in search.keys())

        res = self.interrogate(search,
                               exclude,
                               show,
                               subcorpora=subcorpora,
                               just_metadata=jst,
                               skip_metadata=skp,
                               **kwargs)

        return res.language_model(name, search=search, **kwargs)

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

    def unannotate(annotation, dry_run=True):
        """
        Delete annotation from a corpus

        :param annotation: a tag or field and value
        :type annotation: ``str``/``dict``

        :returns: ``None``
        """
        from corpkit.annotate import annotator
        annotator(self, annotation, dry_run=dry_run, deletemode=True)

class Subcorpus(Corpus):
    """
    Model a subcorpus, containing files but no subdirectories.

    Methods for interrogating, concordancing and configurations are the same as
    :class:`corpkit.corpus.Corpus`.
    """

    def __init__(self, path, datatype, **kwa):
        self.path = path
        kwargs = {'print_info': False, 'level': 's', 'datatype': datatype}
        kwargs.update(kwa)
        self.kwargs = kwargs
        Corpus.__init__(self, self.path, **kwargs)

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<%s instance: %s>" % (classname(self), self.name)

    def __getitem__(self, key):

        from corpkit.process import makesafe

        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            key = list(key.indices(len(self.files)))
            return Datalist(list(self.files)[slice(*key)])
            #bits = [self[i] for i in range(*key.indices(len(self.files)))]
            #return [self[ii] for ii in range(*key.indices(len(self.files)))])
        elif isinstance(key, int):
            return list(self.files)[key]
        else:
            try:
                return self.files.__getattribute__(key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)


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
        if self.path.endswith('.conll'):
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

        if self.datatype == 'tokens':
            import cPickle as pickle
            with open(self.path, "rb", **kwargs) as fo:
                data = pickle.load(fo)
            return data
        else:
            with open(self.path, 'r', **kwargs) as fo:
                data = fo.read()
            return data

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
            return saferead(self)[0]
    
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
        return '\n'.join(text)

class Datalist(object):
    """
    A list-like object containing subcorpora or corpus files.

    Objects can be accessed as attributes, dict keys or by indexing/slicing.

    Methods for interrogating, concordancing and getting configurations are the 
    same as for :class:`corpkit.corpus.Corpus`
    """

    def __init__(self, data, **kwargs):
        import re
        import os
        from os.path import join, isfile, isdir
        from corpkit.process import makesafe
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
        self.symbolic = kwargs.get('symbolic')
        self.just = kwargs.get('just')
        self.skip = kwargs.get('skip')

    def __str__(self):
        stringform = []
        for i in self.data:
            stringform.append(i.name)
        return '\n'.join(stringform)

    def __repr__(self):
        return "<%s instance: %d items>" % (classname(self), len(self))

    def __delitem__(self, key):
        self.__delattr__(key)

    def __getitem__(self, key):

        from corpkit.process import makesafe

        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return Datalist([self[ii] for ii in range(*key.indices(len(self)))])
        elif isinstance(key, int):
            return self.__getitem__(makesafe(self.data[key]))
        else:
            try:
                return self.__getattribute__(key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    def __setitem__(self, key, value):
        from corpkit.process import makesafe, is_number
        if key.startswith('c') and len(key) > 1 and all(
                is_number(x) for x in key[1:]):
            self.__setattr__(key.lstrip('c'), value)
        else:
            self.__setattr__(key, value)

    def __iter__(self):
        for datum in self.data:
            yield datum

    def __len__(self):
        return len(self.data)

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

    def interrogate(self, *args, **kwargs):
        """
        Interrogate the corpus using :func:`~corpkit.corpus.Corpus.interrogate`
        """
        
        kwargs['just'] = self.just
        kwargs['skip'] = self.skip
        kwargs['subcorpora'] = self.symbolic

        from corpkit.interrogator import interrogator
        return interrogator(self, *args, **kwargs)

    def concordance(self, *args, **kwargs):
        """
        Concordance the corpus using :func:`~corpkit.corpus.Corpus.concordance`
        """
        kwargs['just'] = self.just
        kwargs['skip'] = self.skip
        kwargs['subcorpora'] = self.symbolic

        from corpkit.interrogator import interrogator
        return interrogator(self, conc='only', *args, **kwargs)

    def configurations(self, search, **kwargs):
        """
        Get a configuration using :func:`~corpkit.corpus.Corpus.configurations`
        """
        kwargs['just'] = self.just
        kwargs['skip'] = self.skip
        kwargs['subcorpora'] = self.symbolic

        from corpkit.configurations import configurations
        return configurations(self, search, **kwargs)

class Corpora(Datalist):
    """
    Models a collection of Corpus objects. Methods are available for 
    interrogating and plotting the entire collection. This is the highest level 
    of abstraction available.

    :param data: Corpora to model. A `str` is interpreted as a path containing 
                 corpora. A `list` can be a list of corpus paths or 
                 :class:`corpkit.corpus.Corpus` objects. )
    :type data: `str`/`list`
    """

    def __init__(self, data=False, **kwargs):

        # if no arg, load every corpus in data dir
        if not data:
            data = 'data'
            
        # handle a folder containing corpora
        if isinstance(data, STRINGTYPE):
            import os
            from os.path import join, isfile, isdir
            if not os.path.isdir(data):
                raise ValueError('Corpora(str) needs to point to a directory.')
            data = sorted([join(data, d) for d in os.listdir(data)
                           if isdir(join(data, d)) and not d.startswith('.')])
        # otherwise, make a list of Corpus objects
        for index, i in enumerate(data):
            if isinstance(i, str):
                data[index] = Corpus(i, **kwargs)

        # now turn it into a Datalist
        Datalist.__init__(self, data, **kwargs)

    def __repr__(self):
        return "<%s instance: %d items>" % (classname(self), len(self))

    def __getitem__(self, key):
        """allow slicing, indexing"""
        from corpkit.process import makesafe
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return Corpora([self[ii] for ii in range(*key.indices(len(self)))], **kwargs)
        elif isinstance(key, int):
            return self.__getitem__(makesafe(self.data[key]))
        else:
            try:
                return self.__getattribute__(key)
            except:
                from corpkit.process import is_number
                if is_number(key):
                    return self.__getattribute__('c' + key)

    def parse(self, **kwargs):
        """
        Parse multiple corpora

        :param kwargs: Arguments to pass to the
                       :func:`~corpkit.corpus.Corpus.parse` method.
        :returns: :class:`corpkit.corpus.Corpora`

        """
        from corpkit.corpus import Corpora
        objs = []
        for v in list(self):
            objs.append(v.parse(**kwargs))
        return Corpora(objs)

    @lazyprop
    def features(self):
        """
        Generate features attribute for all corpora
        """
        for corpus in self:
            corpus.features

    @lazyprop
    def postags(self):
        """
        Generate postags attribute for all corpora
        """
        for corpus in self:
            corpus.postags

    @lazyprop
    def wordclasses(self):
        """
        Generate wordclasses attribute for all corpora
        """
        for corpus in self:
            corpus.wordclasses
