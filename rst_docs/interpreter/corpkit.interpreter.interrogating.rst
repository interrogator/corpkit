Interrogating corpora
=======================

The most powerful thing about *corpkit* is its ability to search parsed corpora for very complex constituency, dependency or token level features.

Before we begin, make sure you've ``set`` the corpus as the thing to search:

.. code-block:: bash

   > set nyt-parsed as corpus
   # you could also try just typing `set` ...

.. note::
   
   By default, when using the interpreter, searching also produces concordance lines. If you don't need them, you can use ``toggle conc`` to switch them off, or on again. This can dramatically speed up processing time.

Search examples
--------------------

.. code-block:: bash

   > search corpus ### interactive search helper
   > search corpus for words matching ".*"
   > search corpus for words matching "^[A-M]" showing lemma and word with case_sensitive
   > search corpus for cql matching '[pos="DT"] [pos="NN"]' showing pos and word with coref
   > search corpus for function matching roles.process showing dependent-lemma
   > search corpus for governor-lemma matching processes.verbal showing governor-lemma, lemma
   > search corpus for words matching any and not words matching wordlists.closedclass
   > search corpus for trees matching '/NN.?/ >># NP'
   > search corpus for pos matching NNP showing ngram-word and pos with gramsize as 3
   > etc.

Under the surface, what you are doing is selecting a `Corpus` object to search, and then generating arguments for the :func:`~corpkit.corpus.Corpus.interrogate` method. These arguments, in order, are:

1. `search` criteria
2. `exclude` criteria
3. `show` values
4. Keyword arguments

Here is a syntax example that might help you see how the command gets parsed. Note that there are two ways of setting `exclude` criteria.

.. code-block:: bash

   > search corpus \                                    # select object
   ... for words matching 'ing$' and \                  # search criterion
   ... not lemma matching 'being' and \                 # exclude criterion
   ... pos matching 'NN' \                              # seach criterion
   ... excluding words matching wordlists.closedclass \ # exclude criterion
   ... showing lemma and pos and function \             # show values
   ... with preserve_case and \                         # boolean keyword arg
   ... not no_punct and \                               # bool keyword arg
   ... excludemode as 'all'                             # keyword arg



Working with metadata
----------------------

By default, *corpkit* treats folders within your corpus as subcorpora. If you want to treat files, rather than folders, as subcorpora, you can do:

.. code-block:: bash

   > search corpus for words matching 'ing$' with subcorpora as files

If you have metadata in your corpus, you can use the metadata value as the subcorpora:

.. code-block:: bash

   > search corpus for words matching 'ing$' with subcorpora as speaker

If you don't want to keep specifying the subcorpus structure every time you search a corpus, you have a couple of choices. First, you can set the default subcorpus value with for the session with ``set subcorpora``. This applies the filter globally, to whatever corpus you search:

.. code-block:: bash

   # use speaker metadata as subcorpora
   > set subcorpora as speaker
   # ignore folders, use files as subcorpora
   > set subcorpora as files

You can also define metadata filters, which skip sentences matching a metadata feature, or which keep only sentences matching a metadata feature:

.. code-block:: bash

   # if you have a `year` metadata field, skip this decade
   > set skip year as '^201'
   # if you want only this decade:
   > set keep year as '^201'

If you want to set subcorpora and filters for a corpus, rather than globally, you can do this by passing in the values when you select the corpus:

.. code-block:: bash

   > set mydata-parsed as corpus with year as subcorpora and \
   ... just year as '^201' and skip speaker as 'chomsky'
   # forget filters for this corpus:
   > set mydata-parsed

Sampling a corpus
------------------

Sometimes, your corpus is too big to search quickly. If this is the case, you can use the ``sample`` command to create a randomise sample of the corpus data:

.. code-block:: bash

   > sample 3 subcorpora of corpus
   > sample 100 files of corpus

If you pass in a float, it will try to get a proportional amount of data: ``sample 0.33 subcorpora of corpus`` will return a third of the subcorpora in the corpus.

A sampled corpus becomes an object called ``sampled``. You can then refer to it when searching:

.. code-block:: bash

   > search sampled for words matching '^[abcde]'

Global metadata filters and subcorpus declarations will be observed when searching this corpus as well.
