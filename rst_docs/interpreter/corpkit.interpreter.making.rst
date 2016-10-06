Making projects and corpora
============================

The first two things you need to do when using *corpkit* are to create a project, and to create (and optionally parse) a corpus. These steps can all be accomplished quickly using shell commands. They can also be done using the interpreter, however.

Once you're in *corpkit*, the command below will create a new project called `iran-news`, and move you into it.

.. code-block:: bash

   > new project named iran-news

Adding a corpus
----------------

Adding a corpus simply copies it to the project's data directory. The syntax is simple:

.. code-block:: bash

   > add '../../my_corpus'

Parsing a corpus
-----------------

To parse a text file, folder of text files, or folder of folder of text files, you first ``set`` the corpus, and then use the ``parse`` command:

.. code-block:: bash

   > set my_corpus as corpus
   > parse corpus

Tokenising, POS tagging and lemmatising
-----------------------------------------

If you don't want/need full parses, or if you aren't working with English, you might want to use the ``tokenise`` method.

.. code-block:: bash

   > set abstracts as corpus
   > tokenise corpus

POS tagging and lemmatisation are switched on by default, but you could also disable them:

.. code-block:: bash

   > tokenise corpus with postag as false and lemmatise as false

Working with metadata
-------------------------

Parsing/tokenising can be made way cooler when your data has some metadata in it. The metadata will be transferred over to the parsed version of the corpus, and then you can search or filter by metadata features, use metadata values as symbolic subcorpora, or display metadata alongside concordances.

Metadata should take the form of an XML tag at the end of a line, which could be a sentence or a paragraph:

.. code-block:: xml

   I hope everyone is hanging in with this blasted heat. As we all know being hot, sticky,
   stressed and irritated can bring on a mood swing super fast. So please make sure your 
   all takeing your meds and try to stay out of the heat. <metadata username="Emz45" 
   totalposts="5063" currentposts="4051" date="2011-07-13" postnum="0" threadlength="1">

Then, parse with metadata:

.. code-block:: bash

   > parse corpus with metadata

The parser output will look something like:

.. code-block:: none

   # sent_id 1
   # parse=(ROOT (S (NP (PRP I)) (VP (VBP hope) (SBAR (S (NP (NN everyone)) (VP (VBZ is) (VP (VBG hanging) (PP (IN in) (IN with) (NP (DT this) (VBN blasted) (NN heat)))))))) (. .)))
   # speaker=Emz45
   # totalposts=5063
   # threadlength=1
   # currentposts=4051
   # stage=10
   # date=2011-07-13
   # year=2011
   # postnum=0
   1   1   I         I         PRP O   2   nsubj      0       1
   1   2   hope      hope      VBP O   0   ROOT       1,5,11  _
   1   3   everyone  everyone  NN  O   5   nsubj      0       _
   1   4   is        be        VBZ O   5   aux        0       _
   1   5   hanging   hang      VBG O   2   ccomp      3,4,10  _
   1   6   in        in        IN  O   10  case       0       _
   1   7   with      with      IN  O   10  case       0       _
   1   8   this      this      DT  O   10  det        0       2
   1   9   blasted   blast     VBN O   10  amod       0       2
   1   10  heat      heat      NN  O   5   nmod:with  6,7,8,9 2*
   1   11  .         .         .   O   2   punct      0       _


The next page will show you how to search the corpus you've built, and to work with metadata if you've added it.


