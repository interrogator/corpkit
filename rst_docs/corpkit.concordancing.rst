
Concordancing
==============

Concordancing is the task of getting an aligned list of *keywords in context*. Here's a very basic example, using *Industrial Society and Its Future* as a corpus:

.. code-block:: python

   >>> tech = corpus.concordance({W: r'techn*'})
   >>> tech.format(n=10, columns=[L, M, R])


  0    The continued development of  technology     will worsen the situation     
  1  vernments but the economic and  technological  basis of the present society  
  2     They want to make him study  technical      subjects become an executive o
  3   program to acquire some petty  technical      skill then come to work on tim
  4  rom nature are consequences of  technological  progress                      
  5  n them and modern agricultural  technology     has made it possible for the e
  6                      -LRB- Also  technology     exacerbates the effects of cro
  7   changes very rapidly owing to  technological  change                        
  8   they enthusiastically support  technological  progress and economic growth  
  9  e rapid drastic changes in the  technology     and the economy of a society w

Generating a concordance
-------------------------

When using *corpkit*, any interrogation is also optionally a concordance. If you use the ``do_concordancing`` keyword argument, your interrogation will have a ``concordance`` attribute containing concordance lines. Like interrogation results, concordances are stored as *Pandas DataFrames*. ``maxconc`` controls the number of lines produced.

.. code-block:: python

   >>> withconc = corp.interrogate({L: ['man', 'woman', 'person']},
   ...                             show=[W,P],
   ...                             do_concordancing=True,
   ...                             maxconc=500)

   0   T Asian/JJ a/DT disabled/JJ  person/nn    or/cc a/dt woman/nn origin
   1   led/JJ person/NN or/CC a/DT  woman/nn     originally/rb had/vbd no/d
   2    woman/NN or/CC disabled/JJ  person/nn    but/cc a/dt minority/nn of
   3   n/JJ immigrant/JJ abused/JJ  woman/nn     or/cc disabled/jj person/n
   4   ing/VBG weak/JJ -LRB-/-LRB-  women/nns    -rrb-/-rrb- defeated/vbn -

If you like, you can use ``only_format_match=True`` to keep the left and right context simple:

   >>> withconc = corp.interrogate({L: ['man', 'woman', 'person']},
   ...                             show=[W,P],
   ...                             only_format_match=True,
   ...                             do_concordancing=True,
   ...                             maxconc=500)

   0   African an Asian a disabled  person/nn    or a woman originally had 
   1   sian a disabled person or a  woman/nn     originally had no derogato
   2   nt abused woman or disabled  person/nn    but a minority of activist
   3   ller Asian immigrant abused  woman/nn     or disabled person but a m
   4   n image of being weak -LRB-  women/nns    -rrb- defeated -lrb- ameri


If you don't want or need the interrogation data, you can use the :func:`~corpkit.corpus.Corpus.concordance` method:

.. code-block:: python

   >>> conc = corpus.concordance(T, r'/JJ.?/ > (NP <<# /man/)')

Displaying concordance lines
------------------------------

How concordance lines will be displayed really depends on your interpreter and environment. For the most part, though, you'll want to use the :func:`~corpkit.interrogation.Concordance.format` method.

.. code-block:: python

   >>> lines.format(kind='s',
   ...              n=100,
   ...              window=50,
   ...              columns=[L, M, R])

``kind='c'/'l'/'s'`` allows you to print as CSV, LaTeX, or simple string. ``n`` controls the number of results shown. ``window`` controls how much context to show in the left and right columns. ``columns`` accepts a list of column names to show.

Pandas' set_option_ can be used to customise some visualisation defaults.

Working with concordance lines
-------------------------------

You can edit concordance lines using the :func:`~corpkit.interrogation.Concordance.edit` method. You can use this method to keep or remove entries or subcorpora matching regular expressions or lists. Keep in mind that because concordance lines are DataFrames, you can use Pandas' dedicated methods for working with text data.

.. code-block:: python

   ### get just uk variants of words with variant spellings
   >>> from dictionaries import usa_convert
   >>> concs = result.concordance.edit(just_entries=usa_convert.keys())


Concordance objects can be saved just like any other ``corpkit`` object:

.. code-block:: python

   >>> concs.save('adj_modifying_man')

You can also easily turn them into CSV data, or into LaTeX:

.. code-block:: python

   ### pandas methods
   >>> concs.to_csv()
   >>> concs.to_latex()

   ### corpkit method: csv and latex
   >>> concs.format('c', window=20, n=10)
   >>> concs.format('l', window=20, n=10)

The *calculate* method
------------------------

You might have begun to notice that interrogating and concordancing aren't really very different tasks. If we drop the left and right context, and move the data around, we have all the data we get from an interrogation.

For this reason, you can use the :func:`~corpkit.interrogation.Concordance.calculate` method to generate an :class:`corpus.interrogation.Interrogation` object containing a frequency count of the middle column of the concordance as the ``results`` attribute.

Therefore, one method for ensuring accuracy is to:

   1. Run an interrogation, using ``do_concordance=True`` 
   2. Remove false positives from the concordance result using :func:`~corpkit.interrogation.Concordance.edit`
   3. Use the :func:`~corpkit.interrogation.Concordance.calculate` method to regenerate the overall frequencies
   4. Edit, visualise or export the data

If you'd like to randomise the order of your results, you can use ``lines.shuffle()``

.. _set_option: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.set_option.html