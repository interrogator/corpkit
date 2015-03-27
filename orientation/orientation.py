# <headingcell level=1>
# *corpkit*: a Python-based toolkit for working with parsed linguistic corpora
# <headingcell level=2>

# <markdowncell>
# [Daniel McDonald](mailto:mcdonaldd@unimelb.edu.au?Subject=IPython%20NYT%20risk%20project)**
#---------------------------
# <markdowncell>
# <br>

# > **SUMMARY:** This *IPython Notebook* shows you how to use `corpkit` to investigate a corpus of paragraphs containing the word *risk* in the NYT between 1963 and 2014.

# <headingcell level=2>
# Orientation

# <markdowncell>
# First, let's import the functions we'll be using to investigate the corpus. These functions are designed for this interrogation, but also have more general use in mind, so you can likely use them on your own corpora.

# | **Function name** | Purpose                            | |
# | ----------------- | ---------------------------------- | |
# | `interrogator()`  | interrogate parsed corpora         | |
# | `dependencies()`  | interrogate parsed corpora for dependency info (presented later)         | |
# | `plotter()`       | visualise `interrogator()` results | |
# | `table()`          | return plotter() results as table | |
# | `quickview()`     | view `interrogator()` results      | |
# | `tally()`       | get total frequencies for `interrogator()` results      | |
# | `surgeon()`       | edit `interrogator()` results      | |
# | `merger()`       | merge `interrogator()` results      | |
# | `conc()`          | complex concordancing of subcorpora | |
# | `keywords()`          | get keywords and ngrams from `conc()` output | |
# | `collocates()`          | get collocates from `conc()` output| |
# | `quicktree()`          | visually represent a parse tree | |
# | `searchtree()`          | search a parse tree with a Tregex query | |

# <codecell>
import corpkit
from corpkit import interrogator, plotter
# show visualisations inline:
%matplotlib inline

# <markdowncell>
# Next, let's set the path to our corpus. If you were using this interface for your own corpora, you would change this to the path to your data.

# <codecell>
# to unzip nyt files:
# gzip -dc data/nyt.tar.gz | tar -xf - -C data
# corpus with annual subcorpora
annual_trees = 'data/nyt/years' 

# <headingcell level=3>
# The data

# <markdowncell>

# Our main corpus is comprised of paragraphs from *New York Times* articles that contain a risk word, which we have defined by regular expression as '(?i)'.?\brisk.?\b'. This includes *low-risk*, or *risk/reward* as single tokens, but excludes *brisk* or *asterisk*.

# The data comes from a number of sources.

# * 1963 editions were downloaded from ProQuest Newsstand as PDFs. Optical character recognition and manual processing was used to create a set of 1200 risk sentences.
# * The 1987--2006 editions were taken from the *NYT Annotated Corpus*.
# * 2007--2014 editions were downloaded from *ProQuest Newsstand* as HTML.

# In total, 149,504 documents were processed. The corpus from which the risk corpus was made is over 150 million words in length!

# The texts have been parsed for part of speech and grammatical structure by [`Stanford CoreNLP*](http://nlp.stanford.edu/software/corenlp.shtml). In this Notebook, we are only working with the parsed versions of the texts. We rely on [*Tregex*](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html) to interrogate the corpora. Tregex allows very complex searching of parsed trees, in combination with [Java Regular Expressions](http://docs.oracle.com/javase/7/docs/api/java/util/regex/Pattern.html). It's definitely worthwhile to learn the Tregex syntax, but in case you're time-poor, at the end of this notebook are a series of Tregex queries that you can copy and paste into *interrogator()` and `conc()` queries.

# <headingcell level=3>
# Interrogating the corpus

# <markdowncell>
# So, let's start by generating some general information about this corpus. First, let's define a query to find every word in the corpus. Run the cell below to define the `allwords_query` variable as the Tregex query to its right.

# > *When writing Tregex queries or Regular Expressions, remember to always use `r'...'` quotes!*

# <codecell>
# any token containing letters or numbers (i.e. no punctuation):
allwords_query = r'/[A-Za-z0-9]/ !< __' 

# <markdowncell>
# Next, we perform interrogations with `interrogator()`. Its most important arguments are:
#
# 1. **path to corpus**
#
# 2. Tregex **options**:
#   * **'-t'**: return only words
#   * **'-C'**: return a count of matches
#   * **'-u'**: return only the tag
#   * **'-o'**: return tag and word together
#
# 3. the **Tregex query**

