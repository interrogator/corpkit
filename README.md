## *corpkit*: a Python-based toolkit for working with parsed linguistic corpora

[![Join the chat at https://gitter.im/interrogator/corpkit](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/interrogator/corpkit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

### D. McDonald

> Because I kept building new tools and functions for my corpus linguistic work, I decided to put them together into `corpkit`, a simple toolkit for working with parsed and structured linguistic corpora.

### What's in here?

Essentially, the module contains a bunch of functions for interrogating corpora, then manipulating or visualising the results. Thee most important of them are:

| **Function name** | Purpose                            | 
| ----------------- | ---------------------------------- | 
| `interrogator()`  | interrogate parsed corpora         | 
| `dependencies()`  | interrogate parsed corpora for dependency info        | 
| `plotter()`       | visualise `interrogator()` results with *matplotlib* | 
| `surgeon()`       | edit `interrogator()` results      | 
| `merger()`        | merge `interrogator()` results      | 
| `conc()`          | complex concordancing of subcorpora | 
| `keywords()`      | get keywords and ngrams from corpus/subcorpus/concordance lines | 
| `collocates()`    | get collocates from corpus/subcorpus/concordance lines | 

Because I mostly use systemic functional grammar, there also some simple dictionaries to distinguish between process types (relational, mental, verbal). These don't have much documentation right now, but they can be seen in action in my research projects:

1. [Longitudinal linguistic change in an online support group](https://github.com/interrogator/sfl_corpling) (thesis project)
2. [Discourse-semantics of *risk* in the NYT, 1963&ndash;2014](https://github.com/interrogator/risk)
3. [Learning Python, IPython and NLTK by investigating a corpus of Malcolm Fraser's speeches](https://github.com/resbaz/nltk)

Though everything should work alright in Python, it's much easier to use [IPython Notebooks](http://ipython.org/notebook.html). 

Included here is a sample project, `orientation`, which you can run in order to familiarise yourself with the `corpkit` module. It uses a corpus of paragraphs of the NYT containing the word *risk*. This project isn't included in the pip package.

### Installation

You can get `corpkit` running by downloading or cloning this repository, or via `pip`.

#### By downloading the repository

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

#### Via `pip`:

```shell
# might need sudo:
pip install corpkit
```

To interrogate corpora and plot results, you need *Java*, *NLTK* and *matplotlib*. Other tools require *Beautiful Soup*, *Pandas*, etc. 

The `pip` installation of NLTK does not come with the data needed for NLTK's tokeniser, so we'll also need to install that:

```python
import nltk
# change 'punkt' to 'all' to get everything
nltk.download('punkt')
```

### Unpacking the orientation data

If you installed by downloading or cloning this repository, you'll have the orientation project installed. To use it, `cd` into the orientation project and unzip the data files:

```shell
cd orientation
# unzip data to data folder
gzip -dc data/nyt.tar.gz | tar -xf - -C data
```

### Quickstart

This is the best way to use `corpkit` by opening `orientation.ipynb` with IPython, and executing the first few cells:

```shell
ipython notebook orientation.ipynb
```

Or, just use Python (much more difficult, less fun):

```python
import corpkit
from corpkit import interroplot

# set corpus path
corpus = 'data/nyt/years'

# search nyt for modal auxiliaries:
interroplot(corpus, r'MD')
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/md.png" />
<br>

### Example

Here's another basic example of `interrogator()` and `plotter()` at work on the NYT corpus:

```python
# make tregex query: head of NP in PP containing 'of'
# in NP headed by risk word:
q = r'/NN.?/ >># (NP > (PP <<# /(?i)of/ > (NP <<# (/NN.?/ < /(?i).?\brisk.?/))))'

# count terminals/leaves of trees only, and do lemmatisation:
riskofnoun = interrogator(corpus, '-t', q, lemmatise = True)

# plot top 7 entries as percentage of all entries:
plotter('Risk of (noun)', riskofnoun.results, 
        fract_of = riskofnoun.totals, num_to_plot = 7, 
        skip63 = False)
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/riskofnoun.png" />
<br>

### IPython Notebook usability

When running the Notebook locally, a couple of IPython extensions come in very handy:

* First, you can use [this](https://github.com/minrk/ipython_extensions) to generate a floating table of contents that makes the Notebook much easier to navigate.
* Second, given that some of the code can take a while to process, it can be handy to have [browser-based notifications](https://github.com/sjpfenninger/ipython-extensions) when the kernel is no longer busy.

### Coming soon:

* Connecting concordance output to HTML
* Corpus building resources
* More `.tex`!


