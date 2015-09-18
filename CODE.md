# Description (for geeks)

This repo contains mostly Python code. While it started out as a library to be used at the command-line or in a REPL, it now includes a graphical user interface, which rests in `corpkit/python-gui.py`, or as an executable in the `corpkit-app` submodule.

Some of the heavy computational work is done by forking out to Stanford's CoreNLP suite, written in Java.

The GUI is written using the Tkinter module, a set of bindings for the Tk graphical toolkit.

Links:

 - http://nlp.stanford.edu/software/corenlp.shtml
 - http://wiki.tcl.tk
 - https://en.wikipedia.org/wiki/Tk_(software)

In the orientation folder, you can find a sample dataset and an IPython notebook for getting started with the command-line interface. The library source code is in the `corpkit` folder. And there's some slides and TeX source in the talks folder, for more info.
