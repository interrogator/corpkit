.. _interpreter-page:

Overview
=======================

The syntax of the interpreter is based around *objects*, which you do things to, and *commands*, which are actions. The example below uses the `search` command on a `corpus` object, which produces a `result`, `concordance`, `totals` and `query` object. More specifically, the `corpus` is searched for lemmata starting with the letter `t`, whose POS is verbal:

.. code-block:: bash

   search corpus for lemma matching '^t' and pos matching 'VB'

Objects
---------

The most common objects you'll be using are:

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

When you start the interperter, these are all empty. You'll need to use commands to put data in their namespace.

Commands 
-----------

You do things to the objects via commands. Each command has its own syntax, designed to be as similar to natural language as possible.

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

In the pages that follow, the syntax is provided for the most common commands. You can also type the name of the command with no arguments into the interpreter, in order to show usage examples.
