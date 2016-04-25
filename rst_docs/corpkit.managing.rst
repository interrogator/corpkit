Managing projects
=================



Loading saved data
-------------------

When you're starting a new session, you probably don't want to start totally from scratch. It's handy to be able to load your previous work. The ``load_saved = True`` keyword argument will find any saved interrogations for a ``Corpus`` object, and load them in as attributes.

.. code-block:: python
   >>> corpus = Corpus('data/psyc-parsed', load_saved = True)

An alternative approach stores all interrogations within an Interrodict object

.. code-block:: python
   >>> import corpkit
   >>> r = corpkit.load_all_results()

Using the GUI
-------------

Your project can also be understood by the corpkit GUI. If you open it, you can simply select your project via ``Open Project`` and resume work in a graphical environment.