# We only need to count tokens, so we can use the **-C** option (it's often faster than getting lists of matching tokens). The cell below will run `interrogator()` over each annual subcorpus and count the number of matches for the query.

# <codecell>
allwords = interrogator(annual_trees, '-C', allwords_query) 

# <markdowncell>
# When the interrogation has finished, we can view our results:

# <codecell>
# from the allwords results, print the totals
print allwords.totals

# <markdowncell>
# If you want to see the query and options that created the results, you can use:

# <codecell>
print allwords.query

# <headingcell level=3>
# Plotting results

# <markdowncell>
# Lists of years and totals are pretty dry. Luckily, we can use the `plotter()` function to visualise our results. At minimum, `plotter()` needs two arguments:

# 1. a title (in quotation marks)
# 2. a list of results to plot

# There is also an argument for projecting the 1963 and 2014 results, which can either be set to true or false. By default, it is true, and in this Notebook from now on we'll leave it turned on. We'll try both options here:

# <codecell>
plotter('Word counts in each subcorpus', allwords.totals, projection = False)
plotter('Word counts in each subcorpus (projected)', allwords.totals, projection = True)

# <markdowncell>
# Great! So, we can see that the number of words per year varies quite a lot. That's worth keeping in mind.

# <headingcell level=3>
# Frequency of risk words in the NYT

# <markdowncell>
# Next, let's count the total number of risk words. Notice that we are using the '-o' flag, instead of the **-C** flag.

# <codecell>
# our query:
riskwords_query = r'__ < /(?i).?\brisk.?\b/' # any risk word and its word class/part of speech
# get all risk words and their tags:
riskwords = interrogator(annual_trees, '-o', riskwords_query)

# <markdowncell>
# Even when do not use the `-C` flag, we can access the total number of matches as before:

# <codecell>
plotter('Risk words', riskwords.totals)

# <markdowncell>
# At the moment, it's hard to tell whether or not these counts are simply because our annual NYT samples are different sizes. To account for this, we can calculate the percentage of parsed words that are risk words. This means combining the two interrogations we have already performed.

# We can do this by passing a third argument to `plotter()`.

# <codecell>
plotter('Relative frequency of risk words', riskwords.totals, 
    fract_of = allwords.totals)

# <markdowncell>
# That's more helpful. We can now see some interesting peaks and troughs in the proportion of risk words. We can also see that 1963 contains the highest proportion of risk words. This is because the manual corrector of 1963 OCR entries preserved only the sentence containing risk words, rather than the paragraph.

# It's often helpful to not plot 1963 results for this reason. To do this, we can add an argument to the `plotter()` call:

# <codecell>
plotter('Relative frequency of risk words', riskwords.totals, 
    fract_of = allwords.totals, skip63 = True)

# <markdowncell>
# Perhaps we're interested in not only the frequency of risk words, but the frequency of different `kinds* of risk words. We actually already collected this data during our last *interrogator()` query.

# We can print just the first three entries of the results list, rather than the totals list:

# <codecell>
for word in riskwords.results[:3]:
    print word
# uncomment below to print the totals:
# print riskwords.totals

# <markdowncell>
# We now have enough data to do some serious plotting.

# <codecell>
plotter('Risk word / all risk words', riskwords.results, 
    fract_of = riskwords.totals)
plotter('Risk word / all words', riskwords.results, 
    fract_of = allwords.totals)


# <headingcell level=3>
# Customising visualisations

# <markdowncell>
# By default, `plotter()` plots the seven most frequent results, including 1963 and projecting 1963 and 2014.

#  We can use other `plotter()` arguments to customise what our chart shows. `plotter()`'s possible arguments are:

