Making projects and corpora
============================

The first two things you need to do when using *corpkit* are to create a project, and to create (and optionally parse) a corpus. These steps can all be accomplished quickly using shell commands. They can also be done using the interpreter, however.

Once you're in *corpkit*, the command below will create a new project called `iran-news`, and move you into it.

.. code-block:: bash

   new project named iran-news

Adding a corpus
----------------

Adding a corpus simply copies it to the project's data directory. The syntax is simple:

.. code-block:: bash

   add '../../my_corpus'