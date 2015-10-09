---
title: "Visualise"
tags: [visualise, pandas, matplotlib]
keywords: visualise, pandas, plot, matplotlib, python, corpkit, gui
summary: "This tab is all about representing your results graphically. You should be able to generate publication-quality figures without needing to export the data from the tool."
last_updated: 2015-09-01
---

Most options here are self-explanatory. Pick the results you want to plot, play with some options, and hit `Plot`. This can be a great way to identify salient linguistic features in your dataset. Once you've plotted something, a navigation pane appears under the figure, allowing scrolling, zooming, saving and so forth.

Below are explanations of the various options.

## Visualisation options

### Data to plot

Here, you select the interrogation or edited result you want to plot, as well its branch.

### Results to show

Plot only the top `n` entries from the results of interest. If you don't want these, go back to the `Edit` tab and remove/sort the results some more. You can type in `all` to get every result&mdash;but be warned, this often won't look so good!

### Kind of chart

You can choose between line, area, pie and bar charts.

### Axis labels

*corpkit* tries to guess useful axis labels. When it fails, you can enter your own.

### Explode

When making pie charts, you can *explode* one or more results&mdash;that is, cut them slightly out of the pie for emphasis. Enter the name of the entry you want to explode, or use a list:

> `[me,myself,i]`

Or use a pre-defined wordlist:

> `LIST:MENTAL`

### Log axes

You can plot using a logarithmic scale for either axis.

### Cumulative

This option adds counts from previous subcorpora to later subcorpora, to give a cumulative distribution.

### Transpose

Temporarily flip the x and y axis. This can be performed when editing, too.

### Black and white

Render the figure in black and white. For line charts, try to create unique-looking line markers.

{{note}}You could also use a greyscale colour scheme with a line plot, in order to produce a black and white figure without the complex line types{{end}}

## TeX 

Checking the `Use TeX` option will mean that the plotter will try to use `LaTeX` to typeset the text in the chart. If you have a TeX distribution, but this option isn't working for you, you may need to use the command-line version of `corpkit`.

### Reverse legend

This option reverses the order in which legend entries occur. It can be useful when making horizontal bar ('barh') charts.

### Subplots

Subplots creates a separate figure for each entry in your results. You might have to resize the figure a little when using this option to give it sensible proportions.

### Grid

Show or hide the grid in the figure's background.

### Stacked

For bar charts, stack entries on top of each other, rather than beside each other.

### Colour scheme

Choose the colourmap for plotted entries.

### Plot style

Slight aesthetic changes to the plot: background colour, line size, etc.

### Legend position

Choose where in the figure the legend should sit, or let it float around with `best`.

### Figure size

Choose dimensions for the figure. Equal dimensions is probably a good idea for pie charts.

### Show totals

Try to display aggregates or total percentages on the plot, in the legend, or both.

## Interacting with your figure

Once you've generated a figure, a toolbar appears beneath it, with options for panning and zooming. The figure is smart enough to reposition the legend depending on the position of the data currently being shown.

You can use this toolbar to save the image to disk. Your `project/images` directory is a good place for them.

## Visualising data with other tools

If you're more confortable generating visualisations in another tool, you can head to the `Manage` tab to export a CSV version of any interrogations or edited results. This can be imported into Excel, for example.

## Viewing other images

You can use the `Previous`/`Next` buttons to bring up any images that have been saved in the `project/images` directory.

## Next steps

Through the process of interrogating, editing and visualising, you may find something that sticks out: maybe something is very frequent in a subcorpus, or maybe something is conspicuously absent. The `Concordance` tab allows you to resuse your `Interrogate` queries to look at language in co(n)text.
