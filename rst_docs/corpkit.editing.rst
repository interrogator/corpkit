Editing results
=====================

Corpus interrogation is the task of getting frequency counts for a lexicogrammatical phenomenon in a corpus. Simple absolute frequencies, however, are of limited use. The :func:`~corpkit.interrogation.Interrogation.edit` method allows us to do complex things with our results, including:

.. contents::
   :local:

Each of these will be covered in the sections below. Keep in mind that because results are stored as DataFrames, you can also use Pandas/Numpy/Scipy to manipulate your data in ways not covered here.

Keeping or deleting results and subcorpora
-------------------------------------------

One of the simplest kinds of editing is removing or keeping results or subcorpora. This is done using keyword arguments: `skip_subcorpora`, `just_subcorpora`, `skip_entries`, `just_entries`. The value for each can be:

   1. A string (treated as a regular expression to match)
   2. A list (a list of words to match)
   3. An integer (treated as an index to match)

.. code-block:: python

   >>> criteria = r'ing$'
   >>> result.edit(just_entries = criteria)

.. code-block:: python

   >>> criteria = ['everything', 'nothing', 'anything']
   >>> result.edit(skip_entries = criteria)


.. code-block:: python

   >>> result.edit(just_subcorpora = ['Chapter_10', 'Chapter_11'])

You can also span subcorpora, using a tuple of ``(first_subcorpus, second_subcorpus)``. This works for numerical and non-numerical subcorpus names:

.. code-block:: python

   >>> just_span = result.edit(span_subcorpora = (3, 10))

Editing result names
--------------------

You can use the ``replace_names`` keyword argument to edit the text of each result. If you pass in a string, it is treated as a regular expression to delete from every result:

.. code-block:: python

   >>> ingdel = result.edit(replace_names = r'ing$')

You can also pass in a ``dict`` with the structure of ``{newname: criteria}``:

.. code-block:: python

   >>> replaced = result.edit(replace_names = {'-ing words': r'ing$', '-ed words': r'ed$'})

If you wanted to see how commonly words start with a particular letter, you could do something creative:

.. code-block:: python

   >>> from string import lowercase
   >>> crit = {k.upper() + ' words': r'(?i)^%s.*' % k for k in lowercase}
   >>> firstletter = result.edit(replace_names = crit, sort_by = 'total')

Spelling normalisation
-----------------------

When results are single words, you can normalise to UK/US spelling:

.. code-block:: python

   >>> spelled = result.edit(spelling = 'UK')

You can also perform this step when interrogating a corpus.

Generating relative frequencies
---------------------------------

Because subcorpora often vary in size, it is very common to want to create relative frequency versions of results. The best way to do this is to pass in an ``operation`` and a ``denominator``. The ``operation`` is simply a string denoting a mathematical operation: '+', '-', '*', '/', '%'. The last two of these can be used to get relative frequencies and percentage.

Denominator is what the result will be divided by. Quite often, you can use the string ``'self'``. This means, after all other editing (deleting entries, subcorpora, etc.), use the totals of the result being edited as the denominator. When doing no other editing operations, the two lines below are equivalent:

.. code-block:: python

   >>> rel = result.edit('%', 'self')
   >>> rel = result.edit('%', result.totals)

The best denominator, however, may not simply be the totals for the results being edited. You may instead want to relativise by the total number of words:

.. code-block:: python

.. code-block:: python

   >>> rel = result.edit('%', corpus.features.Words)

Or by some other result you have generated:

.. code-block:: python

   >>> words_with_oo = corpus.interrogate(W, 'oo')
   >>> rel = result.edit('%', words_with_oo.totals)

Keywording
---------------------------------

``corpkit`` treats keywording as an editing task, rather than an interrogation task. This makes it easy to get key nouns, or key Agents, or key grammatical features. To do keywording, use the ``'k'`` operation:

.. code-block:: python

   ### use predefined global variables
   >>> from corpkit import *
   >>> keywords = result.edit(K, SELF)

This finds out which words are key in each subcorpus, compared to the corpus as a whole. You could also pass in word frequency counts from some other source. A wordlist of the British National Corpus is included:

.. code-block:: python

   >>> keywords = result.edit(K, 'bnc')

Sorting
---------------------------------

You can sort results using the ``sort_by`` keyword. Possible values are:

   * 'total' (most common first)
   * 'infreq' (inverse total)
   * 'name' (alphabetical)
   * 'increase' (most increasing)
   * 'decrease' (most decreasing)
   * 'turbulent' (by most change)
   * 'static' (by least change)
   * 'p' (by p value)

.. code-block:: python

   >>> inc = result.edit(sort_by = 'increase', keep_stats = False)

Many of these rely on Scipy's ``linregress` calculator. If you want to keep the generated statistics, use ``keep_stats = True``. 

Calculating trends, P values
---------------------------------

``keep_stats = True`` will cause slopes, p values and stderr to be calculated for each result.

Saving results
----------------

You can save edited results to disk.

.. code-block:: python

   >>> edited.save('savename')

Exporting results
------------------

You can generate CSV data very easily using Pandas:

.. code-block:: python

   >>> result.results.to_csv()