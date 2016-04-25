Interrogating corpora
=====================

Once you've built a corpus, you can search it for linguistic phenomena.

Coming soon.


Saving interrogations
======================

.. code-block:: python
   >>> interro.save('savename')

Interrogation savenames will be prefaced with the name of the corpus interrogated.

Concordancing
==============

Any interrogation is also optionally a concordance. If you use the ``do_concordancing`` keyword argument, your interrogation will have a ``concordance`` attribute containing concordance lines.

.. code-block:: python
   >>> withconc = corpus.interrogate(T, r'/JJ.?/ > (NP <<# /man/)',
                                     do_concordancing=True, maxconc = 500)

If you don't want or need the interrgation data, you can use the :func:`~corpkit.interrogation.Interrogation.concordance` method:

.. code-block:: python
   >>> conc = corpus.concordance(T, r'/JJ.?/ > (NP <<# /man/)')

Working with concordance lines
===============================

Like interrogation results, concordances are stored as Pandas DataFrames.

You can edit concordance lines using the func:`~corpkit.interrogation.Concordance.edit` method. You can use this method to keep or remove entries or subcorpora matching regular expressions or lists.

.. code-block:: python
   ### get just uk variants of words with variant spellings
   >>> from dictionaries import usa_convert
   >>> concs = result.concordance.edit(just_entries = usa_convert.keys())

Because concordance lines are DataFrames, you can use Pandas' dedicated methods for working with text data.

Concordance objects can be saved just like any other ``corpkit`` object:

.. code-block:: python
   >>> concs.save('adj_modifying_man')

You can also easily turn them into CSV data, or into LaTeX:

.. code-block:: python
   # pandas methods
   >>> concs.to_csv()
   >>> concs.to_latex()

   ### corpkit method: csv and latex
   >>> concs.shuffle().format('c', window = 20, n = 10)
   >>> concs.shuffle().format('l', window = 20, n = 10)

You can use the func:`~corpkit.interrogation.Concordance.calculate` method to generate a frequency count of the middle column of the concordance. Therefore, one method for ensuring accuracy is to:

   1. Run an interrogation, using ``do_concordance = True`` 
   2. Remove false positives from the concordance result
   3. Use the calculate method to regenerate the overall frequency


