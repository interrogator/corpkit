It ain't all strings! You can use the corpkit library functions to manipulate different data structures.

**Parsed NYT Text**

Upon unzipping orientation/data/nyt.tar.gz one can discover two collections of text files. They seem to be the same data, just organised in different ways.

One collection is organised by year. The other collection is organised first by topic (economics, health or politics) and then by year (from 1987 to 2014).

The text files are essentially sets of trees. Each line is a parse tree for a sentence from the original corpus. The encoding used for the trees looks a lot like Lisp code. I think the style is called Penn Treebank. Though I am not sure.

**Interrogation Format**

It seems that sessions can be saved in some kind of file format called an interrogation. An interrogation is a directory of CSV files that are actually TSV files.

**Dictionaries**

In the dictionaries folder there are .p files and .py files which contain data. The .p files are Python pickles. Each pickle contains a dict object which maps words to integers, presumably a frequency count. The .py files are miscellaneous data. Some are just lists of words and others are more complicated. For example, in roles.py there is some kind of compatibility mapping between CoreNLP and SFL. CoreNLP is a Java library made by researchers from Stanford and SFL is systemic functional linguistics.
