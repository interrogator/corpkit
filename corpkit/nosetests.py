"""
This file contains tests for the corpkit API, to be run by Nose.

There are fast and slow tests. Slow tests include those that test the parser.
These should be run before anything goes into master. Fast tests are just corpus
interrogations. These are done on commit.

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

def test_import():
    import corpkit
    from dictionaries.wordlists import wordlists
    from corpus import Corpus
    assert_equals(wordlists.articles, ['a', 'an', 'the', 'teh'])

def test_corpus_class():
    """Test that Corpus can be created"""
    unparsed = Corpus(unparsed_path)
    assert_equals(os.path.basename(unparsed_path), unparsed.name)
 
def test_parse():
    """Test CoreNLP parsing"""
    import shutil
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree(parsed_path)
    except:
        pass
    parsed = unparsed.parse()
    fnames = []
    for subc in parsed.subcorpora:
        for f in subc.files:
            fnames.append(f.name)
    shutil.move(parsed.path, parsed_path)
    assert_equals(fnames, ['intro.txt.conll', 'body.txt.conll'])

def test_speak_parse():
    """Test CoreNLP parsing with speaker segmentation"""
    import shutil
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree(speak_path)
    except:
        pass
    parsed = unparsed.parse(speaker_segmentation=True)
    fnames = []
    for subc in parsed.subcorpora:
        for f in subc.files:
            fnames.append(f.name)
    shutil.move(parsed.path, speak_path)
    assert_equals(fnames, ['intro.txt.conll', 'body.txt.conll'])

# this is how you define a slow test
test_parse.slow = 1
test_speak_parse.slow = 1

def test_interro1():
    """Testing interrogation 1"""
    corp = Corpus(parsed_path)
    data = corp.interrogate('t', r'__ < /JJ.?/')
    assert_equals(data.results.shape, (2, 6))

def test_interro2():
    """Testing interrogation 2"""
    corp = Corpus(parsed_path)
    data = corp.interrogate({'t': r'__ < /JJ.?/'})
    assert_equals(data.results.shape, (2, 6))

def test_interro3():
    """Testing interrogation 3"""
    corp = Corpus(parsed_path)
    data = corp.interrogate({'w': r'^c'}, exclude={'l': r'check'}, show=['l', 'f'])
    st = {'can/aux',
          'computational/amod',
          'concordancing/appos',
          'corpkit/nmod:poss',
          'corpus/compound',
          'case/nmod:in',
          'continuum/nmod:on',
          'conduit/nmod:as',
          'concordancing/nmod:like',
          'corpus/nsubjpass',
          }
    assert_equals(set(list(data.results.columns)), st)

# skipping this for now, as who cares about tokens
#def test_interro4():
#    """Testing interrogation 4"""
#    corp = Corpus('data/test-stripped-tokenised')
#    data = corp.interrogate({'w': 'any'}, show='nw')
#    d = {'and interrogating': {'first': 0, 'second': 2},
#         'concordancing and': {'first': 0, 'second': 2}}
#    assert_equals(data.results.to_dict(), d)
  
def test_interro_multiindex_tregex_justspeakers():
    """Testing interrogation 6"""
    import pandas as pd
    corp = Corpus(speak_path)
    data = corp.interrogate('t', r'__ < /JJ.?/', just_speakers=['each'])
    assert_equals(all(data.results.index), 
                  all(pd.MultiIndex(levels=[['ANONYMOUS', 'NEWCOMER',
                    'TESTER', 'UNIDENTIFIED'], ['first', 'second']],
           labels=[[0, 0, 1, 1, 2, 2, 3, 3], [0, 1, 0, 1, 0, 1, 0, 1]])))

test_interro_multiindex_tregex_justspeakers.slow = 1

def test_conc():
    """Testing concordancer"""
    corp = Corpus(parsed_path)
    data = corp.concordance({'f': 'amod'})
    assert_equals(data.ix[0]['m'], 'small')

# this syntax isn't recognised by tgrep, so we'll skip it in tests
def test_edit():
    """Testing edit function"""
    corp = Corpus(parsed_path)
    data = corp.interrogate({'t': r'__ !< __'})
    data = data.edit('%', 'self')
    assert_equals(data.results.iloc[0,0], 10.204081632653061)
    #assert_equals(data.results.iloc[0,0], 11.627906976744185)

test_edit.slow = 1

