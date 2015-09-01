---
title: "Concordance"
tags: pandas, concordance, gui, corpkit
keywords: pandas, concordance, gui, corpkit
summary: "This concordancer does the basics, but also does some more sophisticated stuff: you can searching constituency and dependency parses, save, load and merge results, and define coloured annotation schemes for thematic categorisation."
last_updated: 2015-09-01
---

Many features this pane are similar to those provided by other concordancers, such as `Window`, `Random`, and some of the kinds of sorting. A key difference, however, is that you can search using Tregex patterns, or by dependency function(s). You can reuse your queries from `Interrogate` if you like.

When searching Trees, you can use the `Trees` option to output bracketted trees instead of plain text. This can be useful in understanding phrase structure grammar, or how to write Tregex queries.

Depending on the kind of data you wish to search, different options become available. If using dependencies, for example, you can select the type of dependency, or write a regular expression to match functions, in addition to words. As with `Interrogate`, you can use special queries, like `ROLES:ACTOR`, or select some preset queries.

> You can use `ctrl/cmd-minus` `ctrl/cmd-plus` to change the concordance window font size.

## Speaker IDs

If you have speaker segmented data, you can restrict your concordancing to specific speakers. Concordancing using speaker IDs is often slow, however. If you want to concordance your data faster, and you don't care if you don't get speaker ID information, leave the `Speakers` option unchecked.

If you select `ALL` as the speaker, you'll get speaker IDs for every line, but it will be quite slow, especially for tree-based queries.

## Editing

You can use `backspace` to delete selected lines, or `shift-backspace` to inverse-delete. Alternatively, buttons are provided.

## Sorting

Sorting is always by the first character in a word. `L1` sorts by the rightmost word in the left-hand column; `L2` sorts by the second rightmost. This is similar for the other columns. Sorting by `M-1` will sort by the last word in the middle column, and `M-2` by the second last. These options are useful if, for example, you are looking at the most common verbal groups in your data.

You can also sort by index, filename, colour, theme or speaker (if available), or randomise your results.

Clicking `Sort` again without making any other changes will invert the sort order.

## Colours and schemes

Something unique about *corpkit* is that you can quickly and easily group, colour and/or categorise your concordance lines.

You can use the numbers 0-9 to colour-code your text. `9` blacks out a line, and `0` returns the line to its default white.

You can also attach names to these colours via `File` &rarr; `Coding scheme`. By using colours in combination with a coding scheme, you can categorise the concordance lines by theme or by a linguistic feature, and then export the categorisations alongside the data.

If you've defined anything in a coding scheme, you can sort by `Scheme` to group your categories together. 

If you do `File` &rarr; `Save project settings`, *corpkit* will remember your coding scheme for next time.

## Exporting concordance lines

`Export` allows you to save results to CSV files, which can be loaded into Excel, or similar.

> Concordance lines are Pandas DataFrames. If you want to work from the command line, you can quickly output them to `LaTeX` tables, and all kinds of other cool things.

## Saving, loading and merging

Unlike corpus interrogations, concordance lines aren't stored by default. Once you're happy with the data on screen, however, you can hit `Store as` and choose a name for the concordance. It will then appear in the list of items that you can reload, as well as in the `Manage` pane, where you can save it permanently.

You can use `Load` to show saved concordance lines, or `Merge` to combine multiple saved lines into the current window. If your current concordance is unsaved, you'll be asked if you want to save it first.

