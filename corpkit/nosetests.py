from nose.tools import assert_equals
from corpkit import *

def test_import():
    from corpkit import Corpus

def test_corpus_class():
    p = 'test'
    unparsed = Corpus(p)
    assert_equals(p, unparsed.name)
 
def test_parse():
    print ('Testing parser')
    p = 'test'
    unparsed = Corpus(p)
    parsed = unparsed.parse()
    assert_equals(list([i.name for i in parsed.files]), ['intro.txt.xml', 'body.txt.xml'])