
#   Building parsed corpora for discourse analysis
#   Author: Daniel McDonald


def dictmaker(path, 
              dictname,
              query = 'any',
              dictpath = 'data/dictionaries',
              lemmatise = False,
              just_content_words = False):
    """makes a pickle wordlist named dictname in dictpath"""
    import os
    import pickle
    import re
    import nltk
    from time import localtime, strftime
    from StringIO import StringIO
    import shutil
    from collections import Counter
    from corpkit.progressbar import ProgressBar
    from corpkit.other import tregex_engine
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    
    if lemmatise:
        dictname = dictname + '-lemmatised'
    if not dictname.endswith('.p'):
        dictname = dictname + '.p'

    # allow direct passing of dirs
    path_is_list = False
    if type(path) == str:
        sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    # if no subcorpora, just do the dir passed in
        if len(sorted_dirs) == 0:
            sorted_dirs = [path]
    elif type(path) == list:
        path_is_list = True
        sorted_dirs = sorted(path)
        if type(sorted_dirs[0]) == int:
            sorted_dirs = [str(d) for d in sorted_dirs]

    try:
        sorted_dirs.sort(key=int)
    except:
        pass
    try:
        if not os.path.exists(dictpath):
            os.makedirs(dictpath)
    except IOError:
        print "Error making " + dictpath + "/ directory."
    while os.path.isfile(os.path.join(dictpath, dictname)):
        time = strftime("%H:%M:%S", localtime())
        selection = raw_input('\n%s: %s already exists in %s.\n' \
               '          You have the following options:\n\n' \
               '              a) save with a new name\n' \
               '              b) delete %s\n' \
               '              c) exit\n\nYour selection: ' % (time, dictname, dictpath, os.path.join(dictpath, dictname)))
        if 'a' in selection:
            sel = raw_input('\nNew save name: ')
            dictname = sel
            if lemmatise:
                dictname = dictname.replace('-lemmatised.p', '')
                dictname = dictname + '-lemmatised'
            if not dictname.endswith('.p'):
                dictname = dictname + '.p'
        elif 'b' in selection:
            os.remove(os.path.join(dictpath, dictname))
        elif 'c' in selection:
            print ''
            return
        else:
            as_str = str(selection)
            print '          Choice "%s" not recognised.' % selection

    time = strftime("%H:%M:%S", localtime())
    print '\n%s: Extracting words from files ... \n' % time
    p = ProgressBar(len(sorted_dirs))
    all_results = []
    
    # translate any query---though at the moment there is no need to use any 
    # query other than 'any' ...
    if query == 'any':
        if lemmatise:
            query = r'__ <# (__ !< __)'
        else:
            query = r'__ !< __'
    
    if lemmatise:
        options = ['-o']
    else:
        options = ['-t', '-o']
    
    allwords = []

    for index, d in enumerate(sorted_dirs):
        p.animate(index)
        if not path_is_list:
            if len(sorted_dirs) == 1:
                subcorp = d
            else:
                subcorp = os.path.join(path, d)
        else:
            subcorp = d

        # check query first time through    
        if index == 0:
            trees_found = tregex_engine(corpus = subcorp, check_for_trees = True)
            if not trees_found:
                lemmatise = False
                dictname = dictname.replace('-lemmatised', '')
        if trees_found:
            results = tregex_engine(corpus = subcorp, options = options, query = query, 
                                    lemmatise = lemmatise,
                                    just_content_words = just_content_words) 

            for result in results:
                allwords.append(result)  

        else:
            for f in os.listdir(subcorp):
                raw = unicode(open(os.path.join(subcorp, f)).read(), 'utf-8', errors = 'ignore')
                sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
                sents = sent_tokenizer.tokenize(raw)
                tokenized_sents = [nltk.word_tokenize(i) for i in sents]
                for sent in tokenized_sents:
                    for w in sent:
                        allwords.append(w.lower()) 

    # make a dict
    p.animate(len(sorted_dirs))

    dictionary = Counter(allwords)

    with open(os.path.join(dictpath, dictname), 'wb') as handle:
        pickle.dump(dictionary, handle)
    time = strftime("%H:%M:%S", localtime())
    print '\n\n' + time + ': Done! ' + dictname + ' created in ' + dictpath + '/'

