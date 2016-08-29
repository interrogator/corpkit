Concordancing
===============

By default, every search also produces concordance lines. You can view them by typing ``concordance``. This opens an interactive display, which can be scrolled and searched---hit ``h`` to get help on possible commands.

Showing concordance lines in different ways
---------------------------------------------

.. code-block:: bash

   # hide subcorpus name, speaker name
   > show concordance with columns as lmr
   # enlarge window
   > show concordance with columns as lmr and window as 60
   # limit number of results to 100
   > show concordance with columns as lmr and window as 60 and n as 100

The values you enter here are persistant---the window size, number of lines, etc. will remain the same until you shut down the interpreter or provide new values.

Editing, sorting and colouring concordances
----------------------------------

To edit concordance lines, you use the same syntax as you would use to edit results:

.. code-block:: bash

   > edit concordance by skipping subcorpora matching '[123]$'
   > edit concordance by merging entries matching wordlist:people as 'people' 
   > edit concordance by keeping entries matching r'PRP'

Sorting can be by column, or by word 


One nice feature is that concordances can be coloured. This can be done through either indexing or regular expression matches. Note that ``background`` can be added to colour the background instead of the foreground, and ``reset`` can be used to retun things to normal.

.. code-block:: bash

   # indexing methods
   > mark 10 blue
   > mark -10 background red
   > mark 10-15 cyan
   > mark 15- magenta
   # reset all
   > mark - reset

.. code-block:: bash

   # regular expression methods: specify column(s) to search
   > mark m '^PRP.*' yellow
   > mark r 'be(ing)' background green
   > mark lm 'JJR$' blue
   # reset via regex
   > mark m '.*' reset

