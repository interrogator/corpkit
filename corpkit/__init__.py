__all__ = ["interrogator",
           "editor",
           "plotter",
           "conc",
           "save_result",
           "quickview",
           "load_result",
           "load_all_results",
           "as_regex",
           "new_project",
           "make_corpus",
           "flatten_treestring",
           "interroplot"]

__version__ = "1.77"
__author__ = "Daniel McDonald"
__license__ = "MIT"

import sys
import os
import inspect

# probably not needed, but adds corpkit to path for tregex.sh

corpath = inspect.getfile(inspect.currentframe())
baspat = os.path.dirname(corpath)
dicpath = os.path.join(baspat, 'dictionaries')
for p in [corpath, baspat, dicpath]:
    if p not in sys.path:
        sys.path.append(p)
    if p not in os.environ["PATH"].split(':'): 
        os.environ["PATH"] += os.pathsep + p

from interrogator import interrogator
from editor import editor
from plotter import plotter
from conc import conc
from other import save_result
from other import load_result
from other import load_all_results
from other import quickview
from other import as_regex
from other import new_project
from other import interroplot
from make import make_corpus
from build import flatten_treestring
