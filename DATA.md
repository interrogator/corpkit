This repository contains some sample data, in the form of syntax trees from The New York Times.

**Parsed NYT Text**

Upon unzipping orientation/data/nyt.tar.gz one can discover two collections of text files.

One collection is organised by year (1963-2014). The other collection is a subset of the first, containing three topics (economics, health or politics), which are also sorted into annual subcorpora. Any of these directories can be used as the path for a *corpkit* query.

The text files are essentially loads and loads of syntax trees. These were created using Stanford CoreNLP. Most of them contain the word *risk*, or are immediately adjacent to a sentence containing a risk word.

**Dictionaries and wordlists**

In the dictionaries folder there are .p files and .py files which contain data. The .p files are Python pickles, inside of which are word frequency dicts from various corpora. These can be used as reference corpora.

The `dictionaries/*.py` files are essentially wordlists and basic functions for generating wordlists with inflections. `roles.py`, for example, provides a mapping of some systemic functional linguistic constructs to Universal Dependencies, so that corpkit can search and edit using SF categories. `process_types` generates a named tuple of word lists for mental, verbal and relational processes, which can also be fed into queries and edits.