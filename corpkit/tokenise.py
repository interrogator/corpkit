from __future__ import print_function

"""
Tokenise, POS tag and lemmatise a corpus, returning CONLL-U data
"""

def nested_list_to_pandas(toks):
    """
    Turn sent/word tokens into Series
    """
    import pandas as pd
    index = []
    words = []
    for si, sent in enumerate(toks, start=1):
        for wi, w in enumerate(sent, start=1):
            index.append((si, wi))
            words.append(w)
    ix = pd.MultiIndex.from_tuples(index)
    ser = pd.Series(words, index=ix)
    ser.name = 'w'
    return ser

def pos_tag_series(ser, tagger):
    """
    Create a POS tag Series from token Series
    """
    import nltk
    import pandas as pd
    tags = [i[-1] for i in nltk.pos_tag(ser.values)]
    tagser = pd.Series(tags, index=ser.index)
    tagser.name = 'p'
    return tagser

def lemmatise_series(words, postags, lemmatiser):
    """
    Create a lemma Series from token and postag Series
    """
    import nltk
    import pandas as pd
    tups = zip(words.values, postags.values)
    lemmata = []
    tag_convert = {'j': 'a'}
    
    for word, tag in tups:
        tag = tag_convert.get(tag[0].lower(), tag[0].lower())
        if tag in ['n', 'a', 'v', 'r']:
            lem = lemmatiser.lemmatize(word, tag)
        else:
            lem = word
        lemmata.append(lem)

    lems = pd.Series(lemmata, index=words.index)
    lems.name = 'l'
    return lems

def write_df_to_conll(df, fo, metadata=False):
    """
    Turn a DF into CONLL-U text, and write to file
    """
    import os
    from corpkit.constants import OPENER, PYTHON_VERSION
    outstring = ''
    sent_ixs = set(df.index.labels[0])
    for si in sent_ixs:
        si = si + 1
        outstring += '# sent_id %d\n' % si
        sent = df.loc[si:si]
        csv = sent.to_csv(None, sep='\t', header=False)
        outstring += csv + '\n'
    try:
        os.makedirs(os.path.dirname(fo))
    except OSError:
        pass
    with OPENER(fo, 'w') as fo:
        if PYTHON_VERSION == 2:
            outstring = outstring.encode('utf-8', errors='ignore')
        fo.write(outstring)


def new_fname(oldpath, inpath):
    """
    Determine output filename
    """
    import os
    newf, ext = os.path.splitext(f)
    newf = newf + '.conll'
    if '-stripped' in newf:
        return newf.replace('-stripped', '-tokenised')
    else:
        return newf.replace(inpath, inpath + '-tokenised')

def plaintext_to_conll(inpath, postag=False, lemmatise=False,
                       lang='en', metadata=False, outpath=False,
                       nltk_data_path=False, speaker_segmentation=False):
    """
    Take a plaintext corpus and sent/word tokenise.

    :param inpath: The corpus to read in
    :param postag: do POS tagging?
    :param lemmatise: do lemmatisation?
    :param lang: choose language for pos/lemmatiser (not implemented yet)
    :param metadata: add metadata to conll (not implemented yet)
    :param outpath: custom name for the resulting corpus
    :param speaker_segmentation: did the corpus has speaker names?
    """
    
    import nltk
    import shutil
    import pandas as pd
    from corpkit.process import saferead
    
    fps = get_filepaths(inpath, 'txt')

    # IN THE SECTIONS BELOW, WE COULD ADD MULTILINGUAL
    # ANNOTATORS, PROVIDED THEY BEHAVE AS THE NLTK ONES DO
    tokenisers = {'en': nltk.word_tokenize}
    tokeniser = tokenisers.get(lang, nltk.word_tokenize)

    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr = WordNetLemmatizer()
        lemmatisers = {'en': lmtzr}
        lemmatiser = lemmatisers.get(lang, lmtzr)

    if postag:
        # nltk.download('averaged_perceptron_tagger')
        postaggers = {'en': nltk.pos_tag}
        tagger = postaggers.get(lang, nltk.pos_tag)

    for f in fps:
        for_df = []
        data, enc = saferead(f)
        if metadata:
            raise NotImplementedError()
        toks = [tokeniser(sent) for sent in nltk.sent_tokenize(data)]
        ser = nested_list_to_pandas(toks)
        for_df.append(ser)
        if postag or lemmatise:
            postags = pos_tag_series(ser, tagger)
        if lemmatise:
            lemma = lemmatise_series(ser, postags, lemmatiser)
            for_df.append(lemma)
            for_df.append(postags)
        else:
            if postag:
                for_df.append(postags)
        df = pd.concat(for_df, axis=1)
        fo = new_fname(f, inpath)
        write_df_to_conll(df, fo, metadata=metadata)
        nsent = len(set(df.index.labels[0]))
        print('%s created (%d sentences)' % (fo, nsent))

    if '-stripped' in inpath:
        return inpath.replace('-stripped', '-tokenised')
    else:
        return inpath + '-tokenised'
