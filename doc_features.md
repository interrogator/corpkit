---
title: "Key features"
tags: [features, getting-started, pandas, matplotlib, concordance]
keywords: features, gui, corpkit
summary: "corpkit does what you'd expect, plus a lot more. Better still, it's free and open-source!"
last_updated: 2015-09-01
---

#### Parsing

*corpkit* helps you parse texts, without needing to go the command line!

#### Speaker IDs

*corpkit* can recognise speaker IDs when parsing, and restrict searches to particular speakers. All you need to do is format your data like a transcript:

    PROSECUTOR: Good afternoon, Mr. President.
    CLINTON: Good afternoon.
    PROSECUTOR: Could you please state your full name for the record, sir?
    CLINTON: William Jefferson Clinton.

#### Search lexis and grammar

*corpkit* allows you to search for lexical and grammatical features, separately or together.

#### Compare subcorpora

*corpkit* is designed to work with structured corpora (those containing subfolders). 

#### Concordance grammatically

You can concordance using Tregex queries or dependency roles, rather than a simple regular expression search of the text.

There are also preset queries for concordancing of particular moods (imperative, interrogate, (modalised) declarative), process types (relational, mental, verbal).

#### Annotate concordances

You can quickly highlight concordance lines, add tags, sort by tag, and export these tags alongside your data.

#### Store everything

Every interrogation is stored in memory, alongside all options used to generate the result. You can save these to disk and auto-load them when you open a project. Concordances can be stored, saved, merged and loaded too. This means that you can always reproduce a particular interrogation. You can even share your project with others.

#### Command line interface

*corpkit* has a lot of functionality, and could probably keep you busy for a long time. If you ever find that the tools aren't intuitive, it is useful to remember that the major functions at work in the interface can also be called via the command line. Generally speaking, command line operation makes it possible to do far more complicated things with your data.

* When interrogating, you can quickly make lists of corpora or queries and perform each simultaneously. 
* When editing, you can create lists of entries to rename or merge, and iterate over them.
* When plotting, you can generate HTML based visuals that are clickable, highlightable, embeddable, and so on.
* You could also be quite recursive, and automatically generate concordance lines for the most key and unkey keywords in every subcorpus.

If you're interested in trying out the command line interface, on OSX, you could simply enter `Terminal` and do:

```
sudo easy_install corpkit
python
```

to download and install *corpkit*, and then to enter Python. From there, you can import the main functions, and begin:

```python
>>> from corpkit import interrogator, editor, plotter, conc
>>> q = r'/NN.?/ >># NP'
>>> result = interrogator('path/to/corpus', 'word', lemmatise = True)
```

Because *corpkit* data is generally stored as [Pandas](http://pandas.pydata.org/) objects, from the command line it is easy to manipulate results in complex ways, with most of the functionality of `MATLAB` or `R`.

Command line operation of *corpkit* is presented in more detail at the [`corpkit GitHub repostitory`](https://www.github.com/interrogator/corpkit).

#### Open source

*corpkit* is free and open source!