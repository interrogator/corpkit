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
           "download_large_file", 
           "extract_cnlp", 
           "get_corpus_filepaths", 
           "check_jdk", 
           "parse_corpus", 
           "move_parsed_files", 
            "corenlp_exists"]

__version__ = "1.59"
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
from build import download_large_file
from build import extract_cnlp
from build import get_corpus_filepaths
from build import check_jdk
from build import parse_corpus
from build import move_parsed_files
from build import corenlp_exists
