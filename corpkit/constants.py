import sys
PYTHON_VERSION = sys.version_info.major
STRINGTYPE = str if PYTHON_VERSION == 3 else basestring
INPUTFUNC = input if PYTHON_VERSION == 3 else raw_input

transshow = {'f': 'Function',
             'l': 'Lemma',
             'r': 'Distance from root',
             'w': 'Word',
             't': 'Trees',
             'i': 'Index',
             'n': 'N-grams',
             'p': 'POS',
             'x': 'Word class',
             's': 'Sentence'}
transobjs = {'g': 'Governor',
             'd': 'Dependent',
             'm': 'Match',
             'h': 'Head'}