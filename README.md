## *corpkit*: a Python-based toolkit for working with parsed linguistic corpora

[![Join the chat at https://gitter.im/interrogator/corpkit](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/interrogator/corpkit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

### D. McDonald

> Because I kept building new tools and functions for my linguistic research, I decided to put them together into `corpkit`, a simple toolkit for working with parsed and structured linguistic corpora.

> **Note**: I'm currently making everything Pandas compliant, so that we may all bask in the glory of the DataFrame. Documentation of major changes forthcoming.

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
  - [Concordancing](#concordancing)
  - [Systemic functional stuff](#systemic-functional-stuff)
  - [More complex queries and plots](#more-complex-queries-and-plots)
  - [Visualisation options](#visualisation-options)
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
| `conc()`          | complex concordancing of subcorpora | 
| `editor()`       | edit `interrogator()` or `conc()` results      | 
| `keywords()`      | get keywords and ngrams from corpus/subcorpus/concordance lines | 
| `collocates()`    | get collocates from corpus/subcorpus/concordance lines | 

While most of the tools are designed to work with corpora that are parsed (by e.g. [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml)) and structured (in a series of directories representing different points in time, speaker IDs, chapters of a book, etc.), the tools can also be used on text that is unparsed and/or unstructured. That said, you won't be able to do nearly as much cool stuff.

The idea is to run the tools from an [IPython Notebook](http://ipython.org/notebook.html), but you could also operate the toolkit from the command line if you wanted to have less fun.

The most comprehensive use of `corpkit` to date has been for an investigation of the word *risk* in The New York Times, 1963&ndash;2014. The repository for that project is [here](https://www.github.com/interrogator/risk); the Notebook demonstrating the use of `corpkit` can be best viewed via [NBviewer](http://nbviewer.ipython.org/github/interrogator/risk/blob/master/risk.ipynb).

### Key features

#### `interrogator()`

* Use [Tregex](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html) or regular expressions to search parse trees or plain text for complex lexicogrammatical phenomena
* Search Stanford dependencies (whichever variety you like) for information about the role, governor, dependent or index of a token matching a regular expression
* Return words or phrases, POS/group/phrase tags, raw counts, or all three.
* Return lemmatised or unlemmatised results (using WordNet for constituency trees, and CoreNLP's lemmatisation for dependencies). Add words to `dictionaries/word_transforms.py` manually if need be
* Look for keywords in each subcorpus (using code from [*Spindle*](https://github.com/sgrau/spindle-code), and chart their keyness
* Look for ngrams in each subcorpus, and chart their frequency
* Two-way UK-US spelling conversion (superior as the former may be), and the ability to add words manually
* Output Pandas DataFrames that can be easily edited and visualised

#### `editor()`

* Remove, keep or merge interrogation results or subcorpora using indices, words or regular expressions (see below)
* Sort results by name or total frequency
* Use linear regression to figure out the trajectories of results, and sort by the most increasing, decreasing or static values
* Show the *p*-value for linear regression slopes, or exclude results above *p*
* Work with absolute frequency, or determine ratios/percentage of another list: 
    * determine the total number of verbs, or total number of verbs that are *be*
    * determine the percentage of verbs that are *be*
    * determine the percentage of *be* verbs that are *was*
    * determine the ratio of *was/were* ...
    * etc.
* Plot more advanced kinds of relative frequency: for example, find all proper nouns that are subjects of clauses, and plot each word as a percentage of all instances of that word in the corpus (see below)

#### `plotter()` 

* Plot using *Pandas*/*Matplotlib*
* Plot anything you like: words, tags, counts for grammatical features ...
* Create line charts, bar charts, pie charts, etc. with the `kind` argument
* Use `subplots = True` to produce individual charts for each result
* Customisable figure titles, axes labels, legends, image size, colormaps, etc.
* Use `TeX` if you have it
* Use log scales if you really want
* Use a number of chart styles, such as `ggplot` or `fivethirtyeight`
* Save images to file

#### Other stuff

* View top results as a table via `Pandas`
* Tools for quickly and easily generating lists of keywords, ngrams, collocates and concordances
* Concordance using Tregex (i.e. concordance all nominal groups containing *gross* as an adjective with `NP < (JJ < /gross/)`)
* Randomise concordance results, determine window size, output to CSV, etc.
* Quickly save interrogations and figures to file, and reload results in new sessions with `save_result()` and `load_result()`
* Build dictionaries from corpora, subcorpora or concordance lines, which can then be used as reference corpora for keyword generation
* Start a new blank project with `new_project()`

One of the main reasons for these tools was to make it quicker and easier to explore corpora in complex ways, using output from one tool as input for the next.

* n-gramming and keywording can be done via `interrogator()`
* keywording can easily be done on your concordance lines
* Use loops to concordance the top results from an interrogation, or check their keyness
* use `editor()` to edit concordance line output as well as interrogations
* build a dictionary from a corpus, subcorpus, or from concordance lines, and use it as a reference corpus for keywording
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

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/md2.png" />
<br>

## Examples

`interroplot()` is just a demo function that does three things in order:

1. uses `interrogator()` to search `corpus` for a (Regex or Tregex) `query`
2. uses `editor()` to calculate the relative frequencies of each result
3. uses `plotter()` to show the top seven results
 
Here's an example of the three functions at work on the NYT corpus:

```python
>>> from corpkit import interrogator, editor, plotter
# make tregex query: head of NP in PP containing 'of'
# in NP headed by risk word:
>>> q = r'/NN.?/ >># (NP > (PP <<# /(?i)of/ > (NP <<# (/NN.?/ < /(?i).?\brisk.?/))))'

# count terminals/leaves of trees only, and do lemmatisation:
>>> risk_of = interrogator(corpus, 'words', q, lemmatise = True)

# use editor to turn absolute into relative frequencies
>>> to_plot = editor(risk_of.results, '%', risk_of.totals)

# plot the results
>>> plotter('Risk of (noun)', to_plot.results, y_label = 'Percentage of all results')
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-of-noun.png" />
<br>

### Concordancing

You can use Tregex queries to concordance things, too:

```python
>>> from corpkit import conc

>>> subcorpus = 'data/nyt/years/2005'
>>> query = r'/JJ.?/ > (NP <<# (/NN.?/ < /\brisk/))'
>>> lines = conc(subcorpus, query, window = 50, 
...    n = 10, random = True)
```

Output (a *Pandas DataFrame*):

```
0    hedge funds or high-risk stocks obviously poses a         greater   risk to the pension program than a portfolio of   
1           contaminated water pose serious health and   environmental   risks                                             
2   a cash break-even pace '' was intended to minimize       financial   risk to the parent company                        
3                                                Other           major   risks identified within days of the attack        
4                           One seeks out stocks ; the           other   monitors risks                                    
5        men and women in Colorado Springs who were at            high   risk for H.I.V. infection , because of            
6   by the marketing consultant Seth Godin , to taking      calculated   risks , in the opinion of two longtime business   
7        to happen '' in premises '' where there was a            high   risk of fire                                      
8       As this was match points , some of them took a          slight   risk at the second trick by finessing the heart   
9     said that the agency 's continuing review of how         Guidant   treated patient risks posed by devices like the 
```

You can use this output as a dictionary, or extract keywords and ngrams from it, or keep or remove certain results with `editor()`.

### Systemic functional stuff

Because I mostly use systemic functional grammar, there is also a simple(ish) tool for building Regular Expressions to distinguish between process types (relational, mental, verbal) when interrogating a corpus. If you add words to `dictionaries/process_types.py`, they will be added to the regex.

```python
>>> from corpkit import quickview
>>> from dictionaries.process_types import processes

# use verbal process regex as the query
# deprole finds the dependent of verbal processes, and its functional role
# keep only results matching function_filter regex
>>> sayers = interrogator(corpus, 'deprole', processes.verbal, 
...    function_filter = r'^nsubj$', lemmatise = True)

# have a look at the top results
>>> quickview(sayers.results, n = 20)
```

Output:

```python
['   0: he (23507)',
 '   1: she (5383)',
 '   2: they (4952)',
 '   3: official (4160)',
 '   4: it (2732)',
 '   5: who (2572)',
 '   6: that (2265)',
 '   7: expert (2011)',
 '   8: i (1926)',
 '   9: analyst (1342)',
 '  10: we (1027)',
 '  11: report (1012)',
 '  12: company (945)',
 '  13: researcher (930)',
 '  14: you (889)',
 '  15: which (870)',
 '  16: critic (796)',
 '  17: study (743)',
 '  18: executive (731)',
 '  19: doctor (726)']
```

Let's plot *he* and *she*:

```python
>>> plotter('Gender of sayers in the NYT', sayers.results, num_to_plot = 2)
```

Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/gender-of-sayers-in-the-nyt.png" />
<br>

Woohoo, a decreasing gender divide! Next, let's remove the pronouns using `editor()`, and plot something:

```python
>>> from corpkit import editor

# give editor() indices to keep or remove
>>> specific_sayers = editor(sayers.results, skip_entries = [0, 1, 2, 4, 5, 6, 
...    8, 10, 14, 15, 27], skip_subcorpora = [1963], sort_by = 'total')

# plot
>>> plotter('People who say stuff', specific_sayers.results, num_to_plot = 9)
```

Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/people-who-say-stuff.png" />
<br>

### More complex queries and plots

Let's find out what kinds of noun lemmas are subjects of risk processes (e.g. *risk*, *take risk*, *run risk*, *pose risk*).

```python
# a query to find heads of nps that are subjects of risk processes
>>> query = r'/^NN(S|)$/ !< /(?i).?\brisk.?/ >># (@NP $ (VP <+(VP) (VP ( <<# (/VB.?/ < ' /(?i).?\brisk.?/) ' \
...         r'| <<# (/VB.?/ < /(?i)\b(take|taking|takes|taken|took|run|running|runs|ran|put|putting|puts)/) < ' \
...         r'(NP <<# (/NN.?/ < /(?i).?\brisk.?/))))))'
>>> noun_riskers = interrogator(c, 'words', query, lemmatise = True)
 
>>> quickview(noun_riskers.results, n = 10)
```

Output:

```python
['   0: person (195)',
 '   1: company (139)',
 '   2: bank (80)',
 '   3: investor (66)',
 '   4: government (63)',
 '   5: man (51)',
 '   6: leader (48)',
 '   7: woman (43)',
 '   8: official (40)',
 '   9: player (39)']
```

We can use `editor()` to make some thematic categories:

```python
# get everyday people
>>> p = ['person', 'man', 'woman', 'child', 'consumer', 'baby', 'student', 'patient']
>>> them_cat = editor(noun_riskers.results, merge_entries = p, newname = 'Everyday people')

# get business, gov, institutions
>>> i = ['company', 'bank', 'investor', 'government', 'leader', 'president', 'officer', 
...      'politician', 'institution', 'agency', 'candidate', 'firm']
>>> them_cat = editor(them_cat.results, '%', noun_riskers.totals, merge_entries = i, 
...    newname = 'Institutions', sort_by = 'total', skip_subcorpora = 1963,
...    just_entries = ['Everyday people', 'Institutions'])

# plot result
>>> plotter('Types of riskers', them_cat.results, y_label = 'Percentage of all riskers')
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
>>> people = ['man', 'woman', 'child', 'baby', 'politician', 
...           'senator', 'obama', 'clinton', 'bush']
>>> selected = editor(noun_riskers.results, '%', noun_lemmata.results, 
...    just_entries = people, just_totals = True, threshold = 0, sort_by = 'total')

# make a bar chart:
>>> plotter('Risk and power', selected.results, num_to_plot = 'all', kind = k, 
...    x_label = 'Word', rot = 45, y_label = 'Risker percentage', fontsize = 15)
```

Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" />
<br>

### Visualisation options

With a bit of creativity, you can do some pretty awesome data-viz, thanks to *Pandas* and *Matplotlib*. The following plots require only one interrogation:

```python
>>> modals = interrogator(annual_trees, 'words', 'MD < __')
# simple stuff: make relative frequencies for individual or total results
>>> rel_modals = editor(modals.results, '%', modals.totals)

# trickier: make an 'others' result from low-total entries
>>> low_indices = [i for i, w in enumerate(list(modals.results.index)) if i > 6]
>>> each_modal_total = editor(modals.results, '%', modals.totals, merge_entries = low_indices, 
                          newname = 'other', sort_by = 'total', just_totals = True, keep_top = 7)

# complex stuff: merge results
>>> entries_to_merge = [r'(^w|\'ll|\'d)', r'^c', r'^m']
>>> for regex in entries_to_merge:
    >>> modals = editor(modals.results, merge_entries = regex)
    
# complex stuff: merge subcorpora
>>> subcorpora_to_merge = [('1960s', r'^196'), ('1980s', r'^198'), ('1990s', r'^199'), 
                       ('2000s', r'^200'), ('2010s', r'^201')]
for subcorp, search in subcorpora_to_merge:
    modals = editor(modals.results, merge_subcorpora = search, new_subcorpus_name=subcorp)
    
# make relative, sort, remove what we don't want
>>> modals = editor(modals.results, '%', modals.totals,
                 just_subcorpora = [n for n, s in subcorpora_to_merge], sort_by = 'total', keep_top = 3)

# show results
print rel_modals.results, each_modal_total.results, '\n\n', modals.results
```
Output:
```
          would       will        can      could  ...        need     shall      dare  shalt
1963  22.326833  23.537323  17.955615   6.590451  ...    0.000000  0.537996  0.000000      0
1987  24.750614  18.505132  15.512505  11.117537  ...    0.072286  0.260228  0.014457      0
1988  23.138986  19.257117  16.182067  11.219364  ...    0.091338  0.060892  0.000000      0
1989  22.766053  19.368358  15.371950  11.749738  ...    0.134710  0.014968  0.014968      0
1990  24.631154  18.061811  15.716726  12.253456  ...    0.062121  0.046591  0.000000      0
...         ...        ...        ...        ...  ...         ...       ...       ...    ...
2010  24.989858  17.200811  15.388776  14.171738  ...    0.108181  0.067613  0.000000      0
2011  23.185818  17.574289  15.584747  14.577222  ...    0.089274  0.000000  0.000000      0
2012  23.097345  16.283186  15.132743  15.353982  ...    0.029499  0.029499  0.000000      0
2013  22.136269  17.286522  16.349301  15.620351  ...    0.029753  0.029753  0.000000      0
2014  21.618357  17.101449  16.908213  14.347826  ...    0.024155  0.000000  0.000000      0

[29 rows x 17 columns] would     23.235853
will      17.484034
can       15.844070
could     13.243449
may        9.581255
should     7.292294
other      7.290155
Name: Combined total, dtype: float64 

       would/will/'ll...  can/could/ca  may/might/must  should/shall/shalt
1960s          47.276395     25.016812       19.569603            7.800941
1980s          44.756285     28.050776       19.224476            7.566817
1990s          44.481957     29.142571       19.140310            6.892708
2000s          42.386571     30.710739       19.182867            7.485681
2010s          42.581666     32.045745       17.777845            7.397044

```

Now, some intense plotting:

```python
# exploded pie chart
>>> expl = [0 for s in list(each_modal_total.results)]
>>> expl[-1] = 0.1
>>> plotter('Pie chart of common modals in the NYT', each_modal_total.results, explode = expl,
...    num_to_plot = 'all', kind = 'pie', colours = 'Accent', figsize = (11, 11))

# stacked area chart
>>> plotter('An ocean of modals', rel_modals.results.drop('1963'), kind = 'area', 
...    stacked = True, colours = 'summer', figsize = (8, 10), num_to_plot = 'all', 
...    legend_pos = 'outside lower right', y_label = 'Percentage of all modals')

# bar chart, transposing and reversing the data
>>> plotter('Modals use by decade', modals.results.iloc[::-1].T.iloc[::-1], kind = 'barh',
...    x_label = 'Percentage of all modals', y_label = 'Modal group')
```
Output:
<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png"  height="400" width="400"/>
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/modals-use-by-decade.png"  height="230" width="550"/>
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/an-ocean-of-modals.png"  height="450" width="550"/>
</p>

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
* Concordance lines using dependencies
* More corpus building resources and documentation
* More `.tex`!
