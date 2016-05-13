---
title: "Interrogate"
tags: [interrogate, writing-queries, python, sfl]
keywords: interrogation, gui, corpkit
summary: "This tab provides the main means of searching your corpus for lexical and grammatical patterns."
last_updated: 2015-09-01
---

{% include linkrefs.html %}

## Selecting a corpus

If you were working in the `Build` tab, *corpkit* will try to guess the corpus you want to interrogate. If a corpus hasn't been selected, or you'd like to interrogate a different corpus, you can select it now. Corpora can also be selected via the menu.

Your choice of an unparsed, tokenised or parsed corpus will restrict the kinds of searches that are available to you.

## Selecting something to search

*corpkit* is designed to deal with *parsed* corpora. As such, you can search many more things than simply the text itself. Options here will be enabled or disabled depending on whether or not the corpus selected is parsed, tokenised, or plaintext. The most options are available when working with parsed corpora. Currently, you can search:

| Search           | Description |
|------------------------|---------------------------------------------------|
| `Trees` | Search parse trees using Tregex syntax
| `Words`      | Words/tokens as they originally appeared in the text          |
| `Lemma`      | Search lemmatised forms of each token      |
| `POS`      |  Search by part-of-speech tag      |
| `Function` | Find tokens by their dependency function |
| `Index`      | Search by position in sentence ('1' is the leftmost, etc)       |
| `Governors`  | Match governor token (locating dependent) | 
| `Dependents`  | Match dependent token (locating governor) | 
| `N-grams`      | Find n-grams/clusters (**deprecated!**)       |
| `Stats` | Get general stats (number of tokens, clauses, etc.) | 

### Adding criteria

You can use the `plus` button to search by multiple criteria. When you have multiple criteria, you need to decide between a search where every match is shown, or where only tokens matching all criteria are shown.

## Tree querying

If you have elected to search `Trees`, you'll need to write a *Tregex query*. Tregex is a language for searching syntax trees like this one:

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/const-grammar.png"  height="400" width="400"/>
</p>

To write a Tregex query, you specify **words and/or tags** you want to match, in combination with **operators** that link them together. First, let's understand the Tregex syntax.

To match any adjective, you can simply write:

> `JJ`

with `JJ` representing adjective as per the [Penn Treebank tagset](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html). If you want to get NPs containing adjectives, you might use:

> `NP < JJ`
 
where `<` means `with a child/immediately below`. These operators can be reversed: If we wanted to show the adjectives within NPs only, we could use:

> `JJ > NP`

It's good to remember that **the output will always be the left-most part of your query**.

If you only want to match Subject NPs, you can use bracketting, and the `$` operator, which means `sister/directly to the left/right of`:

> `JJ > (NP $ VP)`

In this way, you build more complex queries, which can extent all the way from a sentence's *root* to particular tokens. The query below, for example, finds adjectives modifying `book`:

> `JJ > (NP <<# /book/)`

Notice that here, we have a different kind of operator. The `<<` operator means that the node on the right does not need to be a child, but can be a descendent. the `#` means `head`&mdash;that is, in SFL, it matches the `Thing` in a Nominal Group.

If we wanted to also match `magazine` or `newspaper`, there are a few different approaches. One way would be to use `|` as an operator meaning `or`:

> `JJ > (NP ( <<# /book/ | <<# /magazine/ | <<# /newspaper/))`

