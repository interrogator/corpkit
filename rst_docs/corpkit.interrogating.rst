Interrogating corpora
=====================

Once you've built a corpus, you can search it for linguistic phenomena.

.. contents::
   :local:

Search types
---------------------

Coming soon.

What to show
---------------------

Coming soon.

Excluding results
---------------------


Coming soon.

Working with trees
---------------------

Coming soon.


Working with dependencies
---------------------------

Coming soon.

Multiprocessing
---------------------


Saving interrogations
----------------------

.. code-block:: python

   >>> interro.save('savename')

Interrogation savenames will be prefaced with the name of the corpus interrogated.

You can also quicksave interrogations:

.. code-block:: python

   >>> corpus.interrogate(T, r'/NN.?/', save='savename')