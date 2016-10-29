Interrogating corpora
=====================

Once you've built a corpus, you can search it for linguistic phenomena. This is done with the :func:`~corpkit.corpus.Corpus.interrogate` method.

.. contents::
   :local:

Introduction
--------------

Interrogations can be performed on any :class:`corpkit.corpus.Corpus` object, but also, on :class:`corpkit.corpus.Subcorpus` objects, :class:`corpkit.corpus.File` objects and :class:`corpkit.corpus.Datalist` objects (slices of ``Corpus`` objects). You can search plaintext corpora, tokenised corpora or fully parsed corpora using the same method. We'll focus on parsed corpora in this guide.

.. code-block:: python
   
   >>> from corpkit import *
   ### words matching 'woman', 'women', 'man', 'men'
   >>> query = {W: r'/(^wo)m.n/'}
   ### interrogate corpus
   >>> corpus.interrogate(query)
   ### interrogate parts of corpus
   >>> corpus[2:4].interrogate(query)
   >>> corpus.files[:10].interrogate(query)
   ### if you have a subcorpus called 'abstract':
   >>> corpus.subcorpora.abstract.interrogate(query)

Corpus interrogations will output a :class:`corpkit.interrogation.Interrogation` object, which stores a DataFrame of results, a Series of totals, a ``dict`` of values used in the query, and, optionally, a set of concordance lines. Let's search for proper nouns in *The Great Gatsby* and see what we get:

.. code-block:: python

   >>> corp = Corpus('gatsby-parsed')
   ### turn on concordancing:
   >>> propnoun = corp.interrogate({P: '^NNP'}, do_concordancing=True)
   >>> propnoun.results

             gatsby  tom  daisy  mr.  wilson  jordan  new  baker  york  miss  
   chapter1      12   32     29    4       0       2   10     21     6    19   
   chapter2       1   30      6    8      26       0    6      0     6     0   
   chapter3      28    0      1    8       0      22    5      6     5     1   
   chapter4      38   10     15   25       1       9    5      8     4     7   
   chapter5      36    3     26    4       0       0    1      1     1     1   
   chapter6      37   21     19   11       0       1    4      0     3     4   
   chapter7      63   87     60    9      27      35    9      2     5     1   
   chapter8      21    3     19    1      19       1    0      1     0     0   
   chapter9      27    5      9   14       4       3    4      1     4     1   

   >>> propnoun.totals

   chapter1    232
   chapter2    252
   chapter3    171
   chapter4    428
   chapter5    128
   chapter6    219
   chapter7    438
   chapter8    139
   chapter9    208
   dtype: int64

   >>> propnoun.query

   {'case_sensitive': False,
    'corpus': 'gatsby-parsed',
    'dep_type': 'collapsed-ccprocessed-dependencies',
    'do_concordancing': True,
    'exclude': False,
    'excludemode': 'any',
    'files_as_subcorpora': True,
    'gramsize': 1,
    ...}

   >>> propnoun.concordance # (sample)

   54 chapter1             They had spent a year in  france      for no particular reason and then d
   55 chapter1   n't believe it I had no sight into  daisy       's heart but i felt that tom would 
   56 chapter1  into Daisy 's heart but I felt that  tom         would drift on forever seeking a li
   57 chapter1       This was a permanent move said  daisy       over the telephone but i did n't be
   58 chapter1   windy evening I drove over to East  egg         to see two old friends whom i scarc
   59 chapter1   warm windy evening I drove over to  east        egg to see two old friends whom i s
   60 chapter1  d a cheerful red and white Georgian  colonial    mansion overlooking the bay        
   61 chapter1  pen to the warm windy afternoon and  tom         buchanan in riding clothes was stan
   62 chapter1  to the warm windy afternoon and Tom  buchanan    in riding clothes was standing with

Cool, eh? We'll focus on what to do with these attributes later. Right now, we need to learn how to generate them.

Search types
---------------------

