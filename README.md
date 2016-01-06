## *corpkit*: a Python-based toolkit for working with linguistic corpora

[![Join the chat at https://gitter.im/interrogator/corpkit](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/interrogator/corpkit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![DOI](https://zenodo.org/badge/14568/interrogator/corpkit.svg)](https://zenodo.org/badge/latestdoi/14568/interrogator/corpkit) [![PyPI](https://img.shields.io/pypi/v/corpkit.svg)](https://pypi.python.org/pypi/corpkit)

### Daniel McDonald ([@interro_gator](https://twitter.com/interro_gator))

> Because I kept building new tools for my linguistic research, I decided to put them together into *corpkit*, a simple toolkit for working with parsed and structured linguistic corpora.
> 
> **Over the last few months I've developed a GUI version of the tool. This resides as pure Python in `corpkit/corpkit-gui.py`. There is also a zipped up version of an OSX executable in the [`corpkit-app` submodule](https://www.github.com/interrogator/corpkit-app). Documentation for the GUI is [here](http://interrogator.github.io/corpkit/). From here on out, though, this readme concerns the command line interface only.**

<!-- MarkdownTOC -->

- [What's in here?](#whats-in-here)
  - [Key features](#key-features)
    - [`make_corpus()`](#make_corpus)
    - [`interrogator()`](#interrogator)
    - [`interrogation.edit()` / `editor()](#interrogationedit--editor)
    - [`interrogation.plot()` / plotter()](#interrogationplot--plotter)
    - [Other stuff](#other-stuff)
- [Installation](#installation)
  - [By downloading the repository](#by-downloading-the-repository)
  - [By cloning the repository](#by-cloning-the-repository)
  - [Via `pip`](#via-pip)
- [Unpacking the orientation data](#unpacking-the-orientation-data)
- [Quickstart](#quickstart)
- [More detailed examples](#more-detailed-examples)
  - [Building corpora](#building-corpora)
    - [Speaker IDs](#speaker-ids)
  - [Concordancing](#concordancing)
  - [Systemic functional stuff](#systemic-functional-stuff)
  - [Keywording](#keywording)
    - [Plotting keywords](#plotting-keywords)
    - [Traditional reference corpora](#traditional-reference-corpora)
  - [Parallel processing](#parallel-processing)
  - [More complex queries and plots](#more-complex-queries-and-plots)
  - [Visualisation options](#visualisation-options)
- [More information](#more-information)
- [Cite](#cite)

<!-- /MarkdownTOC -->

<a name="whats-in-here"></a>
## What's in here?

Essentially, the module contains classes and functions for building and interrogating corpora, then manipulating or visualising the results. The three main functions are:

| **Function name** | Purpose                            | 
| ----------------- | ---------------------------------- | 
| `make_corpus()`   | Use CoreNLP/NLTK to make to make parsed, speaker-segmented corpora from plain text files      |
| `interrogator()`  | Interrogate parse trees, dependencies, or find keywords or ngrams in parsed corpora |
| `conc()`          | Lexicogrammatical concordancing via constituency/dependency annotations | 

Interrogations create `Interrogation` objects. These have attributes:

| ** Attribute** | Contains |
| ---------------|----------|
| `interrogation.results` |  Pandas DataFrame of counts in each subcorpus |
| `interrogation.totals` | Pandas Series of totals for each subcorpus/result |
| interrogation.query` | a `dict` of values used to generate the interrogation |

and methods:

| **Method** | Purpose |
|------------|---------|
| `interrogation.edit()`        | Get relative frequencies, merge/remove results/subcorpora, calculate keywords, sort using linear regression, etc. |
| `interrogation.plot()`       | visualise results via *matplotlib* | 

These methods can also be used as functions (explained below), in order to do more advanced work with Pandas objects.


There are also quite a few helper functions for making regular expressions, saving and loading data, making new projects, and so on.

Also included are some lists of words and dependency roles, which can be used to match functional linguistic categories. These are explained in more detail [here](#systemic-functional-stuff).

While most of the tools are designed to work with corpora that are parsed (by [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml)) and structured (in a series of directories representing different points in time, speaker IDs, chapters of a book, etc.), the tools can also be used on text that is unparsed and/or unstructured. That said, you won't be able to do nearly as much cool stuff.

I think it's a great idea to use *corpkit* from within a [Jupyter Notebook](http://jupyter.org), but you could also operate the toolkit from the command line if you wanted to have less fun.

The most comprehensive use of *corpkit* to date has been for an investigation of the word *risk* in *The New York Times*, 1963&ndash;2014. The repository for that project is [here](https://www.github.com/interrogator/risk); the Notebook demonstrating the use of *corpkit* can be viewed via either [GitHub](https://github.com/interrogator/risk/blob/master/risk.ipynb) or [NBviewer](http://nbviewer.ipython.org/github/interrogator/risk/blob/master/risk.ipynb).

<a name="key-features"></a>
### Key features

<a name="make_corpus"></a>
#### `make_corpus()` 

* A simple Python wrapper around CoreNLP
* Creates a parsed version of a structured or unstructured plaintext corpus
* Optionally detects speaker IDs and adds them to CoreNLP XML

<a name="interrogator"></a>
#### `interrogator()`

* Use [Tregex](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html) or regular expressions to search parse trees, dependencies or plain text for complex lexicogrammatical phenomena
* Search Stanford dependencies (whichever variety you like) for information about the role, governor, dependent, index (etc) of a token matching a regular expression
* Return words or phrases, POS/group/phrase tags, raw counts, or all three.
* Return lemmatised or unlemmatised results (using WordNet for constituency trees, and CoreNLP's lemmatisation for dependencies). Add words to `dictionaries/word_transforms.py` manually if need be
* Look for ngrams in each subcorpus, and chart their frequency
* Two-way UK-US spelling conversion, and the ability to add words manually
* Output Pandas DataFrames that can be easily edited and visualised
* Use parallel processing to search for a number of patterns, or search for the same pattern in multiple corpora

<a name="interrogationedit--editor"></a>
#### `interrogation.edit()` / `editor()

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

<a name="interrogationplot--plotter"></a>
#### `interrogation.plot()` / plotter() 

* Plot using *Matplotlib*
* Interactive plots (hover-over text, interactive legends) using *mpld3* (examples in the [*Risk Semantics* notebook](https://github.com/interrogator/risk/blob/master/risk.ipynb))
* Plot anything you like: words, tags, counts for grammatical features ...
* Create line charts, bar charts, pie charts, etc. with the `kind` argument
* Use `subplots = True` to produce individual charts for each result
* Customisable figure titles, axes labels, legends, image size, colormaps, etc.
* Use `TeX` if you have it
* Use log scales if you really want
* Use a number of chart styles, such as `ggplot`, `fivethirtyeight` or 'seaborn-talk' (if you've got `seaborn` installed)
* Save images to file, as `.pdf` or `.png`

<a name="other-stuff"></a>
#### Other stuff

* Concordance using Tregex (i.e. concordance all nominal groups containing *gross* as an adjective with `NP < (JJ < /gross/)`)
* Randomise concordance results, determine window size, output to CSV, etc.
* Quickly save interrogations and figures to file, and reload results in new sessions with `save()` and `load()`
* Build dictionaries from corpora, subcorpora or concordance lines, which can then be used as reference corpora for keyword generation
* Start a new blank project with `new_project()`

Included here is `orientation/orientation.ipynb`, which is a Jupyter Notebook version of this readme. In `orientation/data` is a sample corpus of paragraph from *The New York Times* containing the word *risk*. Due to size restrictions, This data only includes parse trees (no dependencies), and isn't included in the pip package. With the notebook and the data, you can easily run all the code in this document yourself.

<a name="installation"></a>
## Installation

You can get *corpkit* running by downloading or cloning this repository, or via `pip`.

<a name="by-downloading-the-repository"></a>
### By downloading the repository

Hit 'Download ZIP' and unzip the file. Then `cd` into the newly created directory and install:

```shell
cd corpkit-master
# might need sudo:
python setup.py install
```

<a name="by-cloning-the-repository"></a>
### By cloning the repository

Clone the repo, `cd` into it and run the setup:

```shell
git clone https://github.com/interrogator/corpkit.git
cd corpkit
# might need sudo:
python setup.py install
```

<a name="via-pip"></a>
### Via `pip`

```shell
# might need sudo:
pip install corpkit
# or, for a local install:
# pip install --user corpkit
```

*corpkit* should install all the necessary dependencies, including *pandas*, *NLTK*, *matplotlib*, etc, as well as some NLTK data files. 

If you get an NLTK error, you might need to manually download the tokeniser and lemmatiser data:

```python
>>> import nltk
# change 'punkt' to 'all' to get everything
>>> nltk.download('punkt')
>>> nltk.download('wordnet')
```

<a name="unpacking-the-orientation-data"></a>
## Unpacking the orientation data

If you installed by downloading or cloning this repository, you'll have the orientation project installed. To use it, `cd` into the orientation project and unzip the data files:

```shell
cd orientation
# unzip data to data folder
gzip -dc data/nyt.tar.gz | tar -xf - -C data
```

<a name="quickstart"></a>
## Quickstart

The best way to use *corpkit* is by opening `orientation/orientation.ipynb` with Jupyter, and executing the relevant cells:

```shell
ipython notebook orientation.ipynb
```

Or, just use *(I)Python*:

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
<br><br>

<a name="more-detailed-examples"></a>
## More detailed examples

`interroplot()` is just a demo function that does three things in order:

1. uses `interrogator()` to search corpus for a (Regex or Tregex) query
2. uses `edit()` to calculate the relative frequencies of each result
3. uses `plot()` to show the top seven results
 
Here's an example of the three functions at work on the NYT corpus:

```python
>>> from corpkit import interrogator, editor, plotter
# make tregex query: head of NP in PP containing 'of'
# in NP headed by risk word:
>>> q = r'/NN.?/ >># (NP > (PP <<# /(?i)of/ > (NP <<# (/NN.?/ < /(?i).?\brisk.?/))))'

# search trees, output lemma
>>> risk_of = interrogator(corpus, 'trees', q, show = ['l'])

# use edit() to turn absolute into relative frequencies
>>> to_plot = risk_of.edit('%', risk_of.totals)

# plot the results
>>> to_plot.plot('Risk of (noun)', y_label = 'Percentage of all results',
...    style = 'fivethirtyeight')
```

Output: 

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-of-noun.png" />
<br><br>

<a name="building-corpora"></a>
### Building corpora

*corpkit* contains a modest function for created parsed and/or tokenised corpora. The main thing you need is **a folder, containing either text files, or subfolders that contain text files**. If you want to parse the corpus, you'll also need to have downloaded and unzipped [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml). If you're tokenising, you'll need to make sure you have NLTK's tokeniser data. You can then run:

```python
>>> parsed = make_corpus(unparsed, parse = True, tokenise = True,
...    corenlppath = 'Downloads/corenlp', nltk_data_path = 'Downloads/nltk_data')
```

which creates the parsed corpora, and returns their paths. You can also optionally pass in a string of annotators:

```python
ans = 'tokenize,ssplit,pos'
parsed = make_corpus(unparsed, operations = ans)
```

<a name="speaker-ids"></a>
#### Speaker IDs

Something novel about *corpkit* is that it can work with corpora containing speaker IDs (scripts, transcripts, logs, etc.), like this:

    JOHN: Why did they change the signs above all the bins?
    SPEAKER23: I know why. But I'm not telling.

If you use:

```python
>>> parsed = make_corpus(path, speaker_segmentation = True)
```

The function will:

1. Detect any IDs in any file
2. Create a duplicate version of the corpus with IDs removed
3. Parse this 'cleaned' corpus
4. Add an XML tag to each sentence with the name of the speaker
5. Return paths to the cleaned and parsed corpora

When interrogating or concordancing, you can then pass in a keyword argument to restrict searches to one or more speakers:

```python
>>> s = ['BRISCOE', 'LOGAN']
>>> npheads = interrogator(parsed, 'trees', r'/NN.?/ >># NP', just_speakers = s)
```

This makes it possible to not only investigate individual speakers, but to form an understanding of the overall tenor/tone of the text as well: *Who does most of the talking? Who is asking the questions? Who issues commands?*

<a name="concordancing"></a>
### Concordancing

Unlike most concordancers, which are based on plaintext corpora, *corpkit* can concordance via Tregex queries or dependency tokens:

```python
>>> from corpkit import conc

>>> subcorpus = 'data/nyt/years/2005'
>>> query = r'/JJ.?/ > (NP <<# (/NN.?/ < /\brisk/))'
# 't' option for tree searching
>>> lines = conc(subcorpus, 't', query, window = 50, n = 10, random = True)
```

Output (a `Pandas DataFrame`):

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

When searching dependencies, you have more flexibility:

```python
# match words starting with 'st' filling function of nsubj
>>> criteria = {'w': '^st', 'f': 'nsubj$'}
>>> lines = conc(subcorpus, criteria)
```

You can search tokenised corpora or plaintext corpora for regular expressions as well:

```python
>>> lines = conc(subcorpus, 'plaintext', query)
>>> lines = conc(subcorpus, 'tokens', query)
```

where `query` can be a regular expression or list of words to match.

If you really wanted, you can then go on to use `conc()` output as a dictionary, or extract keywords and ngrams from it, or keep or remove certain results with `editor()`. If you want to [give the GUI a try](http://interrogator.github.io/corpkit/), you can colour-code and create thematic categories for concordance lines as well.

<a name="systemic-functional-stuff"></a>
### Systemic functional stuff

Because I mostly use systemic functional grammar, there is also a simple tool for distinguishing between process types (relational, mental, verbal) when interrogating a corpus. If you add words to the lists in `dictionaries/process_types.py`, corpkit will get their inflections automatically.

```python
>>> from corpkit import quickview
>>> from dictionaries.process_types import processes

# match nsubj with verbal process as governor
>>> crit = {'f': '^nsubj$', 'g': processes.verbal}
# return lemma of the nsubj
>>> sayers = interrogator(corpus, crit, show = ['l'])

# have a look at the top results
>>> quickview(sayers, n = 20)
```

Output:

```
  0: he (n=24530)
  1: she (n=5558)
  2: they (n=5510)
  3: official (n=4348)
  4: it (n=3752)
  5: who (n=2940)
  6: that (n=2665)
  7: i (n=2062)
  8: expert (n=2057)
  9: analyst (n=1369)
 10: we (n=1214)
 11: report (n=1103)
 12: company (n=1070)
 13: which (n=1043)
 14: you (n=987)
 15: researcher (n=987)
 16: study (n=901)
 17: critic (n=826)
 18: person (n=802)
 19: agency (n=798)
 20: doctor (n=770)

```

First, let's try removing the pronouns using `editor()`. The quickest way is to use the editable wordlists stored in `dictionaries/wordlists`:

```python
>>> from corpkit import editor
>>> from dictionaries.wordlists import wordlists
>>> prps = wordlists.pronouns

# alternative approaches:
# >>> prps = [0, 1, 2, 4, 5, 6, 7, 10, 13, 14, 24]
# >>> prps = ['he', 'she', 'you']
# >>> prps = as_regex(wl.pronouns, boundaries = 'line')

# give edit() indices, words, wordlists or regexes to keep remove or merge
>>> sayers_no_prp = sayers.edit(skip_entries = prps,
...    skip_subcorpora = [1963])
>>> quickview(sayers_no_prp, n = 10)
```

Output:

```
  0: official (n=4342)
  1: expert (n=2055)
  2: analyst (n=1369)
  3: report (n=1098)
  4: company (n=1066)
  5: researcher (n=987)
  6: study (n=900)
  7: critic (n=825)
  8: person (n=801)
  9: agency (n=796)
```

Great. Now, let's sort the entries by trajectory, and then plot:

```python
# sort with editor()
>>> sayers_no_prp = sayers_no_prp.edit('%', sayers.totals, sort_by = 'increase')

# make an area chart with custom y label
>>> sayers_no_prp.plot('Sayers, increasing', kind = 'area', 
...    y_label = 'Percentage of all sayers')
```

Output:

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/sayers-increasing.png" />
<br><br>

We can also merge subcorpora. Let's look for changes in gendered pronouns:

```python
>>> merges = {'1960s': r'^196', 
...           '1980s': r'^198', 
...           '1990s': r'^199', 
...           '2000s': r'^200',
...           '2010s': r'^201'}

>>> sayers = sayers.edit(merge_subcorpora = merges)

# now, get relative frequencies for he and she
>>> genders = sayers.edit('%', 'self', just_entries = ['he', 'she'])

# and plot it as a series of pie charts, showing totals on the slices:
>>> genders.plot('Pronominal sayers in the NYT', kind = 'pie',
...    subplots = True, figsize = (15, 2.75), show_totals = 'plot')
```

Output:

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/ann_he_she.png" />
<br><br>

Woohoo, a decreasing gender divide! 

<a name="keywording"></a>
### Keywording

As I see it, there are two main problems with keywording, as typically performed in corpus linguistics. First is the reliance on 'balanced'/'general' reference corpora, which are obviously a fiction. Second is the idea of stopwords. Essentially, when most people calculate keywords, they use stopword lists to automatically filter out words that they think will not be of interest to them. These words are generally closed class words, like determiners, prepositions, or pronouns. This is not a good way to go about things: the relative frequencies of *I*, *you* and *one* can tell us a lot about the kinds of language in a corpus. More seriously, stopwords mean adding subjective judgements about what is interesting language into a process that is useful precisely because it is not subjective or biased.

So, what to do? Well, first, don't use 'general reference corpora' unless you really really have to. With *corpkit*, you can use your entire corpus as the reference corpus, and look for keywords in subcorpora. Second, rather than using lists of stopwords, simply do not send all words in the corpus to the keyworder for calculation. Instead, try looking for key *predicators* (rightmost verbs in the VP), or key *participants* (heads of arguments of these VPs):

```python
# just heads of participants' lemma form (no pronouns, though!)
>>> part = r'/(NN|JJ).?/ >># (/(NP|ADJP)/ $ VP | > VP)'
>>> p = interrogator(corpus, 'trees', part, show = 'l')
```

When using `editor()` to calculate keywords, there are a few default parameters that can be easily changed:

| Keyword argument | Function | Default setting | Type
|---|---|---|---|
| `threshold`  | Remove words occurring fewer than `n` times in reference corpus  | `False` | `'high/medium/low'`/ `True/False` / `int`
| `calc_all`  | Calculate keyness for words in both reference and target corpus, rather than just target corpus  | `True` | `True/False`
| `selfdrop`  | Attempt to remove target data from reference data when calculating keyness  | `True`  | `True/False`

Let's have a look at how these options change the output:

```python
# 'self' as reference corpus uses p.results
>>> options = {'selfdrop': False, 
...            'calc_all': False, 
...            'threshold': False}

>>> for k, v in options.items():
...    key = p.edit('keywords', 'self', k = v)
...    print key.results.ix['2011'].order(ascending = False)

```
Output:

| #1: default       | |   #2: no `selfdrop` | |  #3: no `calc_all`    |  |  #4: no `threshold` | |
|---|---:|---|---:|---|---:|---|---:|
| risk        | 1941.47  |  risk        |  1909.79  |  risk        | 1941.47   |  bank       |   668.19 |
| bank        | 1365.70  |  bank        |  1247.51  |  bank        | 1365.70   |  crisis     |   242.05 |
| crisis      |  431.36  |  crisis      |   388.01  |  crisis      |  431.36   |  obama      |   172.41 |
| investor    |  410.06  |  investor    |   387.08  |  investor    |  410.06   |  demiraj    |   161.90 |
| rule        |  316.77  |  rule        |   293.33  |  rule        |  316.77   |  regulator  |   144.91 |
|             |   ...    |              |    ...    |              |   ...     |             |    ...   |
| clinton     |  -37.80  |  tactic      |   -35.09  |  hussein     |  -25.42   |  clinton    |   -87.33 |
| vioxx       |  -38.00  |  vioxx       |   -35.29  |  clinton     |  -37.80   |  today      |   -89.49 |
| greenspan   |  -54.35  |  greenspan   |   -51.38  |  vioxx       |  -38.00   |  risky      |  -125.76 |
| bush        | -153.06  |  bush        |  -143.02  |  bush        | -153.06   |  bush       |  -253.95 |
| yesterday   | -162.30  |  yesterday   |  -151.71  |  yesterday   | -162.30   |  yesterday  |  -268.29 |

As you can see, slight variations on keywording give different impressions of the same corpus!

A key strength of *corpkit*'s approach to keywording is that you can generate new keyword lists without re-interrogating the corpus. Let's use Pandas syntax to look for keywords in the past few years.

```python
>>> yrs = ['2011', '2012', '2013', '2014']
>>> keys = editor(p.results.ix[yrs].sum(), 'keywords', p.results.drop(yrs),
...    threshold = False)
>>> print keys.results
```

Output:

```
bank          1795.24
obama          722.36
romney         560.67
jpmorgan       527.57
rule           413.94
dimon          389.86
draghi         349.80
regulator      317.82
italy          282.00
crisis         243.43
putin          209.51
greece         208.80
snowden        208.35
mf             192.78
adoboli        161.30
```

... or track the keyness of a set of words over time:

```python
>>> terror = ['terror', 'terrorism', 'terrorist']
>>> terr = p.edit('k', 'self', merge_entries = terror, newname = 'terror')
>>> print terr.results.terror
```

Output:

```
1963    -2.51
1987    -3.67
1988   -16.09
1989    -6.24
1990   -16.24
...       ...
Name: terror, dtype: float64
```

<a name="plotting-keywords"></a>
#### Plotting keywords

Naturally, we can use `plotter()` for our keywords too:

```python
>>> plotter('Terror* as Participant in the \emph{NYT}', pols.results.terror, 
...    kind = 'area', stacked = False, y_label = 'L/L Keyness')
>>> politicians = ['bush', 'obama', 'gore', 'clinton', 'mccain', 
...                'romney', 'dole', 'reagan', 'gorbachev']
>>> plotter('Keyness of politicians in the \emph{NYT}', k.results[politicans], 
...    num_to_plot = 'all', y_label = 'L/L Keyness', kind = 'area', legend_pos = 'center left')
```
Output:
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/terror-as-participant-in-the-emphnyt.png" />
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/keyness-of-politicians-in-the-emphnyt.png" />
<br><br>

<a name="traditional-reference-corpora"></a>
#### Traditional reference corpora

If you still want to use a standard reference corpus, you can do that (and a dictionary version of the BNC is included). For the reference corpus, `editor()` recognises `dicts`, `DataFrames`, `Series`, files containing `dicts`, or paths to plain text files or trees.

```python
# arbitrary list of common/boring words
>>> from dictionaries.stopwords import stopwords
>>> print editor(p.results.ix['2013'], 'k', 'bnc.p', 
...    skip_entries = stopwords).results
>>> print editor(p.results.ix['2013'], 'k', 'bnc.p', calc_all = False).results
```

Output (not so useful):

```
#1                                #2
bank           5568.25            bank      5568.25
person         5423.24            person    5423.24
company        3839.14            company   3839.14
way            3537.16            way       3537.16
state          2873.94            state     2873.94
                ...                           ...  
three          -691.25            ten       -199.36
people         -829.97            bit       -205.97
going          -877.83            sort      -254.71
erm           -2429.29            thought   -255.72
yeah          -3179.90            will      -679.06
```

<a name="parallel-processing"></a>
### Parallel processing

`interrogator()` can also parallel-process multiple queries or corpora. Parallel processing will be automatically enabled if you pass in either:

1. a `list` of paths as `path` (i.e. `['path/to/corpus1', 'path/to/corpus2']`)
2. a `dict` as `query` (i.e. `{'Noun phrases': r'NP', 'Verb phrases': r'VP'}`)

Let's look at different risk processes (e.g. *risk*, *take risk*, *run risk*, *pose risk*, *put at risk*) using constituency parses:

```python
>>> q = {'risk':        r'VP <<# (/VB.?/ < /(?i).?\brisk.?\b/)', 
...      'take risk':   r'VP <<# (/VB.?/ < /(?i)\b(take|takes|taking|took|taken)+\b/) < (NP <<# /(?i).?\brisk.?\b/)', 
...      'run risk':    r'VP <<# (/VB.?/ < /(?i)\b(run|runs|running|ran)+\b/) < (NP <<# /(?i).?\brisk.?\b/)', 
...      'put at risk': r'VP <<# /(?i)(put|puts|putting)\b/ << (PP <<# /(?i)at/ < (NP <<# /(?i).?\brisk.?/))', 
...      'pose risk':   r'VP <<# (/VB.?/ < /(?i)\b(pose|poses|posed|posing)+\b/) < (NP <<# /(?i).?\brisk.?\b/)'}

>>> processes = interrogator(corpus, 'trees', q, show = 'count')
>>> proc_rel = editor(processes.results, '%', processes.totals)
>>> plotter('Risk processes', proc_rel.results)
```

Output:

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" />
<br><br>

<a name="more-complex-queries-and-plots"></a>
### More complex queries and plots

Next, let's find out what kinds of noun lemmas are subjects of any of these risk processes:

```python
# a query to find heads of nps that are subjects of risk processes
>>> query = r'/^NN(S|)$/ !< /(?i).?\brisk.?/ >># (@NP $ (VP <+(VP) (VP ( <<# (/VB.?/ < /(?i).?\brisk.?/) ' \
...    r'| <<# (/VB.?/ < /(?i)\b(take|taking|takes|taken|took|run|running|runs|ran|put|putting|puts)/) < ' \
...    r'(NP <<# (/NN.?/ < /(?i).?\brisk.?/))))))'
>>> noun_riskers = interrogator(c, 'trees', query, show = 'l')
 
>>> quickview(noun_riskers, 10)
```

Output:

```
  0: person (n=195)
  1: company (n=139)
  2: bank (n=80)
  3: investor (n=66)
  4: government (n=63)
  5: man (n=51)
  6: leader (n=48)
  7: woman (n=43)
  8: official (n=40)
  9: player (n=39)
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
<br><br>

Let's also find out what percentage of the time some nouns appear as riskers:

```python
# find any head of an np not containing risk
>>> query = r'/NN.?/ >># NP !< /(?i).?\brisk.?/'
>>> noun_lemmata = interrogator(corpus, 'trees', query, show = 'l')

# get some key terms
>>> people = ['man', 'woman', 'child', 'baby', 'politician', 
...           'senator', 'obama', 'clinton', 'bush']
>>> selected = editor(noun_riskers.results, '%', noun_lemmata.results, 
...    just_entries = people, just_totals = True, threshold = 0, sort_by = 'total')

# make a bar chart:
>>> plotter('Risk and power', selected.results, num_to_plot = 'all', kind = 'bar', 
...    x_label = 'Word', y_label = 'Risker percentage', fontsize = 15)
```

Output:

<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" />
<br><br>

<a name="visualisation-options"></a>
### Visualisation options

With a bit of creativity, you can do some pretty awesome data-viz, thanks to *Pandas* and *Matplotlib*. The following plots require only one interrogation:

```python
>>> modals = interrogator(annual_trees, 'trees', 'MD < __', show = 'l')
# simple stuff: make relative frequencies for individual or total results
>>> rel_modals = editor(modals.results, '%', modals.totals)

# trickier: make an 'others' result from low-total entries
>>> low_indices = range(7, modals.results.shape[1])
>>> each_md = editor(modals.results, '%', modals.totals, merge_entries = low_indices, 
...    newname = 'other', sort_by = 'total', just_totals = True, keep_top = 7)

# complex stuff: merge results
>>> entries_to_merge = [r'(^w|\'ll|\'d)', r'^c', r'^m', r'^sh']
>>> modals = editor(modals.results, merge_entries = entries_to_merge)
    
# complex stuff: merge subcorpora
>>> merges = {'1960s': r'^196', 
...           '1980s': r'^198', 
...           '1990s': r'^199', 
...           '2000s': r'^200',
...           '2010s': r'^201'}

>>> modals = editor(sayers.results, merge_subcorpora = merges)
    
# make relative, sort, remove what we don't want
>>> modals = editor(modals.results, '%', modals.totals, keep_stats = False,
...    just_subcorpora = merges.keys(), sort_by = 'total', keep_top = 4)

# show results
>>> print rel_modals.results, each_md.results, modals.results
```
Output:
```
          would       will        can      could  ...        need     shall      dare  shalt
1963  22.326833  23.537323  17.955615   6.590451  ...    0.000000  0.537996  0.000000      0
1987  24.750614  18.505132  15.512505  11.117537  ...    0.072286  0.260228  0.014457      0
1988  23.138986  19.257117  16.182067  11.219364  ...    0.091338  0.060892  0.000000      0
...         ...        ...        ...        ...  ...         ...       ...       ...    ...
2012  23.097345  16.283186  15.132743  15.353982  ...    0.029499  0.029499  0.000000      0
2013  22.136269  17.286522  16.349301  15.620351  ...    0.029753  0.029753  0.000000      0
2014  21.618357  17.101449  16.908213  14.347826  ...    0.024155  0.000000  0.000000      0
[29 rows x 17 columns] 

would     23.235853
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
>>> plotter('Pie chart of common modals in the NYT', each_md.results, explode = ['other'],
...    num_to_plot = 'all', kind = 'pie', colours = 'Accent', figsize = (11, 11))

# bar chart, transposing and reversing the data
>>> plotter('Modals use by decade', modals.results.iloc[::-1].T.iloc[::-1], kind = 'barh',
...    x_label = 'Percentage of all modals', y_label = 'Modal group')

# stacked area chart
>>> plotter('An ocean of modals', rel_modals.results.drop('1963'), kind = 'area', 
...    stacked = True, colours = 'summer', figsize = (8, 10), num_to_plot = 'all', 
...    legend_pos = 'lower right', y_label = 'Percentage of all modals')
```
Output:
<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png"  height="400" width="400"/>
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/modals-use-by-decade.png"  height="230" width="500"/>
<img src="https://raw.githubusercontent.com/interrogator/risk/master/images/an-ocean-of-modals2.png"  height="600" width="500"/>
</p>

<a name="more-information"></a>
## More information

Some things are likely lacking documentation right now. For now, the more complex functionality of the toolkit is presented best in some of the research projects I'm working on:

1. [Longitudinal linguistic change in an online support group](https://github.com/interrogator/sfl_corpling) (thesis project)
2. [Discourse-semantics of *risk* in the NYT, 1963&ndash;2014](https://github.com/interrogator/risk) (most *corpkit* use)
3. [Learning Python, IPython and NLTK by investigating a corpus of Malcolm Fraser's speeches](https://github.com/resbaz/nltk)

<a name="cite"></a>
## Cite

If you want to cite *corpkit*, please use:

> `McDonald, D. (2015). corpkit: a toolkit for corpus linguistics. Retrieved from https://www.github.com/interrogator/corpkit. DOI: http://doi.org/10.5281/zenodo.28361`