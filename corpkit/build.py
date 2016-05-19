#!/usr/bin/python

from __future__ import print_function

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
    from io import StringIO
    import shutil
    from collections import Counter
    from textprogressbar import TextProgressBar
    from process import tregex_engine
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
        print("Error making " + dictpath + "/ directory.")
    while os.path.isfile(os.path.join(dictpath, dictname)):
        time = strftime("%H:%M:%S", localtime())
        selection = input('\n%s: %s already exists in %s.\n' \
               '          You have the following options:\n\n' \
               '              a) save with a new name\n' \
               '              b) delete %s\n' \
               '              c) exit\n\nYour selection: ' % (time, dictname, dictpath, os.path.join(dictpath, dictname)))
        if 'a' in selection:
            sel = input('\nNew save name: ')
            dictname = sel
            if lemmatise:
                dictname = dictname.replace('-lemmatised.p', '')
                dictname = dictname + '-lemmatised'
            if not dictname.endswith('.p'):
                dictname = dictname + '.p'
        elif 'b' in selection:
            os.remove(os.path.join(dictpath, dictname))
        elif 'c' in selection:
            print('')
            return
        else:
            as_str = str(selection)
            print('          Choice "%s" not recognised.' % selection)

    time = strftime("%H:%M:%S", localtime())
    print('\n%s: Extracting words from files ... \n' % time)

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
                    raw = str(open(os.path.join(subcorp, f)).read(), 'utf-8', errors = 'ignore')
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
    print('\n\n' + time + ': Done! ' + dictname + ' created in ' + dictpath + '/')

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
    filtered_urls = [_f for _f in urls if _f]
    unique_urls = sorted(set(filtered_urls))
    return unique_urls


def downloader(url_list, new_path = 'html', wait = 5):
    """download a bunch of urls and store in a local folder"""
    import corpkit
    import urllib.request, urllib.parse, urllib.error
    import time
    import os
    from time import localtime, strftime
    from textprogressbar import TextProgressBar
    thetime = strftime("%H:%M:%S", localtime())
    print("\n%s: Attempting to download %d URLs with %d seconds wait-time ... \n" % (thetime, len(url_list), wait))
    p = TextProgressBar(len(urls))
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    paths = []
    for index, url in enumerate(url_list):
        p.animate(index)
        base = os.path.basename(url)
        new_filename = os.path.join(new_path, base)
        paths.append(new_filename)
        urllib.request.urlretrieve(url, new_filename)
        time.sleep(wait)
    p.animate(len(url_list))
    num_downloaded = len(paths)
    thetime = strftime("%H:%M:%S", localtime())
    print('\n\n%s: Done! %d files downloaded.' % (thetime, num_downloaded))
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
    soup = BeautifulSoup(raw, 'lxml')
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
    print('text: %s\n\nmetadata: %s' %(text, metadata))

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
            soup = BeautifulSoup(raw, 'lxml')


def correctspelling(path, newpath):
    import corpkit
    """Feed this function an unstructured corpus and get a version with corrected spelling"""
    import enchant
    import codecs
    import os
    subdirs = [d for d in os.listdir(path) if os.path.isdir(d)]
    for subdir in subdirs:
        txtFiles = [f for f in os.listdir(os.path.join(path,subdir)) if f.endswith(".txt")]
        print('Doing ' + subdir + ' ...')
        for txtFile in txtFiles: 
            d = enchant.Dict("en_UK")
            try:
                f = codecs.open(os.path.join(path,subdir,txtFile), "r", "utf-8")
            except IOError:
                print("Error reading the file, right filepath?")
                return
            textdata = f.read()
            textdata = str(textdata, 'utf-8')
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
                print("Error")
                return 
            fo.write(textdata.encode("UTF-8"))
            fo.close()
    return

def structure_corpus(path_to_files, new_corpus_name='structured_corpus'):
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
    print('Done!')

