import os
from nose.tools import assert_equals
from corpkit import *

unparsed_path = 'data/test'
parsed_path = 'data/test-stripped-parsed'

def test_import():
    import corpkit
    from dictionaries.wordlists import wordlists
    from corpkit import Corpus

def test_corpus_class():
    unparsed = Corpus(unparsed_path)
    assert_equals(os.path.basename(unparsed_path), unparsed.name)
 
def test_parse():
    print 'Testing parser'
    unparsed = Corpus(unparsed_path)
    parsed = unparsed.parse()
    assert_equals(list([i.name for i in parsed.files]), ['intro.txt.xml', 'body.txt.xml'])

test_parse.slow = 1

def test_parse_speakseg(skipassert = False):
    print 'Testing parser with speaker segmentation'
    unparsed = Corpus(unparsed_path)
    parsed = unparsed.parse(speaker_segmentation = True)
    if skipassert:
        assert_equals(list([i.name for i in parsed.files]), ['intro.txt.xml', 'body.txt.xml'])

test_parse_speakseg.slow = 1

if os.path.isdir(parsed_path):
    corp = Corpus('data/test-stripped-parsed')
else:
    test_parse_speakseg(skipassert = True)

def test_interro1():
    print 'Testing interrogation 1'

    data = corp.interrogate('t', r'__ < /JJ.?/')
    assert_equals(data.results.shape, (2, 5))

def test_interro2():
    print 'Testing interrogation 2'
    corp = Corpus('data/test-parsed')
    data = corp.interrogate({'t': r'__ < /JJ.?/'})
    assert_equals(data.results.shape, (2, 5))

#def test_interro3():
#    print 'Testing interrogation 3'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro4():
#    print 'Testing interrogation 4'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro5():
#    print 'Testing interrogation 5'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro6():
#    print 'Testing interrogation 6'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro7():
#    print 'Testing interrogation 7'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro8():
#    print 'Testing interrogation 8'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_interro9():
#    print 'Testing interrogation 9'
#    corp = Corpus('data/test-parsed')
#    tot = False
#    assert_equals(tot, tot)
#
#def test_edit1():
#    print 'Testing edit'
#    tot = False
#    assert_equals(tot, tot)

def test_interro_multiindex_tregex_justspeakers():
    import pandas as pd
    data = corp.interrogate('t', r'__ < /JJ.?/', just_speakers = ['each'])
    assert_equals(all(data.multiindex().index), all(pd.MultiIndex(levels=[[u'ANONYMOUS', u'TESTER', u'Total'], 
           [u'first', u'second', u'Total']],
           labels=[[0, 0, 1, 1], [0, 1, 0, 1]],
           names=[u'corpus', u'subcorpus'])))