#  | plotter() argument | Mandatory/default?       |  Use          | Type  |
#  | :------|:------- |:-------------|:-----|
#  | *title* | **mandatory**      | A title for your plot | string |
#  | `results* | **mandatory**      | the results you want to plot | *interrogator()` total |
#  | *fract_of* | None      | results for plotting relative frequencies/ratios etc. | list (interrogator(-C) form) |
#  | *num_to_plot* | 7     | number of top results to display     |   integer |
#  | *skip63* | False    | do not plot 1963     |    integer |
#  | *proj63* | 4     | multiplier to project 1963 results and totals | integer |
#  | *multiplier* | 100     | result * multiplier / total: use 1 for ratios | integer |
#  | *x_label* | False    | custom label for the x-axis     |  string |
#  | *y_label* | False    | custom label for the y-axis     |  string |
#  | *legend_totals* | False    | Print total/rel freq in legend     |  boolean 
#  | *projection* | True    | Project 1963 and 2014 editions     |  boolean |
#  | *yearspan* | False    | plot a span of years |  a list of two int years |
#  | *csvmake* | False    | make csvmake the title of csv output file    |  string |
#  | *save* | False    | save generated image (True = with title as name)   |  True/False/string |

# You can easily use these to get different kinds of output. Try changing some parameters below:

# <codecell>
plotter('Relative frequencies of risk words', riskwords.results, fract_of = allwords.totals,
    y_label = 'Percentage of all risk words', num_to_plot = 5, 
    skip63 = False, projection = True, proj63 = 5, csvmake = 'riskwords.csv', legend_totals = True)

# <markdowncell>
# If you just generated a csv file, you can quickly get the results with:

# <codecell>
!cat 'riskwords.csv'  | head -n 7
# and to delete it:
#!rm 'riskwords.csv'

# Use *yearspan* or *justyears* to specify years of interest:

# <codecell>
plotter('Relative frequencies of risk words', riskwords.results, fract_of = allwords.totals,
    y_label = 'Percentage of all risk words', num_to_plot = 5, skip63 = False, 
    yearspan = [1963,1998])

# <markdowncell>
# Another way to change `plotter()` visualisations is by not passing certain results to `plotter()`.

# Each entry in the list of results is indexed: the top result is item 0, the second result is item 1, and so on.

# So, you can skip the first 2 results by using [2:] after the results list:

# <codecell>
plotter('Relative frequencies of risk words', riskwords.results[2:], fract_of = allwords.totals,
    y_label = 'Percentage of all risk words', num_to_plot = 5, skip63 = False, projection = True, proj63 = 5, legend_totals = True)

# <markdowncell>
# If you are after a specific set of indexed items, it's probably better to use `surgeon()` (described below). For completeness, though, here's another way:

# <codecell>
indices_we_want = [32,30,40]
plotter('Relative frequencies of risk words', [ riskwords.results[i] for i in indices_we_want], 
        num_to_plot = 5, skip63 = True, projection = True, proj63 = 5)


# <markdowncell>
# Another neat thing you can do is save the results of an interrogation, so they don't have to be run the next time you load this notebook:

# <codecell>
# specify what to save, and a name for the file.
save_result(allwords, 'allwords')

# <markdowncell>
# You can then load these results:

# <codecell>
fromfile_allwords = load_result('allwords')
fromfile_allwords.totals

# <headingcell level=3>
# table()

# <markdowncell>
# If you want to quickly table the results of a csv file, you can use `table()`. Its only main argument is the path to the csv file as string. There are two optional arguments. First, you can set `allresults` to `True` to table all results, rather than just the plotted results. When this option is set to true, you may get *way* too many results. To cope with this, there is a `maxresults` argument, whose value by default is 50. You can overwrite this default to table more or fewer results.

# <codecell>

table('riskwords.csv')

# <codecell>
table('riskwords.csv', allresults = True, maxresults = 30)

# <headingcell level=3>
# quickview()

# <markdowncell>
# `quickview()` is a function that quickly shows the n most frequent items in a list. Its arguments are:

# 1. an `interrogator()` result
# 2. number of results to show (default = 50)

# <codecell>
quickview(riskwords.results, n = 25)

# <markdowncell>
# The number shown next to the item is its index. You can use this number to refer to an entry when editing results.

# <headingcell level=3>
# tally()

# <markdowncell>
# `tally()` simply displays the total occurrences of results. Its first argument is the list you want tallies from. For its second argument, you can use:

# * a list of indices for results you want to tally
# * a single integer, which will be interpreted as the index of the item you want
# * a regular expression to search for
# * a string, 'all', which will tally every result. This could be very many results, so it may be worth limiting the number of items you pass to it with [:n], as in the second example below:

# <codecell>
tally(riskwords.results, [0, 5, 10])

# <codecell>
tally(riskwords.results[:10], 'all')

# <markdowncell>
# The Regular Expression option is useful for merging results (see below).

# <headingcell level=3>
# surgeon()

