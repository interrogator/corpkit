Interrogating corpora
=====================

Once you've built a corpus, you can search it for linguistic phenomena. This is done with the :func:`~corpkit.corpus.Corpus.interrogate` method.

.. contents::
   :local:

Introduction
--------------

Interrogations can be performed on any :class:`corpkit.corpus.Corpus` object, but also, on :class:`corpkit.corpus.Subcorpus` objects, :class:`corpkit.corpus.File` objects and :class:`corpkit.corpus.Datalist`s (slices of ``Corpus`` objects). You can search plaintext corpora, tokenised corpora or fully parsed corpora using the same method. We'll focus on parsed corpora in this guide.

.. code-block:: python
   
   >>> from corpkit import *
   ### words matching 'woman', 'women', 'man', 'men'
   >>> query = {W: r'/(^wo)m.n/'}
   ### interrogate corpus
   >>> corpus.interrogate(query)
   ### interrogate parts of corpus
   >>> corpus[2:4].interrogate(query)
   >>> corpus.files[:10].interrogate(query)
   >>> corpus.subcorpora.abstract.interrogate(query)

.. note::

   Single capital letter variables in code examples represent lowercase strings ``(W = 'w')``. These variables are made available by doing ``from corpkit import *``. They are used here for readability.

Search types
---------------------

Parsed corpora contain many different kinds of annotation we might like to search. The annotation types, and how to specify them, are given in the table below:

+--------+-----------------------+
| Search | Gloss                 |
+========+=======================+
| W      |  Word                 |
+--------+-----------------------+
| L      |  Lemma                |
+--------+-----------------------+
| F      |  Function             |
+--------+-----------------------+
| P      |  POS tag              |
+--------+-----------------------+
| G/GW   |  Governor word        |
+--------+-----------------------+
| GL     |  Governor lemma       |
+--------+-----------------------+
| GF     |  Governor function    |
+--------+-----------------------+
| GP     |  Governor POS         |
+--------+-----------------------+
| D/DW   |  Dependent word       |
+--------+-----------------------+
| DL     |  Dependent lemma      |
+--------+-----------------------+
| DF     |  Dependent function   |
+--------+-----------------------+
| DP     |  Dependent POS        |
+--------+-----------------------+
| PL     |  Word class           |
+--------+-----------------------+
| N      |  Ngram                |
+--------+-----------------------+
| R      |  Distance from root   |
+--------+-----------------------+
| I      |  Index in sentence    |
+--------+-----------------------+
| T      |  Tregex tree          |
+--------+-----------------------+

The ``search`` argument is generally a ``dict`` object, whose keys specify the annotation to search (i.e. a string from the above table), and whose values are the regular-expression or wordlist based queries. Because it comes first, and because it's always needed, you can pass it in as an argument, rather than a keyword argument.

.. code-block:: python

   ### get variants of the verb 'be'
   >>> corpus.interrogate({L: 'be'})
   ### get words in 'nsubj' position
   >>> corpus.interrogate({F: 'nsubj'})

Multiple key/value pairs can be supplied. By default, all must match for the result to be counted, though this can be changed with ``searchmode = ANY`` or ``searchmode = ALL``:

.. code-block:: python

   >>> goverb = {P: r'^v', L: r'^go'}
   ### get all variants of 'go' as verb
   >>> corpus.interrogate(goverb, searchmode = 'all')
   ### get all verbs and any word starting with 'go':
   >>> corpus.interrogate(goverb, searchmode = 'any')

Excluding results
---------------------

You may also wish to exclude particular phenomena from the results. The ``exclude`` argument takes a ``dict`` in the same form a ``search``. By default, if any key/value pair in the ``exclude`` argument matches, it will be excluded. This is controlled by ``excludemode = ANY`` or ``excludemode=ALL``.

.. code-block:: python

   >>> from dictionaries import wordlists
   ### get any noun, but exclude closed class words
   >>> corpus.interrogate({P: r'^n'}, exclude = {W: wordlists.closedclass})
   ### when there's only one search criterion, you can also write:
   >>> corpus.interrogate(P, r'^n', exclude = {W: wordlists.closedclass})

In many cases, rather than using ``exclude``, you could also remove results later, during editing.

What to show
---------------------

Up till now, all searches have simply returned words. The final major argument of the ``interrogate`` method is ``show``, which dictates what is returned from a search. Words are the default value. You can use any of the search values as a show value, plus a few extra values for n-gramming:

+------+-------------+------------------------+
| Show | Gloss       | Example                |
+======+=============+========================+
| NW   |  Word       | `The women were`       |
+------+-------------+------------------------+
| NL   |  Lemma      | `The woman be`         |
+------+-------------+------------------------+
| NF   |  Function   | `det nsubj root`       |
+------+-------------+------------------------+
| NP   |  POS tag    | `DT NNS VBN`           |
+------+-------------+------------------------+
| NPL  |  Word class | `determiner noun verb` |
+------+-------------+------------------------+

Show can be either a single string or a list of strings. If a list is provided, each value is returned in a slash separated form.

.. code-block:: python

   >>> example = corpus.interrogate({W: r'fr?iends?'}, show=[W, L, P])
   >>> list(example.results)

   ['friend/friend/nn', 'friends/friend/nns', 'fiend/fiend/nn', 'fiends/fiend/nns']

One further extra show value is ``'c'`` (count), which simply counts occurrences of a phenomenon. Rather than returning a DataFrame of results, it will result in a single Series. It cannot be combined with other values.

Working with trees
---------------------

