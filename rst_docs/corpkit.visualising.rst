Visualising results
=====================

One thing missing in a lot of corpus linguistic tools is the ability to produce high-quality visualisations of corpus data. ``corpkit`` uses the :class:`corpkit.interrogation.Interrogation.visualise` method to do this.

.. contents::
   :local:

.. note::

   Most of the keyword arguments from Pandas' plot_ method are available. See their documentation for more information.

Introduction
---------------------

``visualise()`` is a method of all :class:`corpkit.interrogation.Interrogation` objects. If you use `from corpkit import *`, it is also monkey-patched to Pandas objects. A common workflow is to interrogate the data, relative results, and visualise:

.. code-block:: python

   >>> from corpkit import *
   >>> corpus = Corpus('data/P-parsed', load_saved = True)
   >>> counts = corpus.interrogate({T: r'MD < __'})
   >>> reldat = counts.edit('%', SELF)
   >>> reldat.visualise('Modals', kind = 'line', num_to_plot = ALL).show()
   ### the visualise method can also attach to the df:
   >>> reldat.results.visualise(...).show()

The current behaviour of ``visualise()`` is to return the ``pyplot`` module. This allows you to edit figures further before showing them. Therefore, there are two ways to show the figure: 

.. code-block:: python

   >>> data.visualise().show()

.. code-block:: python

   >>> plt = data.visualise()
   >>> plt.show()

Plot type
---------------------

The visualise method allows line, bar, horizontal bar (``barh``), area, and pie charts. Those with `seaborn` can also use ``'heatmap'`` (docs_). Just pass in the type as a string with the ``kind`` keyword argument.

Stacked area/line plots can be made with ``stacked = True``. You can also use ``filled = True`` to attempt to make all values sum to 100. Cumulative plotting can be done with ``cumulative = True``.

Plot style
---------------------

You can select from a number of styles, such as ``ggplot``, ``fivethirtyeight``, ``bmh``, and ``classic``. If you have `seaborn` installed (and you should), then you can also select from `seaborn` styles (``seaborn-paper``, ``seaborn-dark``, etc.).

Figure and font size
---------------------

You can pass in a tuple of ``(width, height)`` to control the size of the figure. You can also pass an integer as ``fontsize``.

Title and labels
---------------------

You can label your plot with `title`, `x_label` and `y_label`:

   >>> data.visualise('Modals', x_label = 'Subcorpus', y_label = 'Relative frequency')

Subplots
---------------------

``subplots = True`` makes a separate plot for every entry in the data. If using it, you'll probably also want to use ``layout = (rows, columns)`` to specify how you'd like the plots arranged.

TeX
---------------------

If you have LaTeX installed, you can use ``tex = True`` to render text with LaTeX. By default, ``visualise()`` tries to use LaTeX if it can.

Legend
---------------------

You can turn the legend off with ``legend = False``. Legend placement can be controlled with ``legend_pos``, which can be:

.. table:: 
    :column-dividers: single double double single

+---------------------+----------------------------+----------------------+
| Margin              |      Figure                |  Margin              |
+=====================+=============+==============+======================+
| outside upper left  | upper left  | upper right  | outside upper right  |
+---------------------+-------------+--------------+----------------------+
| outside center left | center left | center right | outside center right |
+---------------------+-------------+--------------+----------------------+
| outside lower left  | lower left  | lower right  | outside lower right  |
+---------------------+-------------+--------------+----------------------+

The default value, ``'best'``, tries to find the best place automatically (without leaving the figure boundaries).

Colours
---------------------

You can use the ``colours`` keyword argument to pass in:

   1. A colour name recognised by *matplotlib*
   2. A colour hash
   3. A colourmap object

There is an extra argument, ``black_and_white``, which can be used to make greyscale plots. Unlike ``colours``, it also updates line styles.

Saving figures
---------------------

To save a figure to a project's `images` directory, simply use:

.. code-block:: python

   >>> data.visualise(save='name')

You can use ``output_format = 'png'/'pdf`` to change the file format.


.. _plot: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html
.. _docs: .. https://stanford.edu/~mwaskom/software/seaborn/generated/seaborn.heatmap.html