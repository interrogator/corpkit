"""
scikit-learn stuff
"""

def tfidf(self, search={'w': 'any'}, show=['w'], **kwargs):
    """
    Generate TF-IDF vector representation of corpus
    using interrogate method
    """

    from sklearn.feature_extraction.text import TfidfVectorizer

    def tokeniser(s):
        return [s]

    vectoriser = TfidfVectorizer(input='content', tokenizer=tokeniser)

    matrices = {}

    res = self.interrogate(search=search,
                           show=show,
                           **kwargs).results

    def dupe_string(line):
        """
        turn {'corpus': 3, 'linguistics': 2} into
        'corpus corpus corpus linguistics linguistics'
        """
        return ''.join([(w + ' ') * line[w] \
               for w in line.index])

    ser = res.apply(dupe_string, axis=1)

    vec = vectoriser.fit_transform(ser.values)
    return vectoriser, vec
    #vec = vectoriser.transform(ser.values)
    #return vec
    
def translate_show_for_surprisal(show, gramsize):
    """
    Translate a simple show query into 
    """
    return show

def surprisal(self,
              search={'w', 'any'},
              exclude=False,
              show=['w'],
              gramsize,
              subcorpora='default',
              **kwargs):
    """
    A method to show surprisal for tokens (and averages for sents?)

    It involves two parts. First, we generate a model over the whole corpus
    Then, we score each sent by it

    It should then be possible to annotate the corpus with this info.
    """
    model = self.interrogate(search=search, exclude=exclude, show=show,
                             subcorpora=subcorpora, **kwargs)
    

def shannon(self):
    from corpkit.interrogation import Interrogation
    
    def to_apply(ser):
        data = []
        import numpy as np
        import pandas as pd
        for word in ser.index:
            if not ser[word]:
                probability = np.nan
                self_information = np.nan
            else:
                probability = ser[word] / float(1.0 * len(ser)) 
                self_information = np.log2(1.0/probability)
            data.append(self_information)
        return pd.Series(data, index=ser.index)
    
    res = getattr(self, 'results', self)
    appl = res.apply(to_apply, axis=1)
    ents = appl.sum(axis=1) / appl.shape[1]
    ents.name = 'Entropy'
    return Interrogation(results=appl, totals=ents)
