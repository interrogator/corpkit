# full suite: must delete some corpora
# nosetests corpkit/nosetests.py

# skip parsing
# nosetests corpkit/nosetests.py -a '!slow'

import os
import nose
from nose.tools import assert_equals
import corpkit
from corpus import Corpus


unparsed_path = 'data/test'
parsed_path = 'data/test-stripped-parsed'

def test_import():
    import corpkit
    from dictionaries.wordlists import wordlists
    from corpus import Corpus
    assert_equals(wordlists.articles, ['a', 'an', 'the', 'teh'])

def test_corpus_class():
    unparsed = Corpus(unparsed_path)
    assert_equals(os.path.basename(unparsed_path), unparsed.name)
 
def test_parse():
    import shutil
    print('Testing parser')
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree('data/test-parsed')
    except:
        pass
    parsed = unparsed.parse()
    fnames = []
    for subc in parsed.subcorpora:
        for f in subc.files:
            fnames.append(f.name)
    assert_equals(fnames, ['intro.txt.xml', 'body.txt.xml'])

test_parse.slow = 1

def test_parse_speakseg(skipassert = False):
    print('Testing parser with speaker segmentation')
    unparsed = Corpus(unparsed_path)
    import shutil
    try:
        shutil.rmtree(parsed_path)
    except:
        pass
    parsed = unparsed.parse(speaker_segmentation = True)
    fnames = []
    for subc in parsed.subcorpora:
        for f in subc.files:
            fnames.append(f.name)
    assert_equals(fnames, ['intro.txt.xml', 'body.txt.xml'])

test_parse_speakseg.slow = 1

if os.path.isdir(parsed_path):
    corp = Corpus('data/test-stripped-parsed')
else:
    test_parse_speakseg(skipassert = True)
    corp = Corpus('data/test-stripped-parsed')

def test_interro1():
    print('Testing interrogation 1')
    data = corp.interrogate('t', r'__ < /JJ.?/')
    assert_equals(data.results.shape, (2, 6))

def test_interro2():
    print('Testing interrogation 2')
    data = corp.interrogate({'t': r'__ < /JJ.?/'})
    assert_equals(data.results.shape, (2, 6))

def test_interro3():
    print('Testing interrogation 3')
    data = corp.interrogate({'w': r'^c'}, exclude = {'l': r'check'}, show = ['l', 'f'])
    st = set(['corpus/nsubjpass',
             'corpus/compound',
             'corpkit/nmod:poss',
             'continuum/nmod:on',
             'conduit/nmod:as',
             'concordancing/nmod:like',
             'concordancing/appos',
             'computational/amod',
             'case/nmod:in',
             'can/aux'])
    assert_equals(set(list(data.results.columns)), st)

def test_interro4():
    print('Testing interrogation 4')
    corp = Corpus('data/test-stripped-tokenised')
    data = corp.interrogate({'n': 'any'})
    d = {'and interrogating': {'first': 0, 'second': 2},
         'concordancing and': {'first': 0, 'second': 2}}
    assert_equals(data.results.to_dict(), d)

def test_interro5():
    print('Testing interrogation 5')
    corp = Corpus('data/test-stripped')
    data = corp.interrogate({'w': r'\bl[a-z]+?\s'})
    assert_equals(data.results.sum().sum(), 4)
  
def test_interro_multiindex_tregex_justspeakers():
    print('Testing multiindex')
    import pandas as pd
    data = corp.interrogate('t', r'__ < /JJ.?/', just_speakers = ['each'])
    assert_equals(all(data.multiindex().results.index), all(pd.MultiIndex(levels=[['ANONYMOUS', 
           'NEWCOMER', 'TESTER', 'UNIDENTIFIED', 'Total'], ['first', 'second', 'Total']],
           labels=[[3, 3, 1, 1, 0, 0, 2, 2], [0, 1, 0, 1, 0, 1, 0, 1]],
           names=['corpus', 'subcorpus'])))

def test_conc():
    print('Testing concordancer')
    data = corp.concordance({'f': 'amod'})
    assert_equals(data.ix[0]['m'], 'small')

def test_edit():
    print('Testing simple edit')
    data = corp.interrogate({'t': r'__ !< __'})
    data = data.edit('%', 'self')
    assert_equals(data.results.iloc[0,0], 11.627906976744185)

