#!/usr/bin/python

#   Building parsed corpora for discourse analysis
#   Author: Daniel McDonald


def dictmaker(path, 
              dictname,
              query = 'any',
              dictpath = 'data/dictionaries',
              lemmatise = False,
              just_content_words = False,
              use_dependencies = False):
    """makes a pickle wordlist named dictname in dictpath"""
    import corpkit
    import os
    import pickle
    import re
    import nltk
    from time import localtime, strftime
    from StringIO import StringIO
    import shutil
    from collections import Counter
    from textprogressbar import TextProgressBar
    from other import tregex_engine
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
    one_big_corpus = False
    if type(path) == str:
        sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    # if no subcorpora, just do the dir passed in
        if len(sorted_dirs) == 0:
            one_big_corpus = True
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

    # all this just to get a list of files and make a better progress bar
    if use_dependencies:
        counts = []
        for d in sorted_dirs:
            if not one_big_corpus:
                subcorpus = os.path.join(path, d)
            else:
                subcorpus = path
            if use_dependencies:
                files = [f for f in os.listdir(subcorpus) if f.endswith('.xml')]
            else:
                files = [f for f in os.listdir(subcorpus)]
            counts.append(len(files))
        num_files = sum(counts)
        c = 0
        p = TextProgressBar(num_files)
    else:
        p = TextProgressBar(len(sorted_dirs))

    def tokener(xmldata):
        import corpkit
        """print word, using good lemmatisation"""
        from bs4 import BeautifulSoup
        import gc
        open_classes = ['N', 'V', 'R', 'J']
        result = []
        just_good_deps = SoupStrainer('tokens')
        soup = BeautifulSoup(xmldata, parse_only=just_good_deps)   
        for token in soup.find_all('token'):
            word = token.word.text
            query = re.compile(r'.*')
            if re.search(query, word):
                if lemmatise:
                    word = token.lemma.text
                    if just_content_words:
                        if not token.pos.text[0] in open_classes:
                            continue        
                result.append(word)
        # attempt to stop memory problems. 
        # not sure if this helps, though:
        soup.decompose()
        soup = None
        data = None
        gc.collect()
        return result
    
    # translate 'any' query
    if query == 'any':
        if lemmatise:
            query = r'__ <# (__ !< __)'
        else:
            query = r'__ !< __'
    
    if lemmatise:
        options = ['-o']
    else:
        options = ['-t', '-o']
    
    if use_dependencies:
        from bs4 import BeautifulSoup, SoupStrainer
        if query == 'any':
            query = r'.*'
        query = re.compile(query)

    allwords = []

    for index, d in enumerate(sorted_dirs):
        if not use_dependencies:
            p.animate(index)
        if not path_is_list:
            if len(sorted_dirs) == 1:
                subcorp = d
            else:
                subcorp = os.path.join(path, d)
        else:
            subcorp = d

        # check query first time through    
        if not use_dependencies:
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

        elif use_dependencies:
            regex_nonword_filter = re.compile("[A-Za-z]")
            results = []
            fs = [os.path.join(subcorp, f) for f in os.listdir(subcorp)]
            for f in fs:
                p.animate(c, str(c) + '/' + str(num_files))
                c += 1
                data = open(f).read()
                result_from_a_file = tokener(data)
                for w in result_from_a_file:
                    if re.search(regex_nonword_filter, w):
                        allwords.append(w.lower())

        if not use_dependencies:
            if not trees_found:
                for f in os.listdir(subcorp):
                    raw = unicode(open(os.path.join(subcorp, f)).read(), 'utf-8', errors = 'ignore')
                    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
                    sents = sent_tokenizer.tokenize(raw)
                    tokenized_sents = [nltk.word_tokenize(i) for i in sents]
                    for sent in tokenized_sents:
                        for w in sent:
                            allwords.append(w.lower()) 

    #100%
    p.animate(len(sorted_dirs))
    
    # make a dict
    dictionary = Counter(allwords)

    with open(os.path.join(dictpath, dictname), 'wb') as handle:
        pickle.dump(dictionary, handle)
    time = strftime("%H:%M:%S", localtime())
    print '\n\n' + time + ': Done! ' + dictname + ' created in ' + dictpath + '/'