def get_urls(url, criteria = False, remove = True):
    """Get a list of all urls within an html document"""
    from bs4 import BeautifulSoup
    configure_ipython_beautifulsoup(show_html=True, show_css=True, show_js=False)
    soup = p(url)
    urls = []
    if criteria:
        import re
        regex = re.compile(criteria)
    for link in soup.find_all('a'):
        a_url = link.get('href')
        if a_url.startswith('#'):
            continue
        if a_url.startswith('/'):
            a_url = url + a_url
        if criteria:
            if re.search(regex, a_url):
                if not remove:
                    urls.append(a_url)
            else:
                if remove:
                    urls.append(a_url)
        else:
            urls.append(a_url)
    urls.sort()
    filtered_urls = filter(None, urls)
    unique_urls = sorted(set(filtered_urls))
    return unique_urls


def downloader(url_list, new_path = 'html', wait = 5):
    """download a bunch of urls and store in a local folder"""
    import urllib
    import time
    import os
    from time import localtime, strftime
    from corpkit.progressbar import ProgressBar
    thetime = strftime("%H:%M:%S", localtime())
    print "\n%s: Attempting to download %d URLs with %d seconds wait-time ... \n" % (thetime, len(url_list), wait)
    p = ProgressBar(len(urls))
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    paths = []
    for index, url in enumerate(url_list):
        p.animate(index)
        base = os.path.basename(url)
        new_filename = os.path.join(new_path, base)
        paths.append(new_filename)
        urllib.urlretrieve(url, new_filename)
        time.sleep(wait)
    p.animate(len(url_list))
    num_downloaded = len(paths)
    thetime = strftime("%H:%M:%S", localtime())
    print '\n\n%s: Done! %d files downloaded.' % (thetime, num_downloaded)
    return paths

def simple_text_extractor(html, stopwords = 'English'):
    """extract text from html/xml files using justext"""
    import requests
    import justext
    import os
    import copy
    # if on hard disk:
    if type(html) != list:
        html_files = [copy.deepcopy(html)]
    else:
        html_files = copy.deepcopy(html)
    output = []
    for html in html_files:
        if os.path.isfile(html):
            f = open(html)
            raw_html_text = f.read()
        # if it's a web address
        elif html.startswith('http'):
            response = requests.get(html)
            raw_html_text = response.content
        # if it's already html text:
        else:
            raw_html_text = copy.deepcopy(html)
        paragraphs = justext.justext(raw_html_text, justext.get_stoplist(stopwords))
        text = []
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate:
                text.append(paragraph.text)
        text = '\n'.join(text)
        metadata = os.path.basename(html)
        tup = (text, metadata)
        output.append(tup)
    return output




def practice_run(path_to_html_file):
    import os
    import warnings
    from bs4 import BeautifulSoup
    if type(path_to_html_file) == list:
        path_to_html_file = str(path_to_html_file[0])
    f = open(path_to_html_file)
    raw = f.read()
    soup = BeautifulSoup(raw)
    try:
        text = get_text(soup)
    except:
        function_defined = False
        from corpkit.build import simple_text_extractor
        simple_text_extractor(path_to_html_file)
    try:
        metadata = get_metadata(soup)
    except:
        warnings.warn('get_metadata function not defined. Using filename as metadata.')
        metadata = os.path.basename(path_to_html_file)
    print 'text: %s\n\nmetadata: %s' %(text, metadata)


def souper(corpus_path):
    """The aim is to make a tuple of (text, metadata)"""
    import os
    from bs4 import BeautifulSoup
    for root, dirs, files in os.walk(corpus_path, topdown=True):
        for name in files:
            filepath = os.path.join(root, name)
            f = open(filepath)
            raw = f.read()
            soup = BeautifulSoup(raw)


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
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                fo=open(os.path.join(newpath, txtFile), "w")
            except IOError:
                print "Error"
                return 
            fo.write(textdata.encode("UTF-8"))
            fo.close()
    return


