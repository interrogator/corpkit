import os
from nose.tools import assert_equals
from corpkit import *

unparsed_path = 'data/test'
parsed_path = 'data/test-stripped-parsed'

def test_import():
    import corpkit
    from dictionaries.wordlists import wordlists
    from corpkit import Corpus
    assert_equals(wordlists.articles, ['a', 'an', 'the', 'teh'])
