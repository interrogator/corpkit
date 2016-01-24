"""A toolkit for corpus linguistics

.. moduleauthor:: Daniel McDonald <mcdonaldd@unimelb.edu.au>

"""


# asterisk import
__all__ = ["interrogator",
    "editor",
    "plotter",
    "conc",
    "save",
    "quickview",
    "load",
    "load_all_results",
    "as_regex",
    "new_project",
    "make_corpus",
    "flatten_treestring",
    "interroplot",
    "Corpus",
    "Corpora"]

#metadata
__version__ = "1.84"
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

import corpkit.dictionaries as dictionaries

# import functions, though most are now class methods
from interrogator import interrogator
from editor import editor
from plotter import plotter
from conc import conc
from other import save
from other import load
from other import load_all_results
from other import quickview
from other import as_regex
from other import new_project
from other import interroplot
from make import make_corpus
from build import flatten_treestring

# monkeypatch editing and plotting to pandas objects
import pandas as pd

def plotfunc(self, title, *args, **kwargs):
    from corpkit import plotter
    plotter(title, self, *args, **kwargs)

def editfunc(self, *args, **kwargs):
    from corpkit import editor
    return editor(self, *args, **kwargs)

def savefunc(self, savename, *args, **kwargs):
  from corpkit import save
  save(self, savename, *args, **kwargs)

def quickviewfunc(self, n = 25):
    from corpkit.other import quickview
    quickview(self, n = n)

def formatfunc(self, *args, **kwargs):
    from corpkit.other import concprinter
    concprinter(self, *args, **kwargs)

pd.DataFrame.edit = editfunc
pd.Series.edit = editfunc

pd.DataFrame.plot = plotfunc
pd.Series.plot = plotfunc

pd.DataFrame.save = savefunc
pd.Series.save = savefunc

pd.DataFrame.quickview = quickviewfunc
pd.Series.quickview = quickviewfunc

pd.DataFrame.format = formatfunc
pd.Series.format = formatfunc
