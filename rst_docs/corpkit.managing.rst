Managing projects
=================

.. contents::
   :local:

Loading saved data
-------------------

When you're starting a new session, you probably don't want to start totally from scratch. It's handy to be able to load your previous work. You can load data in a few ways.

First, you can use ``corpkit.load()``:

.. code-block:: python

   >>> import corpkit
   >>> nouns = corpkit.load('nouns')

Second, you can use ``corpkit.loader()``, which provides a list of items to load, and asks the user for input:

.. code-block:: python

   >>> import corpkit
   >>> nouns = corpkit.loader()

Third, when instantiating a ``Corpus`` object, you can add ``load_saved = True`` keyword argument to load any saved data belonging to this corpus as an attribute.

.. code-block:: python

   >>> corpus = Corpus('data/psyc-parsed', load_saved = True)

A final alternative approach stores all interrogations within an :class:`corpkit.interrogation.Interrodict` object object:

.. code-block:: python

   >>> import corpkit
   >>> r = corpkit.load_all_results()

Managing multiple corpora
--------------------

``corpkit`` can handle one further level of abstraction for both Corpus and Interrogations. :class:`corpkit.corpus.Corpora` models a collection of :class:`corpkit.corpus.Corpus` objects. To create one, pass in a directory containing corpora, or a list of paths/``Corpus`` objects:

.. code-block:: python

   >>> from corpkit import Corpora
   >>> corpora = Corpora('data')

Individual corpora can be accessed as attributes, by index, or as keys:

.. code-block:: python

   >>> corpora.first
   >>> corpora[0]
   >>> corpora['first']

You can use the :func:`~corpkit.corpus.Corpora.interrogate` method to search them, using the same arguments as you would for :func:`~corpkit.corpus.Corpus.interrogate`.

Interrogating these objects often returns an :class:`corpkit.interrogation.Interrodict` object, which models a collection of DataFrames.

Editing can be performed with :func:`~corpkit.interrogation.Interrodict.edit`. The editor will iterate over each DataFrame in turn, generally returning another ``Interrodict``.

.. note::
   
   There is no ``visualise()`` method for Interrodict objects.

:func:`~corpkit.interrogation.Interrodict.multiindex` can turn an ``Interrodict`` into a `Pandas MultiIndex`:

.. code-block:: python

   >>> multiple_res.multiinedx()

:func:`~corpkit.interrogation.Interrodict.collapse` will collapse one dimension of the ``Interrodict``. You can collapse the x axis (``'x'``), the y axis (``'y'``), or the Interrodict keys (``'k'``).

.. code-block:: python

    >>> d = corpora.interrogate({F: 'compound', GL: r'^risk'}, show = L)
    >>> d.keys()
        ['CHT', 'WAP', 'WSJ']
    >>> d['CHT'].results
        ....  health  cancer  security  credit  flight  safety  heart
        1987      87      25        28      13       7       6      4
        1988      72      24        20      15       7       4      9
        1989     137      61        23      10       5       5      6
    >>> d.collapse().results
        ...  health  cancer  credit  security
        CHT    3174    1156     566       697
        WAP    2799     933     582      1127
        WSJ    1812     680    2009       537
    >>> d.collapse(axis = 'x').results
        ...  1987  1988  1989
        CHT   384   328   464
        WAP   389   355   435
        WSJ   428   410   473
    >>> d.collapse(axis = 'k').results
        ...   health  cancer  credit  security
        1987     282     127      65        93
        1988     277     100      70       107
        1989     379     253      83        91

:func:`~corpkit.interrogation.Interrodict.topwords` quickly shows the top results from every interrogation in the ``Interrodict``.

.. code-block:: python

   >>> data.topwords(n = 5)

.. code-block:: none:

   TBT            %   UST            %   WAP            %   WSJ            %
   health     25.70   health     15.25   health     19.64   credit      9.22
   security    6.48   cancer     10.85   security    7.91   health      8.31
   cancer      6.19   heart       6.31   cancer      6.55   downside    5.46
   flight      4.45   breast      4.29   credit      4.08   inflation   3.37
   safety      3.49   security    3.94   safety      3.26   cancer      3.12


Using the GUI
-------------

Your project can also be understood by the corpkit GUI. If you open it, you can simply select your project via ``Open Project`` and resume work in a graphical environment.