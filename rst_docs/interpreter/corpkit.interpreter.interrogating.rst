Interrogating corpora
==================

The most powerful thing about *corpkit* is its ability to search parsed corpora for very complex constituency, dependency or token level features.

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
   ... for words matching r'ing$' and \                 # search criterion
   ... not lemma matching 'being' and \                 # exclude criterion
   ... pos matching 'NN' \                              # seach criterion
   ... excluding words matching wordlists.closedclass \ # exclude criterion
   ... showing lemma and pos and function \             # show values
   ... with preserve_case and \                         # boolean keyword arg
   ... not no_punct and \                               # bool keyword arg
   ... excludemode as 'all'                             # keyword arg

