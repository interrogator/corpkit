
from __future__ import division
from __future__ import print_function

import math
import os
import dill as pickle
import nltk

def _make_model_from_interro(self, **kwargs):
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

    for subc in list(to_iter_over):
        # get name for file
        if kwargs.get('just_totals'):
            name = os.path.basename(self.query.get('corpus', 'untitled'))
        else:
            name = subc.name
        dat = Counter(subc.to_dict())
        train(dat, name=name)
    print('Model created.')
    return model

        scores[subc.name] = score_text_with_model(trained)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

class LanguageModel(object):
    """
    A Language Model class
    """
    def __init__(self, order, alpha, token_counter):
        self.order = order
        self.alpha = alpha
        if order > 1:
            self.backoff = LangModel(order - 1, alpha, token_counter)
            self.lexicon = None
        else:
            self.backoff = None
            self.n = 0
        from collections import Counter
        self.ngramFD = Counter()
        lexicon = set()
        for i, words in enumerate(token_counter.keys()):
            #print('%d/%d\r' % (i + 1, len(token_counter)))
            wordNGrams = nltk.ngrams(words, order)
            for wordNGram in wordNGrams:
                self.ngramFD[wordNGram] += 1 * token_counter[words]
                if order == 1:
                    lexicon.add(wordNGram)
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

def train(self, name, **kwargs):
    """
    Load, make and save a model
    """
    ofile = '%s-model.p' % name
    d = os.path.basename(os.path.dirname(self.path))
    if not os.path.isdir('models'):
        os.makedirs('models')
    odir = os.path.join('models', d)
    if not os.path.isdir(odir):
        os.makedirs(odir)
    fp = os.path.join(odir, ofile)
    if os.path.isfile(fp):
        from corpkit.other import load
        return load(fp, loaddir='.')
    else:
        print('Making model: %s ... ' % name)

    lm = LanguageModel(kwargs.get('size', 3), kwargs.get('alpha', 0.4), sents)
    if not os.path.isfile(fp):
        with open(fp, 'wb') as fo:
            pickle.dump(lm, fo)
    return lm
