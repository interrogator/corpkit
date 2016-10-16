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
    Create a lemma Series from token+postag Series
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
 
def write_df_to_conll(df, newf, plain=False, stripped=False,
                      metadata=False, speaker_segmentation=False, offsets=False):
    """
    Turn a DF into CONLL-U text, and write to file, newf
    """
    import os
    from corpkit.constants import OPENER, PYTHON_VERSION
    from corpkit.conll import get_speaker_from_offsets
    outstring = ''
    sent_ixs = set(df.index.labels[0])
    for si in sent_ixs:
        si = si + 1

        outstring += '# sent_id %d\n' % si
        if metadata:
            metad = get_speaker_from_offsets(stripped,
                                             plain,
                                             offsets[si - 1],
                                             metadata_mode=metadata,
                                             speaker_segmentation=speaker_segmentation)
            
            for k, v in sorted(metad.items()):
                outstring += '# %s=%s\n' % (k, v)

        sent = df.loc[si:si]
        csv = sent.to_csv(None, sep='\t', header=False)
        outstring += csv + '\n'
    try:
        os.makedirs(os.path.dirname(newf))
    except OSError:
        pass
    with OPENER(newf, 'w') as newf:
        if PYTHON_VERSION == 2:
            outstring = outstring.encode('utf-8', errors='ignore')
        newf.write(outstring)

def new_fname(oldpath, inpath):
    """
    Determine output filename
    """
    import os
    newf, ext = os.path.splitext(oldpath)
    newf = newf + '.conll'
    if '-stripped' in newf:
        return newf.replace('-stripped', '-tokenised')
    else:
        return newf.replace(inpath, inpath + '-tokenised')

def process_meta(data, speaker_segmentation, metadata):
    import re
    from corpkit.constants import MAX_SPEAKERNAME_SIZE
    meta_offsets = []
    if metadata and speaker_segmentation:
        reg = re.compile(r'(^.{,%d}?:\s| <metadata (.*?)>)')
    elif metadata and not speaker_segmentation:
        reg = re.compile(r' <metadata (.*?)>')
    elif not metadata and not speaker_segmentation:
        reg = re.compile(r'^.{,%d}?:\s' % MAX_SPEAKERNAME_SIZE)

    #splt = re.split(reg, data)
    if speaker_segmentation or metadata:
        for i in re.finditer(reg, data):
            meta_offsets.append((i.start(), i.end()))
        for s, e in reversed(meta_offsets):
            data = data[:s] + data[e:]
    return data, meta_offsets

def plaintext_to_conll(inpath,
                       postag=False,
                       lemmatise=False,
                       lang='en',
                       metadata=False,
                       outpath=False,
                       nltk_data_path=False,
                       speaker_segmentation=False):
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

    from corpkit.build import get_filepaths
    fps = get_filepaths(inpath, 'txt')

    # IN THE SECTIONS BELOW, WE COULD ADD MULTILINGUAL
    # ANNOTATORS, PROVIDED THEY BEHAVE AS THE NLTK ONES DO

    # SENT TOKENISERS
    from nltk.tokenize.punkt import PunktSentenceTokenizer
    stoker = PunktSentenceTokenizer()
    s_tokers = {'en': stoker}
    sent_tokenizer = s_tokers.get(lang, stoker)

    # WORD TOKENISERS
    tokenisers = {'en': nltk.word_tokenize}
    tokeniser = tokenisers.get(lang, nltk.word_tokenize)

    # LEMMATISERS
    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr = WordNetLemmatizer()
        lemmatisers = {'en': lmtzr}
        lemmatiser = lemmatisers.get(lang, lmtzr)

    # POS TAGGERS
    if postag:
        # nltk.download('averaged_perceptron_tagger')
        postaggers = {'en': nltk.pos_tag}
        tagger = postaggers.get(lang, nltk.pos_tag)

    # iterate over files, make df of each, convert this
    # to conll and sent to new filename
    for f in fps:
        for_df = []
        data, enc = saferead(f)
        plain, enc = saferead(f.replace('-stripped', ''))
        #orig_data = data
        #data, offsets = process_meta(data, speaker_segmentation, metadata)
        #nest = []
        sents = sent_tokenizer.tokenize(data)
        soffs = sent_tokenizer.span_tokenize(data)
        toks = [tokeniser(sent) for sent in sents]
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
        write_df_to_conll(df, fo,
                          metadata=metadata,
                          plain=plain,
                          stripped=data,
                          speaker_segmentation=speaker_segmentation,
                          offsets=soffs)
        nsent = len(set(df.index.labels[0]))
        print('%s created (%d sentences)' % (fo, nsent))

    if '-stripped' in inpath:
        return inpath.replace('-stripped', '-tokenised')
    else:
        return inpath + '-tokenised'
