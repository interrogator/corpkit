
#   Building parsed corpora for discourse analysis
#   Author: Daniel McDonald

def correctspelling(path, newpath):
    """Feed this function an unstructured corpus and get a version with corrected spelling"""
    import enchant
    import codecs
    import os
    subdirs = [d for d in os.listdir(path) if os.path.isdir(d)]
    for subdir in subdirs:
        txtFiles = [f for f in os.listdir(os.path.join(path,subdir)) if f.endswith(".txt")]
        print 'Doing ' + subdir + ' ...'
        for txtFile in txtFiles: 
            d = enchant.Dict("en_UK")
            try:
                f = codecs.open(os.path.join(path,subdir,txtFile), "r", "utf-8")
            except IOError:
                print "Error reading the file, right filepath?"
                return
            textdata = f.read()
            textdata = unicode(textdata, 'utf-8')
            mispelled = [] # empty list. Gonna put mispelled words in here
            words = textdata.split()
            for word in words:
                # if spell check failed and the word is also not in
                # our mis-spelled list already, then add the word
                if d.check(word) == False and word not in mispelled:
                    mispelled.append(word)
            # print mispelled
            for mspellword in mispelled:
                mspellword_withboundaries = '\b' + str(mspellword) + '\b'
                #get suggestions
                suggestions=d.suggest(mspellword)
                #make sure we actually got some
                if len(suggestions) > 0:
                    # pick the first one
                    picksuggestion=suggestions[0]
                    picksuggestion_withboundaries = '\b' + str(picksuggestion) + '\b'

                textdata = textdata.replace(mspellword_withboundaries,picksuggestion_withboundaries)
            try:
                if not os.path.exists(fraser_corpus_corrected):
                    os.makedirs(fraser_corpus_corrected)
                fo=open(os.path.join(newpath, txtFile), "w")
            except IOError:
                print "Error"
                return 
            fo.write(textdata.encode("UTF-8"))
            fo.close()
    return


def dictmaker(path, dictname, dictpath = 'data/dictionaries'):
    """makes a pickle wordlist named dictname in dictpath"""
    import os
    import pickle
    import re
    import nltk
    from time import localtime, strftime
    from StringIO import StringIO
    import shutil
    from collections import Counter
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    # if no subcorpora, just do the dir passed in
    if len(sorted_dirs) == 0:
        sorted_dirs = [path]
    sorted_dirs.sort(key=int)
    try:
        if not os.path.exists(dictpath):
            os.makedirs(dictpath)
    except IOError:
        print "Error making " + dictpath + "/ directory."
    if os.path.isfile(os.path.join(dictpath, dictname)):
        raise ValueError(os.path.join(dictpath, dictname) + " already exists. Delete it or use a new filename.")
    time = strftime("%H:%M:%S", localtime())
    print time + ': Concordancing ... \n'
    p = ProgressBar(len(sorted_dirs))
    all_results = []
    query = r'ROOT < __'
    for d in sorted_dirs:
        if len(sorted_dirs) == 1:
            subcorp = d
        else:
            subcorp = os.path.join(path, d)

        if have_ipython:
            tregex_command = 'tregex.sh -o %s \'%s\' %s 2>/dev/null | grep -vP \'^\s*$\'' %(options, query, subcorp)
            results = get_ipython().getoutput(tregex_command)
        else:
            tregex_command = ["tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % subcorp]
            FNULL = open(os.devnull, 'w')
            results = subprocess.check_output(tregex_command, stderr=FNULL)
            results = os.linesep.join([s for s in results.splitlines() if s]).split('\n')
        for line in results:
            all_results.append(line)
    time = strftime("%H:%M:%S", localtime())
    print '\n\n' + time + ': Tokenising ' + str(len(all_results)) + ' lines ... \n'
    all_results = '\n'.join(all_results)
    text = unicode(all_results.lower(), 'utf-8', errors = 'ignore')
    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_tokenizer.tokenize(text)
    tokenized_sents = [nltk.word_tokenize(i) for i in sents]
    # flatten  allwords
    allwords = [item for sublist in tokenized_sents for item in sublist]
    # sort allwords
    allwords = sorted(allwords)
    time = strftime("%H:%M:%S", localtime())
    print time + ': Counting ' + str(len(allwords)) + ' words ... \n'
    # make a dict
    dictionary = Counter(allwords)
    with open(os.path.join(dictpath, dictname), 'wb') as handle:
        pickle.dump(dictionary, handle)
    time = strftime("%H:%M:%S", localtime())
    print time + ': Done! ' + dictname + ' created in ' + dictpath + '/'

def downloader():
    """download a bunch of urls and store in a local folder"""
    return downloaded

def text_extractor():
    """extract text from html/xml files"""
    return extracted_text

def structure_corpus():
    """structure a corpus in some kind of sequence"""
    print 'Done!'

def stanford_parse(unparsed_texts):
    """Parse a directory (recursively) with the Stanford parser..."""
    # 
    # make file list with os.walk
    # 
    # parse every file
    # 
    # connect old to new?
    # 
    # make metadata?
    # 
    print 'Done!'
