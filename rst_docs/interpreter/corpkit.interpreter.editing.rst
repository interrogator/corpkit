Editing results
================

Once you have generated a `result` object via the `search` command, you can edit the result in a number of ways. You can delete, merge or otherwise alter entries or subcorpora; you can do statistics, and you can sort results.

Editing, calculating and sorting each create a new object, called `edited`. This means that if you make a mistake, you still have access to the original `result` object.

The edit command
------------------

When using the `edit` command, the main things you'll want to do is skip, keep, span or merge results or subcorpora.

.. code-block:: bash

   > edit result by keeping subcorpora matching '[01234]'
   > edit result by skipping entries matching wordlists.closedclass
   > edit result by merging entries matching 'be|have' as 'aux'

.. note::

    The syntax above works for concordance lines too, if you change `result` to `concordance`. Merging, of course, is not possible.

Doing basic statistics 
------------------------

The `calculate` command allows you to turn the absolute frequencies into relative frequencies, keyness scores, etc.

.. code-block:: bash

   > calculate result as percentage of self
   > calculate edited as percentage of features.clauses
   > calculate result as keyness of self

If you want to run more complicated operations on the results, you might like to use the `ipython` command to enter an IPython session, and then manipulate the Pandas objects directly.

Sorting results
------------------

The `sort` command allows you to change the search result order.

Possible values are `total`, `name`, `infreq`, `increase`, `decrease`, `static`, `turbulent`.

.. code-block:: bash

   > sort result by total
   # requires scipy
   > sort edited by increase
