# corpkit: sophisticated corpus linguistics

[![Join the chat at https://gitter.im/interrogator/corpkit](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/interrogator/corpkit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![DOI](https://zenodo.org/badge/14568/interrogator/corpkit.svg)](https://zenodo.org/badge/latestdoi/14568/interrogator/corpkit) [![Travis](https://img.shields.io/travis/interrogator/corpkit.svg)](https://travis-ci.org/interrogator/corpkit) [![PyPI](https://img.shields.io/pypi/v/corpkit.svg)](https://pypi.python.org/pypi/corpkit) [![ReadTheDocs](https://readthedocs.org/projects/corpkit/badge/?version=latest)](http://corpkit.readthedocs.org/en/latest/)

> **corpkit** is a module for doing more sophisticated corpus linguistics. It links state-of-the-art natural language processing technologies to functional linguistic research aims, allowing you to easily build, search and visualise grammatically annotated corpora in novel ways.

The basic workflow involves making corpora, parsing them, and searching them. The results of searches are Pandas objects, which can be edited, visualised or exported in a lot of ways. The tool has three interfaces, each with its own documentation:

1. [A Python API](https://readthedocs.org/projects/corpkit)
2. [A natural language interpreter](http://corpkit.readthedocs.io/en/latest/rst_docs/corpkit.interpreter.html)
3. [A graphical interface](http://interrogator.github.io/corpkit/)

A quick demo for each interface is provided in this document.

## Feature summary

From all three interfaces, you can do a lot of neat things. In general:

### Parsing

> Corpora are stored as `Corpus` objects, with methods for viewing, parsing, interrogating and concordancing.

* A very simple wrapper around the full Stanford CoreNLP pipeline
* Automatically add annotations, speaker names and metadata to parser output
* Detect speaker names and make these into metadata features
* Multiprocessing
* Store dependency parsed texts, parse trees and metadata in CONLL-U format

### Interrogating corpora

> Interrogating a corpus produces an `Interrogation` object, with results as Pandas DataFrame attributes.

* Search corpora using regular expressions, wordlists, CQL, Tregex, or a rich, purpose built dependency searching syntax
* Collocation, n-gramming
* Restrict searches by metadata feature
* Use metadata as symbolic subcorpora
* Choose what search results return: show any combination of words, lemmata, POS, indices, distance from root node, syntax tree, etc.
* Generate concordances alongside interrogations
* Work with coreference annotation

### Editing results

> `Interrogation` objects have `edit`, `visualise` and `save` methods, to name just a few. Editing creates a new `Interrogation` object.

* Quickly delete, sort, merge entries and subcorpora
* Make relative frequencies (e.g. calculate results as percentage of all words/clauses/nouns ...)
* Use linear regression sorting to find increasing, decreasing, turbulent or static trajectories 
* Calculate p values, etc.
* Keywording
* Simple multiprocessing available for parsing and interrogating
* Results are Pandas objects, so you can do fast, good statistical work on them

### Visualising results

> The `visualise` method of `Interrogation` objects uses matplotlib and seaborn if installed to produce high quality figures.

* Many chart types
* Easily customise titles, axis labels, colours, sizes, number of results to show, etc.
* Make subplots
* Save figures in a number of formats

### Concordancing

> When interrogating a corpus, concordances are also produced, which can allow you to check that your query matches what you want it to.

* Colour, sort, delete lines using regular expressions
* Recalculate results from edited concordance lines (great for removing false positives)
* Format lines for publication with TeX

### Other stuff

* Language modelling
* Save and load results, images, concordances
* Export data to other tools
* Switch between API, GUI and interpreter whenever you like

## Installation

Via pip:

```shell
pip install corpkit
```

Via Git:

```shell
git clone https://www.github.com/interrogator/corpkit
cd corpkit
python setup.py install
```

## Creating a project

Once you've got everything installed, you'll want to create a project---this is just a folder hierarchy that stores your corpora, saved results, figures and so on. You can do it from the command line:

```shell
new_project junglebook
```

Or, from Python:

```python
>>> from corpkit import new_project
>>> new_project('junglebook')
```

### Adding data

Once you've made a new project, you'll want to add a corpus of texts to the `<project>/data` folder.

```shell
cp -R chapters junglebook/data
```

Or, if you really want, from Python:

```python
>>> import shutil
>>> shutil.copytree('/Users/me/Documents/transcripts', 'junglebook/data')
```

You can create projects via the graphical interface as well.

## Ways to use *corpkit*

As explained earlier, there are three ways to use the tool. Each has unique strengths and weaknesses. To summarise them, the Python API is the most powerful, but has the steepest learning curve. The GUI is the least powerful, but easy to learn (though it is still arguably the most powerful linguistics GUI available). The interpreter strikes a happy middle ground, especially for those who are not familiar with Python.

## Interpreter

The first way to use *corpkit* is by entering its natural language interpreter. To activate it, use the `corpkit` command:

```shell
cd junglebook
corpkit
```

You'll get a lovely new prompt into which you can type commands: 

```none
corpkit@junglebook:no-corpus> 
```

Generally speaking, it has the comforts of home, such as history, search, backslash line breaking, and `ls` and `cd` commands. 

### Making corpora

```python
# specify corpus to work on
> set chapters as corpus

# parse the corpus
> parse corpus with speaker_segmentation and metadata and multiprocess as 2
```

### Searching and concordancing

```
# search and exclude
> search corpus for governor-function matching 'root' \
... excluding governor-lemma matching 'be'

# show pos, lemma, index, (e.g. 'NNS/thing/3')
> search corpus for pos matching '^N' showing pos and lemma and index

# further arguments and dynamic structuring
> search corpus for word matching any \
... with pagenum as subcorpora and preserve_case

# show concordance lines
> show concordance with window as 50 and columns as LMR

# colouring concordances
> mark m matching 'have' blue

# recalculate results
> calculate result from concordance
```

### Editing results

```
# skip some numerical subcorpora
> edit result by skipping subcorpora matching [1,2,3,4,5]
> calculate result as percentage of self
# use scipy to calculate trends and sort by them
> sort edited by decrease
```

### Visualise edited results

```
> plot edited as line chart \
... with x_label as 'Subcorpus' and \
... y_label as 'Frequency' and \
... colours as 'summer'
```

### Switching interfaces

```shell
# open graphical interface
> gui
# enter ipython with current namespace
> ipython
# use a new/existing jupyter notebook
> jupyter notebook findings.ipynb
```

## API

Using straight Python is the most powerful way to use *corpkit*, because you can manipulate results with Pandas syntax, construct loops, make recursive queries, and so on. Here are some simple examples of the API syntax:

### Instantiate and search a parsed corpus

```python
### import everything
>>> from corpkit import *
>>> from corpkit.dictionaries import *

### instantiate corpus
>>> corp = Corpus('chapters-parsed')

### search for processes, excluding closed class words,
### and showing lemma forms alongside dependency function
### also, generate a concordance
>>> proc = corp.interrogate(search={F: roles.process},
...                         exclude=wordlists.closedclass,
...                         show=[L, F],
...                         conc=True)
```

The variables `L`, `F` and so on are imported during `from corpkit import *`. They are simply lowercase strings (i.e. `L == 'l'`)

### Edit and visualise the result

```python
### calculate and sort---this sort requires scipy
>>> proc = proc.edit('%', SELF, sort_by='increase')

### make line subplots for the first nine results
>>> plt = proc.visualise('Processes, increasing', subplots=True, layout=(3,3))
### Tweak figure directly here if you need to, before showing it
>>> plt.show()
```

There are also some [more detailed API examples over here](https://www.github.com/interrogator/corpkit/rst_docs/API-README.md). This document is fairly thorough, but now deprecated, because the docs are now over at [ReadTheDocs](https://readthedocs.org/projects/corpkit).

## Graphical interface

Screenshots coming soon! For now, just head [here](http://interrogator.github.io/corpkit/).

## Contact

Twitter: [@interro_gator](https://twitter.com/interro_gator)

## Cite

> `McDonald, D. (2015). corpkit: a toolkit for corpus linguistics. Retrieved from https://www.github.com/interrogator/corpkit. DOI: http://doi.org/10.5281/zenodo.28361`

```

```