# <markdowncell>
# Results lists can be edited quickly with `surgeon()`. `surgeon()`'s arguments are:

# 1. an `interrogator()` results list
# 2. *criteria*: either a [Regular Expression](http://www.cheatography.com/davechild/cheat-sheets/regular-expressions/) or a list of indices.
# 3. *remove = True/False*

# By default, `surgeon()` keeps anything matching the regex, but this can be inverted with a *remove = True* argument. Because you are duplicating the original list, you don't have to worry about deleting `interrogator()` results.

# <codecell>
# low and high risks, using indices 
lowhighrisks = surgeon(riskwords.results, [4, 9, 17]) # keep 4, 9 and 17
plotter('Low-, high- and higher- risk', lowhighrisks.results, num_to_plot = 3, skip63 = True)

# only hyphenate words:
nohyphenates = surgeon(riskwords.results, r'\b.*-.*\b', remove = True) # remove tokens with hyphens
quickview(nohyphenates.results)
plotter('Non-hypenate risk words', nohyphenates.results, fract_of = riskwords.totals, 
    y_label = 'Percentage of all risk words', num_to_plot = 7, skip63 = True)

# only verbal risk words
verbalrisks = surgeon(riskwords.results, r'^\(v.*') #keep any token with tag starting with 'v'
plotter('Verbal risk words', verbalrisks, fract_of = allwords.totals, 
    y_label = 'Percentage of all words', num_to_plot = 6, skip63 = True)

# <markdowncell>
# Note the warning you'll receive if you specify an interrogation, rather than a results list.

# <headingcell level=3>
# merger()

# <markdowncell>
# `merger()` is for merging items in a list. Like `surgeon()`, it duplicates the old list. Its arguments are:

# 1. the list you want to modify
# 2. the indices of results you want to merge, or a regex to match
# 3. newname = *str/int/False*: 
#   * if string, the string becomes the merged item name.
#   * if integer, the merged entry takes the name of the item indexed with the integer.
#   * if not specified/False, the most most frequent item in the list becomes the name.

# <codecell>
low_high_combined = merger(lowhighrisks.results, [0, 2],  newname = 'high/higher risk')
plotter('Low and high risks', low_high_combined.results)

# <markdowncell>


# <headingcell level=4>
# Diversity of risk words

# <markdowncell>
# It's important to note that the kind of results we generate are hackable. Using some straight Python, combined with `merger()`, we can figure out how unique risk words appear in the NYT each year.

# To do this, we can take `riskwords.results`, duplicate it, and change every count over 0 into 1.

# <codecell>
import copy
all_ones = copy.deepcopy(riskwords.results)
for entry in all_ones:
    for tup in entry[1:]:
        if tup[1] > 0:
            tup[1] = 1

# <markdowncell>
We can then use `merger()` to merge every entry. This will tell use how many unique words there are each year.

# <codecell>
# this generates heaps of output, so let's clear it
mergedresults = merger(all_ones.results, r'.*', newname = 'Different risk words')
clear_output()

# <codecell>
# you could also use mergedresults.results[0]
plotter('Diversity of risk words', mergedresults.totals, 
    skip63 = True, y_label = 'Unique risk words')

# <markdowncell>
# So, we can see a generally upward trajectory, with more risk words constantly being used. Many of these results appear once, however, and many are nonwords. *Can you figure out how to remove words that appear only once per year?*

# <headingcell level=3>
# conc()

# <markdowncell>
# `conc()` produces concordances of a subcorpus based on a Tregex query. Its main arguments are:

# 1. A subcorpus to search *(remember to put it in quotation marks!)*
# 2. A Tregex query

# <codecell>
# here, we use a subcorpus of politics articles,
# rather than the total annual editions.
lines = conc('data/nyt/trees/politics/1999', r'/JJ.?/ << /(?i).?\brisk.?\b/') # adj containing a risk word

# <markdowncell>
# You can set `conc()` to print *n* random concordances with the *random = n* parameter. You can also store the output to a variable for further searching.

# <codecell>
lines = randoms = conc('data/nyt/trees/years/2007', r'/VB.?/ < /(?i).?\brisk.?\b/', random = 25)

# <markdowncell>
# `conc()` takes another argument, window, which alters the amount of co-text appearing either side of the match. The default is 50 characters