Parsed corpora contain many different kinds of things we might like to search. There are word forms, lemma forms, POS tags, word classes, indices, and constituency and (three different) dependency grammar annotations. For this reason, the search query is a ``dict`` object passed to the ``interrogate()`` method, whose keys specify what to search, and whose values specify a query. The simplest ones are given in the table below.

.. note::

   Single capital letter variables in code examples represent lowercase strings ``(W = 'w')``. These variables are made available by doing ``from corpkit import *``. They are used here for readability.

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
| X      |  Word class           |
+--------+-----------------------+
| E      |  NER tag              |
+--------+-----------------------+
| A      |  Distance from root   |
+--------+-----------------------+
| I      |  Index in sentence    |
+--------+-----------------------+
| S      |  Sentence index       |
+--------+-----------------------+
| R      | Coref representative  |
+--------+-----------------------+


Because it comes first, and because it's always needed, you can pass it in like an argument, rather than a keyword argument.

.. code-block:: python

   ### get variants of the verb 'be'
   >>> corpus.interrogate({L: 'be'})
   ### get words in 'nsubj' position
   >>> corpus.interrogate({F: 'nsubj'})

Multiple key/value pairs can be supplied. By default, all must match for the result to be counted, though this can be changed with ``searchmode=ANY`` or ``searchmode=ALL``:

.. code-block:: python

   >>> goverb = {P: r'^v', L: r'^go'}
   ### get all variants of 'go' as verb
   >>> corpus.interrogate(goverb, searchmode=ALL)
   ### get all verbs and any word starting with 'go':
   >>> corpus.interrogate(goverb, searchmode=ANY)

Grammatical searching
----------------------

In the examples above, we match attributes of tokens. The great thing about parsed data, is that we can search for relationships between words. So, other possible search keys are:

+--------+------------------------+
| Search | Gloss                  |
+========+========================+
| G      | Governor               |
+--------+------------------------+
| D      | Dependent              |
+--------+------------------------+
| H      | Coreference head       |
+--------+------------------------+
| T      | Syntax tree            |
+--------+------------------------+
| A1     | Token 1 place to left  |
+--------+------------------------+
| Z1     | Token 1 place to right |
+--------+------------------------+

.. code-block:: python

   >>> q = {G: r'^b'}
   ### return any token with governor word starting with 'b'
   >>> corpus.interrogate(q)

`Governor`, `Dependent` and `Left/Right` can be combined with the earlier table, allowing a large array of search types:

+--------------------+-------+----------+-----------+------------+-----------------+
|                    | Match | Governor | Dependent | Coref head | Left/right      |
+====================+=======+==========+===========+============+=================+
| Word               | W     | G        | D         | H          | A1/Z1           |
+--------------------+-------+----------+-----------+------------+-----------------+
| Lemma              | L     | GL       | DL        | HL         | A1L/Z1L         |
+--------------------+-------+----------+-----------+------------+-----------------+
| Function           | F     | GF       | DF        | HF         | A1F/Z1F         |
+--------------------+-------+----------+-----------+------------+-----------------+
| POS tag            | P     | GP       | DP        | HP         | A1P/Z1P         |
+--------------------+-------+----------+-----------+------------+-----------------+
| Word class         | X     | GX       | DX        | HX         | A1X/Z1X         |
+--------------------+-------+----------+-----------+------------+-----------------+
| Distance from root | A     | GA       | DA        | HA         | A1A/Z1A         |
+--------------------+-------+----------+-----------+------------+-----------------+
| Index              | I     | GI       | DI        | HI         | A1I/Z1I         |
+--------------------+-------+----------+-----------+------------+-----------------+
| Sentence index     | S     | GS       | DS        | HS         | A1S/Z1S         |
+--------------------+-------+----------+-----------+------------+-----------------+

Syntax tree searching can't be combined with other options. We'll return to them in a minute, however.

Excluding results
---------------------

You may also wish to exclude particular phenomena from the results. The ``exclude`` argument takes a ``dict`` in the same form a ``search``. By default, if any key/value pair in the ``exclude`` argument matches, it will be excluded. This is controlled by ``excludemode=ANY`` or ``excludemode=ALL``.

