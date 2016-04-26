Visualising results
=====================

One thing missing in a lot of corpus linguistic tools is the ability to produce high-quality visualisations of corpus data. ``corpkit`` uses the :class:`corpkit.interrogation.Interrogation.visualise` method to do this.

.. contents::
   :local:

.. note::

   Most of the keyword arguments from Pandas' plot_ method are available. See their documentation for more information.

Basics
---------------------

``visualise()`` is a method of all :class:`corpkit.interrogation.Interrogation` objects. If you use `from corpkit import *`, it is also monkey-patched to Pandas objects.

.. note::

   If you're using a *Jupyter Notebook*, make sure you use ``%matplotlib inline`` or ``%matplotlib notebook`` to set the appropriate backend.

A common workflow is to interrogate a corpus, relative results, and visualise:

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

The visualise method allows ``line``, ``bar``, horizontal bar (``barh``), ``area``, and ``pie`` charts. Those with `seaborn` can also use ``'heatmap'`` (docs_). Just pass in the type as a string with the ``kind`` keyword argument. Arguments such as ``robust = True`` can then be used.

.. code-block:: python

   >>> data.visualise(kind='heatmap', robust=True, figsize = (4, 12),
   ...                x_label = 'Subcorpus', y_label = 'Event').show()

.. figure:: https://raw.githubusercontent.com/interrogator/corpkit/master/images/event-heatmap.png
   :width: 60%
   :target: https://raw.githubusercontent.com/interrogator/corpkit/master/images/event-heatmap.png


Stacked area/line plots can be made with ``stacked = True``. You can also use ``filled = True`` to attempt to make all values sum to 100. Cumulative plotting can be done with ``cumulative = True``.

.. figure:: https://raw.githubusercontent.com/interrogator/corpkit/master/images/area.png
   :width: 60%
   :caption: Area plot using viridis colourmap
   :target: https://raw.githubusercontent.com/interrogator/corpkit/master/images/area.png

.. figure:: https://raw.githubusercontent.com/interrogator/corpkit/master/images/area-filled.png
   :width: 60%
   :caption: Filled area plot using viridis colourmap
   :target: https://raw.githubusercontent.com/interrogator/corpkit/master/images/area-filled.png

Plot style
---------------------

You can select from a number of styles, such as ``ggplot``, ``fivethirtyeight``, ``bmh``, and ``classic``. If you have `seaborn` installed (and you should), then you can also select from `seaborn` styles (``seaborn-paper``, ``seaborn-dark``, etc.).

Figure and font size
---------------------

You can pass in a tuple of ``(width, height)`` to control the size of the figure. You can also pass an integer as ``fontsize``.

Title and labels
---------------------

You can label your plot with `title`, `x_label` and `y_label`:

.. code-block:: python

   >>> data.visualise('Modals', x_label = 'Subcorpus', y_label = 'Relative frequency')

Subplots
---------------------

``subplots = True`` makes a separate plot for every entry in the data. If using it, you'll probably also want to use ``layout = (rows, columns)`` to specify how you'd like the plots arranged.

.. code-block:: python

   >>> data.visualise(subplots = True, layout = (2, 3)).show()

.. figure:: https://raw.githubusercontent.com/interrogator/corpkit/master/images/subplots.png
   :target: https://raw.githubusercontent.com/interrogator/corpkit/master/images/subplots.png
   :caption: Line charts using subplots and layout specification


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

If you pass in ``draggable = True``, you should be able to drag the legend around the figure.

Colours
---------------------

You can use the ``colours`` keyword argument to pass in:

   1. A colour name recognised by *matplotlib*
   2. A hex colour string
   3. A colourmap object

There is an extra argument, ``black_and_white``, which can be set to ``True`` to make greyscale plots. Unlike ``colours``, it also updates line styles.

Saving figures
---------------------

To save a figure to a project's `images` directory, simply use:

.. code-block:: python

   >>> data.visualise(save='name')

You can use ``output_format = 'png'/'pdf`` to change the file format.

Other options
--------------------

There are a number of further keyword arguments for customising figures:

+--------------------+------------+---------------------------------+
| Argument           | Type       | Action                          |
+====================+============+=================================+
| ``grid``           | ``bool``   | Show grid in background         |
+--------------------+------------+---------------------------------+
| ``rot``            | ``int``    | Rotate x axis labels n degrees  |
+--------------------+------------+---------------------------------+
| ``shadow``         | ``bool``   | Shadows for some parts of plot  |
+--------------------+------------+---------------------------------+
| ``ncol``           | ``int``    | n columns for legend entries    |
+--------------------+------------+---------------------------------+
| ``explode``        | ``list``   | Explode these entries in pie    |
+--------------------+------------+---------------------------------+
| ``partial_pie``    | ``bool``   | Allow plotting of pie slices    |
+--------------------+------------+---------------------------------+
| ``legend_frame``   | ``bool``   | Show frame around legend        |
+--------------------+------------+---------------------------------+
| ``legend_alpha``   | ``float``  | Opacity of legend               |
+--------------------+------------+---------------------------------+
| ``reverse_legend`` | ``bool``   | Reverse legend entry order      |
+--------------------+------------+---------------------------------+
| ``transpose``      | ``bool``   | Flip axes of DataFrame          |
+--------------------+------------+---------------------------------+
| ``logx/logy``      | ``bool``   | Log scales                      |
+--------------------+------------+---------------------------------+
| ``show_p_val``     | ``bool``   | Try to show p value in legend   |
+--------------------+------------+---------------------------------+
| ``interactive``    | ``bool``   | Experimental mpld3_ use          |
+--------------------+------------+---------------------------------+

A number of these and other options for customising figures are also described in the :class:`corpkit.interrogation.Interrogation.visualise` method documentation.

.. _plot: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html
.. _docs: https://stanford.edu/~mwaskom/software/seaborn/generated/seaborn.heatmap.html
.. _mpld3: http://mpld3.github.io/
