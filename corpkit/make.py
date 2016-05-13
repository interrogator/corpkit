
def make_corpus(unparsed_corpus_path,
                project_path=None,
                parse=True,
                tokenise=False,
                corenlppath=False,
                nltk_data_path=False,
                operations=False,
                speaker_segmentation=False,
                root=False,
                multiprocess=False,
                split_texts=400,
                **kwargs):
    """
    Create a parsed version of unparsed_corpus using CoreNLP or NLTK's tokeniser

    :param unparsed_corpus_path: path to corpus containing text files, 
                                 or subdirs containing text files
    :type unparsed_corpus_path: str

    :param project_path: path to corpkit project
    :type project_path: str

    :param parse: Do parsing?
    :type parse: bool

    :param tokenise: Do tokenising?
    :type tokenise: bool
    
    :param corenlppath: folder containing corenlp jar files
    :type corenlppath: str
    
    :param nltk_data_path: path to tokeniser if tokenising
    :type nltk_data_path: str
    
    :param operations: which kinds of annotations to do
    :type operations: str
    
    :param speaker_segmentation: add speaker name to parser output if your corpus is script-like:
    :type speaker_segmentation: bool

    :returns: list of paths to created corpora
    """

    import sys
    import os    
    import shutil
    import codecs
    from corpkit.build import folderise, can_folderise
    pyver = sys.version_info.major
    if pyver == 2:
        inputfunc = raw_input
    elif pyver == 3:
        inputfunc = input
    from corpkit.build import (get_corpus_filepaths, 
                               check_jdk, 
                               add_ids_to_xml, 
                               rename_all_files,
                               make_no_id_corpus, parse_corpus, move_parsed_files)

    if parse is True and tokenise is True:
        raise ValueError('Select either parse or tokenise, not both.')
    if project_path is None:
        project_path = os.getcwd()

    # raise error if no tokeniser
    if tokenise:
        newpath = unparsed_corpus_path + '-tokenised'
        if os.path.isdir(newpath):
            shutil.rmtree(newpath)
        import nltk
        if nltk_data_path:
            if nltk_data_path not in nltk.data.path:
                nltk.data.path.append(nltk_data_path)
        try:
            from nltk import word_tokenize as tokenise
        except:
            print('\nTokeniser not found. Pass in its path as keyword arg "nltk_data_path = <path>".\n')
            raise

    if sys.platform == "darwin":
        if not check_jdk():
            print("Get the latest Java from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html")

    cop_head = kwargs.get('copula_head', True)
    note = kwargs.get('note', False)
    stdout = kwargs.get('stdout', False)

    # make absolute path to corpus
    unparsed_corpus_path = os.path.abspath(unparsed_corpus_path)

    # move it into project
    if os.path.isdir(os.path.join(project_path, 'data', os.path.basename(unparsed_corpus_path))):
        pass
    else:
        print('Copying files to project ...')
        shutil.copytree(unparsed_corpus_path, os.path.join(project_path, 'data', os.path.basename(unparsed_corpus_path)))
        unparsed_corpus_path = os.path.join(project_path, 'data', os.path.basename(unparsed_corpus_path))


    # ask to folderise?
    if can_folderise(unparsed_corpus_path):
        do_folderise = inputfunc("Your corpus has multiple files, but no subcorpora. "\
                                 "Would you like each file to be treated as a subcorpus? (y/n)")
        if do_folderise:
            folderise(unparsed_corpus_path)
            
    # this is bad!    
    if os.path.join('data', 'data') in unparsed_corpus_path:
        unparsed_corpus_path = unparsed_corpus_path.replace(os.path.join('data', 'data'), 'data')

    if parse:

        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i+n]

        # this loop shortens files containing more than 500 lines, for corenlp memory sake
        # maybe user needs a warning or something in case s/he is doing coref
        for rootx, dirs, fs in os.walk(unparsed_corpus_path):
            for f in fs:
                if f.startswith('.'):
                    continue
                fp = os.path.join(rootx, f)
                with codecs.open(fp, 'r', encoding='utf-8') as fo:
                    data = fo.read().splitlines()
                if len(data) > split_texts:
                    chk = chunks(data, split_texts)
                    for index, c in enumerate(chk):
                        newname = fp.replace('.txt', '-%s.txt' % str(index + 1).zfill(3))
                        with codecs.open(newname, 'w', encoding='utf-8') as fo:
                            fo.write('\n'.join(c) + '\n')
                    os.remove(fp)
                else:
                    pass
                    #newname = fp.replace('.txt', '-000.txt')
                    #os.rename(fp, newname)

        if speaker_segmentation:
            newpath = unparsed_corpus_path + '-stripped-parsed'
            if os.path.isdir(newpath) and not root:
                ans = inputfunc('\n Path exists: %s. Do you want to overwrite? (y/n)\n' %newpath)
                if ans.lower().strip()[0] == 'y':
                    shutil.rmtree(newpath)
                else:
                    return
            elif os.path.isdir(newpath) and root:
                raise OSError('Path exists: %s' %newpath)
            print('Processing speaker IDs ...')
            make_no_id_corpus(unparsed_corpus_path, unparsed_corpus_path + '-stripped')
            to_parse = unparsed_corpus_path + '-stripped'
        else:
            to_parse = unparsed_corpus_path

        print('Making list of files ... ')
    
        filelist = get_corpus_filepaths(projpath = os.path.dirname(unparsed_corpus_path), 
                                corpuspath = to_parse)

        if multiprocess is not False:

            if multiprocess is True:
                import multiprocessing
                multiprocess = multiprocessing.cpu_count()
            from joblib import Parallel, delayed
            # split old file into n parts
            with codecs.open(filelist, 'r', encoding='utf-8') as fo:
                fs = [i for i in fo.read().splitlines() if i]
            # make generator with list of lists
            divl = len(fs) / multiprocess
            fgen = chunks(fs, divl)
            filelists = []
            # for each list, make new file
            for index, flist in enumerate(fgen):
                as_str = '\n'.join(flist) + '\n'
                new_fpath = filelist.replace('.txt', '-%s.txt' % str(index).zfill(4))
                filelists.append(new_fpath)
                with codecs.open(new_fpath, 'w', encoding='utf-8') as fo:
                    fo.write(as_str)
            try:
                os.remove(filelist)
            except:
                pass

            ds = []
            for listpath in filelists:
                d = {'proj_path': project_path, 
                    'corpuspath': to_parse,
                    'filelist': listpath,
                    'corenlppath': corenlppath,
                    'nltk_data_path': nltk_data_path,
                    'operations': operations,
                    'copula_head': cop_head,
                    'multiprocessing': True,
                    'root': root,
                    'note': note,
                    'stdout': stdout}
                ds.append(d)

            res = Parallel(n_jobs=multiprocess)(delayed(parse_corpus)(**x) for x in ds)
            if len(res) > 0:
                new_parsed_corpus_path = res[0]
            else:
                return
            if all(r is False for r in res):
                return

            for i in filelists:
                try:
                    os.remove(i)
                except:
                    pass

        else:
            new_parsed_corpus_path = parse_corpus(proj_path=project_path, 
                                   corpuspath=to_parse,
                                   filelist=filelist,
                                   corenlppath=corenlppath,
                                   nltk_data_path=nltk_data_path,
                                   operations=operations,
                                   copula_head=cop_head,
                                   root=root,
                                   note=note,
                                   stdout=stdout)

        if new_parsed_corpus_path is False:
            return 
        
        move_parsed_files(project_path, to_parse, new_parsed_corpus_path)
        outpath = new_parsed_corpus_path
        if speaker_segmentation:
            add_ids_to_xml(new_parsed_corpus_path)
        try:
            os.remove(filelist)
        except:
            pass

    else:
        filelist = get_corpus_filepaths(projpath = os.path.dirname(unparsed_corpus_path), 
                                corpuspath = unparsed_corpus_path)

    if tokenise:
        new_tokenised_corpus_path = parse_corpus(proj_path = project_path, 
                                   corpuspath = unparsed_corpus_path,
                                   filelist = filelist,
                                   nltk_data_path = nltk_data_path,
                                   operations = operations,
                                   only_tokenise = True)
        if new_tokenised_corpus_path is False:
            return   
        outpath = new_tokenised_corpus_path

    rename_all_files(outpath)
    print('Done!\n')
    return outpath