.. code-block:: python

   >>> from corpkit.dictionaries import wordlists
   ### get any noun, but exclude closed class words
   >>> corpus.interrogate({P: r'^n'}, exclude={W: wordlists.closedclass})
   ### when there's only one search criterion, you can also write:
   >>> corpus.interrogate(P, r'^n', exclude={W: wordlists.closedclass})

In many cases, rather than using ``exclude``, you could also remove results later, during editing.

What to show
---------------------

Up till now, all searches have simply returned words. The final major argument of the ``interrogate`` method is ``show``, which dictates what is returned from a search. Words are the default value. You can use any of the search values as a show value. ``show`` can be either a single string or a list of strings. If a list is provided, each value is returned with forward slashes as delimiters.

.. code-block:: python

   >>> example = corpus.interrogate({W: r'fr?iends?'}, show=[W, L, P])
   >>> list(example.results)

   ['friend/friend/nn', 'friends/friend/nns', 'fiend/fiend/nn', 'fiends/fiend/nns', ... ]

Unigrams are generated by default. To get n-grams, pass in an n value as ``gramsize``:

.. code-block:: python

   >>> example = corpus.interrogate({W: r'wom[ae]n]'}, show=N, gramsize=2)
   >>> list(example.results)

   ['a/woman', 'the/woman', 'the/women', 'women/are', ... ]


So, this leaves us with a huge array of possible things to show, all of which can be combined if need be:

+--------------------+-------+----------+-----------+------------+-------------+-------------+
|                    | Match | Governor | Dependent | Coref Head | 1L position | 1R position |
+====================+=======+==========+===========+============+=============+=============+
| Word               | W     | G        | D         | H          | A1          | Z1          |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Lemma              | L     | GL       | DL        | HL         | A1L         | Z1L         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Function           | F     | GF       | DF        | HF         | A1F         | Z1F         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| POS tag            | P     | GP       | DP        | HP         | A1P         | Z1P         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Word class         | X     | GX       | DX        | HX         | A1X         | Z1X         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Distance from root | A     | GA       | DA        | HA         | A1A         | Z1R         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Index              | I     | GI       | DI        | HI         | A1I         | Z1I         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+
| Sentence index     | S     | GS       | DS        | HS         | A1S         | Z1S         |
+--------------------+-------+----------+-----------+------------+-------------+-------------+

One further extra show value is ``'c'`` (count), which simply counts occurrences of a phenomenon. Rather than returning a DataFrame of results, it will result in a single Series. It cannot be combined with other values.

Working with trees
---------------------

If you have elected to search trees, by default, searching will be done with Java, using Tregex. If you don't have Java, or if you pass in ``tgrep=True``, searching will the more limited Tgrep2 syntax. Here, we'll concentrate on Tregex.

Tregex is a language for searching syntax trees like this one:

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

Notice that here, we have a different kind of operator. The `<<` operator means that the node on the right does not need to be a child, but can be a descendant. the `#` means `head`—that is, in SFL, it matches the `Thing` in a Nominal Group.

If we wanted to also match `magazine` or `newspaper`, there are a few different approaches. One way would be to use `|` as an operator meaning `or`:

