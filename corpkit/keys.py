"""corpkit: simple keyworder"""

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION

def keywords(target_corpus,
             reference_corpus='bnc.p',
             threshold=False,
             selfdrop=True,
             calc_all=True,
             measure='ll',
             sort_by=False,
             print_info=False,
             **kwargs):
    """Feed this function some target_corpus and get its keywords"""
    
    from pandas import DataFrame, Series
    from collections import Counter
    from corpkit.interrogation import Interrogation

    def data_to_dict(target_corpus):
        """turn Series/DataFrame into Counter"""
        if isinstance(target_corpus, Interrogation):
            if hasattr(target_corpus, 'results'):
                target_corpus = target_corpus.results
            else:
                target_corpus = target_corpus.totals
        if isinstance(target_corpus, Series):
            return Counter(target_corpus.to_dict())
        elif isinstance(target_corpus, DataFrame):
            return Counter(target_corpus.sum().to_dict())
        else:
            return Counter(target_corpus)

    def log_likelihood_measure(word_in_ref, word_in_target, ref_sum, target_sum):
        """calc log likelihood keyness"""
        import math
        neg = (word_in_target / float(target_sum)) < (word_in_ref / float(ref_sum))

        E1 = float(ref_sum)*((float(word_in_ref)+float(word_in_target)) / \
            (float(ref_sum)+float(target_sum)))
        E2 = float(target_sum)*((float(word_in_ref)+float(word_in_target)) / \
            (float(ref_sum)+float(target_sum)))
        
        if word_in_ref == 0:
            logaE1 = 0
        else:
            logaE1 = math.log(word_in_ref/E1)
        if word_in_target == 0:
            logaE2 = 0
        else:
            logaE2 = math.log(word_in_target/E2)
        score = float(2* ((word_in_ref*logaE1)+(word_in_target*logaE2)))
        if neg:
            score = -score
        return score

    def perc_diff_measure(word_in_ref, word_in_target, ref_sum, target_sum):
        """calculate using perc diff measure"""

        norm_target = float(word_in_target) / target_sum
        norm_ref = float(word_in_ref) / ref_sum
        # Gabrielatos and Marchi (2012) do it this way!
        if norm_ref == 0:
            norm_ref = 0.00000000000000000000000001
        return ((norm_target - norm_ref) * 100.0) / norm_ref

    def set_threshold(threshold):
        """define a threshold"""
        if threshold is False:
            return 0
        if threshold is True:
            threshold = 'm'
        if isinstance(threshold, STRINGTYPE):
            if threshold.startswith('l'):
                denominator = 800
            if threshold.startswith('m'):
                denominator = 400
            if threshold.startswith('h'):
                denominator = 100
            totwords = sum(loaded_ref_corpus.values())
            return float(totwords) / float(denominator)
        else:
            return threshold

    def calc_keywords(target_corpus, reference_corpus):
        """
        get keywords in target corpus compared to reference corpus
        this should probably become some kind of row-wise df.apply method
        """
        # get total num words in ref corpus
        key_scores = {}
        ref_sum = sum(reference_corpus.values())
        if isinstance(target_corpus, dict):
            target_sum = sum(target_corpus.values())
        if isinstance(target_corpus, Series):
            target_sum = target_corpus.sum()

        # get words to calculate
        if calc_all:
            wordlist = list(set(list(target_corpus.keys()) + list(reference_corpus.keys())))
        else:
            wordlist = list(target_corpus.keys())
        wordlist = [(word, reference_corpus[word]) for word in wordlist]
        for w, s in wordlist:
            if s < threshold:
                global skipped
                skipped += 1
                continue
            word_in_ref = reference_corpus.get(w, 0)
            word_in_target = target_corpus.get(w, 0)
            if kwargs.get('only_words_in_both_corpora'):
                if word_in_ref == 0:
                    continue
            score = measure_func(word_in_ref, word_in_target, ref_sum, target_sum)
            key_scores[w] = score
        return key_scores

    # load string ref corp 
    if isinstance(reference_corpus, STRINGTYPE):
        from corpkit.other import load
        ldr = kwargs.get('loaddir', 'dictionaries')
        reference_corpus = load(reference_corpus, loaddir=ldr)

    # if a corpus interrogation, assume we want results    
    if isinstance(target_corpus, Interrogation):
        reference_corpus = reference_corpus.results

    # turn data into dict
    loaded_ref_corpus = data_to_dict(reference_corpus)

    df = target_corpus
    index_names = list(df.index)
    results = {}
    threshold = set_threshold(threshold)
    global skipped
    skipped = 0

    # figure out which measure we're using
    if measure == 'll':
        measure_func = log_likelihood_measure
    elif measure == 'pd':
        measure_func = perc_diff_measure
    else:
        raise NotImplementedError("Only 'll' and 'pd' measures defined so far.")

    for subcorpus in index_names:
        if selfdrop:
            ref_calc = loaded_ref_corpus - Counter(reference_corpus.ix[subcorpus].to_dict())
        else:
            ref_calc = loaded_ref_corpus
        results[subcorpus] = calc_keywords(df.ix[subcorpus], ref_calc)

    if print_info:
        print('Skipped %d entries under threshold (%d)\n' % (skipped, threshold))

    df = DataFrame(results).T
    df.sort_index()
    if not sort_by:
        df = df[list(df.sum().sort_values(ascending=False).index)]
    return df
