.. _interpreter-page:

Interpreter
====================

corpkit now has its very own interpreter!

.. note::

   This page under construction.

.. contents::
   :local:

Dependencies
-------------

To use the interpreter, you'll need to have `readline` installed, and ideally `IPython` as well.

Accessing
--------------------

With corpkit installed, you can start the interpreter in a couple of ways:

.. code-block:: bash

   $ corpkit
   # or
   $ python -m corpkit.env

.. note::

   When using the interpreter, the prompt (the text to the left of where you type your command) displays the directory you are in (with an asterisk if it does not appear to be a *corpkit* project) and the currently active corpus. 

Objects
---------------------

The interpreter has a few objects you can work with.

+---------------+-----------------------------------------------+
| Object        | Contains                                      |
+===============+===============================================+
| `corpus`      | Dataset selected for parsing or searching     |
+---------------+-----------------------------------------------+
| `results`     | Search output                                 |
+---------------+-----------------------------------------------+
| `edited`      | Results after sorting, editing or calculating |
+---------------+-----------------------------------------------+
| `concordance` | Concordance lines from search                 |
+---------------+-----------------------------------------------+
| `features`    | General linguistic features of corpus         |
+---------------+-----------------------------------------------+
| `wordclasses` | Distribution of word classes in corpus        |
+---------------+-----------------------------------------------+
| `postags`     | Distribution of POS tags in corpus            |
+---------------+-----------------------------------------------+
| `figure`      | Plotted data                                  |
+---------------+-----------------------------------------------+
| `query`       | Values used to perform search or edit         |
+---------------+-----------------------------------------------+
| `previous`    | Object created before last                    |
+---------------+-----------------------------------------------+


Commands 
-----------

You do things to the objects via commands.

+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| Command         | Purpose                                                      | Syntax                                                                                     |
+=================+==============================================================+============================================================================================+
| `new`           | Make a new project                                           | `new project <name>`                                                                       |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `set`           | Set current corpus                                           | `set <corpusname>`                                                                         |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `parse`         | Parse corpus                                                 | `parse corpus with [options]*`                                                             |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `search`        | Search a corpus for linguistic feature, generate concordance | `search corpus for [feature matching pattern]* showing [feature]* with [options]*`         |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `edit`          | Edit results or edited results                               | `edit result by [skipping subcorpora/entries matching pattern]* with [options]*`           |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `calculate`     | Calculate relative frequencies, keyness, etc.                | `calculate result/edited as operation of denominator`                                      |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `sort`          | Sort results or concordance                                  | `sort result/concordance by value`                                                         |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `plot`          | Visualise result or edited result                            | `plot result/edited as line chart with [options]*`                                         |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `show`          | Show any object                                              | `show object`                                                                              |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `export`        | Export result, edited result or concordance to string/file   | `export result to string/csv/latex/file <filename>`                                        |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `save`          | Save data to disk                                            | `save object to <filename>`                                                                |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `load`          | Load data from disk                                          | `load object as result`                                                                    |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `store`         | Store something in memory                                    | `store object as <name>`                                                                   |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `fetch`         | Fetch something from memory                                  | `fetch <name> as object`                                                                   |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `help`          | Get help on an object or command                             | `help command/object`                                                                      |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `history`       | See previously entered commands                              | `history`                                                                                  |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `ipython`       | Entering IPython with objects available                      | `ipython`                                                                                  |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| `py`            | Execute Python code                                          | `py 'print("hello world")'`                                                                |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+

In square brackets with asterisks are recursive parts of the syntax, which often also accept `not` operators. `<text>` denotes places where you can choose an identifier, filename, etc.

Searching
-----------

The most powerful thing about *corpkit* is its ability to search parsed corpora for very complex constituency, dependency or token level features.

.. note::
   
   By default, searching also produces concordance lines. If you don't need them, you can use ``toggle conc`` to switch them off, or on again. This can dramatically speed up processing time.

Search examples
--------------------

.. code-block:: none

   > search corpus ### interactive search helper
   > search corpus for words matching ".*"
   > search corpus for words matching "^[A-M]" showing lemma and word with case_sensitive
   > search corpus for cql matching '[pos="DT"] [pos="NN"]' showing pos and word with coref
   > search corpus for function matching roles.process showing dependent-lemma
   > search corpus for governor-lemma matching processes.verbal showing governor-lemma, lemma
   > search corpus for words matching any and not words matching wordlists.closedclass
   > search corpus for trees matching '/NN.?/ >># NP'
   > search corpus for pos matching NNP showing ngram-word and pos with gramsize as 3
   > etc.

Concordancing
---------------

By default, every search also produces concordance lines. You can view them by typing ``concordance``. This opens an interactive screen, which can be scrolled and searched---hit ``h`` to get help on possible commands.

Showing concordance lines in different ways
---------------------------------------------

.. code-block:: none

   # hide subcorpus name, speaker name
   > show concordance with columns as lmr
   # enlarge window
   > show concordance with columns as lmr and window as 60
   # limit number of results to 100
   > show concordance with columns as lmr and window as 60 and n as 100

The values you enter here are persistant---the window size, number of lines, etc. will remain the same until you shut down the interpreter or provide new values.

Editing, sorting and colouring
----------------------------------

To edit concordance lines, you use the same syntax as you would use to edit results:

.. code-block:: none

   > edit concordance by skipping subcorpora matching '[123]$'
   > edit concordance by merging entries matching wordlist:people as 'people' 
   > edit concordance by keeping entries matching r'PRP'

Sorting can be by column, or by word 


One nice feature is that concordances can be coloured. This can be done through either indexing or regular expression matches. Note that ``background`` can be added to colour the background instead of the foreground, and ``reset`` can be used to retun things to normal.

.. code-block:: none

   # indexing methods
   > mark 10 blue
   > mark -10 background red
   > mark 10-15 cyan
   > mark 15- magenta
   # reset all
   > mark - reset

.. code-block:: none

   # regular expression methods: specify column(s) to search
   > mark m '^PRP.*' yellow
   > mark r '\bbeing\b' background green
   > mark lm 'JJR$'
   # reset via regex
   > mark m '.*'' reset



Editing, calculating and sorting
----------------------------------

.. code-block:: none

   > edit result by keeping subcorpora matching '[01234]'
   > edit result by skipping entries matching wordlists.closedclass
   > calculate result as percentage of self
   > calculate edited as percentage of features.clauses
   > sort edited by increase

Plotting
---------

.. code-block:: none

   > plot edited as bar chart with title as 'Example plot' and x_label as 'Subcorpus'
   > plot edited as area chart with stacked and colours as Paired
   > plot edited with style as seaborn-talk

Switching to IPython
---------------------

When the interpreter constrains you, you can switch to IPython with `ipython`. Your objects are available there under the same name. When you're done there, do `quit` to return to the *corpkit* interpreter.

