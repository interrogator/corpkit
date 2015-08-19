# corpkit graphical interface:
### users' guide (under construction)

### Daniel McDONALD

<!-- MarkdownTOC -->

- [Build](#build)
    - [Creating a project](#creating-a-project)
    - [Editing your data](#editing-your-data)
    - [Parsing](#parsing)
- [Interrogate](#interrogate)
    - [Selecting a corpus](#selecting-a-corpus)
    - [Selecting a kind of data](#selecting-a-kind-of-data)
    - [Writing queries](#writing-queries)
    - [Search ptions](#search-ptions)
    - [Running interrogations](#running-interrogations)
    - [Editing spreadsheets](#editing-spreadsheets)
- [Edit](#edit)
    - [Selecting data to edit](#selecting-data-to-edit)
    - [Operations and denominators](#operations-and-denominators)
    - [Skipping, keeping, merging](#skipping-keeping-merging)
    - [Sorting](#sorting)
- [Visualise](#visualise)
- [Concordance](#concordance)
    - [Editing concordance lines](#editing-concordance-lines)
    - [Sorting](#sorting-1)
    - [Exporting concordance lines](#exporting-concordance-lines)
- [Manage](#manage)
- [Help](#help)
- [Settings](#settings)
- [Updates](#updates)
- [Forthcoming features](#forthcoming-features)
- [Where to go from here](#where-to-go-from-here)
- [Helping out](#helping-out)

<!-- /MarkdownTOC -->

> This work-in-progress document outlines the basic functionality of the `corpkit` graphical interface. More information coming soon.

## Build

> This tab is for starting projects, and building corpora from plain text files.

### Creating a project

The best way to begin is by creating a project---that is, a folder, with subfolders for saved interrogations, images, dictionaries and data.

Once you have created a new project, you can use `Add corpus` to copy your corpus into the project directory.

Much of the power of `corpkit` is its ability to handle *structured corpora*---that is, folders containing subfolders, representing points in time, speaker names, topics, etc. Ideally, the corpora you add to your project have some kind of structure, but if not, the tool will still work.

Once you have added a corpus to the project, it is automatically selected. If you want to add another corpus, or select a previously added corpus, you can.

### Editing your data

With a corpus selected, you can view and edit the text files in your collection. You can make last-minute changes to the corpus now: after the texts are parsed, they are very difficult to change.

> This interface is not designed for a serious amount of editing work. For large amounts of editing, use a good text editor, like [*Sublime Text*](http://www.sublimetext.com) or [*TextWrangler*](www.barebones.com/products/textwrangler).

### Parsing

Parsing requires the one-time installation of a parser, as well as some things needed to run the parser. Follow the prompts to download and install it. If you want to remove it at any stage, it can be found in your `home` directory as `corenlp`.

Once texts are parsed, there is one more feature you might like to use. If you use `Select corpus in project` to select a corpus of parsed texts, rather than editing the file contents, you can look at visualisations of the parse trees. This can be helpful in learning how to write a Tregex query (see below).

> Some features of `corpkit` work without parsing, but parsing is the best way to find complex and interesting things in your data.

## Interrogate

> `Interrogate` will iterate over subcorpora in a corpus, searching for the same thing, and tabulating the results.

### Selecting a corpus

If the corpus you want to analyse is not already selected, you can select it now.

### Selecting a kind of data

`corpkit` can presently work with three kinds of data:

1. Constituency parse trees
2. Dependency parses
3. Plain text

The first two can both be found inside the parsed version of a corpus. The third is the unparsed version of the corpus.

When you select a kind of data, the kinds of search that are available to you change.

### Writing queries

Depending on the kind of data you want to search, you need to write different kinds of queries.

#### Trees

If you want to search for information in `trees`, you need to write a Tregex query. Tregex is a language for searching syntax trees.

> Image here

Tregex queries also rely on [*Regular Expressions*](http://www.regular-expressions.info): a kind of extended search language. Though it is unfortunately beyond the scope of this guide to teach Regular Expressions, it is important to note that Regular Expressions are extremely powerful 

Detailed documentation for Tregex usage can be found [here](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html).

#### Dependencies

In dependency grammar, words in sentences are connected in a series of governor--dependent relationships. The Predicator is typically the `root` of a sentence, which may have the head of the Subject as a dependent. The head of the subject may in turn have dependants, such as adjectival modifiers or determiners.

> Image here

#### Plain text

Plain text is the simplest kind of search. You can either use Regular Expressions or simple search. When writing simple queries, you can search for a list of words by entering:

> `[cat,dog,fish]`

Using regular expressions, you could do something more complex, like get both the singular and plural forms:

> `(cats?|dogs?|fish)`

This kind of search has drawbacks, though. Lemmatisation, for example, will not work very well, because `corpkit` won't know the word classes of the words you're finding.

#### Special queries

`corpkit` also has some pre-programmed queries and query parts, based around concepts from systemic-functional grammar.

##### Preset queries

`'Any'` will match any word, tag or function, depending on the search type.

##### Query parts

There are also some things you can type into your query that `corpkit` recognises and handles differently. You can, for example, enter

> `PROCESSES:VERBAL`

to match any token corresponding to a verbal process (including all possible inflections). This can be powerful when used in conjunction with Tregex or dependency queries:

> `VP <<# /PROCESSES:MENTAL/ $ NP`
 
will get verbal groups that contain mental process types.

Currently, the special query types are:

| Special query kind | Matches           |
|--------------------|-------------------|
| `PROCESSES:`        | Tokens            |
| `ROLES:`            | CoreNLP functions |
| `WORDLISTS:`        | Tokens            |

* `WORDLISTS:` recognises `PRONOUNS`, `ARTICLES`, `CONJUNCTIONS`, `DETERMINERS`, `PREPOSITIONS`, `CONNECTORS`, `MODALS`, `CLOSEDCLASS` and `TITLES`.
* `ROLES:` recognises `ACTOR`, `ADJUNCT`, `AUXILIARY`, `CIRCUMSTANCE`, `CLASSIFIER`, `COMPLEMENT`, `DEICTIC`, `EPITHET`, `EVENT`, `EXISTENTIAL`, `GOAL`, `MODAL`, `NUMERATIVE`, `PARTICIPANT`, `PARTICIPANT1`, `PARTICIPANT2`, `POLARITY`, `PREDICATOR`, `PROCESS`, `QUALIFIER`, `SUBJECT`, `TEXTUAL` and `THING`.
* `PROCESSES:` recognises `MENTAL`, `VERBAL` and `RELATIONAL`.

When using dependencies, you could get *Sensers* by searching for the role and dependent of `PROCESSES:MENTAL`, and then by using a function filter for `ROLES:PARTICIPANT1`.

### Search ptions

The `Interrogate` tab has many options.

| Option             | Purpose                                                                            |
|--------------------|------------------------------------------------------------------------------------|
| Filter titles      | Remove Mr, Mrs, Dr, etc. to help normalise and count references to specific people |
| Multiword results  |    If each result can be more than one word, this tokenises the results for better processing     |
| Function filter    | Match only words filling specific dependency roles (regular expression)                                                      |
| POS filter         | Match only words with specific POS in dependency queries (regex)   |
| Normalise spelling | Convert between UK and US English     |
| Dependency type    | Which dependency grammar to use (see [here](http://nlp.stanford.edu/software/example.xml) for info)     |

#### Lemmatisation

When working with dependencies, lemmatisation is handled by Stanford CoreNLP. When searching trees, WordNet is used.

If searching trees and using lemmatisation, `corpkit` will try to determine the word class you're searching for by looking at the first part of your Tregex query. If your query is:

> `/VB.?/ >> VP`

then `corpkit` will know that the output will be verbs. If lemmatisation of trees isn't working as expected, you can use the `Result word class` option to force `corpkit` to treat all results as a given part of speech.

### Running interrogations

On large datasets, interrogations can take some time, especially for dependency searches with many options. Be patient!

Be sure to name your interrogation, via the `Name interrogation` box. This makes it much easier to know at a glance what you'll be editing, plotting or exporting.

### Editing spreadsheets

Once results have been generated, the spreadsheets on the right are populated. Here, you can edit numbers, move columns, or delete particular results or subcorpora.

Once you've changed the results, you can hit `'Update interrogation'` to update the version of the data that is stored in memory.

It's important to remember that the results and totals spreadsheets do not communicate with one another. As such, if you are adding or subtracting from individual results, you'd need to update the total results part to reflect these changes. 

Sorting the result order is performed in the edit window (see below).

## Edit

> `Edit` allows you to manipulate results generated in the `interrogate` window, or to re-edit results generated with `edit`

### Selecting data to edit

You can select any interrogation or edited result to edit.

After this, you need to select a `branch`, either `results` or `totals`. These correspond to the two spreadsheets in the `Interrogate` tab.

### Operations and denominators

A common task is to turn absolute into relative frequencies. To do this, you simply select '%' as the operation, and `self` `totals` as the denominator. To calculate a radio, you could use '/'.

Because you can use any result/total as the denominator (provided it has the same subcorpora), you can calculate almost anything in your data. To figure out the ratio of nouns/clauses, you would perform two interrogations, and combine them here.

If you use a `results` branch as a denominator, things get a little more complex still. Rather than being divided by the total from that subcorpus, each entry will be divided by the total occurrences of that particular entry in the denominator data.

You could use this kind of edit to answer a question like:

    When sports are mentioned, what percentage of the time do the sports occur in subject position?

#### Keywording

If you select the `'keywords'` option, you can get log-likelihood keyness scores for the the dataset of interest, compared with the denominator as a reference corpus. When doing keywording, the reference corpus can be either a results branch of an interrogation, or the BNC, `'bnc.p'`.

Using `Self` `results` as denominator will determine which words are key in each subcorpus. Each subcorpus is dropped from the reference corpus in turn in order to calculate these values.

> Negative keywords exist, too: try sorting by inverse total to find out which words are uncommon in the target data.

### Skipping, keeping, merging

You can easily skip, keep or merge particular entries and subcorpora. For entries, you need to to write out some criteria. For subcorpora, you can select from the list.

When writing out entries to keep/remove/merge, you can supply either:

1. A regular expression to match: `^fr*iends?$` will match `fiend`, `fiends`, `friend` and `friends`.
2. A list: [fiend,fiends,friend,friends]

> Special queries work here, too. If you searched for process, you could keep only `PROCCESSES:VERBAL`.

If merging either subcorpora or entries, you may want to provide a new name for the merged item. By default, the first few entry names are joined together with slashes.

Merging entries is a powerful way to do thematic categorisation: you could merge the names of illnesses as `'Illnesses'`, and the names of treatments as `Treatments`. You could then edit the edited results, keeping only those two.

### Sorting

When working with multiple subcorpora, sorting becomes a very powerful feature of `corpkit`. Aside from very normal kinds of sorting (by total, by name), you can also sort by *increase*, *decrease*, *static* or *turbulent*. 

`corpkit` does this using [`Scipy`'s *linear regression* function](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.linregress.html). Essentially, a straight trend line is calculated for each entry in the data. By measuring the angle of this line, we can find out which results are increasingly or decreasingly used across the dataset.

If you tick `Keep stats`, you'll be able to see the `slope`, `intercept`, `stderr` and `p value`, where the null hypothesis is that there is no upward or downward slope. `Remove above p` will automatically exclude results not meeting the standard.

> You can use `Help --> Save log` after performing an edit to get some information about what was performed.

## Visualise

> `Visualise` is all about representing your results graphically

Most options here are self-explanatory. Pick the results you want to plot, play with some options, and hit `Plot`. This can be a great way to identify salient linguistic features in your dataset.

Note that `Number to plot` takes the top `n` entries from the results of interest. If you don't want these, go back to the `Edit` tab and remove/sort the results some more. You can type in 'all' to get every result---but be warned, this often won't look so good!

> Checking the `TeX` option will mean that the plotter will try to use `LaTeX` to typeset the text in the chart. If you have a TeX distribution, but this option isn't working for you, you may need to use the command-line version of `corpkit`.

Once you've plotted something, a navigation pane appears under the figure, allowing scrolling, zooming, saving and so forth.

> If you're more confortable generating visualisations in another tool, you can head to the `Manage` tab to export a CSV version of any interrogations or edited results. This can be imported into Excel, for example.

## Concordance

> Concordance provides a concordancer for constituency trees, dependency parses, or plain text.

Most features here are similar to those provided by other concordancers, such as `Window` and `Random`. The key difference is that you can search using Tregex patterns (other options are in development). This can be a good way to check that a query used to interrogate the corpus is finding what it's supposed to. `Trees` will output bracketted trees instead of plain text, which can be useful in learning how to make Tregex queries.

### Editing concordance lines

You can use `backspace` to delete selected lines, or `shift+backspace` to inverse-delete.

### Sorting

Sorting is always by the first character. `L1` sorts by the rightmost word in the left-hand column; `L2` sorts by the second rightmost. This is similar for the other columns. Sorting by `M-1` will sort by the last word in the middle column, and `M-2` by the second last. These options are useful if, for example, you are looking at the most common verbal groups in your data.

Clicking `Sort` again without making any other changes will invert the sort order.

### Exporting concordance lines

`Export` allows you to save results to CSV files, which can be loaded into Excel, or similar.

> Concordance lines are Pandas DataFrames. If you want to work from the command line, you can quickly output them to LaTeX tables, and all kinds of other cool things.

## Manage

> `Manage` allows you to manipulate your interrogations and edited data.

With `load saved interrogations`, you can load into memory any findings you saved in the project earlier. 

`Load project` will automatically set the path to data, dictionaries, images and saved interrogations. You can still select custom locations for these if you like.

If you select an interrogation and hit `View`, you can see all the options used to generate the result.

`Export` will create CSV files of results, totals and query options in a user-specified directory.

You can use `Remove` to remove one or more interrogations from memory, or `Delete` to remove saved results from the `saved_interrogations` directory of your project.

## Help

`corpkit` is still missing a lot of documentation. For now, when things go wrong, you can select `Help --> Save log` to generate a log file for your session. You can send this to developers to help diagnose the source of a problem.

## Settings

You can use `File --> Save project settings` to save some settings of your project.

## Updates

When you're connected to the web, `corpkit` will look for software updates, and prompt the user to download them. Major changes will be explicated when this occurs. You can also check for updates manually via the `file` menu.

## Forthcoming features

* More preset queries
* More systemic functional grammar
* Ability to easy edit special query lists
* User suggestions!

## Where to go from here

`corpkit` has a lot of functionality, and could probably keep you busy for a long time. If you ever find that the tools aren't intuitive, it is useful to remember that the major functions at work in the interface can also be called via the command line. Generally speaking, command line operation makes it possible to do far more complicated things with your data.

* When interrogating, you can quickly make lists of corpora or queries and perform each simultaneously. 
* When editing, you can create lists of entries to rename or merge.
* When plotting, you can generate HTML based visuals that are clickable, highlightable, embeddable, and so on.

If you're interested in trying out the command line interface, on OSX, you could simply enter `Terminal` and do:

```shell
sudo easy_install corpkit
python
```

to download and install `corpkit`, and then to enter Python. From there, you can import the main functions, and begin:

```python
>>> from corpkit import interrogator, editor, plotter, conc
>>> q = r'/NN.?/ >># NP'
>>> result = interrogator('path/to/corpus', 'word', lemmatise = True)
```

Because `corpkit` data is generally stored as [http://pandas.pydata.org/](Pandas) objects, from the command line it is easy to manipulate results in complex ways, with most of the functionality of `MATLAB` or `R`.

Command line operation of `corpkit` is presented in more detail at [https://www.github.com/interrogator/corpkit]().

## Helping out

`corpkit` is free and open-source. If you find bugs, want to request features, or have questions, you can visit the main repository at [https://github.com/interrogator/corpkit]() and interact with developers there via the `Issues` page. A *Gitter* chatroom is also available at [https://gitter.im/interrogator/corpkit](). If you're using `corpkit` in your research, feel free to cite it, share it, and tell the developers what you're working on.

If you know how to code, you're more than welcome to hack away at the tools however you wish.
