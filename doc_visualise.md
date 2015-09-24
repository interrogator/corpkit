---
title: "Visualise"
tags: [visualise, pandas, matplotlib]
keywords: visualise, pandas, plot, matplotlib, python, corpkit, gui
summary: "This tab is all about representing your results graphically. You should be able to generate publication-quality figures without needing to export the data from the tool."
last_updated: 2015-09-01
---

Most options here are self-explanatory. Pick the results you want to plot, play with some options, and hit `Plot`. This can be a great way to identify salient linguistic features in your dataset. Once you've plotted something, a navigation pane appears under the figure, allowing scrolling, zooming, saving and so forth.

Note that `Number to plot` takes the top `n` entries from the results of interest. If you don't want these, go back to the `Edit` tab and remove/sort the results some more. You can type in `all` to get every result&mdash;but be warned, this often won't look so good!

{{warning}} More documentation forthcoming...{{end}}

## TeX 

Checking the `TeX` option will mean that the plotter will try to use `LaTeX` to typeset the text in the chart. If you have a TeX distribution, but this option isn't working for you, you may need to use the command-line version of `corpkit`.

## Interacting with your figure

Once you've generated a figure, a toolbar appears beneath it, with options for panning and zooming. The figure is smart enough to reposition the legend depending on the position of the data currently being shown.

## Visualising data with other tools

If you're more confortable generating visualisations in another tool, you can head to the `Manage` tab to export a CSV version of any interrogations or edited results. This can be imported into Excel, for example.

## Viewing other images

You can use the `Previous`/`Next` buttons to bring up any images that have been saved in the `project/images` directory.

## Next steps

Through the process of interrogating, editing and visualising, you may find something that sticks out: maybe something is very frequent in a subcorpus, or maybe something is conspicuously absent. The `Concordance` tab allows you to resuse your `Interrogate` queries to look at language in co(n)text.
