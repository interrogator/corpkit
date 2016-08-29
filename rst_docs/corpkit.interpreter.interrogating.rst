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