.. code-block:: none

   JJ > (NP ( <<# /book/ | <<# /magazine/ | <<# /newspaper/))

This can be cumbersome, however. Instead, we could use a regular expression:

.. code-block:: none

   JJ > (NP <<# /^(book|newspaper|magazine)s*$/)

Though it is beyond the scope of this guide to teach Regular Expressions, it is important to note that Regular Expressions are extremely powerful ways of searching text, and are invaluable for any linguist interested in digital datasets.

Detailed documentation for Tregex usage (with more complex queries and operators) can be found here_.

Tree `show` values
-------------------

Though you can use the same Tregex query for tree searches, the output changes depending on what you select as the ``show`` value. For the following sentence:

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

When working with dependencies, you can use any of the long list of search and `show` values. It's possible to construct very elaborate queries:

.. code-block:: python

   >>> from corpkit.dictionaries import process_types, roles
   ### nominal nsubj with verbal process as governor
   >>> crit = {F: r'^nsubj$',
   ...         GL: processes.verbal.lemmata,
   ...         GF: roles.event,
   ...         P: r'^N'}
   ### interrogate corpus, outputting the nsubj lemma
   >>> sayers = parsed.interrogate(crit, show=L)

Working with metadata
----------------------------------

If you've used speaker segmentation and/or metadata addition when building your corpus, you can tell the :func:`~corpkit.corpus.Corpus.interrogate` method to use these values as subcorpora, or restrict searches to particular values. The code below will limit searches to sentences spoken by Jason and Martin, or exclude them from the search:

.. code-block:: python

   >>> corpus.interrogate(query, just_metadata={'speaker': ['JASON', 'MARTIN']})
   >>> corpus.interrogate(query, skip_metadata={'speaker': ['JASON', 'MARTIN']})

If you wanted to compare Jason and Martin's contributions in the corpus as a whole, you could treat them as subcorpora:

.. code-block:: python

   >>> corpus.interrogate(query, subcorpora='speaker',
   ...                    just_metadata={'speaker': ['JASON', 'MARTIN']})

The method above, however, will make an interrogation with two subcorpora, `'JASON'` AND ``MARTIN``. You can pass a list in as the ``subcorpora`` keyword argument to generate a multiindex:

.. code-block:: python

   >>> corpus.interrogate(query, subcorpora=['folder', 'speaker'],
                          just_metadata={'speaker': ['JASON', 'MARTIN']})

Working with coreferences
--------------------------

One major challenge in corpus linguistics is the fact that pronouns stand in for other words. Parsing provides coreference resolution, which maps pronouns to the things they denote. You can enable this kind of parsing by specifying the `dcoref` annotator:

.. code-block:: python

   >>> corpus = Corpus('example.txt')
   >>> ops = 'tokenize,ssplit,pos,lemma,parse,ner,dcoref'
   >>> parsed = corpus.interrogate(operations=ops)
   ### print a plaintext representation of the parsed corpus
   >>> print(parsed.plain)

.. code-block:: none

   0. Clinton supported the independence of Kosovo
   1. He authorized the use of force.

If you have done this, you can use `coref=True` while interrogating to allow coreferent forms to be counted alongside query matches. For example, if you wanted to find all the processes Clinton is engaged in, you could do:

.. code-block:: python

   >>> from corpkit.dictionaries import roles
   >>> query = {W: 'clinton', GF: roles.process}
   >>> res = parsed.interrogate(query, show=L, coref=True)
   >>> res.results.columns

This matches both `Clinton` and `he`, and thus gives us:

.. code-block:: python

   ['support', 'authorize']


Multiprocessing
---------------------

Interrogating the corpus can be slow. To speed it up, you can pass an integer as the ``multiprocess`` keyword argument, which tells the ``interrogate()`` method how many processes to create.

.. code-block:: python

   >>> corpus.interrogate({T: r'__ > MD'}, multiprocess=4)

.. note::

   Too many parallel processes may slow your computer down. If you pass in ``multiprocessing=True``, the number of processes will equal the number of cores on your machine. This is usually a fairly sensible number.

N-grams
---------------------

N-gramming can be generated by making ``gramsize`` > 1:

.. code-block:: python

   >>> corpus.interrogate({W: 'father'}, show='L', gramsize=3)

Collocation
------------

Collocations can be shown by making using ``window``:

.. code-block:: python

   >>> corpus.interrogate({W: 'father'}, show='L', window=6)

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

If you're done interrogating, you can head to the page on :ref:`editing-page` to learn how to transform raw frequency counts into something more meaningful. Or, hit `Next` to learn about concordancing.

.. _here: http://nlp.stanford.edu/~manning/courses/ling289/Tregex.htm
.. _Penn Treebank tagset: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html