If you have elected to search trees, you'll need to write a *Tregex query*. Tregex is a language for searching syntax trees like this one:

.. figure:: https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/const-grammar.png

To write a Tregex query, you specify *words and/or tags* you want to match, in combination with *operators* that link them together. First, let's understand the Tregex syntax.

To match any adjective, you can simply write:

.. code-block:: none

   JJ

with `JJ` representing adjective as per the `Penn Treebank tagset`_. If you want to get NPs containing adjectives, you might use:

.. code-block:: none

   NP < JJ
 
where `<` means `with a child/immediately below`. These operators can be reversed: If we wanted to show the adjectives within NPs only, we could use:

.. code-block:: none

   JJ > NP

It's good to remember that **the output will always be the left-most part of your query**.

If you only want to match Subject NPs, you can use bracketting, and the `$` operator, which means *sister/directly to the left/right of*:

.. code-block:: none

   JJ > (NP $ VP)

In this way, you build more complex queries, which can extent all the way from a sentence's *root* to particular tokens. The query below, for example, finds adjectives modifying `book`:

.. code-block:: none

   JJ > (NP <<# /book/)

Notice that here, we have a different kind of operator. The `<<` operator means that the node on the right does not need to be a child, but can be a descendent. the `#` means `head`&mdash;that is, in SFL, it matches the `Thing` in a Nominal Group.

If we wanted to also match `magazine` or `newspaper`, there are a few different approaches. One way would be to use `|` as an operator meaning `or`:

.. code-block:: none

   JJ > (NP ( <<# /book/ | <<# /magazine/ | <<# /newspaper/))

This can be cumbersome, however. Instead, we could use a regular expression:

.. code-block:: none

   JJ > (NP <<# /^(book|newspaper|magazine)s*$/)

Though it is unfortunately beyond the scope of this guide to teach Regular Expressions, it is important to note that Regular Expressions are extremely powerful ways of searching text, and are invaluable for any linguist interested in digital datasets.

Detailed documentation for Tregex usage (with more complex queries and operators) can be found here_.

Tree return values
-------------------

Though you can use the same Tregex query for tree searches, the output changes depending on what you select as the `return` value. For the following sentence:

.. code-block:: none

   These are prosperous times.

you could write a query:

.. code-block:: python

   r'JJ < __'

Which would return:

+------+----------+----------------------+
| Show | Gloss    | Output               |
+======+==========+======================+
| W    |  Word    |  `prosperous`        |
+------+----------+----------------------+
| T    |  Tree    | `(JJ prosperous)`    |
+------+----------+----------------------+
| p    |  POS tag | `JJ`                 |
+------+----------+----------------------+
| C    |  Count   | `1` (added to total) |
+------+----------+----------------------+

Working with dependencies
--------------------------

When working with dependencies, you can use any of the long list of search and return values. It's possible to construct very elaborate queries:

.. code-block:: python

   >>> from dictionaries import process_types, roles
   ### nominal nsubj with verbal process as governor
   >>> crit = {F: r'^nsubj$',
   ...         GL: processes.verbal.lemmata,
               GF: roles.event,
   ...         P: r'^N'}
   ### interrogate corpus, outputting the nsubj lemma
   >>> sayers = parsed.interrogate(crit, show = L)

You can also select from the three dependency grammars used by CoreNLP: one of ``'basic-dependencies'``, ``'collapsed-dependencies'``, or ``'collapsed-ccprocessed-dependencies'`` can be passed in as ``dep_type``:

.. code-block:: python

   >>> corpus.interrogate(query, dep_type = 'collapsed-ccprocessed-dependencies')

Multiprocessing
---------------------

Interrogating the corpus can be slow. To speed it up, you can pass an integer as the ``multiprocess`` keyword argument, which tells the ``interrogate()`` method how many processes to create.

.. code-block:: python

   >>> corpus.interrogate({T, r'__ > MD', multiprocess = 4)

Note that too many parallel processes may slow your computer down. If you pass in ``multiprocessing = True``, the number of processes will equal the number of cores on your machine. This is usually a fairly sensible number.

N-grams
---------------------

N-gramming can be done simply by using an n-gram string (``N``, ``NL``, ``NP`` or ``NPL``) as the `show` value. Two options for n-gramming are ``gramsize = n``, where ``n`` determines the number of tokens in the n-gram, and ``split_contractions = True``, which controls whether or not words like *doesn't* are treated as one token or two.

.. code-block:: python

   >>> corpus.interrogate({W: 'father'}, show='NL', gramsize = 3, split_contractions = False)

Saving interrogations
----------------------

.. code-block:: python

   >>> interro.save('savename')

Interrogation savenames will be prefaced with the name of the corpus interrogated.

You can also quicksave interrogations:

.. code-block:: python

   >>> corpus.interrogate(T, r'/NN.?/', save='savename')

Exporting interrogations
-------------------------

If you want to quickly export a result to CSV, LaTeX, etc., you can use Pandas' DataFrame methods:

.. code-block:: python

   >>> print(nouns.results.to_csv())
   >>> print(nouns.results.to_latex())

Other options
---------------

:func:`~corpkit.corpus.Corpus.interrogate` takes a number of other arguments, each of which is documented in the API documentation.

If you're done interrogating, you can head to the page on :ref:`editing-page` to learn how to transform raw frequency counts into something more meaningful. Or, Hit `Next` to learn about concordancing.

.. _here: http://nlp.stanford.edu/~manning/courses/ling289/Tregex.htm
.. _Penn Treebank tagset: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html