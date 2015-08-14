__all__ = ["interrogator",
           "editor",
           "plotter",
           "conc",
           "keywords",
           "ngrams",
           "collocates",
           "quickview",
           "concprinter",
           "save_result",
           "load_result",
           "report_display",
           "ipyconverter",
           "conv",
           "pytoipy",
           "new_project",
           "multiquery",
           "interroplot",
           "quicktree",
           "searchtree",
           "tregex_engine",
           "load_all_results",
           "dictmaker",
           "texify",
           "make_nltk_text",
           "pmultiquery",
           "as_regex",
           "sim",
           "show",
           "dictmaker",
           "tokener",
           "get_urls",
           "downloader",
           "simple_text_extractor",
           "practice_run",
           "souper",
           "correctspelling",
           "stanford_parse",
           "structure_corpus",
           "edit_metadata",
           "stanford_parse",
           "download",
           "extract",
           "install",
           "install_corenlp",
           "rename_duplicates",
           "get_corpus_filepaths",
           "check_jdk",
           "parse_corpus",
           "move_parsed_files",
           "corenlp_exist"]

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
from keys import ngrams
from colls import collocates
from plugins import HighlightLines, InteractiveLegendPlugin

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
from other import load_all_results
from other import texify
from other import make_nltk_text
from other import pmultiquery
from other import as_regex
from other import show
from context import sim

from build import download
from build import dictmaker
from build import tokener
from build import get_urls
from build import downloader
from build import simple_text_extractor
from build import practice_run
from build import souper
from build import correctspelling
from build import stanford_parse
from build import structure_corpus
from build import edit_metadata
from build import extract
from build import install
from build import install_corenlp
from build import rename_duplicates
from build import get_corpus_filepaths
from build import check_jdk
from build import parse_corpus
from build import move_parsed_files
from build import corenlp_exist

from dictionaries.process_types import processes
from dictionaries.wordlists import wordlists
from dictionaries.roles import roles


