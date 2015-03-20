## *corpkit*: a Python-based toolkit for working with parsed linguistic corpora

### D. McDonald

> Because I kept building new tools and functions for my corpus linguistic work, I decided to put them together into `corpkit`, a simple toolkit for working with parsed and structured linguistic corpora. Though everything should work alright in Python, it's much easier to use IPython Notebooks. Included here is a notebook that you can run in order to familiarise yourself with the `corpkit` module.

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
| `keywords()`          | get keywords and ngrams from `conc()` output | 
| `collocates()`          | get collocates from `conc()` output| 

Because I mostly use systemic functional grammar, there also some simple dictionaries to distinguish between process types (relational, mental, verbal). These don't have much documentation right now, but they can be seen in action in my research projects.

### Installation


Clone the repo, ``cd`` into it and run the setup:

```shell
git clone https://github.com/interrogator/corpkit.git
cd corpkit
# might need sudo:
python setup.py install
```

or, via pip:

```shell
pip install corpkit
```

To use all the tools, you'll need *Java*, *NLTK*, *matplotlib* and *NumPy*.

### Quickstart

CD into the NYT project and enter Python:

```shell
cd projects/risk
python
```

Then:

```python
import corpkit
from corpkit import interroplot
interroplot('data/trees/years', r'MD < __')
```

or, with IPython, just open `orientation.ipynb` with:

```shell
ipython notebook orientation.ipynb
```

and execute the first few cells.

### Orientation

The best way to use the toolkit is through IPython Notebooks. Open up

      ipython notebook orientation.ipynb

### Coming soon:

* Connecting concordance output to HTML
* Corpus building resources
* More `.tex`!


