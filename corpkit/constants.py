import sys

PYTHON_VERSION = sys.version_info.major
STRINGTYPE = str if PYTHON_VERSION == 3 else basestring
INPUTFUNC = input if PYTHON_VERSION == 3 else raw_input

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