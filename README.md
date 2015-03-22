## *corpkit*: a Python-based toolkit for working with parsed linguistic corpora

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
| `merger()`       | merge `interrogator()` results      | 
| `conc()`          | complex concordancing of subcorpora | 
| `keywords()`          | get keywords and ngrams from corpus, subcorpus and concordance lines | 
| `collocates()`          | get collocates from corpus, subcorpus and concordance lines | 

Because I mostly use systemic functional grammar, there also some simple dictionaries to distinguish between process types (relational, mental, verbal). These don't have much documentation right now, but they can be seen in action in my research projects:

1. [Thesis project: longitudinal linguistic change in an online support group](https://github.com/interrogator/sfl_corpling)
2. [Discourse-semantics of risk in the NYT, 1963--2014](https://github.com/interrogator/risk)
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

#### Via `pip` (though this won't contain the orientation project):

```shell
# might need sudo:
pip install corpkit
```

To interrogate corpora and plot results, you need *Java*, *NLTK* and *matplotlib*. Other tools require *Beautiful Soup*, *Pandas*, etc. 

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
# IPython
ipython notebook orientation.ipynb
```

Or, just use Python (much more difficult, less fun):

```python
python
import corpkit
from corpkit import interroplot
# search nyt for modal auxiliaries:
interroplot('data/nyt/years', r'MD < __')
```

### Coming soon:

* Connecting concordance output to HTML
* Corpus building resources
* More `.tex`!


