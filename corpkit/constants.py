import sys
import codecs

PYTHON_VERSION = sys.version_info.major
STRINGTYPE = str if PYTHON_VERSION == 3 else basestring
INPUTFUNC = input if PYTHON_VERSION == 3 else raw_input
OPENER = open if PYTHON_VERSION == 3 else codecs.open

# quicker access to search, exclude, show types
from itertools import product
_starts = ['M', 'N', 'B', 'G', 'D', 'H']

_ends = ['W', 'L', 'I', 'S', 'P', 'X', 'R', 'F']
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
             'r': 'Distance from root',
             'w': 'Word',
             't': 'Trees',
             'i': 'Index',
             'n': 'N-grams',
             'p': 'POS',
             'x': 'Word class',
             's': 'Sentence index'}

transobjs = {'g': 'Governor',
             'd': 'Dependent',
             'm': 'Match',
             'h': 'Head'}

# modify this if your conll-style data is different from what is provided by the
# parser plus post-processing. data must tart with 's' for sentence index and 'i'
# for token index. after that, you can have whichever fields you like, and should 
# be able to access them using normal corpkit syntax.

# 'd', for deps, is a comma-sep string of dependent token indices

# 'c', for coref, has an artibrary number representing a dependency chain. the
# head of a mention is marked with an asterisk.

# y and z are left as custom fields, not really in use now, but theoretically
# they are searchable

# default: sent, index, word, lem, pos, ner, gov, func, deps, coref, custom * 3
CONLL_COLUMNS = ['s', 'i', 'w', 'l', 'p', 'n', 'g', 'f', 'd', 'c', 'y', 'z']

# what the longest possible speaker ID is. this prevents huge lines with colons
# from getting matched unintentionally
MAX_SPEAKERNAME_SIZE = 40


REPEAT_PARSE_ATTEMPTS = 3
