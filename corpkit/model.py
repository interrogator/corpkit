
from __future__ import division
from __future__ import print_function

import math
import os
import nltk

"""
TO DO:

Store show value in the Language Model, so that a new file could automatically be 

"""


class MultiModel(dict):
    
    def __init__(self, data, name='', order=3, **kwargs):
        import os
        from corpkit.other import load
        if isinstance(data, basestring):
            name = data
            if not name.endswith('.p'):
                name = name + '.p'
        self.name = name
        self.order = order
        self.kwargs = kwargs
        pth = os.path.join('models', self.name)
        if os.path.isfile(pth):
            data = load(name, loaddir='models')
        super(MultiModel, self).__init__(data, **kwargs)

    def score_text(self, text):
        import pandas as pd
        tempscores = {}
        for name, model in self.items():
            tempscores[name] = score_text_with_model(model, text, model.order)
        ser = pd.Series(tempscores)
        ser = ser.sort_values()
        ser['Corpus'] = ser.pop('Corpus')
        return ser

    def score_subcorpus(self, subcorpus_name):
        from collections import OrderedDict
        import pandas as pd
        tempscores = {}
        subc = self.get(subcorpus_name)
        for name, model in self.items():
            if name == subcorpus_name:
                continue
            tempscores[name] = score_subcorpus_with_model(model, subc, model.order)
        ser = pd.Series(tempscores)
        ser = ser.sort_values()
        ser['Corpus'] = ser.pop('Corpus')
        return ser

    def score_file(self, f, **kwargs):
        from collections import Counter
        if f.datatype != 'parse':
            f = f.parse(**kwargs)
        search = self.search
        exclude = self.exclude
        show = self.show
        kwgs = self.kwargs
        # add kwargs
        res = f.interrogate(search, 
                            exclude=exclude, 
                            show=show, 
                            language_model=True, 
                            **kwgs)
        dat = Counter(res.results.to_dict())
        return score_counter_with_model(self, dat)

    def score(self, data):
        """
        Determine data type and score
        """
        from corpkit.corpus import Subcorpus, File
        if isinstance(data, Subcorpus):
            return self.score_subcorpus(data.name)
        elif isinstance(data, basestring) and \
            hasattr(self, 'subcorpora') and \
            data in [i.name for i in self.subcorpora]:
            return self.score_subcorpus(data)
        elif isinstance(data, File):
            return self.score_file(data)
        elif isinstance(data, basestring) and \
            os.path.isfile(data):
            return self.score_file(data)
        elif isinstance(data, basestring) and not \
            os.path.exists(data):
            return self.score_text(data)
        # what else could it be?
        else:
            pass

    def score_subcorpora(self):
        import pandas as pd
        data = []
        for subname in self:
            ser = pd.Series(self.score_subcorpus(subname))
            ser.name = subname
            data.append(ser)
        df = pd.concat(data, axis=1)
        return df[sorted(df.columns)]

class LanguageModel(object):
    def __init__(self, order, alpha, sentences):
        self.order = order
        self.alpha = alpha
        if order > 1:
            self.backoff = LanguageModel(order - 1, alpha, sentences)
            self.lexicon = None
        else:
            self.backoff = None
            self.n = 0
        from collections import Counter
        self.counts = Counter()
        lexicon = set()
        for ngram, count in sentences.items():
            # the issue is that this stays stable when it's supposed
            # to change as per 'order'. to fix it, sent
            gram = tuple(ngram.split('-SPL-IT-'))
            wordNGrams = nltk.ngrams(gram, order)
            for wordNGram in wordNGrams:
                self.counts[wordNGram] += count
                # add to lexicon
                if order == 1:
                    lexicon.add(gram)
                    self.n += 1
        self.v = len(lexicon)

    def logprob(self, ngram):
        return math.log(self.prob(ngram))
    
    def prob(self, ngram):
        if self.backoff != None:
            freq = self.counts[ngram]
            backoffFreq = self.backoff.counts[ngram[1:]]
            if freq == 0:
                return self.alpha * self.backoff.prob(ngram[1:])
            else:
                return freq / backoffFreq
        else:
            # laplace smoothing to handle unknown unigrams
            return (self.counts[ngram] + 1) / (self.n + self.v)

def score_text_with_model(model, text, order):
    """
    Score text against a model
    """
    if isinstance(text, basestring):
        text = nltk.word_tokenize(text)
    grams = [tuple(i) for i in nltk.ngrams(text, order)]
    slogprob = 0
    for gram in grams:
        lb = model.logprob(gram)
        slogprob += lb
    return slogprob / len(text)

def score_subcorpus_with_model(model, subc, order):
    """
    Score text against a model
    """
    grams = []
    for gram, count in subc.counts.items():
        for _ in range(count):
            grams.append(tuple(gram))
    slogprob = 0
    for gram in grams:
        lb = model.logprob(gram)
        slogprob += lb
    return slogprob / len(subc.counts) * order

# todo
def score_counter_with_model(*args, **kwargs):
    pass

def _make_model_from_interro(self, name, **kwargs):
    import os
    print('kwargs', kwargs)
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
        tot = self.results.sum()[self.results.sum() > 0]
        tot.name = 'Corpus'
        to_iter_over.append(tot)
    for subc in list(to_iter_over):
        # get name for file
        if kwargs.get('just_totals'):
            subname = os.path.basename(self.query.get('corpus', 'untitled'))
        else:
            subname = subc.name
        dat = Counter(subc.to_dict())
        model = train(dat, subname, name, **kwargs)
        scores[subname] = model
    mm = MultiModel(scores, name=name, order=kwargs.pop('order', 3), **kwargs)
    if not os.path.isfile(os.path.join('models', name)):
        from corpkit.other import save
        save(scores, name, savedir = 'models')
    print('Done!\n')
    return mm

    #scores[subc.name] = score_text_with_model(trained)
    #return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def train(data, name, corpusname, **kwargs):
    order = kwargs.get('gramsize', 3)
    alpha = kwargs.get('alpha', 0.4)
    print('Making model: %s ... ' % name.replace('.p', ''))
    lm = LanguageModel(order, alpha, data)
    return lm