This can be cumbersome, however. Instead, we could use a [*Regular Expression*](http://www.regular-expressions.info):

> `JJ > (NP <<# /^(book|newspaper|magazine)s*$/)`

Though it is unfortunately beyond the scope of this guide to teach Regular Expressions, it is important to note that Regular Expressions are extremely powerful ways of searching text, and are invaluable for any linguist interested in digital datasets.

Detailed documentation for Tregex usage (with more complex queries and operators) can be found [here](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html). If you want to learn Regular Expressions, there are hundreds of free resources online, including [Regular Expression Crosswords](http://regexcrossword.com/)!

{{tip}}If your searches aren't matching what you think they should, you might want to look at how your data has been parsed. Head to the <code>Build</code> tab and select your parsed corpus. You can then open up a file, and view its parse trees. These visualisations make it much easier to understand how Tregex queries work.{{end}}

### Tree searching options
 
When searching with trees, there are a few extra options available.

`Multiword results` informs *corpkit* that you expect your results to be more than one word long (if you are searching for VPs, for example). This causes *corpkit* to do tokenisation of results, leading to overall better processing.

When working with multiple word results, `Filter titles` will remove `Mr`, `Mrs`, `Dr`, etc. to help normalise and count references to specific people.

### Dependencies

When you search `Words`, `Lemma`, `Function`, `Index` or `POS`, 'Governor' *corpkit* will be interrogating dependency parses.

In dependency grammar, words in sentences are connected in a series of governor--dependent relationships. The Predicator is typically the `root` of a sentence, which may have the head of the Subject as a dependent. The head of the subject may in turn have dependants, such as adjectival modifiers or determiners.

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/dep-grammar.png"  height="60" width="400"/>
</p>

The best source of information on CoreNLP's dependency relationships is the [Stanford Dependencies manual](http://nlp.stanford.edu/software/dependencies_manual.pdf).

### Choosing what to search

When writing queries for dependencies, you can either use Regular Expressions or a list of words. To use a list, either use the `Schemes` &rarr; `Wordlists` feature, or simply write our a list manually, using square brackets and commas:

> `[cat,dog,fish]`

Using regular expressions, you could do something more complex, like get both the singular and plural forms:

> `(cats?|dogs?|fish)`

### Multiple search criteria 

When searching dependencies, a plus button beside the query entry box becomes clickable. If you click this, you are given space to add multiple query components. For example, if you wanted to count *help* as a verb, you might create search for `help` as lemma, and `^V` as POS (which will match any verbal POS tag). Use the plus and minus buttons to create or remove criteria. You can also choose between matching *any* of the criteria, or matching *all* of them.

### Dependency grammars

Your data has actually been annotated with three slightly different dependency grammars. You can choose to work with:

1. Basic dependencies
2. Collapsed dependencies
3. Collapsed dependencies with conjunctions collapsed too

For more information on the dependency grammars, you can look at Section 4 of the [Stanford Dependencies manual](http://nlp.stanford.edu/software/dependencies_manual.pdf#page=12).


## What to return

In the middle of the `Interrogate` tab is daunting grid of *return values*. These are responsible for controlling how the search results are returned to you. Often, multiple values can be selected simultaneously.

There are five rows of return types. Here, you specify **the relationship between the thing being searched for and the thing being shown**.

The `Match` row simply gets the search result. The `Dependent` gets its Dependent (if it has one), and the `Governor` row gets the `Governor`. `N-grams` means that you want to get multiword units containing the match.

For each of these rows, you can specify which of its attributes you would like displayed. You can show the token itself, its lemma form, its POS or its dependency function.

The final row, `Other`, is a little different. `Count` simply returns the total number of results. `Index` returns its position within a sentence. `Distance` calculates the number of links between the token and the root of the dependency parse. `Tree` shows a bracketted syntax tree.

Some options become disabled when they aren't possible. When searching trees, for example, you can't access governor and dependent information.

### Tree return values

When you're searching trees, a reduced set of return values are available. For the following sentence:

> `These are prosperous times.`

you could write a query:

> "`JJ < __`"

This would match the adjective `prosperous`. You could return it in the following ways:

| Search type       | Output      |
|--------|--------|
| Match: Word       | `prosperous`       |
| Match: Lemma       | `prosperous`       |
| Match: POS       |  `JJ`      |
| Match: Word, POS       | `prosperous/JJ`       |
| Tree       | `(JJ prosperous)`       |
| Count       | `1` (added to total)       |

### Dependency return values

When searching dependencies, you can ask *corpkit* to return words, lemmata, parts of speech, and so on. You can also return *functions*, *governors*, *dependents*, *indexes* or *distances from root*. If you select multiple return options, you'll get them joined together with a slash.

### Dependency examples

It's probably useful at this point to see some examples of what kinds of queries return what kinds of output.

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/dep-grammar.png"  height="60" width="400"/>
</p><br>

So, to give some examples of output based on the sentence above:

| Search  | Query  | Return | Exclude | Output |
|---|---:|---:|---:|---:|---:|
| <code>Function</code>  | `lead\b`  | <code>Match: Function</code> |   |  <b>`dobj`</b>  |
| <code>Function</code>  | `LIST:CLOSEDCLASS`  | <code>Match: Function</code> | | <b>`nsubj`, `aux`, `mark`, `nmod:poss`</b>  |
| <code>Function</code> | `any`  | <code>Match: Lemma</code> | <code>Function: (aux&#124;root&#124;.comp)</code>   | <b>`would`, `try`, `follow`</b>  |
| <code>Function</code>  | `LIST:PARTICIPANT_ROLE`  | <code>Match: Word</code> |   | <b>`I`</b>, <b>`lead`</b>  |
| <code>Function</code>  | `LIST:PARTICIPANT_ROLE`  | <code>Match: Word</code> | `POS: ^[^P]`  | <b>`I`</b> |
| <code>Words</code> | `^to$` | <code>Distance</code> |  | <b>2</b>  |
| <code>Lemmata</code>  | `follow`  | <code>Match: Function</code>, <code>Dependent: W ord</code> |  | <b>`to`, `lead`</b>  |
| <code>Lemmata</code>  | `follow`  | <code>Dependent: Lemma</code>  | `Words: LIST:CLOSEDCLASS`  | <b>`lead`</b>  |
| <code>Words</code> | <code>^(would&#124;will&#124;wo)</code> | <code>Match: Function</code>, <code>Governor: word</code>   |  |  <b>`aux/try` </b>  |
| <code>Function</code> | <code>(dobj&#124;nsubj)</code>  | <code>Governor: Word</code> | |  <b>`try`, `follow`</b>   |

Note that only one search criterion and exclude criterion are given here. You can use the plus buttons to add more, increasing the specificity with which you can interrogate the corpus.

### Plain text

When the selected corpus is plain text files, you have the option of searching for words or lemmata, using either regular expressions or wordlists:

> `(cats?|dogs?|fish)`

> `[cat,cats,dog,dogs,fish]`

Plain text searching is language independent, but otherwise not very powerful. Lemmatisation, for example, will not work very well, because *corpkit* won't know the word classes of the words you're finding.

In the `Preferences` pane, you can turn regular expression mode for plaintext corpora off. Then, you'll just be searching for string of characters.

### Tokenised corpora

If a tokenised corpus is selected, you can search for words, lemmata or n-grams.

As with plain text, you can use either a list or a regular expression to match tokens.

An additional option, however, is `N-grams`. When this option is selected, you can leave the query blank to get all n-grams, or add a word or regex that must be in the n-gram in order for it to be counted. The behaviour is the same as when getting n-grams via trees.

{{note}} The `Plaintext` and `Tokenise` options are currently functional, but there are currently limited options available for working with them. More will be in development, especially for tokenised corpora. {{end}}

## Preset queries

Below the query box, there is a dropdown list of preset queries. `'Any'` will match any word, tag or function, depending on the search type. `Participants` and `Processes` approximate notions from systemic functional grammar.

{{tip}} One of the first things you might like to do with your data is calculate the total number of tokens in each subcorpus. The easiest way to do this is to use the <code>Count tokens</code> option in the <code>Trees</code> search type, and to select <code>Any</code> as the preset query. You can then use this data, in combination with a different interrogation, to calculate the relative frequencies of specific words in the corpus. See <a href="doc_edit.html"><i>Edit</i></a> for more details.{{end}}

`Stats` will get the absolute frequencies for general features (number of sentences, clauses, tokens) different moods (imperatives, declaratives, interrogatives) and process types (verbal, relational, mental). It involves many sub-interrogations, and may take a long time.

## Wordlists

*corpkit* also ships with a number of different lists of words or dependency roles that can be added into queries. The query below will match any of the closed class words in a predefined list of closed-class words, called `CLOSEDCLASS`:

> `LIST:CLOSEDCLASS`

This can be powerful when used in conjunction with Tregex or dependency queries. The query below will get any predicator matching a list of mental processes:

> `VP <<# /LIST:MENTAL/ $ NP`

{{tip}} When using special queries inside Tregex queries, always remember to wrap the special query in slashes. <code>"/VB.?/ < /LIST:MENTAL/"</code> will work, but <code>"/VB.?/ < LIST:MENTAL"</code> will not. {{end}}

These wordlists can be used in various places in *corpkit*. If you want to remove closed class words from your n-gram search, you can enter `LIST:CLOSEDCLASS` in the `Exclude` field and select `Words`, or define a list of POS tags you don't want to count (i.e. `[DT,IN,CC,PRP]`) and select `POS`. 

### Creating and modifying wordlists

If you select `Schemes` &rarr; `Wordlists` from the menu bar, you can define your own wordlists, or edit existing lists. To make a new list, simply enter words of interest (or paste them in from another file, one per line), give the list a name, and hit `Store`. You can then use this wordlist in a query with the  `LIST:NAME` syntax.

You can easily select a predefined list, modify and rename it, and access it via `LIST:NAME`. The `Get inflections` buttons will help you make queries that match all possible forms of the lemmata of interest. You can highlight particular words to get inflections for, or leave the text box unselected in order to inflect every word.

Custom wordlists can be stored to memory or, saved to your project under a chosen name. Predefined lists will be highlighted in yellow, unsaved lists in red, and saved in green.

{{tip}} Custom wordlists are stored in <code>`project/custom_wordlists.txt`</code>. You can open up these files and alter them if need be. So long as you respect the file's syntax, the wordlist will be loaded when you open the project. {{end}}

## Lemmatisation

When working with dependencies, lemmatisation is handled by *Stanford CoreNLP*, and is very accurate. When searching trees, *WordNet* is used. In order to work properly, WordNet-based lemmatisation needs to know the part of speech of the word it's lemmatising.

If searching trees and using lemmatisation, *corpkit* will try to determine the word class you're searching for by looking at the first part of your Tregex query. If your query is:

> <code>/<b>V</b>B.?/ >> VP</code>

then *corpkit* will know that the output will be verbs, based on the initial `V`. If lemmatisation of trees isn't working as expected, you can use the `Result word class` option to force *corpkit* to treat all results as a given part of speech.

## Speaker IDs

If you have used the `Speaker segmentation` option, you can restrict your searches to specific speakers. You can use `shift+click` or `ctrl+click` to select multiple speaker IDs. Speaker IDs may slow down tree-based searching quite a lot, so if you don't care too much about them, leave the option as `False`, rather than `ALL`.

If you have selected `ALL` speakers, or have highlighted more than one, multiple interrogations will be performed, with the speaker ID appended to the interrogation name. Only one of these results will be shown as a spreadsheet, but you can use `Previous` and `Next` to navigate between them.

## Naming an interrogation

You are given the option of naming your interrogation. You don't *have to* to do this, but it will help you keep track of which interrogations contain which kinds of data.

If you forgot to name an interrogation before running it, you can head to the `Manage project` window via the Menu to rename it at any time.

## Running interrogations

On large datasets, interrogations can take some time, especially for dependency searches with many options. Speaker IDs also come at the cost of speed. Be patient!

Be sure to name your interrogation, via the `Name interrogation` box. This makes it much easier to know at a glance what you'll be editing, plotting or exporting.

{{tip}} Whenever you run an interrogation that produces results, all options used to generate the query are stored, and accessible via <code>Manage project</code> in the Menu. You can head there to access previous queries, or to save interrogations to disk. {{end}}

Running an interrogation creates both a spreadsheet-style display of frequencies and a concordance, which can be viewed in the `Concordance` pane. If you don't need the concordances, you can turn them off in the `Preferences` pane. This may speed up slow interrogations.

{{note}} Some types of interrogation do not produce concordance lines. Two examples of this are when you search for corpus stats, or when you return counts. {{end}}


## Editing spreadsheets

Once results have been generated, the spreadsheets on the right are populated. Here, you can edit numbers, move columns, or delete particular results or subcorpora. You can flip back and forward between other interrogations with the `Previous` and `Next` buttons.

If you manually edit the results in either the results or totals spreadsheet, you can hit `Update interrogation` to update the version of the data that is stored in memory.

It's important to remember that the results and totals spreadsheets do not communicate with one another. As such, if you are adding or subtracting from individual results, you'd need to update the total results part to reflect these changes. 

{{tip}} Sorting the result order is performed in the <code>Edit</code> tab.{{end}}

## Making dictionaries

If you want, you can use the `Save as dictionary` button to generate a reference corpus from an interrogation, comprised of each word and its total frequency. This will be stored in the `dictionaries/` folder of the project. Every dictionary file in this directory can be loaded when doing keywording in the `Edit` tab.

## Treating files as subcorpora

If you have a corpus with no subdirectories, but a number of files, you may wish to treat each file as a subcorpus. To do this, go to the `Preferences` window and select `Files as subcorpora`. If your corpus has subcorpora and files, and you use this option, the search will ignore the subcorpora.

## Next steps

It can be hard to learn anything interesting from absolute frequencies alone. Generally, you'll next want to go to the `Edit` tab to modify the results into something more informative. Or, go and check out your results in context via the `Concordance` tab.
