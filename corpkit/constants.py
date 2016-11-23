import sys
import codecs

# python 2/3 coompatibility
PYTHON_VERSION = sys.version_info.major
STRINGTYPE = str if PYTHON_VERSION == 3 else basestring
INPUTFUNC = input if PYTHON_VERSION == 3 else raw_input
OPENER = open if PYTHON_VERSION == 3 else codecs.open

# quicker access to search, exclude, show types
from itertools import product
_starts = ['M', 'N', 'B', 'G', 'D', 'H', 'R']
_ends = ['W', 'L', 'I', 'S', 'P', 'X', 'R', 'F', 'E']
_others = ['A', 'ANY', 'ANYWORD', 'C', 'SELF', 'V', 'K', 'T']
_prod = list(product(_starts, _ends))
_prod = [''.join(i) for i in _prod]
_letters = sorted(_prod + _starts + _ends + _others)

_adjacent_start = ['A{}'.format(i) for i in range(1, 9)] + \
                   ['Z{}'.format(i) for i in range(1, 9)]

_adjacent = [''.join(i) for i in list(product(_adjacent_start, _prod))]

LETTERS = sorted(_letters + _adjacent)

# translating search values intro words
transshow = {'f': 'Function',
             'l': 'Lemma',
             'a': 'Distance from root',
             'w': 'Word',
             't': 'Trees',
             'i': 'Index',
             'n': 'N-grams',
             'p': 'POS',
             'e': 'NER',
             'c': 'Count',
             'x': 'Word class',
             's': 'Sentence index'}

transobjs = {'g': 'Governor',
             'd': 'Dependent',
             'm': 'Match',
             'h': 'Head'}

# below are the column names for the conll-u formatted data
# corpkit's format is slightly different, but largely compatible.

# Key differences:
#
#     1. 'e' is used for NER, rather than lang specific POS
#     2. 'd' gives a comma-sep list of dependents, rather than head-deprel pairs
#        this is done for processing speed.
#     3. 'c' is used for corefs, not 'misc comment'. it has an artibrary number 
#        representing a dependency chain. head of a mention is marked with an asterisk.

# 'm' does not have anything in it in corpkit, but denotes morphological features

# default: index, word, lem, pos, ner, morph, gov, func, deps, coref
CONLL_COLUMNS = ['i', 'w', 'l', 'p', 'e', 'v', 'g', 'f', 'd', 'c']

# what the longest possible speaker ID is. this prevents huge lines with colons
# from getting matched unintentionally
MAX_SPEAKERNAME_SIZE = 40

# parsing sometimes fails with a java error. if corpus.parse(restart=True), this will try
# parsing n times before giving up
REPEAT_PARSE_ATTEMPTS = 3

# location of the current corenlp and its version
# old, stable
#CORENLP_URL = 'http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip'
#CORENLP_VERSION = '3.6.0'

# newest, beta
CORENLP_VERSION = '3.7.0'
CORENLP_URL  = 'http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip'

# it can be very slow to load a bunch of unused metadata categories
MAX_METADATA_FIELDS = 99
MAX_METADATA_VALUES = 99