# <codecell>
lines = conc('data/nyt/trees/health/2013', r'/VB.?/ << /(?i).?\brisk.?\b/', random = 25, window = 20)

# <markdowncell>
# `conc()` also allows you to view parse trees. By default, it's false:

# <codecell>
lines = conc('data/nyt/trees/years/2013', r'/VB.?/ < /(?i)\btrad.?/', trees = True)

# <markdowncell>
# The final `conc()` argument is a *csv = 'filename'*, which will produce a tab-separated spreadsheet with the results of your query. You can copy and paste this data into Excel.

# <codecell>
lines = conc('data/nyt/trees/years/2005', r'/JJ.?/ < /(?i).?\brisk.?/ > (NP <<# /(?i)invest.?/)',
    window = 30, trees = False, csvmake = 'concordances.csv')

# <codecell>
! cat 'concordances.csv'
# and to delete it:
# ! rm 'concordances.txt'

# <headingcell level=3>
# Keywords, ngrams and collocates

# <markdowncell>
# There are also functions for keywording, ngramming and collocation. Each can take a number of kinds of input data:

# 1. a path to a subcorpus (of either parse trees or raw text)
# 2. a path to a csv file generated with `conc()`
# 3. a string of text
# 4. a list of strings (i.e. output from `conc()`) 

# `keywords()` produces both keywords and ngrams. It relies on code from the [Spindle](http://openspires.oucs.ox.ac.uk/spindle/) project.

# <codecell>
keys, ngrams = keywords('concordances.csv')
for key in keys[:10]:
    print key
for ngram in ngrams:
    print ngram

# <codecell>
colls = collocates('data/nyt/years/1989')
for coll in colls:
    print coll

# <markdowncell>
# With the `collocates()` function, you can specify the maximum distance at which two tokens will be considered collocates.

# <codecell>
colls = collocates('concordances.csv', window = 2)
for coll in colls:
    print coll

# <headingcell level=3>
# quicktree() and searchtree()

# <markdowncell>
# The two functions are useful for visualising and searching individual syntax trees. They have proven useful as a way to practice your Tregex queries.

# The easiest place to get a parse tree is from a CSV file generated using `conc()` with *trees* set to *True*. Alternatively, you can open files in the data directory directly.

# `quicktree()` generates a visual representation of a parse tree. Here's one from 1989:

# <codecell>
tree = '(ROOT (S (NP (NN Pre-conviction) (NN attachment)) (VP (VBZ carries) (PP (IN with) (NP (PRP it))) (NP (NP (DT the) (JJ obvious) (NN risk)) (PP (IN of) (S (VP (VBG imposing) (NP (JJ drastic) (NN punishment)) (PP (IN before) (NP (NN conviction)))))))) (. .)))'
quicktree(tree)

# <markdowncell>
# `searchtree()` requires a tree and a Tregex query. It will return a list of query matches.

# <codecell>
print searchtree(tree, r'/VB.?/ >># (VP $ NP)')
print searchtree(tree, r'NP')

# <headingcell level=3>
# Process types
# <codecell>
from dictionaries.process_types import processes
print processes.relational
print processes.verbal

# <markdowncell>
# We can use these in our Tregex queries to look for the kinds of processes participant risks are involved in. First, let's get a count for all processes with risk participants:

# <codecell>
query = r'/VB.?/ < /%s/ ># (VP ( < (NP <<# /(?i).?\brisk.?/)))' % processes.relational
relationals = interrogator(annual_trees, '-t', query, lemmatise = True)

# <codecell>
plotter('Relational processes', relationals.results, fract_of = proc_w_risk_part.totals)

# <headingcell level=3>
# Proper nouns and risk sentences

# <markdowncell>
# We searched to find the most common proper noun strings.

# `interrogator()`'s *titlefilter* option removes common titles, first names and determiners to make for more accurate counts. It is useful when the results being returned are groups/phrases, rather than single words.

# <codecell>
# Most common proper noun phrases
query = r'NP <# NNP >> (ROOT << /(?i).?\brisk.?\b/)'
propernouns = interrogator(annual_trees, '-t', query, 
    titlefilter = True)

# <codecell>
plotter('Most common proper noun phrases', propernouns.results, fract_of = propernouns.totals)
# <codecell>
quickview(propernouns.results, n = 200)

# <markdowncell>
# Notice that there are a few entries here that refer to the same group. (f.d.a and food and drug administration, for example). We can use `merger()` to fix these.

