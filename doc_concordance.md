---
title: "Concordance"
tags: [pandas, concordance]
keywords: pandas, concordance, gui, corpkit
summary: "This concordancer does all the basics you'd expect, but also, much more!"
last_updated: 2016-02-04
---
{% include linkrefs.html %}

Many features this pane are similar to those provided by other concordancers, such as `Window`, `Random`, and some of the kinds of sorting. A key difference, however, is that the search interface is the same as the one provided in the `Interrogate` tab, meaning that you have access to very complex kinds of searches. In fact, when you interrogate the corpus, concordance lines are automatically generated, so you can move in and out between levels of abstraction with ease.

{{tip}} You can use <code>ctrl/cmd-minus</code> <code>ctrl/cmd-plus</code> to change the concordance window font size. {{end}}

## Editing

You can use `backspace` to delete selected lines, or `shift-backspace` to inverse-delete. Alternatively, buttons are provided.

## Sorting

Sorting is always by the first character in a word. `L1` sorts by the rightmost word in the left-hand column; `L2` sorts by the second rightmost. This is similar for the other columns. Sorting by `M-1` will sort by the last word in the middle column, and `M-2` by the second last. These options are useful if, for example, you are looking at the most common verbal groups in your data.

You can also sort by index, filename, colour, theme or speaker ID (if available), or randomise your results.

Clicking `Sort` again without making any other changes will invert the sort order.

## Colours and schemes

Something unique about *corpkit* is that you can quickly and easily group, colour and/or categorise your concordance lines. You can use the numbers 0-9 to colour-code your text. `9` blacks out a line, and `0` returns the line to its default white.

You can also attach names to these colours via `Schemes` &rarr; `Coding scheme`. By using colours in combination with a coding scheme, you can categorise the concordance lines by theme or by a linguistic feature, and then export the categorisations alongside the data.

If you've defined anything in a coding scheme, you can sort by `Scheme` to group your categories together. 

If you do `File` &rarr; `Save project settings`, *corpkit* will remember your coding scheme for next time.

## Exporting concordance lines

`Export` allows you to save results to CSV files, which can be loaded into Excel, or similar.

{{note}} Concordance lines are Pandas DataFrames. If you want to work from the command line, you can quickly output them to <code>LaTeX</code> tables, and all kinds of other cool things. {{end}}

## Saving, loading and merging

Unlike corpus interrogations, concordance lines aren't stored by default. Once you're happy with the data on screen, however, you can hit `Store as` and choose a name for the concordance. It will then appear in the list of items that you can reload, as well as in the `Manage Project` window, where you can save it permanently.

You can use `Load` to show saved concordance lines, or `Merge` to combine multiple saved lines into the current window. If your current concordance is unsaved, don't worry, you'll be asked if you want to save it first.

