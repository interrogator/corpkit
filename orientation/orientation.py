# <headingcell level=1>
# *corpkit*: a Python-based toolkit for working with parsed linguistic corpora
# <headingcell level=2>

# <markdowncell>
# [Daniel McDonald](mailto:mcdonaldd@unimelb.edu.au?Subject=corpkit)**
#---------------------------
# <markdowncell>
# <br>

# > **SUMMARY:** This *IPython Notebook* shows you how to use `corpkit` to investigate a corpus of paragraphs containing the word *risk* in the NYT between 1963 and 2014.

# <markdowncell>
# ## Setup

# <markdowncell>
# If you haven't already done so, the first things we need to do are **install corpkit**, download data for NLTK's tokeniser, and **unzip our corpus**.

# <codecell>
# install corpkit with either pip or easy_install
! easy_install -u corpkit

# <codecell>
# download nltk tokeniser data
import nltk
nltk.download('punkt')
nltk.download('wordnet')

# <codecell>
# unzip and untar our data
! gzip -dc data/nyt.tar.gz | tar -xf - -C data

# <markdowncell>
# Great! Now we have everything we need to start.

# <markdowncell>
# ### Orientation

# <markdowncell>
#  Let's import the functions we'll be using to investigate the corpus. These functions are designed for this interrogation, but also have more general use in mind, so you can likely use them on your own corpora.

# | **Function name** | Purpose                            | |
# | ----------------- | ---------------------------------- | |
# | `interrogator()`  | interrogate parsed corpora         | |
# | `editor()`        | edit `interrogator()` results         | |
# | `plotter()`       | visualise `interrogator()` results | |
# | `quickview()`     | view `interrogator()` results      | |
# | `multiquery()`     | run a list of `interrogator()` queries      | |
# | `conc()`          | complex concordancing of subcorpora | |
# | `keywords()`          | get keywords and ngrams from `conc()` output, subcorpora | |
# | `collocates()`          | get collocates from `conc()` output, subcorpora| |
# | `quicktree()`          | visually represent a parse tree | |
# | `searchtree()`          | search a parse tree with a Tregex query | |
# | `save_result()`          | save a result to disk | |
# | `load_result()`          | load a saved result | |
# | `new_project()`          | create a new project | |

# <codecell>
import corpkit
import pandas as pd
from corpkit import (interrogator, editor, plotter, quickview, multiquery,
                    conc, keywords, colls, save_result, load_result, new_project)
# show figures in browser
% matplotlib inline

# <markdowncell>
# Next, let's set the path to our corpus. If you were using this interface for your own corpora, you would change this to the path to your data.

# <codecell>
# corpus of every article, with annual subcorpora
annual_trees = 'data/nyt/years' 

# <markdowncell>
# Let's also quickly set some options for displaying raw data:

# <codecell>
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 10)
pd.set_option('max_colwidth',70)
pd.set_option('display.width', 1000)
pd.set_option('expand_frame_repr', False)

# <markdowncell>
# ### The data

# <markdowncell>

# Our main corpus is comprised of paragraphs from *New York Times* articles that contain a risk word, which we have defined by Regular Expression as `'(?i)'.?\brisk.?\b'`. This includes *low-risk*, or *risk/reward* as single tokens, but excludes *brisk* or *asterisk*.

# The data comes from a number of sources.

# * 1963 editions were downloaded from ProQuest Newsstand as PDFs. Optical character recognition and manual processing was used to create a set of 1200 risk sentences.
# * The 1987&ndash;2006 editions were taken from the *NYT Annotated Corpus*.
# * 2007&ndash;2014 editions were downloaded from *ProQuest Newsstand* as HTML.

# In total, 149,504 documents were processed. The corpus from which the risk corpus was made is over 150 million words in length!

# The texts have been parsed for part of speech and grammatical structure by [`Stanford CoreNLP*](http://nlp.stanford.edu/software/corenlp.shtml). In this Notebook, we are only working with the parsed versions of the texts. We rely on [*Tregex*](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html) to interrogate the corpora. Tregex allows very complex searching of parsed trees, in combination with [Java Regular Expressions](http://docs.oracle.com/javase/7/docs/api/java/util/regex/Pattern.html). It's definitely worthwhile to learn the Tregex syntax, but in case you're time-poor, at the end of this notebook are a series of Tregex queries that you can copy and paste into `interrogator()` and `conc()` queries.

