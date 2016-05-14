
from __future__ import division
from __future__ import print_function

import math
import os
import dill as pickle
import nltk

class MultiModel(dict):
    
    def __init__(self, data, name=False, gramsize=3, **kwargs):
        import os
        from corpkit.other import load
        if isinstance(data, basestring):
            name = data
            if not name.endswith('.p'):
                name = name + '.p'
        self.name = name
        self.gramsize = gramsize
        pth = os.path.join('models', self.name)
        if os.path.isfile(pth):
            data = load(name, loaddir='models')
        super(MultiModel, self).__init__(data, **kwargs)

    def score_text(self, text):
        scores = {}
        for name, model in self.items():
            scores[name] = score_text_with_model(model, text, self.gramsize)
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
            print(gram, count)
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

def score_text_with_model(model, text, gramsize):
    """
    Score text against a model
    """
    if isinstance(text, basestring):
        text = nltk.word_tokenize(text)
    grams = nltk.ngrams(text, gramsize)
    slogprob = 0
    for gram in grams:
        logprob = model.logprob(gram)
        slogprob += logprob
    return slogprob / len(text)

def _make_model_from_interro(self, name, **kwargs):
    import os
    from pandas import DataFrame, Series
    from collections import Counter
    from corpkit.other import load
    if not name.endswith('.p'):
        name = name + '.p'
    pth = os.path.join('models', name)
    if os.path.isfile(pth):
        return load(name, loaddir='models')
    scores = {}
    if not hasattr(self, 'results'):
        raise ValueError('Need results attribute to make language model.')
    # determine what we iterate over
    if kwargs.get('just_totals'):
        to_iter_over = [self.results.sum()[self.results.sum() > 0]]
    else:
        to_iter_over = [self.results.ix[subc][self.results.ix[subc] > 0] 
                        for subc in list(self.results.index)]
    for subc in list(to_iter_over):
        # get name for file
        if kwargs.get('just_totals'):
            subname = os.path.basename(self.query.get('corpus', 'untitled'))
        else:
            subname = subc.name
        dat = Counter(subc.to_dict())
        model = train(dat, subname, name)
        scores[subname] = model
    if not os.path.isfile(os.path.join('models', name)):
        from corpkit.other import save
        save(scores, name, savedir = 'models')
    print('Done!\n')
    return MultiModel(scores, name=name, gramsize=kwargs.get('gramsize', 3))

    #scores[subc.name] = score_text_with_model(trained)
    #return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def train(data, name, corpusname, **kwargs):
    order = kwargs.get('order', 3)
    alpha = kwargs.get('alpha', 0.4)
    print('Making model: %s ... ' % name.replace('.p', ''))
    lm = LanguageModel(order, alpha, data)
    return lm
