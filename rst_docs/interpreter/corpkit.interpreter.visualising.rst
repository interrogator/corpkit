
Plotting
=========

You can plot results and edited results using the `plot` method, which interfaces with *matplotlib*.

.. code-block:: bash

   > plot edited as bar chart with title as 'Example plot' and x_label as 'Subcorpus'
   > plot edited as area chart with stacked and colours as Paired
   > plot edited with style as seaborn-talk # defaults to line chart

There are many possible arguments for customising the figure. The table below shows some of them. 

.. code-block:: bash

   > plot edited as bar chart with rot as 45 and logy and \
   ...    legend_alpha as 0.8 and show_p_val and not grid

+--------------------+------------+---------------------------------+
| Argument           | Type       | Action                          |
+====================+============+=================================+
|  `grid`            |  `bool`    | Show grid in background         |
+--------------------+------------+---------------------------------+
|  `rot`             |  `int`     | Rotate x axis labels n degrees  |
+--------------------+------------+---------------------------------+
|  `shadow`          |  `bool`    | Shadows for some parts of plot  |
+--------------------+------------+---------------------------------+
|  `ncol`            |  `int`     | n columns for legend entries    |
+--------------------+------------+---------------------------------+
|  `explode`         |  `list`    | Explode these entries in pie    |
+--------------------+------------+---------------------------------+
|  `partial_pie`     |  `bool`    | Allow plotting of pie slices    |
+--------------------+------------+---------------------------------+
|  `legend_frame`    |  `bool`    | Show frame around legend        |
+--------------------+------------+---------------------------------+
|  `legend_alpha`    |  `float`   | Opacity of legend               |
+--------------------+------------+---------------------------------+
|  `reverse_legend`  |  `bool`    | Reverse legend entry order      |
+--------------------+------------+---------------------------------+
|  `transpose`       |  `bool`    | Flip axes of DataFrame          |
+--------------------+------------+---------------------------------+
|  `logx/logy`       |  `bool`    | Log scales                      |
+--------------------+------------+---------------------------------+
|  `show_p_val`      |  `bool`    | Try to show p value in legend   |
+--------------------+------------+---------------------------------+

.. note::

   If you want to set a boolean value, you can just say ``and value`` or ``and not value``. If you like, however, you could write it more fully as ``with value as true/false`` as well.