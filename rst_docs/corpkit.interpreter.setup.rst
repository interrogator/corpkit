Setup
==============================

*corpkit* comes with a dedicated interpreter, which receives commands in a natural language syntax like these:

.. code-block:: bash

   set mydata as corpus
   search corpus for pos matching 'JJ.*'
   plot result as line chart with title 'Ajectives'


It's a little less powerful than the full Python API, but it is easier to use, especially if you don't know Python. You can also switch instantly from the interpreter to the full API, so you only need the API for the really tricky stuff.

.. note::

   Interpreter pages under construction.

.. contents::
   :local:

Dependencies
-------------

To use the interpreter, you'll need *corpkit* installed. To use all features of the interpreter, you will also need *readline* and *IPython*.

Accessing
--------------------

With *corpkit* installed, you can start the interpreter in a couple of ways:

.. code-block:: bash

   $ corpkit
   # or
   $ python -m corpkit.env

You can start it from a Python session, too:

.. code-block:: python

   > from corpkit import env
   > env()

The prompt
------------

When using the interpreter, the prompt (the text to the left of where you type your command) displays the directory you are in (with an asterisk if it does not appear to be a *corpkit* project) and the currently active corpus, if any:

```none
corpkit@junglebook:no-corpus> 
```

When you see it, *corpkit* is ready to accept commands!