def get_urls(url, criteria = False, remove = True):
    import corpkit
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
    import corpkit
    """download a bunch of urls and store in a local folder"""
    import urllib
    import time
    import os
    from time import localtime, strftime
    from textprogressbar import TextProgressBar
    thetime = strftime("%H:%M:%S", localtime())
    print "\n%s: Attempting to download %d URLs with %d seconds wait-time ... \n" % (thetime, len(url_list), wait)
    p = TextProgressBar(len(urls))
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
    import corpkit
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
    import corpkit
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
        from build import simple_text_extractor
        simple_text_extractor(path_to_html_file)
    try:
        metadata = get_metadata(soup)
    except:
        warnings.warn('get_metadata function not defined. Using filename as metadata.')
        metadata = os.path.basename(path_to_html_file)
    print 'text: %s\n\nmetadata: %s' %(text, metadata)


def souper(corpus_path):
    import corpkit
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
    import corpkit
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

def structure_corpus(path_to_files, new_corpus_name = 'structured_corpus'):
    import corpkit
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

def download_large_file(proj_path, url, actually_download = True, root = False, **kwargs):
    import corpkit
    """download corenlp to proj_path"""
    import os
    import urllib2
    from time import localtime, strftime
    from textprogressbar import TextProgressBar
    file_name = url.split('/')[-1]
    home = os.path.expanduser("~")
    if 'stanford' in url:
        downloaded_dir = os.path.join(home, 'corenlp')
    else:
        downloaded_dir = os.path.join(home, 'temp')
    fullfile = os.path.join(downloaded_dir, file_name)
    try:
        os.makedirs(downloaded_dir)
    except OSError:
        if 'stanford-corenlp-full-2015-04-20.zip' in os.listdir(downloaded_dir):
            import zipfile
            the_zip_file = zipfile.ZipFile(fullfile)
            ret = the_zip_file.testzip()
            if ret is None:
                return downloaded_dir, fullfile
            else:
                os.remove(fullfile)
    
    if actually_download:
        try:
            u = urllib2.urlopen(url)
            f = open(fullfile, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            if root:
                root.update()
            if 'note' in kwargs.keys():
                kwargs['note'].progvar.set(0)
            else:
                p = TextProgressBar(int(file_size))
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Downloading ... ' % thetime
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
                #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                #status = status + chr(8)*(len(status)+1)
                if 'note' in kwargs.keys():
                    kwargs['note'].progvar.set(file_size_dl * 100.0 / int(file_size))
                else:
                    p.animate(file_size_dl)
                if root:
                    root.update()
            if 'note' in kwargs.keys():  
                kwargs['note'].progvar.set(100)
            else:    
                p.animate(int(file_size))
        except:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Downloaded failed: bad connection.' % time
            f.close()
            if root:
                root.update()
            return
        time = strftime("%H:%M:%S", localtime())
        print '%s: Downloaded successully.' % time
        f.close()
    return downloaded_dir, fullfile

def extract_cnlp(fullfilepath, corenlppath = False, root = False):
    import corpkit
    """extract corenlp"""
    import zipfile
    import os
    from time import localtime, strftime
    time = strftime("%H:%M:%S", localtime())
    print '%s: Extracting CoreNLP files ...' % time
    if root:
        root.update()
    if corenlppath is False:
        home = os.path.expanduser("~")
        corenlppath = os.path.join(home, 'corenlp')
    with zipfile.ZipFile(fullfilepath) as zf:
        zf.extractall(corenlppath)
    time = strftime("%H:%M:%S", localtime())
    print '%s: CoreNLP extracted. ' % time

def get_corpus_filepaths(proj_path, corpuspath):
    import corpkit
    import fnmatch
    import os
    matches = []
    for root, dirnames, filenames in os.walk(corpuspath):
        for filename in fnmatch.filter(filenames, '*.txt'):
            matches.append(os.path.join(root, filename))
    if len(matches) == 0:
        return False
    matchstring = '\n'.join(matches)
    with open(os.path.join(proj_path, 'data', 'corpus-filelist.txt'), "w") as f:
        f.write(matchstring)
    return os.path.join(proj_path, 'data', 'corpus-filelist.txt')

def check_jdk():
    import corpkit
    import subprocess
    from subprocess import PIPE, STDOUT, Popen
    p = Popen(["java", "-version"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if 'java version "1.8' in stderr:
        return True
    else:
        #print "Get the latest Java from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html"
        return False

def parse_corpus(proj_path, corpuspath, filelist, corenlppath = False, operations = False,
                 only_tokenise = False, root = False, stdout = False, **kwargs):
    import corpkit
    import subprocess
    from subprocess import PIPE, STDOUT, Popen
    import os
    import sys
    import chardet
    from time import localtime, strftime
    import time
    
    if not only_tokenise:
        if not check_jdk():
            print 'Need latest Java.'
            return

    # add nltk to path
    td = {}
    from corpkit.other import add_nltk_data_to_nltk_path
    if 'note' in kwargs.keys():
        td['note'] = kwargs['note']
    add_nltk_data_to_nltk_path(**td)

    basecp = os.path.basename(corpuspath)
    if only_tokenise:
        new_corpus_path = os.path.join(proj_path, 'data', '%s-tokenised' % basecp)
    else:
        new_corpus_path = os.path.join(proj_path, 'data', '%s-parsed' % basecp)
    if not os.path.isdir(new_corpus_path):
        os.makedirs(new_corpus_path)
    else:
        fs = os.listdir(new_corpus_path)
        if not only_tokenise:
            if any([f.endswith('.xml') for f in fs]):
                print 'Folder containing xml already exists: "%s-parsed"' % basecp
                return False
        else:
            if any([f.endswith('.txt') for f in fs]):
                print 'Folder containing tokens already exists: "%s-tokenised"' % basecp  
                return False          
    #javaloc = os.path.join(proj_path, 'corenlp', 'stanford-corenlp-3.5.2.jar:stanford-corenlp-3.5.2-models.jar:xom.jar:joda-time.jar:jollyday.jar:ejml-0.23.jar')
    cwd = os.getcwd()
    if corenlppath is False:
        home = os.path.expanduser("~")
        corenlppath = os.path.join(home, 'corenlp')
        find_install = [d for d in os.listdir(corenlppath) \
                   if os.path.isdir(os.path.join(corenlppath, d)) \
                   and os.path.isfile(os.path.join(corenlppath, d, 'jollyday.jar'))]
        if len(find_install) > 0:
            corenlppath = os.path.join(corenlppath, find_install[0])
        else:
            print 'No parser found.'
            return

    if not only_tokenise:
        os.chdir(corenlppath)
        root.update_idletasks()
        reload(sys)
        import os
        import time
        if operations is False:
            operations = 'tokenize,ssplit,pos,lemma,ner,parse,dcoref'
        num_files_to_parse = len([l for l in open(filelist, 'r').read().splitlines() if l])
        proc = subprocess.Popen(['java', '-cp', 
                     'stanford-corenlp-3.5.2.jar:stanford-corenlp-3.5.2-models.jar:xom.jar:joda-time.jar:jollyday.jar:ejml-0.23.jar', 
                     '-Xmx2g', 
                     'edu.stanford.nlp.pipeline.StanfordCoreNLP', 
                     '-annotators', 
                     operations, 
                     '-filelist', filelist,
                     '-noClobber',
                     '-outputDirectory', new_corpus_path, 
                     '--parse.flags', ' -makeCopulaHead'], stdout=sys.stdout)
        #p = TextProgressBar(num_files_to_parse)
        while proc.poll() is None:
            sys.stdout = stdout
            thetime = strftime("%H:%M:%S", localtime())
            num_parsed = len([f for f in os.listdir(new_corpus_path) if f.endswith('.xml')])  
            if num_parsed == 0:
                print '%s: Initialising parser ... ' % (thetime)
            if num_parsed > 0 and num_parsed <= num_files_to_parse:
                print '%s: Parsing file %d/%d ... ' % (thetime, num_parsed + 1, num_files_to_parse)
                if 'note' in kwargs.keys():
                    kwargs['note'].progvar.set((num_parsed) * 100.0 / num_files_to_parse)
                #p.animate(num_parsed - 1, str(num_parsed) + '/' + str(num_files_to_parse))
            if root:
                root.update()
                time.sleep(1)
    else:

        # tokenise each file
        from nltk import word_tokenize as tokenise
        import pickle
        fs = open(filelist).read().splitlines()
        dirs = sorted(list(set([os.path.basename(os.path.dirname(f)) for f in fs])))
        if len(dirs) == 0:
            one_big_corpus = True
        else:
            one_big_corpus = False
        if any(os.path.isdir(os.path.join(new_corpus_path, d)) for d in dirs):
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Directory already exists. Delete it if need be.' % thetime
            return
        for d in dirs:
            os.makedirs(os.path.join(new_corpus_path, d))
        nfiles = len(fs)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Tokenising ... ' % (thetime)
        for index, f in enumerate(fs):
            data = open(f).read()
            enc = chardet.detect(data)
            enc_text = unicode(data, enc['encoding'], errors = 'ignore')
            tokens = tokenise(enc_text)
            thedir = os.path.basename(os.path.dirname(f))
            newname = os.path.basename(f).replace('.txt', '-tokenised.p')
            if one_big_corpus:
                pth = os.path.join(new_corpus_path, newname)
            else:
                pth = os.path.join(new_corpus_path, thedir, newname)
            with open(pth, "wb") as fo:
                pickle.dump(tokens, fo)
            if 'note' in kwargs.keys():
                kwargs['note'].progvar.set((index + 1) * 100.0 / nfiles)
            if root:
                root.update()

    #p.animate(num_files_to_parse)
    if 'note' in kwargs.keys():
        kwargs['note'].progvar.set(100)
    sys.stdout = stdout
    print 'Parsing finished. Moving parsed files into place ...'
    os.chdir(proj_path)
    return new_corpus_path

def move_parsed_files(proj_path, corpuspath, new_corpus_path):
    import corpkit
    import shutil
    import os
    import fnmatch
    cwd = os.getcwd()
    basecp = os.path.basename(corpuspath)
    dir_list = []

    # go through old path, make file list
    for path, dirs, files in os.walk(corpuspath):
        for bit in dirs:
            # is the last bit of the line below windows safe?
            dir_list.append(os.path.join(path, bit).replace(corpuspath, '')[1:])

    os.chdir(new_corpus_path)
    for d in dir_list:
        os.makedirs(d)
    os.chdir(cwd)
    # make list of xml filenames
    parsed_fs = [f for f in os.listdir(new_corpus_path) if f.endswith('.xml')]
    # make a dictionary of the right paths
    pathdict = {}
    for rootd, dirnames, filenames in os.walk(corpuspath):
        for filename in fnmatch.filter(filenames, '*.txt'):
            pathdict[filename] = rootd

    # move each file
    for f in parsed_fs:
        noxml = f.replace('.xml', '')
        right_dir = pathdict[noxml].replace(corpuspath, new_corpus_path)
        # get rid of the temp adding of dirname to fname
        #short_name = f.replace('-%s.txt.xml' % os.path.basename(right_dir), '.txt.xml')
        os.rename(os.path.join(new_corpus_path, f), 
                  os.path.join(new_corpus_path, right_dir, f))
    return new_corpus_path

def corenlp_exists(corenlppath = False):
    import corpkit
    import os
    important_files = ['stanford-corenlp-3.5.2-javadoc.jar', 'stanford-corenlp-3.5.2-models.jar',
                       'stanford-corenlp-3.5.2-sources.jar', 'stanford-corenlp-3.5.2.jar']
    if corenlppath is False:
        home = os.path.expanduser("~")
        corenlppath = os.path.join(home, 'corenlp')
    if os.path.isdir(corenlppath):
        find_install = [d for d in os.listdir(corenlppath) \
                   if os.path.isdir(os.path.join(corenlppath, d)) \
                   and os.path.isfile(os.path.join(corenlppath, d, 'jollyday.jar'))]

        #find_install = [d for d in os.listdir(corenlppath) if os.path.isdir(os.path.join(corenlppath, d))]
        if len(find_install) > 0:
            find_install = find_install[0]
        else:
            return False
        javalib = os.path.join(corenlppath, find_install)
        if len(javalib) == 0:
            return False
        if not all([f in os.listdir(javalib) for f in important_files]):
            return False
        return True
    else:
        return False
    return True

def get_filepaths(a_path, ext = 'txt'):
    """make list of txt files in a_path and remove non txt files"""
    import os
    files = []
    for (root, dirs, fs) in os.walk(a_path):
        for f in fs:
            if f.endswith('.' + ext) \
            and 'Unidentified' not in f \
            and 'unknown' not in f:
                files.append(os.path.join(root, f))
            if not f.endswith('.' + ext):
                os.remove(os.path.join(root, f))
    return files

def get_list_of_speaker_names(corpuspath):
    """return a list of speaker names in a pre-processed corpus"""
    import os
    import re
    from corpkit.build import get_filepaths
    files = get_filepaths(corpuspath)
    names = []
    idregex = re.compile(r'(^.*?):\s+(.*$)')
    for f in files:
        data = open(f).read().splitlines()
        for l in data:
            m = re.search(idregex, l)
            if m:
                if m.group(1) not in names:
                    names.append(m.group(1))
    return sorted(list(set(names)))

def make_no_id_corpus(pth, newpth):
    """make version of pth without ids"""
    import os
    import re
    import shutil
    from corpkit.build import get_filepaths
    # define regex broadly enough to accept timestamps, locations if need be
    idregex = re.compile(r'(^.*?):\s+(.*$)')
    try:
        shutil.copytree(pth, newpth)
    except OSError:
        shutil.rmtree(newpth)
        shutil.copytree(pth, newpth)
    files = get_filepaths(newpth)
    names = []
    for f in files:
        good_data = []
        with open(f) as fo:
            data = fo.read().splitlines()
            for datum in data:
                matched = re.search(idregex, datum)
                if matched:
                    names.append(matched.group(1))
                    good_data.append(matched.group(2))
        with open(f, "w") as fo:
            fo.write('\n'.join(good_data))
    if len(names) == 0:
        from time import localtime, strftime
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: No speaker names found. Turn off speaker segmentation.' % thetime
        shutil.rmtree(newpth)

def add_ids_to_xml(corpuspath, root = False, note = False):
    """add ids to the xml in corpuspath

    needs the raw files to be in the same dir as corpuspath, without
    '-parsed' in the dir name
    also needs the id files to be in the dir, with '-parsed' changed 
    to -cleaned"""
    import os
    import re
    from bs4 import BeautifulSoup, SoupStrainer
    from corpkit.build import get_filepaths
    from time import strftime, localtime

    files = get_filepaths(corpuspath, ext = 'xml')
    if note:
        note.progvar.set(0)
    if root:
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Processing speaker IDs ...' % thetime
        root.update()

    for i, f in enumerate(files):
        if note:
            note.progvar.set(i * 100.0 / len(files))
        if root:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Processing speaker IDs (%d/%d)' % (thetime, i, len(files))
            root.update()
        xmlf = open(f)
        data = xmlf.read()
        xmlf.close()

        # open the unparsed version of the file, read into memory
        stripped_txtfile = f.replace('.xml', '').replace('-parsed', '')
        old_txt = open(stripped_txtfile)
        stripped_txtdata = old_txt.read()
        old_txt.close()

        # open the unparsed version with speaker ids
        id_txtfile = f.replace('.xml', '').replace('-stripped-parsed', '')
        idttxt = open(id_txtfile)
        id_txtdata = idttxt.read()
        idttxt.close()

        # todo: do this with lxml
        soup = BeautifulSoup(data, "lxml")
        for s in soup.find_all('sentence'):
            # don't get corefs
            if s.parent.name == 'sentences':
                tokens = s.find_all('token')
                start = int(tokens[0].find_all('characteroffsetbegin', limit = 1)[0].text)
                end = int(tokens[-1].find_all('characteroffsetend', limit = 1)[0].text)
                # extract this sentence from the unparsed version
                sent = stripped_txtdata[start:end]
                # find out line number
                # sever at start of match
                cut_old_text = stripped_txtdata[:start]
                line_index = cut_old_text.count('\n')
                # lookup this text
                with_id = id_txtdata.splitlines()[line_index]
                split_line = with_id.split(': ', 1)
                if len(split_line) > 1:
                    speakerid = split_line[0]
                else:
                    speakerid = 'UNIDENTIFIED'
                new_tag = soup.new_tag("speakername")
                s.append(new_tag)
                new_tag.string = speakerid
        html = str(soup.root)
        # make changes
        with open(f, "wb") as fopen:
            fopen.write(html)
    if note:
        note.progvar.set(100)

def get_speaker_names_from_xml_corpus(path):
    import os
    import re
    from bs4 import BeautifulSoup
    names = []
    # parsing html with regular expression! :)
    speakid = re.compile(r'<speakername>[\s\n]*?([^\s\n]+)[\s\n]*?<.speakername>', re.MULTILINE)
    for (root, dirs, fs) in os.walk(path):
        for f in fs:
            with open(os.path.join(root, f), 'r') as fo:
                txt = fo.read()
                res = re.findall(speakid, txt)
                if res:
                    res = [i.strip() for i in res]
                    for i in res:
                        if i not in names:
                            names.append(i)
    return list(sorted(set(names)))

def get_speakers(path):
    from corpkit.build import get_speaker_names_from_xml_corpus
    return get_speaker_names_from_xml_corpus(path)

def rename_all_files(dirs_to_do):
    """get rid of the inserted dirname in filenames after parsing"""
    import os
    from corpkit.build import get_filepaths
    for d in dirs_to_do:
        if not d.endswith('-parsed'):
            ext = 'txt'
        else:
            ext = 'txt.xml'
        fs = get_filepaths(d, ext)
        for f in fs:
            fname = os.path.basename(f)
            justdir = os.path.dirname(f)
            subcorpus = os.path.basename(justdir)
            newname = fname.replace('-%s.%s' % (subcorpus, ext), '.%s' % ext)
            os.rename(f, os.path.join(justdir, newname))