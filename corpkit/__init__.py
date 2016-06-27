from __future__ import print_function

"""
A toolkit for corpus linguistics
"""

# quicker access to search, exclude, show types
LETTERS = ['A',
           'ANY',
           'ANYWORD',
           'C',
           'D',
           'D',
           'DF',
           'DI',
           'DL',
           'DP',
           'DS',
           'DW',
           'DX',
           'F',
           'G',
           'GF',
           'GI',
           'GL',
           'GP',
           'GS',
           'GW',
           'GX',
           'H',
           'HF',
           'HI',
           'HL',
           'HP',
           'HS',
           'HW',
           'HX',
           'I',
           'K',
           'L',
           'M',
           'N',
           'NF',
           'NL',
           'NP',
           'NW',
           'P',
           'PL',
           'R',
           'S',
           'SELF',
           'T',
           'V',
           'W',
           'X']

# asterisk import
__all__ = [
    "load",
    "loader",
    "load_all_results",
    "dictionaries",
    "as_regex",
    "new_project",
    "Corpus",
    "File",
    "Corpora",
    "Wordlist",
    "gui"] + LETTERS

#metadata
__version__ = "2.2.6"
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
from corpkit.corpus import Corpus, File, Corpora
from corpkit.model import MultiModel

import corpkit.dictionaries as dictionaries

# import functions, though most are now class methods
from corpkit.other import load, loader, load_all_results
from corpkit.plotter import multiplotter
from corpkit.lazyprop import lazyprop
from other import load_all_results
from other import quickview, as_regex, new_project
from dictionaries.process_types import Wordlist
from process import gui
# monkeypatch editing and plotting to pandas objects
from pandas import DataFrame, Series

def _plot(self, *args, **kwargs):
    from corpkit.plotter import plotter
    return plotter(self, *args, **kwargs)

def _edit(self, *args, **kwargs):
    from corpkit.editor import editor
    return editor(self, *args, **kwargs)

def _save(self, savename, **kwargs):
    from corpkit.other import save
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

def _multiplot(self, leftdict={}, rightdict={}, *args, **kwargs):
    from corpkit.plotter import multiplotter
    return multiplotter(self, leftdict=leftdict, rightdict=rightdict, **kwargs)

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
    return self.iloc[:max_row, :max_col]

DataFrame.edit = _edit
Series.edit = _edit

DataFrame.visualise = _plot
Series.visualise = _plot

DataFrame.multiplot = _multiplot
Series.multiplot = _multiplot


DataFrame.save = _save
Series.save = _save

DataFrame.quickview = _quickview
Series.quickview = _quickview

DataFrame.format = _format
Series.format = _format

Series.texify = _texify

DataFrame.calculate = _calculate
Series.calculate = _calculate

DataFrame.shuffle = _shuffle

DataFrame.top = _top

# Defining globals

A = 'a'
ANY = 'any'
ANYWORD = r'[A-Za-z0-9:_]'
C = 'c'
D = 'd'
D = 'd'
DF = 'df'
DI = 'di'
DL = 'dl'
DP = 'dp'
DS = 'ds'
DW = 'dw'
DX = 'dx'
F = 'f'
G = 'g'
GF = 'gf'
GI = 'gi'
GL = 'gl'
GP = 'gp'
GS = 'gs'
GW = 'gw'
GX = 'gx'
H = 'h'
HF = 'hf'
HI = 'hi'
HL = 'hl'
HP = 'hp'
HS = 'hs'
HW = 'hw'
HX = 'hx'
I = 'i'
K = 'k'
L = 'l'
M = 'm'
N = 'n'
NF = 'nf'
NL = 'nl'
NP = 'np'
NS = 'ns'
NW = 'nw'
P = 'p'
PL = 'pl'
R = 'r'
S = 's'
SELF = 'self'
T = 't'
V = 'v'
W = 'w'
X = 'x'
