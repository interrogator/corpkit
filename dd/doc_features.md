---
layout: page
title: "Command line operation"
category: doc
date: 2015-08-30 22:08:50
order: 9
---

`corpkit` has a lot of functionality, and could probably keep you busy for a long time. If you ever find that the tools aren't intuitive, it is useful to remember that the major functions at work in the interface can also be called via the command line. Generally speaking, command line operation makes it possible to do far more complicated things with your data.

* When interrogating, you can quickly make lists of corpora or queries and perform each simultaneously. 
* When editing, you can create lists of entries to rename or merge, and iterate over them.
* When plotting, you can generate HTML based visuals that are clickable, highlightable, embeddable, and so on.
* You could also be quite recursive, and automatically generate concordance lines for the most key and unkey keywords in every subcorpus.

If you're interested in trying out the command line interface, on OSX, you could simply enter `Terminal` and do:

```
sudo easy_install corpkit
python
```

to download and install `corpkit`, and then to enter Python. From there, you can import the main functions, and begin:

```python
>>> from corpkit import interrogator, editor, plotter, conc
>>> q = r'/NN.?/ >># NP'
>>> result = interrogator('path/to/corpus', 'word', lemmatise = True)
```

Because `corpkit` data is generally stored as [Pandas](http://pandas.pydata.org/) objects, from the command line it is easy to manipulate results in complex ways, with most of the functionality of `MATLAB` or `R`.

Command line operation of `corpkit` is presented in more detail at the [`corpkit GitHub repostitory`](https://www.github.com/interrogator/corpkit).
