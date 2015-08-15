
def collocates(data, nbest = 30, window = 5):
    """Feed this data and get its collocations"""
    import nltk
    from nltk import collocations
    from nltk.collocations import BigramCollocationFinder
    import os
    import time
    from time import localtime, strftime
    from other import datareader
    from tests import check_dit
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
        
    # turn all sentences into long string
    time = strftime("%H:%M:%S", localtime())
    #if noprint is False:
    print "\n%s: Generating %d collocates ... \n" % (time, nbest)
    good = datareader(data)
    if type(good) != unicode:
        good = unicode(good.lower(), 'utf-8', errors = 'ignore')
    else:
        good = good.lower()
    # sent and word tokenise
    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_tokenizer.tokenize(good)
    tokenized_sents = [nltk.word_tokenize(i) for i in sents]
    allwords = []
    # for each sentence,
    for sent in tokenized_sents:
    # for each word,
        for word in sent:
        # make a list of all words
            allwords.append(word)
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(allwords, window_size=window)
    # should be consistent in stopwords
    ignored_words = nltk.corpus.stopwords.words('english')
    finder.apply_word_filter(lambda w: len(w) < 2 or w.lower() \
        in ignored_words or not w.isalnum())
    #unncessary?:
    finder.apply_freq_filter(2)
    results = sorted(finder.nbest(bigram_measures.raw_freq, nbest))
    listversion = []
    for index, thecollocation in enumerate(results):
        aslist = [index, thecollocation[0], thecollocation[1]]
        listversion.append(aslist)
    clear_output()
    return listversion
