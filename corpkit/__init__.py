__all__ = ["interrogator", "editor", "plotter", "conc", "keys", "colls", "other", "build"]

import os
import sys

# these lines here are to let ipython find tregex and potentially
# anything in 'dictionaries'

import corpkit
path_to_corpkit = os.path.dirname(corpkit.__file__)
thepath, corpkitname = os.path.split(path_to_corpkit)
import dictionaries
os.environ["PATH"] += os.pathsep + path_to_corpkit + os.pathsep + os.path.join(thepath, 'dictionaries')

# these add to pythonpath, mostly so we can find dictionaries
# doesn't seem to be working at the moment, though.
sys.path.append(path_to_corpkit)
sys.path.append(os.path.join(thepath, 'dictionaries'))
sys.path.append(thepath)

from interrogator import interrogator
from editor import editor
from plotter import plotter
from conc import conc
from keys import keywords
from colls import collocates

from other import quickview
from other import concprinter
from other import save_result
from other import load_result
from other import report_display
from other import ipyconverter
from other import conv
from other import pytoipy
from other import new_project
from other import multiquery
from other import interroplot
from other import quicktree
from other import searchtree
from other import datareader
from other import tregex_engine

from build import dictmaker
from build import correctspelling

from dictionaries.process_types import processes


