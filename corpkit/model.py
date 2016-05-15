
from __future__ import division
from __future__ import print_function

import math
import os
import nltk

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
        super(MultiModel, self).__init__(data)

    def score_text(self, text):
        import pandas as pd
        tempscores = {}
        for name, model in self.items():
            tempscores[name] = score_text_with_model(model, text, model.order)
        ser = pd.Series(tempscores)
        ser = ser.sort_values(ascending=False)
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
        ser = ser.sort_values(ascending=False)
        ser['Corpus'] = ser.pop('Corpus')
        return ser

    def score_file(self, f, **kwargs):
        from collections import Counter, OrderedDict
        import pandas as pd
        tempscores = {}
        if f.datatype != 'parse':
            f = f.parse(**kwargs)
        search = self.kwargs.pop('search', {'i': r'^1$'})
        exclude = self.kwargs.pop('exclude', False)
        show = self.kwargs.pop('show', ['w'])
        kwgs = self.kwargs
        # add kwargs
        res = f.interrogate(search, 
                            exclude=exclude, 
                            show=show, 
                            language_model=True, 
                            #printstatus=False,
                            **kwgs)
        dat = Counter(res.results.to_dict())
        for name, model in self.items():
            tempscores[name] = score_counter_with_model(model, dat, model.order, **kwargs)
        ser = pd.Series(tempscores)
        ser = ser.sort_values(ascending=False)
        ser['Corpus'] = ser.pop('Corpus')
        return ser

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




    def score_anything(self, data, **kwargs):
        """
        Score text against a model
        """
        # get data into a list of ngram tuples
        from collections import Counter, OrderedDict
        import pandas as pd
        from corpkit.corpus import Subcorpus, File

        order = self.order

        # get subcorpus
        if isinstance(data, Subcorpus) or (isinstance(data, basestring) and \
            hasattr(self, 'subcorpora') and data in [i.name for i in self.subcorpora]):
            print('is subcorpus')
            counts = self[data.name].counts
        #get file
        elif isinstance(data, File) or (isinstance(data, basestring) and \
            os.path.isfile(data)):
            print('is file')
            counts = self.turn_file_obj_into_counts(data)
        # get text
        elif isinstance(data, basestring) and not \
            os.path.exists(data):
            print('is text')
            counted_sents = Counter(nltk.sent_tokenize(data))
            counts = LanguageModel(order, kwargs.get('alpha', 0.4), counted_sents).counts
        # make ngrams
        #grams = []
        #for k, v in counts.items():
        #    for gram in [tuple(i) for i in nltk.ngrams(k, order)]:
        #        grams.append(gram)
        tempscores = {}
        for name, model in self.items():
            tempscores[name] = self.score_counts_against_model(counts, model)
        ser = pd.Series(tempscores)
        ser = ser.sort_values(ascending=False)
        ser['Corpus'] = ser.pop('Corpus')
        return ser

    def score_counts_against_model(self, counts, model):
        grams = []
        for k, v in counts.items():
            for _ in range(v):
                grams.append(k)
        slogprob = 0
        for gram in grams:
            lb = model.logprob(gram)
            slogprob += lb
        return slogprob / len(counts)



    def turn_file_obj_into_counts(self, data, *args, **kwargs):
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
        for subname in self:
            ser = pd.Series(self.score_subcorpus(subname))
            ser.name = subname
            data.append(ser)
        df = pd.concat(data, axis=1)
        return df[sorted(df.columns)]

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
    ngrams = []
    for gram, count in subc.counts.items():
        for _ in range(count):
            grams.append(tuple(gram))
    slogprob = 0
    for gram in grams:
        lb = model.logprob(gram)
        slogprob += lb
    return slogprob / len(subc.counts)

def score_counter_with_model(model, counts, order, **kwargs):
    grams = []
    ngrams = []
    for gram, count in counts.items():
        for _ in range(count):
            grams.append(tuple(gram.split('-SPL-IT-')))
    for gram in grams:
        ns = [tuple(i) for i in nltk.ngrams(gram, order)]
        for n in ns:
            ngrams.append(n)
    slogprob = 0
    for gram in ngrams:
        lb = model.logprob(gram)
        slogprob += lb
    return slogprob / len(counts)

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
        to_iter_over = [(name, self.results.ix[name]) for name in list(self.results.index)]
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
        model = train(dat, subname, name, **kwargs)
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

def train(data, name, corpusname, **kwargs):
    order = kwargs.get('gramsize', 3)
    alpha = kwargs.get('alpha', 0.4)
    print('Making model: %s ... ' % name.replace('.p', ''))
    lm = LanguageModel(order, alpha, data)
    return lm