# <markdowncell>
# ### Interrogating the corpus

# <markdowncell>
# So, let's start by finding out how many words we have in each subcorpus. To do this, we'll interrogate the corpus using `interrogator()`. Its most important arguments are:
#
# 1. **path to corpus**
#
# 2. Tregex **options**:
#   * **'t/w/words'**: return only words
#   * **'c/count'**: return a count of matches
#   * **'p/pos'**: return only the tag
#   * **'b/both'**: return tag and word together
#
# 3. a **Tregex query**

# We only need to count tokens, so we can use the `'count'` option (it's often faster than getting lists of matching tokens). The cell below will run `interrogator()` over each annual subcorpus and count the number of matches for the query.

# Some common Tregex patterns have been predefined. Searching for `'any'` will find any word in the corpus and count it.

# <codecell>
allwords = interrogator(annual_trees, 'count', 'any') 

# <markdowncell>
# When the interrogation has finished, we can view our results:

# <codecell>
# from the allwords results, print the totals
print allwords.totals

# <markdowncell>
# If you want to see the query and options that created the results, you can use:

# <codecell>
print allwords.query

# <markdowncell>
# ### Plotting results

# <markdowncell>
# Lists of years and totals are pretty dry. Luckily, we can use the `plotter()` function to visualise our results. At minimum, `plotter()` needs two arguments:

# 1. a title (in quotation marks)
# 2. a list of results to plot

# <codecell>
plotter('Word counts in each subcorpus', allwords.totals)

# <markdowncell>
# Because we have smaller samples for 1963 and 2014, we might want to project them. To do that, we can pass subcorpus names and projection values to `editor()`:

# <codecell>
proj_vals = [(1963, 5), (2014, 1.37)]
projected = editor(allwords.totals, projection = proj_vals)
plotter('Word counts in each subcorpus (projected)', projected.totals)

# <markdowncell>
# Great! So, we can see that the number of words per year varies quite a lot, even after projection. That's worth keeping in mind.

# <markdowncell>
# ### Frequency of risk words in the NYT

# <markdowncell>
# Next, let's count the total number of risk words. Notice that we are using the `'both'` flag, instead of the `'count'` flag, because we want both the word and its tag.

# <codecell>
# our query:
riskwords_query = r'__ < /(?i).?\brisk.?\b/' # any risk word and its word class/part of speech
# get all risk words and their tags :
riskwords = interrogator(annual_trees, 'both', riskwords_query)

# <markdowncell>
# Even when do not use the `count` flag, we can access the total number of matches as before:

# <codecell>
riskwords.totals

# <markdowncell>
# At the moment, it's hard to tell whether or not these counts are simply because our annual NYT samples are different sizes. To account for this, we can calculate the percentage of parsed words that are risk words. This means combining the two interrogations we have already performed.

# We can do this by using `editor()`:

# <codecell>
# "plot riskwords.totals as a percentage of allwords.totals"
rel_riskwords = editor(riskwords.totals, '%', allwords.totals)

# <codecell>
plotter('Relative frequency of risk words', rel_riskwords.totals)

# <markdowncell>
# That's more helpful. We can now see some interesting peaks and troughs in the proportion of risk words. We can also see that 1963 contains the highest proportion of risk words. This is because the manual corrector of 1963 OCR entries preserved only the sentence containing risk words, rather than the paragraph.

# Here are two methods for excluding 1963 from the chart:

# <codecell>
# using Pandas syntax:
plotter('Relative frequency of risk words', rel_riskwords.totals.drop('1963'))

# the other way: using editor()
#rel_riskwords = editor(rel_riskwords.totals, skip_subcorpora = [1963])
#plotter('Relative frequency of risk words', rel_riskwords.totals)

