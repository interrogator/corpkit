## *corpkit*: a Python-based toolkit for working with parsed linguistic corpora

[![Join the chat at https://gitter.im/interrogator/corpkit](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/interrogator/corpkit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

### D. McDonald

> Because I kept building new tools and functions for my linguistic research, I decided to put them together into `corpkit`, a simple toolkit for working with parsed and structured linguistic corpora.

<!-- MarkdownTOC -->

- [What's in here?](#whats-in-here)
    - [Key features](#key-features)
- [Installation](#installation)
    - [By downloading the repository](#by-downloading-the-repository)
    - [By cloning the repository](#by-cloning-the-repository)
    - [Via `pip`](#via-pip)
- [Unpacking the orientation data](#unpacking-the-orientation-data)
- [Quickstart](#quickstart)
- [Examples](#examples)
    - [Systemic functional stuff](#systemic-functional-stuff)
    - [More complex stuff](#more-complex-stuff)
- [More information](#more-information)
- [IPython Notebook usability](#ipython-notebook-usability)
- [Coming soon](#coming-soon)

<!-- /MarkdownTOC -->

## What's in here?

Essentially, the module contains a bunch of functions for interrogating corpora, then manipulating or visualising the results. Thee most important of them are:

| **Function name** | Purpose                            | 
| ----------------- | ---------------------------------- | 
| `interrogator()`  | interrogate parse trees, dependencies, or find keywords or ngrams | 
| `plotter()`       | visualise `interrogator()` results with *matplotlib* | 
| `surgeon()`       | edit `interrogator()` results      | 
| `merger()`        | merge `interrogator()` results      | 
| `conc()`          | complex concordancing of subcorpora | 
| `keywords()`      | get keywords and ngrams from corpus/subcorpus/concordance lines | 
| `collocates()`    | get collocates from corpus/subcorpus/concordance lines | 

While most of the tools are designed to work with corpora that are parsed (by e.g. [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml)) and structured (in a series of directories representing different points in time, speaker IDs, chapters of a book, etc.), the tools can generally also be used on text that is unparsed and/or unstructured. That said, you won't be able to do nearly as much cool stuff.

The idea is to run the tools from an [IPython Notebook](http://ipython.org/notebook.html), but you could also operate the toolkit from the command line if you wanted to have less fun.

### Key features

#### `interrogator()`

* Use [Tregex](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html) to search parse trees for complex lexicogrammatical phenomena
* Search Stanford dependencies (whichever variety you like) for information about the role, governor, dependent or index of a token matching a regular expression
* Return words or phrases, POS/group/phrase tags, raw counts, or all three.
* Return lemmatised or unlemmatised results (using WordNet for constituency trees, and CoreNLP's lemmatisation for dependencies). Add words to `dictionaries/word_transforms.py` manually if need be
* Look for keywords in each subcorpus (using code from [*Spindle*](https://github.com/sgrau/spindle-code), and chart their keyness
* Look for ngrams in each subcorpus, and chart their frequency
* Two-way UK-US spelling conversion (superior as the former may be), and the ability to add words manually.

#### `plotter()` 

* Plot any number of results onto line charts (see below)
* Plot anything you like: words, tags, counts for grammatical features ...
* Customisable figure titles, axes labels, legends, image size, etc.
* Uses `TeX` if you have it
* Plot by absolute frequency, or as a ratio/percentage of another list: 
    * plot the total number of verbs, or total number of verbs that are *be*
    * plot the percentage of verbs that are *be*
    * plot the percentage of *be* verbs that are *was*
    * plot the ratio of *was/were* ...
    * etc.
* Plot more advanced kinds of relative frequency: for example, find all proper nouns that are subjects of clauses, and plot each word as a percentage of all instances of that word in the corpus (see below)
* Plot only specific subcorpora in your collection, or spans of subcorpora
* Use linear regression to figure out the trajectories of results, sort by the most increasing, decreasing or static values.
* Show the *p*-value for linear regression slopes, or exclude results above *p*
* Use log scales if you really want
* Save output to file and/or generate CSV

#### Other stuff

* View results as a table via `Pandas`
* Quickly edit and merge interrogation results with `surgeon()` and `merger()`, using regular expressions, result indices or lists of words (see below)
* Tools for resorting or doing maths on interrogation results
* Tools for quickly and easily generating lists of keywords, ngrams, collocates and concordances
* Concordance using Tregex (i.e. concordance all nominal groups containing *gross* as an adjective with `NP < (JJ < /gross/)`)
* Randomise concordance results, determine window size, save to CSV, etc.
* Quickly save interrogations and figures to file, and reload results in new sessions
* Build dictionaries from corpora, subcorpora or concordance lines, which can then be used as reference corpora for keyword generation
* Start a new blank project with `new_project()`

One of the main reasons for these tools was to make it quicker and easier to explore corpora in complex ways, using output from one tool as input for the next.

* n-gramming and keywording can be done via `interrogator()`
* keywording can easily be done on your concordance lines
* you can use `surgeon()` to edit concordance line output
* You can build a dictionary from a corpus, subcorpus, or from concordance lines, and use it as a reference corpus for keywording
* and so on ...

Included here is a sample project, `orientation`, which you can run in order to familiarise yourself with the `corpkit` module. It uses a corpus of paragraphs of the NYT containing the word *risk*. Due to size restrictions, This data only includes parse trees (no dependencies), and isn't included in the pip package.

## Installation

You can get `corpkit` running by downloading or cloning this repository, or via `pip`.

### By downloading the repository

Hit 'Download ZIP' and unzip the file. Then `cd` into the newly created directory and install:

```shell
cd corpkit-master
# might need sudo:
python setup.py install
```

### By cloning the repository

Clone the repo, ``cd`` into it and run the setup:

```shell
git clone https://github.com/interrogator/corpkit.git
cd corpkit
# might need sudo:
python setup.py install
```

### Via `pip`

```shell
# might need sudo:
pip install corpkit
```

To interrogate corpora and plot results, you need *Java*, *NLTK* and *matplotlib*. Dependency searching needs *Beautiful Soup*. Tabling results needs *Pandas*, etc. For NLTK, you can also use pip:

```shell
# might need sudo
pip install -U nltk
```

The `pip` installation of NLTK does not come with the data needed for NLTK's tokeniser, so you'll also need to install that from Python:

```python
>>> import nltk
# change 'punkt' to 'all' to get everything
>>> nltk.download('punkt')
```

## Unpacking the orientation data

If you installed by downloading or cloning this repository, you'll have the orientation project installed. To use it, `cd` into the orientation project and unzip the data files:

```shell
cd orientation
# unzip data to data folder
gzip -dc data/nyt.tar.gz | tar -xf - -C data
```

## Quickstart

The best way to use `corpkit` is by opening `orientation.ipynb` with IPython, and executing the first few cells:

```shell
ipython notebook orientation.ipynb
```

Or, just use *(I)Python* (more difficult, less fun):

```python
>>> import corpkit
>>> from corpkit import interroplot

# set corpus path
>>> corpus = 'data/nyt/years'

# search nyt for modal auxiliaries:
>>> interroplot(corpus, r'MD')
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/md.png" />
<br>

## Examples

Here's another basic example of `interrogator()` and `plotter()` at work on the NYT corpus:

```python
>>> from corpkit import interrogator, plotter
# make tregex query: head of NP in PP containing 'of'
# in NP headed by risk word:
>>> q = r'/NN.?/ >># (NP > (PP <<# /(?i)of/ > (NP <<# (/NN.?/ < /(?i).?\brisk.?/))))'

# count terminals/leaves of trees only, and do lemmatisation:
>>> riskofnoun = interrogator(corpus, 'words', q, lemmatise = True)

# plot top 7 entries as percentage of all entries:
>>> plotter('Risk of (noun)', riskofnoun.results, 
...    fract_of = riskofnoun.totals, num_to_plot = 7, 
...    skip63 = False)
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/riskofnoun.png" />
<br>

### Systemic functional stuff

Because I mostly use systemic functional grammar, there is also a simple(ish) tool for building Regular Expressions to distinguish between process types (relational, mental, verbal) when interrogating a corpus. If you add words to `dictionaries/process_types.py`, they will be added to the regex.

```python
>>> from corpkit import quickview, surgeon
>>> from dictionaries.process_types import processes

# find the dependent of verbal processes, and its functional role
# keep only results matching function_filter
>>> sayers = interrogator(corpus, 'deprole', processes.verbal, 
...    function_filter = r'^nsubj$')

# have a look at the top results
>>> quickview(sayers.results, n = 20)
```

Output:

```python
['   0: he',
 '   1: she',
 '   2: they',
 '   3: official',
 '   4: it',
 '   5: who',
 '   6: that',
 '   7: expert',
 '   8: i',
 '   9: analyst',
 '  10: we',
 '  11: report',
 '  12: company',
 '  13: researcher',
 '  14: you',
 '  15: which',
 '  16: critic',
 '  17: study',
 '  18: executive',
 '  19: doctor']
```

Let's remove the pronouns using `surgeon()`, and plot something:

```python
# give surgeon indices to keep or remove
>>> specific_sayers = surgeon(sayers.results, [0, 1, 2, 4, 5, 6, 8, 10, 14, 15, 27], 
...    remove = True)

# plot with a bunch of options
>>> plotter('People who say stuff', specific_sayers.results, 
...    num_to_plot = 9, sort_by = 'total', skip63 = True)
```

Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/people-who-say-stuff.png" />
<br>

### More complex stuff

Let's find out what kinds of noun lemmas are subjects of risk processes (e.g. *risk*, *take risk*, *run risk*, *pose risk*).

```python
# a query to find heads of nps that are subjects of risk processes
>>> query = r'/^NN(S|)$/ !< /(?i).?\brisk.?/ >># (@NP $ (VP <+(VP) (VP ( <<# (/VB.?/ < /(?i).?\brisk.?/) | <<# (/VB.?/ < /(?i)(take|taking|takes|taken|took|run|running|runs|ran|put|putting|puts|pose|poses|posed|posing)/) < (NP <<# (/NN.?/ < /(?i).?\brisk.?/))))))'
>>> noun_riskers = interrogator(c, 'words', query, lemmatise = True)

>>> quickview(riskers.results, n = 10)
```

Output:

```python
['   0: person',
 '   1: company',
 '   2: bank',
 '   3: investor',
 '   4: government',
 '   5: man',
 '   6: leader',
 '   7: woman',
 '   8: official',
 '   9: player',
 '  10: manager']
```

We can use `merger()` to make some thematic categories:

```python
>>> them_cat = merger(noun_riskers.results, ['person', 'man', 'woman', 
...    'child', 'consumer', 'baby', 'student', 'patient'], 
...    newname = 'Everyday people')
>>> them_cat = merger(them_cat.results, ['company', 'bank', 'investor', 
...    'government', 'leader', 'president', 'officer', 'politician', 
...    'institution', 'agency', 'candidate', 'firm'], 
...    newname = 'Institutions')

# plot riskers:
>>> plotter('Types of riskers', them_cat.results, 
...    fract_of = noun_riskers.totals, num_to_plot = 2)
```

Output:

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/types-of-riskers.png" />
<br>

Let's also find out what percentage of the time some nouns appear as riskers:

```python
# find any head of an np not containing risk
>>> query = r'/NN.?/ >># NP !< /(?i).?\brisk.?/'
>>> noun_lemmata = interrogator(corpus, 'words', query, lemmatise = True)

# get some key terms
>>> interesting_riskers = surgeon(noun_riskers.results, 
...    ['politician', 'candidate', 'lawmaker', 'governor', 'man', 
...    'woman', 'child', 'person'], remove = False)

>>> plotter('Risk and power', interesting_riskers.results, 
...    fract_of = noun_lemmata.results, sort_by = 'most', 
...    just_totals = True, y_label = 'Risker percentage',
...    num_to_plot = 8)
```

Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power.png" />
<br>

## More information

Some things are likely lacking documentation right now. For now, the more complex functionality of the toolkit is presented best in some of the research projects I'm working on:

1. [Longitudinal linguistic change in an online support group](https://github.com/interrogator/sfl_corpling) (thesis project)
2. [Discourse-semantics of *risk* in the NYT, 1963&ndash;2014](https://github.com/interrogator/risk)
3. [Learning Python, IPython and NLTK by investigating a corpus of Malcolm Fraser's speeches](https://github.com/resbaz/nltk)

## IPython Notebook usability

When running the Notebook locally, a couple of IPython extensions come in very handy:

* First, you can use [this](https://github.com/minrk/ipython_extensions) to generate a floating table of contents that makes the Notebook much easier to navigate.
* Second, given that some of the code can take a while to process, it can be handy to have [browser-based notifications](https://github.com/sjpfenninger/ipython-extensions) when the kernel is no longer busy.

## Coming soon

* Connecting concordance output to HTML
* More corpus building resources and documentation
* More complex examples in this file
* More `.tex`!


