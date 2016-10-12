from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC

def download_large_file(proj_path, url, actually_download=True, root=False, **kwargs):
    """
    Download something to proj_path
    """
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
                from zipfile import BadZipfile
                try:
                    the_zip_file = zipfile.ZipFile(fullfile)                    
                    ret = the_zip_file.testzip()
                    if ret is None:
                        return downloaded_dir, fullfile
                    else:
                        os.remove(fullfile)
                except BadZipfile:
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
        import __main__ as main
        if not root and not hasattr(main, '__file__'):
            txt = 'CoreNLP not found. Download latest version (%s)? (y/n) ' % url
            
            selection = INPUTFUNC(txt)

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
                p = animator(None, None, init=True, tot_string=tstr, **par_args)
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

def extract_cnlp(fullfilepath, corenlppath=False, root=False):
    """
    Extract corenlp zip file
    """
    import corpkit
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

def get_corpus_filepaths(projpath=False, corpuspath=False,
                         restart=False, out_ext='conll'):
    """
    get a list of filepaths, a la find . -type f

    restart mode will look in restart dir and remove any existing files

    """
    import corpkit
    import fnmatch
    import os
    matches = []

    # get a list of done files minus their paths and extensions
    # this handles if they have been moved to the right dir or not

    already_done = get_filepaths(restart, out_ext) if restart else []
    already_done = [os.path.splitext(os.path.basename(x))[0] for x in already_done]

    for root, dirnames, filenames in os.walk(corpuspath):
        for filename in fnmatch.filter(filenames, '*.txt'):
            if filename not in already_done:
                matches.append(os.path.join(root, filename))
    if len(matches) == 0:
        return False
    matchstring = '\n'.join(matches)

    # maybe not good:
    if projpath is False:
        projpath = os.path.dirname(os.path.abspath(corpuspath.rstrip('/')))

    corpname = os.path.basename(corpuspath)

    fp = os.path.join(projpath, 'data', corpname + '-filelist.txt')
    # definitely not good.
    if os.path.join('data', 'data') in fp:
        fp = fp.replace(os.path.join('data', 'data'), 'data')
    with open(fp, "w") as f:
        f.write(matchstring + '\n')
    return fp, matchstring

