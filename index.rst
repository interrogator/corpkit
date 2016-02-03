.. corpkit documentation master file, created by
   sphinx-quickstart on Thu Nov  5 11:43:02 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

corpkit documentation
========================================

*corpkit* is a Python-based tool for doing more sophisticated corpus linguistics.

It does a lot of the usual things, like parsing, interrogating, concordancing and keywording, but also extends their potential significantly: you can create structured corpora with speaker ID labels, and easily restrict searches to individual speakers, subcorpora or groups of files.

Concordancing can take advantage of parser output, rather than simply lexis. You can keyword lemmas or lexicogrammatical features, or compare keywords in each subcorpus compared to the corpus as a whole. 

Interrogations can be quickly edited, sorted and visualised in complex ways, saved and loaded within projects, or exported to formats that can be handled by other tools.

*corpkit* leverages `Stanford CoreNLP`_, NLTK_ and pattern_ for the linguistic heavy lifting, and pandas_ and matplotlib_ for storing, editing and visualising interrogation results. Multiprocessing is available via `joblib`, and Python 2 and 3 are both supported.

Example
----------------------

Here's a basic workflow, using a corpus of news articles published between 1987 and 2014, structured like this:

.. code-block:: bash
   
   ./data/NYT:

   ├───1987
   │   ├───NYT-1987-01-01-01.txt
   │   ├───NYT-1987-01-02-01.txt
   │   ...
   │
   ├───1988
   │   ├───NYT-1988-01-01-01.txt
   │   ├───NYT-1988-01-02-01.txt
   │   ...
   ...


Below, this corpus is made into a ``Corpus`` object, parsed with *Stanford CoreNLP*, and interrogated for a lexicogrammatical feature. Absolute frequencies are turned into relative frequencies, and results sorted by trajectory. The edited data is then plotted.

.. code-block:: python

   >>> from corpkit import *
   >>> from dictionaries.process_types import processes
   
   >>> # parse corpus of NYT articles containing annual subcorpoa
   >>> unparsed = Corpus('data/NYT')
   >>> parsed = unparsed.parse()
   
   >>> # query: nominal nsubjs that have verbal process as governor
   >>> crit = {F: '^nsubj$', G: processes.verbal, P: r'^N'}

   >>> # interrogate corpus, outputting lemma forms
   >>> sayers = parsed.interrogate(crit, show = L)
   >>> sayers.quickview(10)

      0: official    (n=4348)
      1: expert      (n=2057)
      2: analyst     (n=1369)
      3: report      (n=1103)
      4: company     (n=1070)
      5: which       (n=1043)
      6: researcher  (n=987)
      7: study       (n=901)
      8: critic      (n=826)
      9: person      (n=802)

   >>> # get relative frequency and sort by increasing
   >>> rel_say = sayers.edit('%', SELF, sort_by = 'increase')

   >>> # plot via matplotlib, using tex if possible
   >>> rel_say.visualise('Sayers, increasing', kind = 'area', y_label = 'Percentage of all sayers')

Output:

.. figure:: https://raw.githubusercontent.com/interrogator/risk/master/images/sayers-increasing.png

A graphical interface, incorporating much of corpkit's command line functionality, is documented and downloadable here_. The app is also distributed in the GitHub/pip versions of *corpkit* as a .py file. It can be started with:

.. code-block:: bash
    python corpkit/corpkit-gui.py

Installation
----------------------

Via pip:

.. code-block:: bash

   pip install corpkit

via Git:

.. code-block:: bash

   git clone https://www.github.com/interrogator/corpkit
   cd corpkit
   python setup.py install

Contents
---------------------
.. toctree::
   :maxdepth: 2

   User guide (Via GitHub) <https://github.com/interrogator/corpkit/blob/master/README.md>
   rst_docs/corpkit.corpus.rst
   rst_docs/corpkit.interrogation.rst
   rst_docs/corpkit.other.rst
   rst_docs/corpkit.dictionaries.rst
   rst_docs/corpkit.about.rst

.. _Stanford CoreNLP: http://stanfordnlp.github.io/CoreNLP/
.. _NLTK: http://www.nltk.org/
.. _pandas: http://pandas.pydata.org/
.. _here: http://interrogator.github.io/corpkit/
.. _pattern: http://www.clips.ua.ac.be/pages/pattern-en/
.. _matplotlib: http://matplotlib.org/