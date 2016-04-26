Creating projects and building corpora
=======================================

Doing corpus linguistics involves building and interrogating corpora, and exploring interrogation results. ``corpkit`` helps with all of these things. This page will explain how to create a new project and build a corpus.

.. contents::
   :local:

Creating a new project
-----------------------

The simplest way to begin using corpkit is to import it and to create a new project. Projects are simply folders containing subfolders where corpora, saved results, images and dictionaries will be stored. 

.. code-block:: python

   >>> import corpkit
   >>> corpkit.new_project('psyc')

This creates a new folder in the current directory called `psyc`. We can then move there:

.. code-block:: python

   >>> import os
   >>> os.chdir('psyc')
   >>> os.listdir('.')
   
   ['data',
    'dictionaries',
    'exported',
    'images',
    'logs',
    'saved_concordances',
    'saved_interrogations']

Adding a corpus
----------------

Now that we have a project, we need to add some plain-text data to the `data` folder. At the very least, this is simply a text file. Better than this is a folder containing a number of text files. Best, however, is a folder containing subfolders, with each subfolder containing one or more text files. These subfolders represent subcorpora.

You can add your corpus to the `data` folder from the command line, or using Finder/Explorer if you prefer. Using `shutil`:

.. code-block:: python

   >>> import shutil
   >>> shutil.copytree('/Users/me/Documents/transcripts', '.')

Creating a Corpus object
-------------------------

Once we have a corpus of text files, we need to turn it into a Corpus object.

.. code-block:: python

   >>> from corpkit import Corpus
   >>> unparsed = Corpus('data/psyc')
   >>> unparsed
   <corpkit.corpus.Corpus instance: psyc; 13 subcorpora>

This object can now be interrogated using the :func:`~corpkit.corpus.Corpus.interrogate` method:

.. code-block:: python

   >>> th_words = unparsed.interrogate({W: r'th[a-z-]+'})
   ### show 5x5 (Pandas syntax)
   >>> th_words.results.iloc[:5,:5]

   S   that  the  then  think  thing
   01   144  139    63     53     43
   02   122  114    74     35     45
   03   132   74    56     57     25
   04   138   67    71     35     44
   05   173   76    67     35     49

Parsing a corpus
-----------------

Instead of interrogating the plaintext corpus, what you'll probably want to do, is parse it, and interrogate the parser output. For this, :class:`corpkit.corpus.Corpus` objects have a :func:`~corpkit.corpus.Corpus.parse` method. This relies on Stanford CoreNLP's parser, and therefore, you must have the parser and Java installed. ``corpkit`` will look around in your PATH for the parser, but you can also pass in its location manually with (e.g.) ``corenlppath = 'users/you/corenlp'``.

.. code-block:: python

   >>> corpus = unparsed.parse()

.. note::

    Remember that parsing is a computationally intensive task, and can take a long time!

``corpkit`` can also work with speaker IDs. If lines in your file contain capitalised alphanumeric names, followed by a colon (as per the example below), these IDs can be stripped out and turned into metadata features in the XML.

.. code-block:: none

    JOHN: Why did they change the signs above all the bins?
    SPEAKER23: I know why. But I'm not telling.

To use this option, use the ``speaker_segmentation`` keyword argument:

.. code-block:: python

   >>> corpus = unparsed.parse(speaker_segmentation = True)

Parsing creates a corpus that is structurally identical to the original, but with annotations as XML files in place of the original ``.txt`` files. There are also methods for multiprocessing, memory allocation and so on:

+--------------------------+--------------+---------------------------------------+
| ``parse()`` argument     | Type         | Purpose                               |
+==========================+==============+=======================================+
| ``corenlppath``          | ``str``      | Path to CoreNLP                       |
+--------------------------+--------------+---------------------------------------+
| ``nltk_data_path``       | ``str``      | Path to ``punkt`` tokeniser           |
+--------------------------+--------------+---------------------------------------+
| ``operations``           | ``str``      | `List of annotations`_                |
+--------------------------+--------------+---------------------------------------+
| ``copula_head``          | ``bool``     | Make copula head of dependency parse  |
+--------------------------+--------------+---------------------------------------+
| ``speaker_segmentation`` | ``bool``     | Do speaker segmentation               |
+--------------------------+--------------+---------------------------------------+
| ``memory_mb``            | ``int``      | Amount of memory to allocate          |
+--------------------------+--------------+---------------------------------------+
| ``multiprocess``         | ``int/bool`` | Process in ``n`` parallel jobs        |
+--------------------------+--------------+---------------------------------------+

Once you have a parsed corpus, you're ready to start interrogating. Before constructing your own query, however, you may want to use two predefined methods for counting key features in the corpus:

.. code-block:: python

   >>> corpus.features
   >>> corpus.postags

The first of these can long time, as it counts a number of complex features. Once it's done, however, it saves automatically, so you don't need to do it again.

.. _List of annotations: http://nlp.stanford.edu/index.shtml
