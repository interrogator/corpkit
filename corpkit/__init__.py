from __future__ import print_function

"""A toolkit for corpus linguistics

.. moduleauthor:: Daniel McDonald <mcdonaldd@unimelb.edu.au>

"""

# quicker access to search, exclude, show types
letters = ['A', 'ANY', 'ANYWORD', 'C', 'D', 'D', 'DF', 'DL', 'DP', 'F', 'G', 
           'GF', 'GL', 'GP', 'I', 'K', 'L', 'M', 'N', 'NL', 'NP', 'NW', 'P',
           'PL', 'R', 'S', 'SELF', 'T', 'V', 'W']

# asterisk import
__all__ = ["interrogator",
    "editor",
    "plotter",
    "save",
    "quickview",
    "load",
    "load_all_results",
    "as_regex",
    "Interrogation",
    "Interrodict",
    "Concordance",
    "new_project",
    "make_corpus",
    "flatten_treestring",
    "interroplot",
    "Corpus",
    "Corpora"] + letters

#metadata
__version__ = "2.0.6"
__author__ = "Daniel McDonald"
__license__ = "MIT"

# probably not needed, anymore but adds corpkit to path for tregex.sh
import sys
import os
import inspect

corpath = inspect.getfile(inspect.currentframe())
baspat = os.path.dirname(corpath)
#dicpath = os.path.join(baspat, 'dictionaries')
for p in [corpath, baspat]:
    if p not in sys.path:
        sys.path.append(p)
    if p not in os.environ["PATH"].split(':'): 
        os.environ["PATH"] += os.pathsep + p

# import classes
from corpus import Corpus
from corpus import Corpora

import dictionaries as dictionaries

# import functions, though most are now class methods
from interrogator import interrogator
from editor import editor
from plotter import plotter
from other import save
from other import load
from lazyprop import lazyprop
from other import load_all_results
from other import quickview
from other import as_regex
from other import new_project
from other import interroplot
from make import make_corpus
from build import flatten_treestring
from interrogation import Interrogation, Interrodict, Concordance

# monkeypatch editing and plotting to pandas objects
import pandas as pd

def _plot(self, *args, **kwargs):
    from corpkit import plotter
    return plotter(self, *args, **kwargs)

def _edit(self, *args, **kwargs):
    from corpkit import editor
    return editor(self, *args, **kwargs)

def _save(self, savename, **kwargs):
    from corpkit import save
    save(self, savename, **kwargs)

def _quickview(self, n = 25):
    from corpkit.other import quickview
    quickview(self, n = n)

def _format(self, *args, **kwargs):
    from corpkit.other import concprinter
    concprinter(self, *args, **kwargs)

def _texify(self, *args, **kwargs):
    from corpkit.other import texify
    texify(self, *args, **kwargs)

def _calculate(self, *args, **kwargs):
    from corpkit.process import interrogation_from_conclines
    return interrogation_from_conclines(self)

def _shuffle(self, inplace = False):
    import random
    index = list(self.index)
    random.shuffle(index)
    shuffled = self.ix[index]
    shuffled.reset_index()
    if inplace:
        self = shuffled
    else:
        return shuffled

def _top(self):
    """Show as many rows and cols as possible without truncation"""
    import pandas as pd
    max_row = pd.options.display.max_rows
    max_col = pd.options.display.max_columns
    return self.iloc[:max_row,:max_col]

pd.DataFrame.edit = _edit
pd.Series.edit = _edit

pd.DataFrame.visualise = _plot
pd.Series.visualise = _plot

pd.DataFrame.save = _save
pd.Series.save = _save

pd.DataFrame.quickview = _quickview
pd.Series.quickview = _quickview

pd.DataFrame.format = _format
pd.Series.format = _format

pd.Series.texify = _texify

pd.DataFrame.calculate = _calculate
pd.Series.calculate = _calculate

pd.DataFrame.shuffle = _shuffle

pd.DataFrame.top = _top

# Defining globals
A = 'a'
ANY = 'any'
ANYWORD = r'[A-Za-z0-9:_]'
C = 'c'
D = 'd'
D = 'd'
DF = 'df'
DL = 'dl'
DP = 'dp'
F = 'f'
G = 'g'
GF = 'gf'
GL = 'gl'
GP = 'gp'
I = 'i'
K = 'k'
L = 'l'
M = 'm'
N = 'n'
NL = 'nl'
NP = 'np'
NW = 'nw'
P = 'p'
PL = 'pl'
R = 'r'
S = 's'
SELF = 'self'
T = 't'
V = 'v'
W = 'w'