# <markdowncell>
# Perhaps we're interested in not only the frequency of risk words, but the frequency of different *kinds* of risk words. We actually already collected this data during our last `interrogator()` query.

# We can print just the first few entries of the results list, rather than the totals list.

# <codecell>
# using Pandas syntax:
riskwords.results.head(10)

# <codecell>
# using quickview
from corpkit import quickview
quickview(riskwords.results, n = 10)

# <markdowncell>
# So, let's use this data to do some more serious plotting:

# <codecell>
frac1 = editor(riskwords.results, '%', riskwords.totals)

# an alternative syntax:
# frac1 = editor(riskwords.results, '%', 'self')

# <codecell>
# a colormap is used for > 7 results
plotter('Risk word / all risk words', frac1.results, num_to_plot = 9)

# <markdowncell>
# If `plotter()` can't find a good spot for the legend, you can explicitly move it:

# <codecell>
plotter('Risk word / all risk words', frac1.results, num_to_plot = 9, legend = 'lower right')
plotter('Risk word / all risk words', frac1.results, num_to_plot = 9, legend = 'outside right')

# <codecell>
frac2 = editor(riskwords.results, '%', allwords.totals)

# <codecell>
plotter('Risk word / all words', frac2.results, legend = 'outside right')

# <markdowncell>
# Another neat feature is the `.table` attribute of interrogations, which shows the most common `n` results in each subcorpus:

# <codecell>
riskwords.table

# <markdowncell>
# ### Customising visualisations

# <markdowncell>
# By default, `plotter()` plots the seven most frequent results, including 1963.

#  We can use other `plotter()` arguments to customise what our chart shows. `plotter()`'s possible arguments are:

#  | `plotter()` argument | Mandatory/default?       |  Use          | Type  |
#  | :------|:------- |:-------------|:-----|
#  | `title` | **mandatory**      | A title for your plot | string |
#  | `results` | **mandatory**      | the results you want to plot | `interrogator()` or `editor()` output |
#  | `num_to_plot` | 7    | Number of top entries to show     |  int |
#  | `x_label` | False    | custom label for the x-axis     |  str |
#  | `y_label` | False    | custom label for the y-axis     |  str |
#  | figsize | (13, 6) | set the size of the figure | tuple: `(length, width)`|
#  | tex | `'try'` | use *TeX* to generate image text | boolean |
#  | style | `'ggplot'` | use Matplotlib styles | str: `'dark_background'`, `'bmh'`, `'grayscale'`, `'ggplot'`, `'fivethirtyeight'`, `'matplotlib'` |
#  | legend | `'default'` | legend position | str: `'outside right'` to move legend outside chart |

# <codecell>
plotter('Risk words', frac2.results, num_to_plot = 5, y_label = 'Percentage of all words')

# <markdowncell>
# Keyword arguments for Pandas and matplotlib can also be used:

# <codecell>
plotter('Risk words', frac2.results.drop('1963'), subplots = True)

# <codecell>
# stacked bar chart
plotter('Risk words', frac2.results.drop('1963'), kind = 'bar', stacked = True, legend = 'o r')


# <codecell>
# applying color scheme (see http://matplotlib.org/examples/color/colormaps_reference.html)
# not using tex for fonts
# setting a font size
plotter('Risk words', editor(frac2.results, just_entries= r'^\(v').results, kind = 'area', 
        stacked = True, legend = 'o r', colours = 'Oranges', num_to_plot = 'all', fontsize = 16, tex = False)

# <markdowncell>
# Those already proficient with Python can use [Pandas' `plot()` function](http://pandas.pydata.org/pandas-docs/stable/visualization.html) if they like

# <markdowncell>
# Another neat thing you can do is save the results of an interrogation, so they don't have to be run the next time you load this notebook:

# <codecell>
# specify what to save, and a name for the file.
from corpkit import save_result, load_result
save_result(allwords, 'allwords')

# <markdowncell>
# You can then load these results:

# <codecell>
fromfile_allwords = load_result('allwords')
fromfile_allwords.totals

# <markdowncell>
# ... or erase them from memory:

# <codecell>
fromfile_allwords = None
# fromfile_allwords