def check_jdk():
    """Check for a Java/OpenJDK"""
    import corpkit
    import subprocess
    from subprocess import PIPE, STDOUT, Popen
    # add any other version string to here
    javastrings = ['java version "1.8', 'openjdk version "1.8']
    p = Popen(["java", "-version"], stdout=PIPE, stderr=PIPE)
    _, stderr = p.communicate()
    encoded = stderr.decode(encoding='utf-8').lower()

    return any(j in encoded for j in javastrings)

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
                 outname=False,
                 coref=True,
                 **kwargs
                ):
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
        if outname:
            new_corpus_path = os.path.join(proj_path, 'data', outname)
        else:
            if only_tokenise:
                new_corpus_path = os.path.join(proj_path, 'data', '%s-tokenised' % basecp)
            else:
                new_corpus_path = os.path.join(proj_path, 'data', '%s-parsed' % basecp)

            new_corpus_path = new_corpus_path.replace('-stripped-', '-')

    # todo:
    # this is not stable
    if os.path.join('data', 'data') in new_corpus_path:
        new_corpus_path = new_corpus_path.replace(os.path.join('data', 'data'), 'data')

    # this caused errors when multiprocessing
    # it used to be isdir, but supposedly there was a file there
    # i don't see how it's possible ...
    # i think it is a 'race condition', so we'll also put a try/except there
    
    if not os.path.exists(new_corpus_path):
        try:
            os.makedirs(new_corpus_path)
        except OSError:
            pass
    else:
        if not os.path.isfile(new_corpus_path):
            fs = get_filepaths(new_corpus_path, ext=False)
            if not multiprocessing:
                if not only_tokenise:
                    if any([f.endswith('.xml') for f in fs]):
                        print('Folder containing xml already exists: %s' % new_corpus_path)
                        return False
                    elif any([f.endswith('.conll') for f in fs]):
                        print('Folder containing .conll files already exists: %s' % new_corpus_path)
                        return False
                else:
                    if any([f.endswith('.p') for f in fs]):
                        print('Folder containing tokens already exists: %s' % new_corpus_path)  
                        return False          

    corenlppath = get_corenlp_path(corenlppath)

    if not corenlppath:
        cnlp_dir = os.path.join(os.path.expanduser("~"), 'corenlp')
        corenlppath, fpath = download_large_file(cnlp_dir, url,
                                                 root=root,
                                                 note=note,
                                                 actually_download=True,
                                                 custom_corenlp_dir=corenlppath)
        # cleanup
        if corenlppath is None and fpath is None:
            import shutil
            shutil.rmtree(new_corpus_path)
            shutil.rmtree(new_corpus_path.replace('-parsed', '-stripped'))
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
            # not sure why reloading sys, but seems needed
            # in order to show files in the gui
            try:
                reload(sys)
            except NameError:
                import importlib
                importlib.reload(sys)
                pass
        if memory_mb is False:
            memory_mb = 2024


        # you can pass in 'coref' as kwarg now
        cof = ',dcoref' if coref else ''
        if operations is False:
            operations = 'tokenize,ssplit,pos,lemma,parse,ner' + cof

        if isinstance(operations, list):
            operations = ','.join([i.lower() for i in operations])

        with open(filelist, 'r') as fo:
            dat = fo.read()
        num_files_to_parse = len([l for l in dat.splitlines() if l])

        # get corenlp version number
        reg = re.compile(r'stanford-corenlp-([0-9].[0-9].[0-9])-javadoc.jar')
        fver = next(re.search(reg, s).group(1) for s in os.listdir('.') if re.search(reg, s))
        if fver == '3.6.0':
            extra_jar = 'slf4j-api.jar:slf4j-simple.jar:'
        else:
            extra_jar = ''

        out_form = 'json' if kwargs.get('output_format') in ['conll', 'json'] else 'xml'
        out_ext = 'conll' if kwargs.get('output_format') in ['conll', 'json'] else 'xml'

        arglist = ['java', '-cp', 
                   'stanford-corenlp-%s.jar:stanford-corenlp-%s-models.jar:xom.jar:joda-time.jar:%sjollyday.jar:ejml-0.23.jar' % (fver, fver, extra_jar), 
                   '-Xmx%sm' % str(memory_mb),
                   'edu.stanford.nlp.pipeline.StanfordCoreNLP', 
                   '-annotators',
                   operations, 
                   '-filelist', filelist,
                   '-noClobber',
                   '-outputExtension', '.%s' % out_ext,
                   '-outputFormat', out_form,
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
                num_parsed = len([f for f in os.listdir(new_corpus_path) if f.endswith(out_ext)])  
                if num_parsed == 0:
                    if root:
                        print('%s: Initialising parser ... ' % (thetime))
                if num_parsed > 0 and (num_parsed + 1) <= num_files_to_parse:
                    if root:
                        print('%s: Parsing file %d/%d ... ' % \
                             (thetime, num_parsed + 1, num_files_to_parse))
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
        one_big_corpus = len(dirs) == 0
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

def move_parsed_files(proj_path, old_corpus_path, new_corpus_path,
                      ext='conll', restart=False):
    """
    Make parsed files follow existing corpus structure
    """
    import corpkit
    import shutil
    import os
    import fnmatch
    cwd = os.getcwd()
    basecp = os.path.basename(old_corpus_path)
    dir_list = []
    # go through old path, make file list
    for path, dirs, files in os.walk(old_corpus_path):
        for bit in dirs:
            # is the last bit of the line below windows safe?
            dir_list.append(os.path.join(path, bit).replace(old_corpus_path, '')[1:])
    for d in dir_list:
        if not restart:
            os.makedirs(os.path.join(new_corpus_path, d))
        else:
            try:
                os.makedirs(os.path.join(new_corpus_path, d))
            except OSError:
                pass

    # make list of parsed filenames that haven't been moved already
    parsed_fs = [f for f in os.listdir(new_corpus_path) if f.endswith('.%s' % ext)]

    # make a dictionary of the right paths
    pathdict = {}
    for rootd, dirnames, filenames in os.walk(old_corpus_path):
        for filename in fnmatch.filter(filenames, '*.txt'):
            pathdict[filename] = rootd
    # move each file
    for f in parsed_fs:
        noxml = f.replace('.%s' % ext, '')
        right_dir = pathdict[noxml].replace(old_corpus_path, new_corpus_path)
        # get rid of the temp adding of dirname to fname
        #short_name = f.replace('-%s.txt.xml' % os.path.basename(right_dir), '.txt.xml')
        frm = os.path.join(new_corpus_path, f)
        tom = os.path.join(right_dir, f)
        # forgive errors on restart mode, because some files 
        # might already have been moved into place
        if restart:
            try:
                os.rename(frm, tom)
            except OSError:
                pass
        else:
            os.rename(frm, tom)

    return new_corpus_path

def corenlp_exists(corenlppath=False):
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

def get_filepaths(a_path, ext='txt'):
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

def make_no_id_corpus(pth, newpth, metadata_mode=False, speaker_segmentation=False):
    """
    Make version of pth without ids
    """
    import os
    import re
    import shutil
    from corpkit.process import saferead
    # define regex broadly enough to accept timestamps, locations if need be
    
    from corpkit.constants import MAX_SPEAKERNAME_SIZE
    idregex = re.compile(r'(^.{,%d}?):\s+(.*$)' % MAX_SPEAKERNAME_SIZE)

    try:
        shutil.copytree(pth, newpth)
    except OSError:
        shutil.rmtree(newpth)
        shutil.copytree(pth, newpth)
    files = get_filepaths(newpth)
    names = []
    metadata = []
    for f in files:
        good_data = []
        fo, enc = saferead(f)
        data = fo.splitlines()
        # for each line in the file, remove speaker and metadata
        for datum in data:
            if speaker_segmentation:
                matched = re.search(idregex, datum)
                if matched:
                    names.append(matched.group(1))
                    datum = matched.group(2)
            if metadata_mode:
                splitmet = datum.rsplit('<metadata ', 1)
                # for the impossibly rare case of a line that is '<metadata '
                if not splitmet:
                    continue
                datum = splitmet[0]
            if datum:
                good_data.append(datum)

        with open(f, "w") as fo:
            if PYTHON_VERSION == 2:
                fo.write('\n'.join(good_data).encode('utf-8'))
            else:
                fo.write('\n'.join(good_data))

    if speaker_segmentation:
        from time import localtime, strftime
        thetime = strftime("%H:%M:%S", localtime())
        if len(names) == 0:
            print('%s: No speaker names found. Turn off speaker segmentation.' % thetime)
            shutil.rmtree(newpth)
        else:
            try:
                if len(sorted(set(names))) < 19:
                    print('%s: Speaker names found: %s' % (thetime, ', '.join(sorted(set(names)))))
                else:
                    print('%s: Speaker names found: %s ... ' % (thetime, ', '.join(sorted(set(names[:20])))))
            except:
                pass

def add_ids_to_xml(corpuspath, root=False, note=False, originalname=False):
    """
    Add ids to the xml in corpuspath

    needs the raw files to be in the same dir as corpuspath, without
    '-parsed' in the dir name
    also needs the id files to be in the dir, with '-parsed' changed 
    to -cleaned
    """
    import os
    import re
    from time import strftime, localtime
    from lxml import etree as ET

    files = get_filepaths(corpuspath, ext='xml')
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
        if originalname:
            on = os.path.basename(originalname)
            stripped_txtfile = f.replace('.xml', '').replace(os.path.basename(corpuspath), on, 1)
        else:
            stripped_txtfile = f.replace('.xml', '').replace('-parsed', '-stripped')
        with open(stripped_txtfile, 'r') as old_txt:
            stripped_txtdata = old_txt.read()

        # open the unparsed version with speaker ids
        if originalname:
            on = os.path.basename(originalname)
            id_txtfile = f.replace('.xml', '').replace(os.path.basename(corpuspath), on, 1)
        else:
            id_txtfile = f.replace('.xml', '').replace('-parsed', '').replace('-stripped', '')
        with open(id_txtfile, 'r') as idttxt:
            id_txtdata = idttxt.read()

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
            newtag.text = speakerid
            newtag.tail = '\n    '
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

def add_deps_to_corpus_path(path):
    """add a column to a conll file with dependents"""
    # to do: progress bar
    from corpkit.conll import get_dependents_of_id, parse_conll
    files = get_filepaths(path, 'conll')
    for f in files:
        df = parse_conll(f, first_time=True)
        all_deps = []
        for idx in list(df.index):
            deps = get_dependents_of_id(df, *idx)
            if not deps:
                all_deps.append('0')
                continue
            deps = [str(i) for s, i in deps]
            all_deps.append(','.join(deps))
        df['d'] = all_deps
        df.to_csv(f, sep='\t', header=False)

def get_all_metadata_fields(corpus):
    from corpkit.constants import OPENER, PYTHON_VERSION

    fs = []
    import os
    for root, dirnames, filenames in os.walk(corpus):
        for filename in filenames:
            fs.append(os.path.join(root, filename))

    fields = []
    for f in fs:
        if PYTHON_VERSION == 2:
            from corpkit.process import saferead
            lines = saferead(f)[0].splitlines()
        else:
            with open(f, 'rb') as fo:
                lines = fo.read().decode('utf-8', errors='ignore')
                lines = lines.strip('\n')
                lines = lines.splitlines()

        lines = [l[2:].split('=', 1)[0] for l in lines if l.startswith('# ') \
                 if not l.startswith('# sent_id')]
        for l in lines:
            if l not in fields and l not in ['parse', 'sent_id', 'speaker']:
                fields.append(l)
    return fields


def get_names(filepath, speakid):
    """get a list of speaker names from a file"""
    import re
    from corpkit.process import saferead
    txt, enc = saferead(filepath)
    res = re.findall(speakid, txt)
    if res:
        return sorted(list(set([i.strip() for i in res])))

def get_speaker_names_from_parsed_corpus(corpus, feature='speaker'):
    """
    Use regex to get speaker names from xml without parsing it
    """
    import os
    import re

    path = corpus.path
    
    list_of_files = []
    names = []

    if corpus.datatype == 'parse':
        # parsing html with regular expression! :)
        speakid = re.compile(r'<speakername>[\s\n]*?([^\s\n]+)[\s\n]*?<.speakername>', re.MULTILINE)
    else:
        speakid = re.compile(r'^# %s=(.*)' % re.escape(feature), re.MULTILINE)
    
    # if passed a dir, do it for every file
    if os.path.isdir(path):
        for (root, dirs, fs) in os.walk(path):
            for f in fs:
                list_of_files.append(os.path.join(root, f))
    elif os.path.isfile(path):
        list_of_files.append(path)

    for filepath in list_of_files:
        res = get_names(filepath, speakid)
        if not res:
            continue
        for i in res:
            if i not in names:
                names.append(i)
    return list(sorted(set(names)))

def rename_all_files(dirs_to_do):
    """
    Get rid of the inserted dirname in filenames after parsing
    """
    import os
    if isinstance(dirs_to_do, STRINGTYPE):
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
    """
    Check if corpus can be put into folders
    """
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
    """
    Move each file into a folder
    """
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
