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

## Selecting a kind of data

*corpkit* can presently work with four kinds of data:

1. Constituency parse trees
2. Dependency parses
3. Plain text
4. Tokenised corpora

The first two can both be found inside the parsed version of a corpus. The third is the unparsed version of the corpus. The fourth is your corpus as a list of tokens, which can be created via the `Build` tab.

When you select a kind of data, the kinds of search that are available to you change, as do the kinds of queries that can be understood. These will be explained in the next secitons.

### Trees

If you want to search for information in `trees`, you need to write a Tregex query. Tregex is a language for searching syntax trees like this one:

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/const-grammar.png"  height="400" width="400"/>
</p>

To write a Tregex query, you specify **words and/or tags** you want to match, in combination with **operators** that link them together.

To match any adjective, you can simply write:

> `JJ`

If you want to get NPs containing adjectives, you might use:

> `NP < JJ`
 
Where `<` means `with a child/immediately below`. These operators can be reversed: If we wanted to show the adjectives within these NPs only, we could use:

> `JJ > NP`

It's good to remember that the output will always be the left-most part of your query.

If you only want to match Subject NPs, you can use bracketting, and the `$` operator, which means `sister/directly to the left/right of`:

> `JJ > (NP $ VP)`

In this way, you build more complex queries. The query below finds adjectives modifying `book`:

> `JJ > (NP <<# /book/)`

Notice that here, we have a different kind of operator. The `<<` operator means that the node on the right does not need to be a child, but can be a descendent. the `#` means `head`---that is, in SFL, it matches the `Thing` in a Nominal Group.

If we wanted to also match `magazine` or `newspaper`, there are a few different approaches. One way would be to use `|` as an operator meaning `or`:

> `JJ > (NP ( <<# /book/ | <<# /magazine/ | <<# /newspaper/))`