# <codecell>
# indices change after merger, remember, so
# make sure you quickview results after every merge.
merged_propernouns = merger(propernouns.results, [13, 20])
merged_propernouns = merger(merged_propernouns, [8, 32])
merged_propernouns = merger(merged_propernouns, [42, 107])
merged_propernouns = merger(merged_propernouns, [60, 111])
merged_propernouns = merger(merged_propernouns, [183, 197])
merged_propernouns = merger(merged_propernouns, [65, 127])
merged_propernouns = merger(merged_propernouns, [84, 149], newname = 149)
merged_propernouns = merger(merged_propernouns, [23, 130])
quickview(merged_propernouns, n = 200)

# <markdowncell>
# Now that we've merged some common results, we can use `surgeon()` to build some basic thematic categories.

# <codecell>
# make some new thematic lists
people = surgeon(merged_propernouns, r'(?i)^\b(bush|clinton|obama|greenspan|gore|johnson|mccain|romney'
    r'|kennedy|giuliani|reagan)$\b')
nations = surgeon(merged_propernouns, r'(?i)^\b(iraq|china|america|israel|russia|japan|frace|germany|iran\
|britain|u\.s\.|afghanistan|australia|canada|spain|mexico|pakistan|soviet union|india)$\b')
geopol = surgeon(merged_propernouns, r'(?i)^\b(middle east|asia|europe|america|soviet union|european union)$\b')
#usplaces = surgeon(merged_propernouns, r'(?i)^\b(new york|washington|wall street|california|manhattan\
#|new york city|new jersey|north korea|italy|greece|bosniaboston|los angeles|broadway|texas)$\b',\)
companies = surgeon(merged_propernouns, r'(?i)^\b(merck|avandia\
|citigroup|pfizer|bayer|enron|apple|microsoft|empire)$\b')
organisations = surgeon(merged_propernouns, r'(?i)^\b((white house|congress|federal reserve|nasa|pentagon)\b|'
    r'f\.d\.a\.|c\.i\.a\.|f\.b\.i\.|e\.p\.a\.)$')
medical = surgeon(merged_propernouns, r'(?i)^\b(vioxx|aids|celebrex|f.d.a)\b')
# geopol[5][0] == u'e.u.'

# <codecell>
# plot some results
plotter('People', people, fract_of = propernouns.totals, 
        y_label = 'Percentage of all proper noun groups', skip63 = True)

plotter('Nations', nations, fract_of = propernouns.totals, 
        y_label = 'Percentage of all proper noun groups', skip63 = True)

plotter('Geopolitical entities', geopol, fract_of = propernouns.totals,  
        y_label = 'Percentage of all proper noun groups', skip63 = False)

plotter('Companies', companies, fract_of = propernouns.totals, 
        y_label = 'Percentage of all proper noun groups', skip63 = True)

plotter('Organisations', organisations, fract_of = propernouns.totals, 
        y_label = 'Percentage of all proper noun groups', skip63 = True)

plotter('Medicine', medical, fract_of = propernouns.totals, num_to_plot = 4,
        y_label = 'Percentage of all proper noun groups', skip63 = True, save = True,)


# <markdowncell>

# These charts reveal some interesting patterns.

# * We can clearly see presidencies and rival candidates come and go
# * Similarly, the wars in Iraq and Afghanistan are easy to spot
# * Naturally, the Soviet Union is a very frequent topic in 1963. It rises in frequency until its collapse. More recently, Russia can be seen as more frequently co-occurring with risk words.
# * The Eurozone crisis is visible
# * From the Organisations and Things, we can see the appearance of Merck and Vioxx in 2004, as well as Empire...

# <codecell>
vioxx = surgeon(propernouns.results, r'(?i)^\b(vioxx|merck)\b$')
plotter('Merck and Vioxx', vioxx, fract_of = propernouns.totals, skip63 = True)
plotter('Merck and Vioxx', vioxx, fract_of = propernouns.totals, yearspan = [1998,2012])

# <markdowncell>
# Vioxx was removed from shelves following the discovery that it increased the risk of heart attack. It's interesting how even though terrorism and war may come to mind when thinking of *risk* in the past 15 years, this health topic is easily more prominent in the data.

# <headingcell level=2>
# Free play

# <markdowncell>
# 
# <headingcell level=2>
# Wrap up

# <markdowncell>
# 