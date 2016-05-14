
from __future__ import division
from __future__ import print_function

import math
import os
import dill as pickle
import nltk

class MultiModel(dict):
    
    def __init__(self, data, name=False, **kwargs):
        import os
        from corpkit.other import load
        if isinstance(data, basestring):
            name = data
        self.name = name
        pth = os.path.join('models', self.name)
        if os.path.isdir(pth):
            data = {}
            from glob import glob
            glb = glob(os.path.join(pth, '*.p'))
            for f in glb:
                fname = os.path.splitext(os.path.basename(f))[0]
                data[fname] = load(f, loaddir='.')
        super(MultiModel, self).__init__(data, **kwargs)

    def score_text(self, text):
        scores = {}
        for name, model in self.items():
            scores[name] = score_text_with_model(model, text)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

class LanguageModel(object):
    """
    A Language Model class
    """
    def __init__(self, order, alpha, token_counter):
        self.order = order
        self.alpha = alpha
        if order > 1:
            self.backoff = LanguageModel(order - 1, alpha, token_counter)
            self.lexicon = None
        else:
            self.backoff = None
            self.n = 0
        from collections import Counter
        self.ngramFD = Counter()
        lexicon = set()
        # iterate over each ngram
        for ngram, count in token_counter.items():
            gram = tuple(ngram.split())
            self.ngramFD[gram] += 1 * count
            # add to lexicon
            if order == 1:
                lexicon.add(gram)
                self.n += 1
        self.v = len(lexicon)

    def logprob(self, ngram):
        """
        Log-probability for an n-gram
        """
        return math.log(self.prob(ngram))
  
    def prob(self, ngram):
        """
        Calculate probability
        """
        if self.backoff != None:
            freq = self.ngramFD[ngram]
            backoffFreq = self.backoff.ngramFD[ngram[1:]]
            if freq == 0:
                return self.alpha * self.backoff.prob(ngram[1:])
            else:
                return freq / backoffFreq
        else:
            # laplace smoothing to handle unknown unigrams
            return ((self.ngramFD[ngram] + 1) / (self.n + self.v))

def score_text_with_model(model, text):
    """
    Score text against a model
    """
    if isinstance(text, basestring):
        text = nltk.word_tokenize(text)
    wordTrigrams = nltk.trigrams(text)
    slogprob = 0
    for wordTrigram in wordTrigrams:
        logprob = model.logprob(wordTrigram)
        slogprob += logprob
    return slogprob / len(text)

def _make_model_from_interro(self, name, **kwargs):
    from pandas import DataFrame, Series
    from collections import Counter
    scores = {}
    if not hasattr(self, 'results'):
        raise ValueError('Need results attribute to make language model.')
    # determine what we iterate over
    if kwargs.get('just_totals'):
        to_iter_over = [self.results.sum()]
    else:
        to_iter_over = [self.results.ix[subc] for subc in list(self.results.index)]
    print('')
    for subc in list(to_iter_over):
        # get name for file
        if kwargs.get('just_totals'):
            subname = os.path.basename(self.query.get('corpus', 'untitled'))
        else:
            subname = subc.name
        dat = Counter(subc.to_dict())
        model = train(dat, subname, name)
        scores[subname] = model
    print('\nDone!\n')
    return MultiModel(scores, name=name)

    #scores[subc.name] = score_text_with_model(trained)
    #return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def train(data, name, corpusname, **kwargs):
    """
    Load, make and save a model
    """
    ofile = '%s.p' % name
    if not os.path.isdir('models'):
        os.makedirs('models')
    odir = os.path.join('models', corpusname)
    if not os.path.isdir(odir):
        os.makedirs(odir)
    fp = os.path.join(odir, ofile)
    if os.path.isfile(fp):
        from corpkit.other import load
        return load(fp, loaddir='.')
    else:
        print('Making model: %s ... ' % name)

    size = kwargs.get('size', 3)
    alpha = kwargs.get('alpha', 0.4)
    lm = LanguageModel(size, alpha, data)
    if not os.path.isfile(fp):
        with open(fp, 'wb') as fo:
            pickle.dump(lm, fo)
    return lm
