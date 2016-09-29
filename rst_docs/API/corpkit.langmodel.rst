Using language models 
======================

.. warning::

   Language modelling is currently deprecated, while the tool is updated to use `CONLL` formatted data, rather than `CoreNLP XML`. Sorry!


Language models are probability distributions over sequences of words. They are common in a number of natural language processing tasks. In corpus linguistics, they can be used to judge the similarity between texts.

*corpkit*'s :func:`~corpkit.corpus.Corpus.make_language_model` method makes it very easy to generate a language model:

.. code-block:: python

   >>> corpus = Corpus('threads')
   # save as models/savename.p
   >>> lm = corpus.make_language_model('savename')

One simple thing you can do with a language model is pass in a string of text:

.. code-block:: python

   >>> text = ("We can compare an arbitrary string against the models "\
   ...         "created for each subcorpus, in order to find out how  "\
   ...         "similar the text is to the texts in each subcorpus... ")
   # get scores for each subcorpus, and the corpus as a whole
   >>> lm.score(text)

   01       -4.894732
   04       -4.986471
   02       -5.060964
   03       -5.096785
   05       -5.106083
   07       -5.226934
   06       -5.338614
   08       -5.829444
   09       -5.874777
   10       -6.351399
   Corpus   -5.285553

You can also pass in :class:`corpkit.corpus.Subcorpus` objects, subcorpus names or :class:`corpkit.corpus.File` instances.

Customising models
--------------------

Under the hood, *corpkit* interrogates the corpus using some special parameters, then builds a model from the results. This means that you can pass in arbitrary arguments for the :func:`~corpkit.corpus.Corpus.interrogate` method:

.. code-block:: python

   >>> lm = corpus.make_language_model('lemma_model',
   ...                                 show=L,
   ...                                 just_speakers='MAHSA',
   ...                                 multiprocess=2)


Compare subcorpora
-------------------

You can find out which subcorpora are similar using the :func:`~corpkit.model.MultiModel.score` method:

.. code-block:: python

   >>> lm.score('1996')

Or get a complete *DataFrame* of values using :func:`~corpkit.model.MultiModel.score_subcorpora`:

.. code-block:: python

   >>> df = lm.score_subcorpora()


Advanced stuff
----------------

.. note::

   Coming soon