This can be cumbersome, however. Instead, we could use a [*Regular Expression*](http://www.regular-expressions.info):

> `JJ > (NP <<# /^(book|newspaper|magazine)s*$/)`

Though it is unfortunately beyond the scope of this guide to teach Regular Expressions, it is important to note that Regular Expressions are extremely powerful ways of searching text, and are invaluable for any linguist interested in digital datasets.

Detailed documentation for Tregex usage (with more complex queries and operators) can be found [here](http://nlp.stanford.edu/~manning/courses/ling289/Tregex.html). If you want to learn Regular Expressions, there are hundreds of free resources online, including [Regular Expression Crosswords](http://regexcrossword.com/)!

If your searches aren't matching what you think they should, you might want to look at how your data has been parsed. Head to the `Build` tab and select your parsed corpus. You can then open up a file, and view its parse trees. These visualisations make it much easier to understand how Tregex queries work.

#### Tree searching options
 
When searching with trees, there are a few extra options available.

`Multiword results` informs *corpkit* that you expect your results to be more than one word long (if you are searching for VPs, for example). This causes *corpkit* to do tokenisation of results, leading to overall better processing.

When working with multiple word results, `Filter titles` will remove `Mr`, `Mrs`, `Dr`, etc. to help normalise and count references to specific people.

### Dependencies

In dependency grammar, words in sentences are connected in a series of governor--dependent relationships. The Predicator is typically the `root` of a sentence, which may have the head of the Subject as a dependent. The head of the subject may in turn have dependants, such as adjectival modifiers or determiners.

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/dep-grammar.png"  height="60" width="400"/>
</p>

The best source of information and dependency relationships is the [Stanford Dependencies manual](http://nlp.stanford.edu/software/dependencies_manual.pdf).

#### Dependency grammars

Your data has actually been annotated with three slightly different dependency grammars. You can choose to work with:

1. Basic dependencies
2. Collapsed dependencies
3. Collapsed dependencies with conjunctions collapsed too

For more information on the dependency grammars, you can look at section 4 of the [Stanford Dependencies manual](http://nlp.stanford.edu/software/dependencies_manual.pdf#page=12).

#### Dependency search types

There are many potentially interesting things in dependency annotations, and, accordingly, many different kinds of search available for them. 

The different options match and print different combinations of *governors*, *dependents* and *relationships*. In each case, the kind of query you'll write is a Regular Expression or list.

Below is a basic explanation of what each kind of query matches, and what it outputs.

| Search type            | Query matches | Output                             |
|------------------------|----------|-----------------------------------------|
| Get role of match      | Token   |  Token's role                            |
| Get lemmata of match   | Token   |  Token's lemma form                      |
| Get tokens             | Token   |  Token                                   |
| Get tokens by role     | Role    |  Role's dependent                        |
| Get distance from root | Token   |  Number of steps away from root position |
| Get "role:dependent", matching governor  |  Governor  | role:dependent      |
| Get "role:governor", matching dependent  |  Dependent | role:governor       |


#### Dependency options

Dependency queries can also be filtered, so that only results matching a given role or part-of-speech are returned. Both of these fields are regular expressions or lists.

For the `role:governor` and `role:dependent` search options, if you use a function filter, the `role:` portion of the output is not printed.

<p align="center">
<img src="https://raw.githubusercontent.com/interrogator/sfl_corpling/master/images/dep-grammar.png"  height="60" width="400"/>
</p><br>

So, to give some examples of output based on the sentence above:

| Option  | Query  | Function filter  | POS filter  | Output |
|---|---:|---:|---:|---:|
| <i>Get role of match</i>  | `lead\b`  |   |   | <b>`dobj`</b>  |
| <i>Get role of match</i>  | `WORDLISTS:CLOSEDCLASS`  | | | <b>`nsubj`, `aux`, `mark`, `nmod:poss`</b>  |
| <i>Get tokens by role</i> | `any`  | <code>(aux&#124;root&#124;.comp)</code>  |   | <b>`would`, `try`, `follow`</b>  |
| <i>Get tokens by role</i>  | ROLES:PARTICIPANT  |   |   | <b>`I`, `lead`  |
| <i>Get tokens by role</i>  | ROLES:PARTICIPANT  |   | `^P`  | <b>`I`</b> |
| <i>Get distance from root</i> | `^to$` |   |   | <b>2</b>  |
| <i>Get "role:dependent"</i>  | `\bfollow.*`  |   |  | <b>`to`, `lead`</b>  |
| <i>Get "role:dependent"</i>  | `\bfollow.*`  |   | `^N.*`  | <b>`lead`</b>  |
| <i>Get "role:dependent"</i>  | `^tr`  |   | `MD`  | <b>`aux:would`</b>  |
| <i>Get "role:governor"</i> | <code>^(would&#124;will&#124;wo)</code> |    |    |  <b>`aux:try` </b>  |
| <i>Get "role:governor"</i> | `any` | <code>(dobj&#124;nsubj)</code>  |   |  <b>`try`, `follow`</b>   |

### Plain text

Plain text is the simplest kind of search. You can either use Regular Expressions or simple search. When writing simple queries, you can search for a list of words by entering:

> `[cat,dog,fish]`

Using regular expressions, you could do something more complex, like get both the singular and plural forms:

> `(cats?|dogs?|fish)`

This kind of search has drawbacks, though. Lemmatisation, for example, will not work very well, because *corpkit* won't know the word classes of the words you're finding.

### Tokens

As with plain text, you can use either a list of a regular expression to match tokens.

An additional option, however, is to *Get n-grams*. When this option is selected, you can leave the query blank to get all n-grams, or add a word or regex that must be in the n-gram in order for it to be counted.

Two extra options appear when ngramming is selected. First, you can choose the size of the n-gram. Second, you can choose how to treat contractions: you can either split them, so that `I do n't` is a trigram, or leave them unsplit, so that `I don't` is a bigram. It's up to you to decide which options yield the most telling results.

{{note}} The `Plaintext` and `Tokenise` options are currently functional, but there are currently limited options available for working with them. More will be in development, though they in general allow less sophisticated interrogation, and are not a high priorty. {{end}}

### Plaintext

You can also search the plain text version of the corpus using simple or regular expression based searches.

## Special queries

*corpkit* also has some pre-programmed queries and query parts, based mostly around concepts from systemic-functional grammar. 

### Preset queries

`'Any'` will match any word, tag or function, depending on the search type. `Participants` and `Processes` approximate notions from systemic functional grammar.

{{tip}} One of the first things you might like to do with your data is calculate the total number of tokens in each subcorpus. The easiest way to do this is to use the <code>Count tokens</code> option in the <code>Trees</code> search type, and to select <code>Any</code> as the preset query. You can then use this data, in combination with a different interrogation, to calculate the relative frequencies of specific words in the corpus. See <a href="doc_edit.html"><i>Edit</i></a> for more details.{{end}}

`Stats` will get the absolute frequencies for different moods and process types. It involves many sub-interrogations (for different process types and grammatical moods, mostly), and may take a long time.

### Wordlists

*corpkit* also ships with a number of different lists of words or dependency roles that can be added into queries. The query below will match any of the closed class words in the `CLOSEDCLASS` list:

> `LIST:CLOSEDCLASS`

 You can, for example, enter:

This can be powerful when used in conjunction with Tregex or dependency queries. The query below will get any predicator matching a list of mental processes:

> `VP <<# /LIST:MENTAL/ $ NP`

If you select `Schemes` &rarr; `Wordlists` from the menu bar, you can define your own wordlists, or edit existing lists, including those outlined in the previous section. Simply enter words of interest (or paste them in from another file, one per line), give the list a name, and hit `Store`. You can then use this wordlist in a query with the  `LIST:NAME` syntax.

{{tip}} When using special queries inside Tregex queries, always remember to wrap the special query in slashes. <code>"/VB.?/ < /LIST:MENTAL/"</code> will work, but <code>"/VB.?/ < LIST:MENTAL"</code> will not. {{end}}

### Creating and modifying wordlists

You can easily select a predefined list, modify and rename it, and access it via `LIST:NAME`. The `Get inflections` buttons will help you make queries that match all possible forms of the lemmata of interest.

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

If you forgot to name an interrogation before running it, you can head to the `Manage` tab to rename it at any time.

## Running interrogations

On large datasets, interrogations can take some time, especially for dependency searches with many options. Speaker IDs also come at the cost of speed. Be patient!

Be sure to name your interrogation, via the `Name interrogation` box. This makes it much easier to know at a glance what you'll be editing, plotting or exporting.

{{tip}} Whenever you run an interrogation that produces results, all options used to generate the query are stored, and accessible via the <code>Manage</code> tab. You can head there to access previous queries, or to save interrogations to disk. {{end}}

## Editing spreadsheets

Once results have been generated, the spreadsheets on the right are populated. Here, you can edit numbers, move columns, or delete particular results or subcorpora. You can flip back and forward between other interrogations with the `Previous` and `Next` buttons.

If you manually edit the results in either the results or totals spreadsheet, you can hit `Update interrogation` to update the version of the data that is stored in memory.

It's important to remember that the results and totals spreadsheets do not communicate with one another. As such, if you are adding or subtracting from individual results, you'd need to update the total results part to reflect these changes. 

{{tip}} Sorting the result order is performed in the <code>Edit</code> tab.{{end}}

## Making dictionaries

If you want, you can use the `Save as dictionary` button to generate a reference corpus from an interrogation, comprised of each word and its total frequency. This will be stored in the `dictionaries/` folder of the project. Every dictionary file in this directory can be loaded when doing keywording in the `Edit` tab.

## Next steps

It can be hard to learn anything interesting from absolute frequencies alone. Generally, you'll next want to go to the `Edit` tab to modify the results into something more informative.