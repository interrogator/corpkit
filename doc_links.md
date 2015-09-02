---
title: "Links"
tags: [links, help, resources]
keywords: interrogation, gui, corpkit, links, libraries, python
summary: "A few things that might help you!"
last_updated: 2015-09-01
---
{% include linkrefs.html %}

## Parsing

* [*Stanford CoreNLP*](http://nlp.stanford.edu/index.shtml): the parser used by *corpkit*
* [*Stanford Dependencies Manual*](http://nlp.stanford.edu/software/dependencies_manual.pdf): help understanding dependency grammars and dependency types.
* [*Universal Dependencies*](http://universaldependencies.github.io/docs/#language-en) used by the CoreNLP parser

{{warning}} If you use Speaker IDs, *corpkit* will ever so slightly modify the CoreNLP xml output format to include a tag for each sentece. This could potentially lead to compatibility issues if you want to run the parsed file through other tools. {{end}}

## Querying

* [Introduction to *Tregex*](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html), the query language used to search constituency parse trees.
* [*Regular Expression Cheatsheet*](http://www.cheatography.com/davechild/cheat-sheets/regular-expressions/) (one of *many*!)
* [*Regex Crosswords*](http://regexcrossword.com/): a novel way to learn Regular Expressions

## Related tools

* [*Wmatrix*](http://ucrel.lancs.ac.uk/wmatrix/)
* [*Sketch Engine*](http://www.sketchengine.co.uk/)
* [*AntConc*](http://www.laurenceanthony.net/software.html)
* [*UAM Corpus Tool*](http://www.wagsoft.com/CorpusTool/index.html)
* [*Wordsmith Tools*](http://www.lexically.net/wordsmith/)
* [*Natural Language Toolkit*](http://www.nltk.org/)

## Leveraged libraries and modules

* [*Python*](https://www.python.org/): language in which *corpkit* is written
* [*Jupyter Notebook*](https://jupyter.org/): programmatic web-browser interface 
* [*pandas*](http://pandas.pydata.org/): Manipulating datasets
* [*matplotlib*](http://matplotlib.org/): Plotting data
* [*mpld3*](http://mpld3.github.io/): Interactive visualisation
* [*SciPy*](http://www.scipy.org): Linear regression algorithm
* [*TkInter*](https://wiki.python.org/moin/TkInter): Python GUI
* [*tkintertable*](https://github.com/dmnfarrell/tkintertable): show spreadsheets in a GUI
* [*pattern*](http://www.clips.ua.ac.be/pages/pattern-en): Get verb inflections, etc.
* [*NLTK*](http://www.nltk.org/): lemmatisation, tokenisation
* [*CoreNLP XML*](http://corenlp-xml-library.readthedocs.org/): fast navigation of CoreNLP output
* [*Jekyll*](http://jekyllrb.com/): website generator
* [*Jekyll Documentation Theme*](http://idratherbewriting.com/documentation-theme-jekyll/): template for this site
