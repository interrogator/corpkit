Concordancing
===============

By default, every search also produces concordance lines. You can view them by typing ``concordance``. This opens an interactive display, which can be scrolled and searched---hit ``h`` to get help on possible commands.

Customising appearance
---------------------------------------------

The first thing you might want to do is adjust how concordance lines are displayed:

.. code-block:: shell

   # hide subcorpus name, speaker name
   > show concordance with columns as lmr
   # enlarge window
   > show concordance with columns as lmr and window as 60
   # limit number of results to 100
   > show concordance with columns as lmr and window as 60 and n as 100

The values you enter here are persistant---the window size, number of lines, etc. will remain the same until you shut down the interpreter or provide new values.

Sorting
--------

Sorting can be by column, or by word.

.. code-block:: shell

   # middle column, first word
   > sort concordance by M1
   # left column, last word
   > sort concordance by L1
   # right column, third word
   > sort concordance by R3
   # by index (original order)
   > sort concordance by index

Colouring
-----------

One nice feature is that concordances can be coloured. This can be done through either indexing or regular expression matches. Note that ``background`` can be added to colour the background instead of the foreground, and ``dim``/``bright`` can be used to adjust text brightness. This means that you can code lines for multiple phenomena. Background highlighting could mark the argument structure, foreground highlighting could mark the mood type, and bright and dim could be used to mark exemplars or false positives.

.. note::

   If you're using Python 2, you may find that colouring concordance lines causes some interference with `readline`, making it difficult to select or search previous commands. This is a limitation of readline in Python 2. Use Python 3 instead!

.. code-block:: shell

   # colour by index
   > mark 10 blue
   > mark -10 background red
   > mark 10-15 cyan
   > mark 15- magenta
   # reset all
   > mark - reset

.. code-block:: shell

   # regular expression methods: specify column(s) to search
   > mark m '^PRP.*' yellow
   > mark r 'be(ing)' background green
   > mark lm 'JJR$' dim
   # reset via regex
   > mark m '.*' reset

You can then sort by colour with `sort concordance by scheme`. If you export the concordances to a file (`export concordance as csv to conc.csv`), colour information will be added in additional columns.

Editing
--------

To edit concordance lines, you can use the same syntax as you would use to edit results:

.. code-block:: shell

   > edit concordance by skipping subcorpora matching '[123]$'
   > edit concordance by keeping entries matching 'PRP'

Perhaps faster is the use of `del` and `keep`. For these, specify the column and the criteria using the same methods as you would for colouring:

.. code-block:: shell

   > del m matching 'this'
   > keep l matching '^I\s'
   > del 10-20

Recalculating results from concordance lines
---------------------------------------------

If you've deleted some concordance lines, you can update the ``result`` object to reflect these changes with `calculate result from concordance`.


Working with metadata
------------------------

You can use ``show_conc_metadata`` when interrogating or concordancing to collect and display metadata alongside concordance results:

.. code-block:: shell

   > search corpus for words matching any with show_conc_metadata
   > concordance