# <markdowncell>
# ### `quickview()`

# <markdowncell>
# `quickview()` is a function that quickly shows the n most frequent items in a list. Its arguments are:

# 1. `interrogator()` or `editor()` output (preferably, the whole interrogation, not just the `.results` branch.)
# 2. number of results to show (default = 25)

# <codecell>
quickview(riskwords, n = 15)

# <markdowncell>
# The number shown next to the item is its index. You can use this number to refer to an entry when editing results.

# ### `editor()`

# <markdowncell>
# Results lists can be edited quickly with `editor()`. It has a lot of different options:

#  | `editor()` argument | Mandatory/default?       |  Use          | Type  |
#  | :------|:------- |:-------------|:-----|
#  | `df` | **mandatory**      | the results you want to edit | `interrogator()` or `editor` output |
#  | `operation` | '%'      | if using second list, what operation to perform | `'+', '-', '/', '*' or '%'` |
#  | `df2` | False      | Results to comine in some way with `df` | `interrogator()` or `editor` output (usually, a `.totals` branch) |
#  | `just_subcorpora` | False    |   Subcorpora to keep   |  list |
#  | `skip_subcorpora` | False    |   Subcorpora to skip   |  list |
#  | `merge_subcorpora` | False    |   Subcorpora to merge   |  list |
#  | `new_subcorpus_name` | False    |   name for merged subcorpora   |  index/str |
#  | `just_entries` | False    |   Entries to keep   |  list |
#  | `skip_entries` | False    |   Entries to skip   |  list |
#  | `merge_entries` | False    |   Entries to merge   |  list of words or indices/a regex to match |
#  | `sort_by` | False    |   sort results   |  str: `'total', 'infreq', 'name', 'increase', 'decrease'` |
#  | `keep_top` | False    |   Keep only top n results after sorting   |  int |
#  | `just_totals` | False    |   Collapse all subcorpora, return Series   | bool |
#  | `projection` | False    |   project smaller subcorpora   |  list of tuples: [`(subcorpus_name, projection_value)]` |
#  | `**kwargs` | False    |   pass options to *Pandas*' `plot()` function, *Matplotlib*   |  various |

# <markdowncell>
# Let's try these out on a new interrogation. The query below will get adjectival risk words:

# <codecell>
adj = '/JJ.?/ < /(?i)\brisk/'
adj_riskwords = interrogator(annual_trees, 'words', adj, spelling = 'UK')

# <markdowncell>
# First, we can select specific subcorpora to keep, remove or span:

# <codecell>
editor(adj_riskwords.results, skip_subcorpora = [1963, 1987, 1988]).results

# <codecell>
editor(adj_riskwords.results, just_subcorpora = [1963, 1987, 1988]).results

# <codecell>
editor(adj_riskwords.results, span_subcorpora = [2000, 2010]).results

# <markdowncell>
# We can do similar kinds of things with each *result*:

# <codecell>
quickview(adj_riskwords.results)

# <codecell>
editor(adj_riskwords.results, skip_entries = [2, 5, 6]).results

# <codecell>
editor(adj_riskwords.results, just_entries = [2, 5, 6]).results

# <markdowncell>
# We can also use the words themselves, rather than indices, for all of these operations:

# <codecell>
editor(adj_riskwords.results, just_entries = ['(nn risk-management)', '(jj risk-management)']).results

# <markdowncell>
# Or, we can use Regular Expressions:

# <codecell>
# skip any verbal risk
editor(adj_riskwords.results, skip_entries = r'^\(v').results


# <markdowncell>
# We can also merge entries, and specify a new name for the merged items. In lieu of a name, we can pass an index. 

# <codecell>
editor(adj_riskwords.results, merge_entries = [2, 5, 6], newname = 'New name').results

# <codecell>
editor(adj_riskwords.results, merge_entries = ['(nns risks)', '(nns risk-takers)', '(nns risks)'], newname = 1).results

# <markdowncell>
# Notice how the merged result appears as the final column. To reorder the columns by total frequency, we can use `sort_by = 'total'`.