def download_large_file(proj_path, url, actually_download=True, root=False, **kwargs):
    """download something to proj_path"""
    import corpkit
    import os
    import shutil
    import glob
    import sys
    import zipfile
    from time import localtime, strftime
    from corpkit.textprogressbar import TextProgressBar
    from corpkit.process import animator

    file_name = url.split('/')[-1]
    home = os.path.expanduser("~")
    # if it's corenlp, put it in home/corenlp
    # if that dir exists, check if for a zip file
    # if there's a zipfile and it works, move on
    # if there's a zipfile and it's broken, delete it
    if 'stanford' in url:
        downloaded_dir = os.path.join(home, 'corenlp')
        if not os.path.isdir(downloaded_dir):
            os.makedirs(downloaded_dir)
        else:
            poss_zips = glob.glob(os.path.join(downloaded_dir, 'stanford-corenlp-full*.zip'))
            if poss_zips:
                fullfile = poss_zips[-1]   
                the_zip_file = zipfile.ZipFile(fullfile)
                ret = the_zip_file.testzip()
                if ret is None:
                    return downloaded_dir, fullfile
                else:
                    os.remove(fullfile)
            #else:
            #    shutil.rmtree(downloaded_dir)
    else:
        downloaded_dir = os.path.join(proj_path, 'temp')
        try:
            os.makedirs(downloaded_dir)
        except OSError:
            pass
    fullfile = os.path.join(downloaded_dir, file_name)

    if actually_download:
        if not root:
            txt = 'CoreNLP not found. Download latest version (%s)? (y/n) ' % url
            if sys.version_info.major == 3:
                selection = input(txt)
            else:
                selection = raw_input(txt)
            if 'n' in selection.lower():
                return None, None
        try:
            import requests
            # NOTE the stream=True parameter
            r = requests.get(url, stream=True, verify=False)
            file_size = int(r.headers['content-length'])
            file_size_dl = 0
            block_sz = 8192
            showlength = file_size / block_sz
            thetime = strftime("%H:%M:%S", localtime())
            print('\n%s: Downloading ... \n' % thetime)
            par_args = {'printstatus': kwargs.get('printstatus', True),
                        'length': showlength}
            if not root:
                tstr = '%d/%d' % (file_size_dl + 1 / block_sz, showlength)
                p = animator(None, None, init = True, tot_string = tstr, **par_args)
                animator(p, file_size_dl + 1, tstr)

            with open(fullfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=block_sz): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        file_size_dl += len(chunk)
                        #print file_size_dl * 100.0 / file_size
                        if kwargs.get('note'):
                            kwargs['note'].progvar.set(file_size_dl * 100.0 / int(file_size))
                        else:
                            tstr = '%d/%d' % (file_size_dl / block_sz, showlength)
                            animator(p, file_size_dl / block_sz, tstr, **par_args)
                        if root:
                            root.update()
        except Exception as err:
            import traceback
            print(traceback.format_exc())
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Download failed' % thetime)
            try:
                f.close()
            except:
                pass
            if root:
                root.update()
            return

        if kwargs.get('note'):  
            kwargs['note'].progvar.set(100)
        else:    
            p.animate(int(file_size))
        thetime = strftime("%H:%M:%S", localtime())
        print('\n%s: Downloaded successully.' % thetime)
        try:
            f.close()
        except:
            pass
    return downloaded_dir, fullfile

def extract_cnlp(fullfilepath, corenlppath = False, root = False):
    import corpkit
    """extract corenlp"""
    import zipfile
    import os
    from time import localtime, strftime
    time = strftime("%H:%M:%S", localtime())
    print('%s: Extracting CoreNLP files ...' % time)
    if root:
        root.update()
    if corenlppath is False:
        home = os.path.expanduser("~")
        corenlppath = os.path.join(home, 'corenlp')
    with zipfile.ZipFile(fullfilepath) as zf:
        zf.extractall(corenlppath)
    time = strftime("%H:%M:%S", localtime())
    print('%s: CoreNLP extracted. ' % time)

