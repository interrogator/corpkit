.. corpkit documentation master file, created by
   sphinx-quickstart on Thu Nov  5 11:43:02 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

corpkit documentation
========================================

*corpkit* is a Python-based tool for doing more sophisticated corpus linguistics.

It does a lot of the usual things, like parsing, interrogating, concordancing and keywording, but also extends their potential significantly: you can concordance by searching for combinations of lexical and grammatical features, and can do keywording of lemmas, of subcorpora compared to corpora, or of words in certain positions within clauses. 

Corpus interrogations can be quickly edited, sorted and visualised in complex ways, saved and loaded within projects, or exported to formats that can be handled by other tools.

.. image:: https://raw.githubusercontent.com/interrogator/risk/master/images/sayers-increasing.png

*corpkit* leverages `Stanford CoreNLP`_ and NLTK_, supports multiprocessing, and outputs interrogations as Pandas_ objects.

A GUI, incorporating much of corpkit's command line functionality, is documented and downloadable here_.

Contents:

.. toctree::
   
   corpkit

.. _CoreNLP: http://stanfordnlp.github.io/CoreNLP/
__ CoreNLP_
.. _NLTK: http://www.nltk.org/
.. _Pandas: http://pandas.pydata.org/
.. _here: http://interrogator.github.io/corpkit/