# <codecell>
# if we don't specify a new name, editor makes one for us
generated_name = editor(adj_riskwords.results, merge_entries = [2, 5, 6], sort_by = 'total')
quickview(generated_name.results)

# <markdowncell>
# `editor()` can sort also sort alphabetically, or by least frequent:

# <codecell>
# alphabetically
editor(adj_riskwords.results, sort_by = 'name').results

# <codecell>
# least frequent
editor(adj_riskwords.results, sort_by = 'infreq').results

# <markdowncell>
# Particularly cool is sorting by 'increase' or 'decrease': this calculates the trend lines of each result, and sort by the slope.

# <codecell>
editor(adj_riskwords.results, sort_by = 'increase').results

# <markdowncell>
# We can use `just_totals` to output just the sum of occurrences in each subcorpus:

# <codecell>
editor(adj_riskwords.results, just_totals = True).results

# <markdowncell>
# A handy thing about working with Pandas DataFrames is that we can easily translate our results to other formats:

# <codecell>
deceasing = editor(adj_riskwords.results, sort_by = 'decrease')

# <codecell>
# tranpose with T, get just top 5 results, print as CSV
print deceasing.results.T.head().to_csv()

# <codecell>
# or, print to latex markup:
print deceasing.results.T.head().to_latex()

# <markdowncell>
# Of course, you can perform many of these operations at the same time. Problems may arise, however, especially if your options contradict.

# <codecell>
editor(adj_riskwords.results, '%', adj_riskwords.totals, span_subcorpora = [1990, 2000], 
    just_entries = r'^\(n', merge_entries = r'(nns|nnp)', newname = 'Plural/proper', sort_by = 'name').results

# <markdowncell>
# ### Diversity of risk words

# <markdowncell>
# It's important to note that the kind of results we generate are hackable. We could count the number of unique risk words in each subcorpus by changing any count over 1 to 1.

# <codecell>
import numpy as np
# copy our list
uniques = adj_riskwords.results.copy()
# divide every result by itself
for f in uniques:
    uniques[f] = uniques[f] / uniques[f]
# get rid of inf scores (i.e. 0 / 0) using numpy
uniques = uniques.replace(np.inf, 0)
# sum the results
u = uniques.T.sum()
# give our data a name
u.name = 'Unique risk words'

# <codecell>
plotter('Unique risk words', u.drop(['1963', '2014']), y_label = 'Number of unique risk words', legend = False)

# <markdowncell>
# Just for fun, let's try that again with a few chart styles:

# <codecell>
for sty in ['dark_background', 'bmh', 'grayscale', 'fivethirtyeight', 'matplotlib']:
    plotter('Unique risk words', u.drop(['1963', '2014']), 
        y_label = 'Number of unique risk words', style = sty)

# <markdowncell>
# So, we can see a generally upward trajectory, with more risk words constantly being used. Many of these results appear once, however, and many are nonwords. *Can you figure out how to remove words that appear only once per year?*

# <codecell>
#

# <markdowncell>
# ### conc()

# <markdowncell>
# `conc()` produces concordances of a subcorpus. Its main arguments are:

# 1. A subcorpus to search *(remember to put it in quotation marks!)*
# 2. A query

# If your data consists of parse trees, you can use a Tregex query. If your data is one or more plain-text files, you can just a regex. We'll show Tregex style here.

# <codecell>
lines = conc('data/nyt/years/1999', r'/JJ.?/ << /(?i).?\brisk.?\b/') # adj containing a risk word

# <markdowncell>
# You can set `conc()` to print only the first ten examples with `n = 10`, or ten random these with the `n = 15, random = True` parameter.

# <codecell>
lines = conc('data/nyt/years/2007', r'/VB.?/ < /(?i).?\brisk.?\b/', n = 15, random = True)

# <markdowncell>
# `conc()` takes another argument, window, which alters the amount of co-text appearing either side of the match. The default is 50 characters

# <codecell>
lines = conc('data/nyt/topics/health/2013', r'/VB.?/ << /(?i).?\brisk.?\b/', n = 15, random = True, window = 20)

