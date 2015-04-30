__all__ = ["colls", "edit", "keys", "notebook", "query", "view", "build"]

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

from query import interrogator
from query import interroplot
from query import multiquery
from query import conc
from query import topix_search

from view import plotter
from view import table
from view import topix_plot
from view import tally
from view import quickview

from keys import keywords
from colls import collocates

from edit import merger
from edit import surgeon
from edit import resorter
from edit import mather
from edit import save_result
from edit import load_result
from edit import percenter


from build import dictmaker
from build import correctspelling

from notebook import report_display
from notebook import pytoipy
from notebook import ipyconverter
from notebook import conv
from notebook import new_project

from trees import quicktree
from trees import searchtree
from dictionaries.process_types import processes


