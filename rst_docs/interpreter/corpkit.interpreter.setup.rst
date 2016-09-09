Setup
==============================

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

   >>> from corpkit import env
   >>> env()

The prompt
------------

When using the interpreter, the prompt (the text to the left of where you type your command) displays the directory you are in (with an asterisk if it does not appear to be a *corpkit* project) and the currently active corpus, if any:

.. code-block:: none

   corpkit@junglebook:no-corpus> 

When you see it, *corpkit* is ready to accept commands!