def get_corpus_filepaths(projpath=False,
                         corpuspath=False):
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

    # maybe not good:
    if projpath is False:
        projpath = os.path.dirname(os.path.abspath(corpuspath.rstrip('/')))

    corpname = os.path.basename(corpuspath)

    fp = os.path.join(projpath, 'data', corpname + '-filelist.txt')
    if os.path.join('data', 'data') in fp:
        fp = fp.replace(os.path.join('data', 'data'), 'data')
    with open(fp, "w") as f:
        f.write(matchstring + '\n')
    return fp

def check_jdk():
    import corpkit
    import subprocess
    from subprocess import PIPE, STDOUT, Popen
    p = Popen(["java", "-version"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if 'java version "1.8' in stderr.decode(encoding='utf-8'):
        return True
    else:
        #print "Get the latest Java from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html"
        return False

def parse_corpus(proj_path=False, 
                corpuspath=False, 
                filelist=False, 
                corenlppath=False, 
                operations=False,
                only_tokenise=False, 
                root=False, 
                stdout=False, 
                nltk_data_path=False, 
                memory_mb=2000,
                copula_head=True,
                multiprocessing=False,
                **kwargs):
    """
    Create a CoreNLP-parsed and/or NLTK tokenised corpus
    """
    import corpkit
    import subprocess
    from subprocess import PIPE, STDOUT, Popen
    from corpkit.process import get_corenlp_path
    import os
    import sys
    import re
    import chardet
    from time import localtime, strftime
    import time

    fileparse = kwargs.get('fileparse', False)

    url = 'http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip'
    
    if not only_tokenise:
        if not check_jdk():
            print('Need latest Java.')
            return

    curdir = os.getcwd()
    note = kwargs.get('note', False)

    if nltk_data_path:
        if only_tokenise:
            import nltk
            if nltk_data_path not in nltk.data.path:
                nltk.data.path.append(nltk_data_path)
            from nltk import word_tokenize as tokenise

    if proj_path is False:
        proj_path = os.path.dirname(os.path.abspath(corpuspath.rstrip('/')))

    basecp = os.path.basename(corpuspath)

    if fileparse:
        new_corpus_path = os.path.dirname(corpuspath)
    else:
        if only_tokenise:
            new_corpus_path = os.path.join(proj_path, 'data', '%s-tokenised' % basecp)
        else:
            new_corpus_path = os.path.join(proj_path, 'data', '%s-parsed' % basecp)

    # todo:
    # this is not stable
    if os.path.join('data', 'data') in new_corpus_path:
        new_corpus_path = new_corpus_path.replace(os.path.join('data', 'data'), 'data')

    if not os.path.isdir(new_corpus_path):
        os.makedirs(new_corpus_path)
    else:
        fs = os.listdir(new_corpus_path)
        if not multiprocessing:
            if not only_tokenise:
                if any([f.endswith('.xml') for f in fs]):
                    print('Folder containing xml already exists: "%s-parsed"' % basecp)
                    return False
            else:
                if any([f.endswith('.p') for f in fs]):
                    print('Folder containing tokens already exists: "%s-tokenised"' % basecp)  
                    return False          

    corenlppath = get_corenlp_path(corenlppath)

    if not corenlppath:
        cnlp_dir = os.path.join(os.path.expanduser("~"), 'corenlp')
        from corpkit.build import download_large_file, extract_cnlp
        corenlppath, fpath = download_large_file(cnlp_dir, url,
                                                 root=root,
                                                 note=note,
                                                 actually_download=True,
                                                 custom_corenlp_dir=corenlppath)
        if corenlppath is None and fpath is None:
            import shutil
            shutil.rmtree(new_corpus_path)
            shutil.rmtree(new_corpus_path.replace('-parsed', ''))
            os.remove(new_corpus_path.replace('-parsed', '-filelist.txt'))
            raise ValueError('CoreNLP needed to parse texts.')
        extract_cnlp(fpath)
        import glob
        globpath = os.path.join(corenlppath, 'stanford-corenlp*')
        corenlppath = [i for i in glob.glob(globpath) if os.path.isdir(i)]
        if corenlppath:
            corenlppath = corenlppath[-1]
        else:
            raise ValueError('CoreNLP installation failed for some reason. Try manual download.')

    # if not gui, don't mess with stdout
    if stdout is False:
        stdout = sys.stdout

    if not only_tokenise:
        os.chdir(corenlppath)
        if root:
            root.update_idletasks()
            reload(sys)
        if memory_mb is False:
            memory_mb = 2024
        if operations is False:
            operations = 'tokenize,ssplit,pos,lemma,parse'# 'ner,dcoref'
        if isinstance(operations, list):
            operations = ','.join([i.lower() for i in operations])

        with open(filelist, 'r') as fo:
            dat = fo.read()
        num_files_to_parse = len([l for l in dat.splitlines() if l])

        # get corenlp version number
        import re
        reg = re.compile(r'stanford-corenlp-([0-9].[0-9].[0-9])-javadoc.jar')
        fver = next(re.search(reg, s).group(1) for s in os.listdir('.') if re.search(reg, s))
        if fver == '3.6.0':
            extra_jar = 'slf4j-api.jar:slf4j-simple.jar:'
        else:
            extra_jar = ''
        arglist = ['java', '-cp', 
                     'stanford-corenlp-%s.jar:stanford-corenlp-%s-models.jar:xom.jar:joda-time.jar:%sjollyday.jar:ejml-0.23.jar' % (fver, fver, extra_jar), 
                     '-Xmx%sm' % str(memory_mb), 
                     'edu.stanford.nlp.pipeline.StanfordCoreNLP', 
                     '-annotators', 
                     operations, 
                     '-filelist', filelist,
                     '-noClobber',
                     '-outputExtension', '.xml',
                     '-outputDirectory', new_corpus_path]
        if copula_head:
            arglist.append('--parse.flags')
            arglist.append(' -makeCopulaHead')
        try:
            proc = subprocess.Popen(arglist, stdout=sys.stdout)
        # maybe a problem with stdout. sacrifice it if need be
        except:
            proc = subprocess.Popen(arglist)            
        #p = TextProgressBar(num_files_to_parse)
        while proc.poll() is None:
            sys.stdout = stdout
            thetime = strftime("%H:%M:%S", localtime())
            if not fileparse:
                num_parsed = len([f for f in os.listdir(new_corpus_path) if f.endswith('.xml')])  
                if num_parsed == 0:
                    if root:
                        print('%s: Initialising parser ... ' % (thetime))
                if num_parsed > 0 and (num_parsed + 1) <= num_files_to_parse:
                    if root:
                        print('%s: Parsing file %d/%d ... ' % (thetime, num_parsed + 1, num_files_to_parse))
                    if kwargs.get('note'):
                        kwargs['note'].progvar.set((num_parsed) * 100.0 / num_files_to_parse)
                    #p.animate(num_parsed - 1, str(num_parsed) + '/' + str(num_files_to_parse))
                time.sleep(1)
                if root:
                    root.update()
    else:

        from nltk import word_tokenize as tokenise
        # tokenise each file
        import cPickle as pickle
        fs = open(filelist).read().splitlines()
        dirs = sorted(list(set([os.path.basename(os.path.dirname(f)) for f in fs])))
        if len(dirs) == 0:
            one_big_corpus = True
        else:
            one_big_corpus = False
        if any(os.path.isdir(os.path.join(new_corpus_path, d)) for d in dirs):
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Directory already exists. Delete it if need be.' % thetime)
            return False
        for d in dirs:
            os.makedirs(os.path.join(new_corpus_path, d))
        nfiles = len(fs)
        thetime = strftime("%H:%M:%S", localtime())
        print('%s: Tokenising ... ' % (thetime))
        for index, f in enumerate(fs):
            with open(f, 'r') as fo:
                data = fo.read()
            enc = chardet.detect(data)
            enc_text = data.decode(enc['encoding'], errors='ignore')
            tokens = tokenise(enc_text)
            thedir = os.path.basename(os.path.dirname(f))
            newname = os.path.basename(f).replace('.txt', '-tokenised.p')
            if one_big_corpus:
                pth = os.path.join(new_corpus_path, newname)
            else:
                pth = os.path.join(new_corpus_path, thedir, newname)
            with open(pth, "wb") as fo:
                pickle.dump(tokens, fo)
            if kwargs.get('note'):
                kwargs['note'].progvar.set((index + 1) * 100.0 / nfiles)
            if root:
                root.update()

    #p.animate(num_files_to_parse)
    if kwargs.get('note'):
        kwargs['note'].progvar.set(100)
    sys.stdout = stdout
    thetime = strftime("%H:%M:%S", localtime())
    print('%s: Parsing finished. Moving parsed files into place ...' % thetime)
    os.chdir(curdir)
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

    important_files = ['stanford-corenlp-3.6.0-javadoc.jar', 'stanford-corenlp-3.6.0-models.jar',
                       'stanford-corenlp-3.6.0-sources.jar', 'stanford-corenlp-3.6.0.jar']
    if corenlppath is False:
        home = os.path.expanduser("~")
        corenlppath = os.path.join(home, 'corenlp')
    if os.path.isdir(corenlppath):
        find_install = [d for d in os.listdir(corenlppath) \
                   if os.path.isdir(os.path.join(corenlppath, d)) \
                   and os.path.isfile(os.path.join(corenlppath, d, 'jollyday.jar'))]

        if len(find_install) > 0:
            find_install = find_install[0]
        else:
            return False
        javalib = os.path.join(corenlppath, find_install)
        if len(javalib) == 0:
            return False
        if not any([f.endswith('-models.jar') for f in os.listdir(javalib)]):
            return False
        return True
    else:
        return False
    return True

def get_filepaths(a_path, ext = 'txt'):
    """make list of txt files in a_path and remove non txt files"""
    import os
    files = []
    if os.path.isfile(a_path):
        return [a_path]
    for (root, dirs, fs) in os.walk(a_path):
        for f in fs:
            if ext:
                if not f.endswith('.' + ext):
                    continue
            if 'Unidentified' not in f \
            and 'unknown' not in f \
            and not f.startswith('.'):
                files.append(os.path.join(root, f))
            #if ext:
            #    if not f.endswith('.' + ext):
            #        os.remove(os.path.join(root, f))
    return files

def make_no_id_corpus(pth, newpth):
    """make version of pth without ids"""
    import os
    import re
    import shutil
    from build import get_filepaths
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
        with open(f, 'r') as fo:
            data = fo.read().splitlines()
            for datum in data:
                matched = re.search(idregex, datum)
                if matched:
                    names.append(matched.group(1))
                    good_data.append(matched.group(2))
                else:
                    names.append('UNIDENTIFIED')
                    good_data.append(datum)
        with open(f, "w") as fo:
            fo.write('\n'.join(good_data))

    from time import localtime, strftime
    thetime = strftime("%H:%M:%S", localtime())
    if len(names) == 0:
        print('%s: No speaker names found. Turn off speaker segmentation.' % thetime)
        shutil.rmtree(newpth)
    else:
        if len(sorted(set(names))) < 19:
            print('%s: Speaker names found: %s' % (thetime, ', '.join(sorted(set(names)))))
        else:
            print('%s: Speaker names found: %s ... ' % (thetime, ', '.join(sorted(set(names[:20])))))

def add_ids_to_xml(corpuspath, root = False, note = False):
    """add ids to the xml in corpuspath

    needs the raw files to be in the same dir as corpuspath, without
    '-parsed' in the dir name
    also needs the id files to be in the dir, with '-parsed' changed 
    to -cleaned"""
    import os
    import re
    from build import get_filepaths
    from time import strftime, localtime
    from lxml import etree as ET

    files = get_filepaths(corpuspath, ext = 'xml')
    if note:
        note.progvar.set(0)
    thetime = strftime("%H:%M:%S", localtime())
    print('%s: Processing speaker IDs ...' % thetime)
    if root:
        root.update()

    for i, f in enumerate(files):
        if note:
            note.progvar.set(i * 100.0 / len(files))
        thetime = strftime("%H:%M:%S", localtime())
        print('%s: Processing speaker IDs (%d/%d)' % (thetime, i, len(files)))
        if root:
            root.update()

        # quick check for speakernames already existing
        from itertools import islice
        with open(f, 'r') as xmlf:
            head = list(islice(xmlf, 1000))
        if '<speakername>' in '\n'.join(head):
            continue
        
        tree = ET.parse(f)
        xmlroot = tree.getroot()
        sents = xmlroot[0][0]

        # open the unparsed version of the file, read into memory
        stripped_txtfile = f.replace('.xml', '').replace('-parsed', '')
        old_txt = open(stripped_txtfile, 'r')
        stripped_txtdata = old_txt.read()
        old_txt.close()

        # open the unparsed version with speaker ids
        id_txtfile = f.replace('.xml', '').replace('-stripped-parsed', '')
        idttxt = open(id_txtfile, 'r')
        id_txtdata = idttxt.read()
        idttxt.close()

        for s in sents:
            # don't get corefs
                tokens = [x for x in s.iter('token')]
                start = int(tokens[0][2].text)
                end = int(tokens[-1][3].text)
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
                newtag = ET.Element('speakername')
                newtag.text=speakerid
                newtag.tail='\n    '
                s.append(newtag)
        tree.write(f, pretty_print=True)
        # make changes
        #with open(f, "wb") as fopen:
        #    try:
        #        fopen.write(bytes(html.encode('utf-8')))
        #    except UnicodeDecodeError:
        #        fopen.write(bytes(html))

    if note:
        note.progvar.set(100)

def get_speaker_names_from_xml_corpus(path):
    import os
    import re
    
    list_of_files = []
    names = []

    # parsing html with regular expression! :)
    speakid = re.compile(r'<speakername>[\s\n]*?([^\s\n]+)[\s\n]*?<.speakername>', re.MULTILINE)

    def get_names(filepath):
        """get a list of speaker names from a file"""
        with open(filepath, 'r') as fo:
            txt = fo.read()
            res = re.findall(speakid, txt)
            if res:
                return list(sorted(set([i.strip() for i in res])))

    # if passed a dir, do it for every file
    if os.path.isdir(path):
        for (root, dirs, fs) in os.walk(path):
            for f in fs:
                list_of_files.append(os.path.join(root, f))
    elif os.path.isfile(path):
        list_of_files.append(path)

    for filepath in list_of_files:
        res = get_names(filepath)
        if not res:
            continue
        for i in res:
            if i not in names:
                names.append(i)
    return list(sorted(set(names)))

def rename_all_files(dirs_to_do):
    """get rid of the inserted dirname in filenames after parsing"""
    import os
    from build import get_filepaths
    if type(dirs_to_do) == str:
        dirs_to_do = [dirs_to_do]
    for d in dirs_to_do:
        if d.endswith('-parsed'):
            ext = 'txt.xml'
        elif d.endswith('-tokenised'):
            ext = '.p'
        else:
            ext = '.txt'
        fs = get_filepaths(d, ext)
        for f in fs:
            fname = os.path.basename(f)
            justdir = os.path.dirname(f)
            subcorpus = os.path.basename(justdir)
            newname = fname.replace('-%s.%s' % (subcorpus, ext), '.%s' % ext)
            os.rename(f, os.path.join(justdir, newname))

def flatten_treestring(tree):
    import re
    tree = re.sub(r'\(.*? ', '', tree).replace(')', '')
    tree = tree.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
    return tree
    

def can_folderise(folder):
    import os
    from glob import glob
    if os.path.isfile(folder):
        return False
    fs = glob(os.path.join(folder, '*.txt'))
    if len(fs) > 1:
        if not any(os.path.isdir(x) for x in glob(os.path.join(folder, '*'))):
            return True
    return False

def folderise(folder):
    import os
    import shutil
    from glob import glob
    from corpkit.process import makesafe
    fs = glob(os.path.join(folder, '*.txt'))
    for f in fs:
        newname = makesafe(os.path.splitext(os.path.basename(f))[0])
        newpath = os.path.join(folder, newname)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        shutil.move(f, os.path.join(newpath))
