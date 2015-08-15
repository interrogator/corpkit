#__all__ = ["interrogator",
#           "editor",
#           "plotter",
#           "conc",
#           "save_result",
#           "quickview",
#           "load_result",
#           "load_all_results",
#           "as_regex"]

import sys
import os
import inspect

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
from other import add_corpkit_to_path