# <markdowncell>
# `conc()` also allows you to view parse trees. By default, it's false:

# <codecell>
lines = conc('data/nyt/years/2013', r'/VB.?/ < /(?i)\btrad.?/', trees = True)

# <markdowncell>
# Just like our other data, conc lines can be edited with `editor()`, or outputted as CSV.

# <codecell>
lines = editor(lines, skip_entries = [1, 2, 4, 5])
print lines

# <markdowncell>
# If the concordance lines aren't print well, you can use `concprinter()`:

# <codecell>
from corpkit import concprinter
concprinter(lines)

# <markdowncell>
# Or, you can just use Pandas syntax:

# <codecell>
# Because there may be commas in the concordance lines, 
# it's better to generate a tab-separated CSV:
print lines.to_csv(sep = '\t')

# <markdowncell>
# You can also print some `TeX`, if you're that way inclined:

# <codecell>
print lines.to_latex()

# <markdowncell>
# ### Keywords and ngrams

# <markdowncell>
# `corpkit` has some functions for keywording, ngramming and collocation. Each can take a number of kinds of input data:

# 1. a path to a subcorpus (of either parse trees or raw text)
# 2. `conc()` output
# 3. a string of text

# `keywords()` produces both keywords and ngrams. It relies on code from the [Spindle](http://openspires.oucs.ox.ac.uk/spindle/) project.

# <codecell>
from corpkit import keywords
keys, ngrams = keywords(lines)
for key in keys[:10]:
    print key
for ngram in ngrams:
    print ngram

# <markdowncell>
# You can also use `interrogator()` to search for keywords or ngrams. To do this, instead of a Tregex query, pass `'keywords'` or `'ngrams'`. You should also specify a dictionary to use as the reference corpus. If you specify `dictionary = 'self'`, a dictionary will be made of the entire corpus, saved, and used.

# <codecell>
kwds_bnc = interrogator(annual_trees, 'words', 'keywords', dictionary = 'bnc.p')

# <codecell>
kwds = interrogator(annual_trees, 'words', 'keywords', dictionary = 'self')

# <markdowncell>
# Now, rather than a frequency count, you will be given the keyness of each word.

# <codecell>
quickview(kwds.results)

# <codecell>
kwds.table

# <markdowncell>
# Let's sort these, based on those increasing/decreasing frequency:

# <codecell>
inc = editor(kwds.results, sort_by = 'increase')
dec = editor(kwds.results, sort_by = 'decrease')

# <markdowncell>
# ... and have a look:

# <codecell>
quickview(inc, 15)

# <codecell>
quickview(dec, 15)

# <markdowncell>
# As expected, really. Defunct states and former politicans are on the way out, while newer politicans are on the way in. We can do the same with n-grams, of course:

# <codecell>
ngms = interrogator(annual_trees, 'words', 'ngrams')

# <markdowncell>
# Neat. Now, let's make some thematic categories. This time, we'll make a list of tuples, containing regexes to match, and the result names:

# <codecell>
regexes = [(r'\b(legislature|medicaid|republican|democrat|federal|council)\b', 'Government organisations'),
(r'\b(empire|merck|commerical)\b', 'Companies'),
(r'\b(athlete|policyholder|patient|yorkers|worker|infant|woman|man|child|children|individual|person)\b', 'People, everyday'),
(r'\b(marrow|blood|lung|ovarian|breast|heart|hormone|testosterone|estrogen|pregnancy|prostate|cardiovascular)\b', 'The body'),
(r'\b(reagan|clinton|obama|koch|slaney|starzl)\b', 'Specific people'),
(r'\b(implant|ect|procedure|abortion|radiation|hormone|vaccine|medication)\b', 'Treatments'),
(r'\b(addiction|medication|drug|statin|vioxx)\b', 'Drugs'),
(r'\b(addiction|coronary|aneurysm|mutation|injury|fracture|cholesterol|obesity|cardiovascular|seizure|suicide)\b', 'Symptoms'),
(r'\b(worker|physician|doctor|midwife|dentist)\b', 'Healthcare professional'),
(r'\b(transmission|infected|hepatitis|virus|hiv|lung|aids|asbestos|malaria|rabies)\b', 'Infectious disease'),
(r'\b(huntington|lung|prostate|breast|heart|obesity)\b', 'Non-infectious disease'), 
(r'\b(policyholder|reinsurance|applicant|capitation|insured|insurer|insurance|uninsured)\b', 'Finance'),
(r'\b(experiment|council|journal|research|university|researcher|clinical)\b', 'Research')]