def stanford_parse(corpus_path):
    """Parse a directory (recursively) with the Stanford parser..."""
    import os
    import ast
    try:
        from corenlp import StanfordCoreNLP
    except:
        raise ValueError("CoreNLP not installed.")
    path_part, corpus_name = os.path.split(corpus_path)
    new_corpus_folder = 'parsed_%s' % corpus_name
    new_corpus_path = os.path.join(path_part, new_corpus_folder)
    if not os.path.exists(new_corpus_path):
        os.makedirs(new_corpus_path)
    corenlp = StanfordCoreNLP()
    files = os.listdir(corpus_path)
    for root, dirs, files in os.walk(corpus_path, topdown=True):
        for name in files:
            filepath = os.path.join(root, name)
            f = open(filepath)
            raw = f.read()
            parsed_text = ast.literal_eval(corenlp.parse(raw))
            for index, sent in enumerate(parsed_text['sentences']):
                syntax_tree = sent['parsetree']
                plain_text = sent['text']
            subcorpus_path = os.path.join(new_corpus_path, subcorpus_name)
            if not os.path.exists(subcorpus_path):
                os.makedirs(subcorpus_path)


def structure_corpus(path_to_files, new_corpus_name = 'structured_corpus'):
    """structure a corpus in some kind of sequence"""
    import os
    import shutil
    base = os.path.basename(path_to_files)
    new_corpus_name = 'structured_' + base
    if not os.path.isdir(path_to_files):
        raise ValueError('Directory not found: %s' % path_to_files)
    if not os.path.exists(new_corpus_name):
        os.makedirs(new_corpus_name)
    files = os.listdir(path_to_files)
    for f in files:
        filepath = os.path.join(path_to_files, f)
        
        subcorpus_name = 'what goes here?'
        subcorpus_path = os.path.join(new_corpus_name, subcorpus_name)
        if not os.path.exists(subcorpus_path):
            os.makedirs(subcorpus_path)
        shutil.copy(filepath, subcorpus_path)
    print 'Done!'

def edit_metadata():
    return edited

def stanford_parse(data, corpus_name = 'corpus'):
    from time import localtime, strftime
    thetime = strftime("%H:%M:%S", localtime())
    print "\n%s: Initialising CoreNLP... \n" % thetime
    import os
    import ast
    try:
        from corenlp import StanfordCoreNLP
    except:
        raise ValueError("CoreNLP not installed.")
    from corpkit.progressbar import ProgressBar
    corenlp = StanfordCoreNLP()
    if not os.path.exists(corpus_name):
        os.makedirs(corpus_name)
    p = ProgressBar(len(data))
    for index, datum in enumerate(data):
        p.animate(index)
        text = datum[0]
        metadata = datum[1]
        number_of_zeroes = len(str(len(data))) - 1
        filename = str(index).zfill(number_of_zeroes) + '.txt' 
        file_data = []
        parsed_text = ast.literal_eval(corenlp.parse(text))
        trees = []
        raw_texts = []
        for index, sent in enumerate(parsed_text['sentences']):
            syntax_tree = sent['parsetree']
            plain_text = sent['text']
            trees.append(syntax_tree)
            raw_texts.append(plain_text)
                    #subcorpus_path = os.path.join(new_corpus_path, subcorpus_name)
        file_data = ['<raw>' + '\n'.join(raw_texts) + '\n</raw>', '<parse>' + '\n'.join(trees) + '\n</parse>', ]
        if not os.path.exists(os.path.join(corpus_name, metadata)):
            os.makedirs(os.path.join(corpus_name, metadata))
        try:
            fo=open(os.path.join(corpus_name, metadata, filename),"w")
        except IOError:
            print "Error writing file."
        fo.write('\n'.join(file_data))
        fo.close()
    p.animate(len(data))
    print 'Done!'
