Language models 
================

Language models are probability distributions over sequences of words. They are common in a number of natural language processing tasks. In corpus linguistics, they can be used to judge the similarity between texts.

*corpkit* makes it very easy to generate a language model:

.. code-block:: python

   >>> corpus = Corpus('threads')
   # save as models/savename.p
   >>> lm = corpus.make_language_model('savename')

One simple thing you can do with a language model is 

.. code-block:: python

   >>> text = ("We can compare an arbitrary string against the models "\
               "created for each subcorpus, in order to find out how  "\
               "similar the text is to the texts in each subcorpus... ")
   >>> lm.score(text)

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

You can find out which subcorpora are similar:

.. code-block:: python

   >>> lm.score('1996')

Or get a complete *DataFrame* of values:

.. code-block:: python

   >>> df = lm.score_subcorpora()


Advanced stuff
----------------

.. note::

   Coming soon
