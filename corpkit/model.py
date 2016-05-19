
from __future__ import division
from __future__ import print_function

import math
import os
import nltk


class LanguageModel(object):
    def __init__(self, order, alpha, sentences):
        """
        :param sentences: a Counter of unsplit sents"""
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
            gram = tuple(ngram.split('-spl-it-'))
            wordNGrams = nltk.ngrams(gram, order)
            for wordNGram in wordNGrams:
                self.counts[wordNGram] += count
                # add to lexicon
                if order == 1:
                    lexicon.add(gram)
                    self.n += 1
        self.v = len(lexicon)

    def _logprob(self, ngram):
        return math.log(self._prob(ngram))
    
    def _prob(self, ngram):
        if self.backoff != None:
            freq = self.counts[ngram]
            backoffFreq = self.backoff.counts[ngram[1:]]
            if freq == 0:
                return self.alpha * self.backoff._prob(ngram[1:])
            else:
                return freq / backoffFreq
        else:
            # laplace smoothing to handle unknown unigrams
            return (self.counts[ngram] + 1) / (self.n + self.v)

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
        if os.path.isfile(self.name):
            data = load(self.name, loaddir='models')
        else:
            pth = os.path.join('models', self.name)
            if os.path.isfile(pth):
                data = load(self.name, loaddir='models')
        super(MultiModel, self).__init__(data)

    def score(self, data, **kwargs):
        """
        Score text against a model
        """
        # get data into a list of ngram tuples
        from collections import Counter, OrderedDict
        import pandas as pd
        from corpkit.corpus import Subcorpus, File

        # get subcorpus
        if isinstance(data, Subcorpus):
            counts = self[data.name].counts
        elif isinstance(data, basestring) and data in self.keys():
            counts = self[data].counts 
        #get file
        elif isinstance(data, File) or (isinstance(data, basestring) and \
            os.path.isfile(data)):
            counts = self._turn_file_obj_into_counts(data)
        # get text
        elif isinstance(data, basestring) and not \
            os.path.exists(data):
            dat = []
            sents = nltk.sent_tokenize(data)
            for sent in sents:
                dat.append('-spl-it-'.join(nltk.word_tokenize(sent)))
            counted_sents = Counter(dat)
            counts = LanguageModel(self.order, kwargs.get('alpha', 0.4), counted_sents).counts
        tempscores = {}
        for name, model in self.items():
            tempscores[name] = self._score_counts_against_model(counts, model)
        ser = pd.Series(tempscores)
        ser = ser.sort_values(ascending=False)
        ser['Corpus'] = ser.pop('Corpus')
        return ser

    def _score_counts_against_model(self, counts, model):
        grams = []
        for k, v in counts.items():
            for _ in range(v):
                grams.append(k)
        slogprob = 0
        for gram in grams:
            lb = model._logprob(gram)
            slogprob += lb
        return slogprob / len(counts)

    def _turn_file_obj_into_counts(self, data, *args, **kwargs):
        if data.datatype != 'parse':
            data = data.parse(**kwargs)
        search = self.kwargs.pop('search', {'i': r'^1$'})
        exclude = self.kwargs.pop('exclude', False)
        show = self.kwargs.pop('show', ['w'])
        kwgs = self.kwargs
        # add kwargs
        res = data.interrogate(search, 
                               exclude=exclude, 
                               show=show, 
                               language_model=True, 
                               #printstatus=False,
                               **kwgs)
        model = _make_model_from_interro(res, self.name, nosave=True,singlemod=True, *args, **kwargs)
        return model.counts

    def score_subcorpora(self):
        import pandas as pd
        data = []
        for subname in self.keys():
            ser = pd.Series(self.score(subname))
            ser.name = subname
            data.append(ser)
        df = pd.concat(data, axis=1)
        return df[sorted(df.columns)]

def _make_model_from_interro(self, name, **kwargs):
    import os
    from pandas import DataFrame, Series
    from collections import Counter
    from corpkit.other import load
    nosave = kwargs.get('nosave')
    singlemod = kwargs.get('singlemod')
    if not nosave:
        if not name.endswith('.p'):
            name = name + '.p'
        pth = os.path.join('models', name)
        if os.path.isfile(pth):
            return load(name, loaddir='models')
    scores = {}
    if not hasattr(self, 'results'):
        raise ValueError('Need results attribute to make language model.')
    # determine what we iterate over
    if not singlemod:
        to_iter_over = [(nm, self.results.ix[nm][self.results.ix[nm] > 0]) \
                        for nm in list(self.results.index)]
    else:
        if isinstance(self.results, Series):
            to_iter_over = [(name, self.results)]
        else:
            to_iter_over = [(name, self.results.sum())]
    try:
        tot = self.results.sum()[self.results.sum() > 0]
        to_iter_over.append(('Corpus', tot))
    except:
        pass
    for subname, subc in list(to_iter_over):
        # get name for file
        dat = Counter(subc.to_dict())
        model = _train(dat, subname, name, **kwargs)
        scores[subname] = model
    if singlemod:
        return scores.values()[0]
    mm = MultiModel(scores, name=name, order=kwargs.pop('order', 3), **kwargs)
    if not os.path.isfile(os.path.join('models', name)):
        from corpkit.other import save
        save(scores, name, savedir='models')
    print('Done!\n')
    return mm

    #scores[subc.name] = score_text_with_model(trained)
    #return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def _train(data, name, corpusname, **kwargs):
    order = kwargs.get('gramsize', 3)
    alpha = kwargs.get('alpha', 0.4)
    print('Making model: %s ... ' % name.replace('.p', ''))
    lm = LanguageModel(order, alpha, data)
    return lm

