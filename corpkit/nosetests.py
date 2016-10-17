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
 
def test_parse():
    """Test CoreNLP parsing"""
    import shutil
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree(parsed_path)
    except:
        pass
    parsed = unparsed.parse(metadata=True)
    fnames = []
    for subc in parsed.subcorpora:
        for f in subc.files:
            fnames.append(f.name)
    shutil.move(parsed.path, parsed_path)
    assert_equals(fnames, ['intro.txt.conll', 'body.txt.conll'])

def test_tokenise():
    """Test the tokeniser, lemmatiser and POS tagger"""
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree(tok_path)
    except:
        pass
    tok = unparsed.tokenise(speaker_segmentation=True, lemmatise=True, postag=True, metadata=True)

    df = tok[0][0].document
    assert_equals(tok.name, 'test-tokenised')
    assert_equals(len(tok.subcorpora), 2)
    #assert_equals(list(df.columns), ['w', 'l', 'p'])
    assert_equals(list(df.index.names), ['s', 'i'])

def test_speak_parse():
    """Test CoreNLP parsing with speaker segmentation"""
    import shutil
    unparsed = Corpus(unparsed_path)
    try:
        shutil.rmtree(speak_path)
    except:
        pass
    parsed = unparsed.parse(speaker_segmentation=True, metadata=True)
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

def test_tok1_interro():
    """
    Check that indexes can be shown
    """
    corpus = Corpus(tok_path)
    res = corpus.interrogate(show=['s', 'i', 'l'])
    sortd = res.results[sorted(res.results.columns)]
    three = ['0/0/corpus', '0/0/this', '0/1/linguistics']
    assert_equals(list(sortd.columns)[:3], three)
    assert_equals(sortd.sum().sum(), 77)

def test_tok2_interro():
    """
    Check a tokenised corpus interrogation
    """
    corpus = Corpus(tok_path)
    res = corpus.interrogate(show=['w', 'l', 'p'], conc=True)
    assert_equals(res.results['is/be/vbz']['second'], 1)
    assert_equals(res.results['is/be/vbz']['first'], 2)
    assert_equals(str(res.results.ix[0].dtype), 'int64')
    flo = res.edit('%', 'self').results.iat[0,0].round(2)
    assert_equals(flo, 5.71)
    assert_equals(res.concordance.m.iloc[-1], 'work/work/nn')
    attributes = ['query', 'results', 'totals', 'visualise', 'edit', 'concordance']
    allat = all(getattr(res, i) is not None for i in attributes)
    assert_equals(allat, True)

def document_check():
    """
    Check that the document lazy attribute works
    """
    corpus = Corpus(speak_path)
    df = corpus[0][0].document
    fir = ['This', 'this', 'DT', 'O', 3, 'det', '0', '1']
    assert_equals(list(df.ix[1,1], fir))
    kys = list(df._metadata[5].keys())
    lst = ['year', 'test', 'parse', 'speaker', 'num']
    assert_equals(kys, lst)
    assert_equals(corpus.files, None)
    assert_equals(corpus.datatype, 'conll')

def test_conc_edit():
    """
    Make sure we can edit concordance lines
    """
    corpus = Corpus(speak_path)
    res = corpus.interrogate(show=['l','gl'], conc=True)
    assert_equals(len(res.concordance), 77)
    noling = len(res.concordance.edit(skip_entries='ling'))
    assert_equals(noling, 69)

def test_symbolic_subcorpora():
    """
    Check that we can make speaker into subcorpora
    """
    corpus = Corpus(speak_path, subcorpora='speaker')
    res = corpus.interrogate({'l': r'^[abcde]'})
    spks = ['ANONYMOUS', 'NEWCOMER', 'TESTER', 'UNIDENTIFIED']
    assert_equals(list(res.results.index), spks)

def test_symbolic_multiindex():
    """
    Check that we can make a named multiindex
    """
    subval = ['speaker', 'test']
    corpus = Corpus(speak_path, subcorpora=subval)
    res = corpus.interrogate({'l': r'^[abcde]'})
    test_poss = {'none', 'off', 'on'}
    assert_equals(set(res.results.index.levels[1]), test_poss)
    assert_equals(list(res.results.index.names), subval)

def check_skip_filt():
    """
    Check that we can make a skip filter
    """
    corpus = Corpus(speak_path, skip={'speaker': 'UNIDENTIFIED'})
    res = corpus.interrogate()
    assert_equals(len(res.results.columns), 47)

def check_just_filt():
    """
    Check that we can make a just filter
    """
    corpus = Corpus(speak_path, just={'speaker': 'UNIDENTIFIED'})
    res = corpus.interrogate()
    assert_equals(len(res.results.columns), 22)

def test_interpreter():
    """
    Test for errors in interpreter functionality
    """
    import os
    try:
        os.remove('saved_interrogations/test-speak-parsed-anylemma.p')
    except:
        pass
    from corpkit.env import interpreter
    try:
        os.makedirs('exported')
    except:
        pass
    try:
        os.makedirs('saved_interrogations')
    except:
        pass
    # this will make some data in exported/
    out = interpreter(fromscript='corpkit/interpreter_tests.cki')
    assert_equals(out, None)
    
def check_interpreter_res_csv():
    """
    Interpreter check made exported/res.csv---check it
    """
    import pandas as pd
    df = pd.read_csv('exported/res.csv', sep='\t', index_col=0)
    assert_equals(df.mean()['a'], 1.5)

def check_interpreter_conc_csv():
    """
    Interpreter check made exported/conc.csv---check it
    """
    import pandas as pd
    import shutil
    df = pd.read_csv('exported/conc.csv', sep='\t', index_col=0)
    shutil.rmtree('exported')
    assert_equals(df.shape, (77, 7))

def check_interpreter_saved_interro():
    """
    Interpreter made a pickled result. Check it
    """
    import pandas as pd
    import shutil    
    from corpkit import load
    dat = load('test-speak-parsed-anylemma')
    shutil.rmtree('saved_interrogations')
    assert hasattr(dat, 'results')
    assert hasattr(dat, 'totals')
    assert hasattr(dat, 'query')
    assert('concordancing' in dat.results)
    rel = dat.results.T / dat.totals
    assert_equals(rel.ix[0].sum().round(2), 0.19)

# test to write:
# annotation
# unannotation
# language model
# tgrep