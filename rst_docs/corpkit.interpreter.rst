Interpreter
====================

corpkit now has its very own interpreter!

.. note::

   This page under construction.

.. contents::
   :local:

Accessing
--------------------

With corpkit installed, you can start the interpreter in a couple of ways:

.. code-block:: bash

   $ corpkit
   # or
   $ python -m corpkit.env


Objects
---------------------

The interpreter has a few objects you can work with.

+-------------+-----------------------------------------------+
| Object      | Contains                                      |
+=============+===============================================+
| corpus      | Dataset selected for parsing or searching     |
+-------------+-----------------------------------------------+
| results     | Search output                                 |
+-------------+-----------------------------------------------+
| edited      | Results after sorting, editing or calculating |
+-------------+-----------------------------------------------+
| concordance | Concordance lines from search                 |
+-------------+-----------------------------------------------+
| features    | General linguistic features of corpus         |
+-------------+-----------------------------------------------+
| wordclasses | Distribution of word classes in corpus        |
+-------------+-----------------------------------------------+
| postags     | Distribution of POS tags in corpus            |
+-------------+-----------------------------------------------+
| figure      | Plotted data                                  |
+-------------+-----------------------------------------------+
| query       | Values used to perform search or edit         |
+-------------+-----------------------------------------------+


Commands 
-----------

You do things to the objects via commands.

+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| Command         | Purpose                                                      | Syntax                                                                                     |
+=================+==============================================================+============================================================================================+
| ``new``         | Make a new project                                           | ``new project <name>``                                                                     |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``set``         | Set current corpus                                           | ``set <corpusname>``                                                                       |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``parse``       | Parse corpus                                                 | ``parse corpus with [options]\*``                                                          |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``search``      | Search a corpus for linguistic feature, generate concordance | ``search corpus for [feature matching pattern]\* showing [feature]\* with [options]\*``    |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``edit``        | Edit results or edited results                               | ``edit result by [skipping subcorpora/entries matching pattern]\* with [options]\*``       |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``calculate``   | Calculate relative frequencies, keyness, etc.                | ``calculate result as operation of denominator``                                           |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``sort``        | Sort results or concordance                                  | ``sort result/concordance by value ``                                                      |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``plot``        | Visualise result or edited result                            | ``plot edited as line chart with [options]\*``                                             |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``export``      | Export result, edited result or concordance to string/file   | ``export result to string/csv/latex/file <filename>``                                      |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``save``        | Save data to disk                                            | ``save object to <filename>``                                                              |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``load``        | Load data from disk                                          | ``load object as result``                                                                  |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``store``       | Store something in memory                                    | ``store object as <name>``                                                                 |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``fetch``       | Fetch something from memory                                  | ``fetch <name> as result/edited/concordance``                                              |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``help``        | Get help on an object or command                             | ``help command/object``                                                                    |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+
| ``history``     | See previously entered commands                              | ``history``                                                                                |
+-----------------+--------------------------------------------------------------+--------------------------------------------------------------------------------------------+

In square brackets with asterisks are recursive parts of the syntax, which often also accepted `not` operators. `<text>` denotes places where you can choose an identifier, filename, etc.

Search examples
--------------------

.. code-block:: none

   > search corpus for words matching ".*"
   > search corpus for words matching "^[A-M]" showing lemma and word with case_sensitive
   > search corpus for cql matching '[pos="DT"] [pos="NN"]' showing pos and word with coref
   > search corpus for function matching roles.process showing dependent-lemma
   > etc.

Switching to IPython
---------------------

When the interpreter constrains you, you can switch to IPython with `ipython`. Your objects are available there under the same name. When you're done there, do `quit` to return to the *corpkit* interpreter.