# <markdowncell>
# Now, let's loop through out list and merge keyword and n-gram entries:

# <codecell>
# NOTE: you can use `print_info = False` if you don't want all this stuff printed.
for regex, name in regexes:
    kwds = editor(kwds.results, merge_entries = regex, newname = name)
    ngms = editor(ngms.results, merge_entries = regex, newname = name, print_info = False)

# now, remove all other entries
kwds = editor(kwds.results, just_entries = [name for regex, name in regexes])
ngms = editor(ngms.results, '%', ngms.totals, just_entries = [name for regex, name in regexes])

# <markdowncell>
# Pretty nifty, eh? Welp, let's plot them:

# <codecell>
plotter('Key themes: keywords', kwds.results.drop('1963'), y_label = 'L/L Keyness')
plotter('Key themes: n-grams', ngms.results.drop('1963'), y_label = 'Percentage of all n-grams')

# <markdowncell>
# ### Collocates

# <markdowncell>
# You can easily generate collocates for corpora, subcorpora or concordance lines:

# <codecell>
from corpkit import collocates
conc_colls = collocates(adj_lines)
for coll in conc_colls:
    print coll

subc_colls = collocates('data/nyt/years/2003')
for coll in subc_colls:
    if 'risk' not in coll:
        print coll

# <markdowncell>
# With the `collocates()` function, you can specify the maximum distance at which two tokens will be considered collocates.

# <codecell>
colls = collocates(adj_lines, window = 3)
for coll in colls:
    print coll

# <markdowncell>
# ### quicktree() and searchtree()

# <markdowncell>
# The two functions are useful for visualising and searching individual syntax trees. They have proven useful as a way to practice your Tregex queries.

# You could get trees by using `conc()` with a very large window and *trees* set to *True*. Alternatively, you can open files in the data directory directly, and paste them in.

# `quicktree()` generates a visual representation of a parse tree. Here's one from 1989:

# <codecell>
tree = '(ROOT (S (NP (NN Pre-conviction) (NN attachment)) (VP (VBZ carries) (PP (IN with) (NP (PRP it))) (NP (NP (DT the) (JJ obvious) (NN risk)) (PP (IN of) (S (VP (VBG imposing) (NP (JJ drastic) (NN punishment)) (PP (IN before) (NP (NN conviction)))))))) (. .)))'
# currently broken!
quicktree(tree)

# <markdowncell>
# `searchtree()` requires a tree and a Tregex query. It will return a list of query matches.

# <codecell>
print searchtree(tree, r'/VB.?/ >># (VP $ NP)')
print searchtree(tree, r'NP')

# <markdowncell>
# Now you're familiar with the corpus and functions. Get more examples at the [Risk Semantics GitHub[(https://www.github.com/interrogator/risk), start your own new project, or wait for more advanced examples, which are coming soon.

# <codecell>
new_project('my-project')
# now go to File -> Open, and open it!

# <markdowncell>
# ## More advanced usage

# <markdowncell>
# ### Concordances for each keyword:

# <codecell>
import os
# kwds = interrogator(annual_trees, 'words', 'keywords')
kwds = load_result('kwds')
# iterate through results
for index, w in enumerate(kwds.results[:5]):
    # get the year with most occurrences
    top_year = kwds.results[w].idxmax()
    # print some info
    print '\n%d: %s, %s' % (index + 1, w, str(top_year))
    # get path to that subcorpus
    top_dir = os.path.join(annual_trees, str(top_year))
    # make a tregex query with token start and end defined
    query = r'/(?i)^' + w + r'$/'
    # do concordancing
    lines = conc(top_dir, query, random = True, n = 10)

# <markdowncell>
# 