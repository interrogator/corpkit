"""
This file contains tests for the corpkit API, to be run by Nose.

There are fast and slow tests. Slow tests include those that test the parser.
These should be run before anything goes into master. Fast tests corpus
interrogations, edits, concordances and so on. These are done on commit.

The tests don't cover everything in the module yet.

To run all tests:

    nosetests corpkit/nosetests.py

Just fast tests:

    nosetests corpkit/nosetests.py -a '!slow'

"""

import os
import nose
from nose.tools import assert_equals
import corpkit
from corpus import Corpus

unparsed_path = 'data/test'
parsed_path = 'data/test-plain-parsed'
speak_path = 'data/test-speak-parsed'
tok_path = 'data/test-tokenised'

def test_import():
    import corpkit
    from dictionaries.wordlists import wordlists
    from corpus import Corpus
    assert_equals(wordlists.articles, ['a', 'an', 'the', 'teh'])

def test_corpus_class():
    """Test that Corpus can be created"""
    unparsed = Corpus(unparsed_path)
    assert_equals(os.path.basename(unparsed_path), unparsed.name)
