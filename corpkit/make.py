from __future__ import print_function

from corpkit.constants import INPUTFUNC, PYTHON_VERSION
def make_corpus(unparsed_corpus_path,
                project_path=None,
                parse=True,
                tokenise=False,
                postag=False,
                lemmatise=False,
                corenlppath=False,
                nltk_data_path=False,
                operations=False,
                speaker_segmentation=False,
                root=False,
                multiprocess=False,
                split_texts=400,
                outname=False,
                metadata=False,
                restart=False,
                coref=True,
                lang='en',
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
    from os.path import join, isfile, isdir, basename, splitext, exists
    import shutil
    import codecs
    from corpkit.build import folderise, can_folderise
    from corpkit.process import saferead

    from corpkit.build import (get_corpus_filepaths, 
                               check_jdk, 
                               add_ids_to_xml, 
                               rename_all_files,
                               make_no_id_corpus, parse_corpus, move_parsed_files)
    from corpkit.constants import REPEAT_PARSE_ATTEMPTS

    if parse is True and tokenise is True:
        raise ValueError('Select either parse or tokenise, not both.')
    
    if project_path is None:
        project_path = os.getcwd()


    fileparse = isfile(unparsed_corpus_path)
    if fileparse:
        copier = shutil.copyfile
    else:
        copier = shutil.copytree

    # raise error if no tokeniser
    #if tokenise:
    #    if outname:
    #        newpath = os.path.join(os.path.dirname(unparsed_corpus_path), outname)
    #    else:
    #        newpath = unparsed_corpus_path + '-tokenised'
    #    if isdir(newpath):
    #        shutil.rmtree(newpath)
    #    import nltk
    #    if nltk_data_path:
    #        if nltk_data_path not in nltk.data.path:
    #            nltk.data.path.append(nltk_data_path)
    #    try:
    #        from nltk import word_tokenize as tokenise
    #    except:
    #        print('\nTokeniser not found. Pass in its path as keyword arg "nltk_data_path = <path>".\n')
    #        raise

    if sys.platform == "darwin":
        if not check_jdk():
            print("Get the latest Java from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html")

    cop_head = kwargs.get('copula_head', True)
    note = kwargs.get('note', False)
    stdout = kwargs.get('stdout', False)

    # make absolute path to corpus
    unparsed_corpus_path = os.path.abspath(unparsed_corpus_path)

    # move it into project
    if fileparse:
        datapath = project_path
    else:
        datapath = join(project_path, 'data')
    
    if isdir(datapath):
        newp = join(datapath, basename(unparsed_corpus_path))
    else:
        os.makedirs(datapath)
        if fileparse:
            noext = splitext(unparsed_corpus_path)[0]
            newp = join(datapath, basename(noext))
        else:
            newp = join(datapath, basename(unparsed_corpus_path))

    if exists(newp):
        pass
    else:
        copier(unparsed_corpus_path, newp)
    
    unparsed_corpus_path = newp

    # ask to folderise?
    check_do_folderise = False
    do_folderise = kwargs.get('folderise', None)
    if can_folderise(unparsed_corpus_path):
        import __main__ as main
        if do_folderise is None and not hasattr(main, '__file__'):
            check_do_folderise = INPUTFUNC("Your corpus has multiple files, but no subcorpora. "\
                                 "Would you like each file to be treated as a subcorpus? (y/n) ")
            check_do_folderise = check_do_folderise.lower().startswith('y')
        if check_do_folderise or do_folderise:
            folderise(unparsed_corpus_path)
            
    # this is bad!
    if join('data', 'data') in unparsed_corpus_path:
        unparsed_corpus_path = unparsed_corpus_path.replace(join('data', 'data'), 'data')

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    if parse or tokenise:
        
        # this loop shortens files containing more than 500 lines,
        # for corenlp memory's sake. maybe user needs a warning or
        # something in case s/he is doing coref?
        for rootx, dirs, fs in os.walk(unparsed_corpus_path):
            for f in fs:
                if f.startswith('.'):
                    continue
                fp = join(rootx, f)
                data, enc = saferead(fp)
                data = data.splitlines()
                if len(data) > split_texts:
                    chk = chunks(data, split_texts)
                    for index, c in enumerate(chk):
                        newname = fp.replace('.txt', '-%s.txt' % str(index + 1).zfill(3))
                        # does this work?
                        if PYTHON_VERSION == 2:
                            with codecs.open(newname, 'w', encoding=enc) as fo:
                                txt = '\n'.join(c) + '\n'
                                fo.write(txt.encode(enc))
                        else:
                            with open(newname, 'w', encoding=enc) as fo:
                                txt = '\n'.join(c) + '\n'
                                fo.write(txt)

                    os.remove(fp)
                else:
                    pass
                    #newname = fp.replace('.txt', '-000.txt')
                    #os.rename(fp, newname)

        if speaker_segmentation or metadata:
            if outname:
                newpath = os.path.join(os.path.dirname(unparsed_corpus_path), outname)
            else:
                newpath = unparsed_corpus_path + '-parsed'
            if restart:
                restart = newpath
            if isdir(newpath) and not root:
                import __main__ as main
                if not restart and not hasattr(main, '__file__'):
                    ans = INPUTFUNC('\n Path exists: %s. Do you want to overwrite? (y/n)\n' %newpath)
                    if ans.lower().strip()[0] == 'y':
                        shutil.rmtree(newpath)
                    else:
                        return
            elif isdir(newpath) and root:
                raise OSError('Path exists: %s' % newpath)
            if speaker_segmentation:
                print('Processing speaker IDs ...')
            make_no_id_corpus(unparsed_corpus_path,
                              unparsed_corpus_path + '-stripped',
                              metadata_mode=metadata,
                              speaker_segmentation=speaker_segmentation)
            to_parse = unparsed_corpus_path + '-stripped'
        else:
            to_parse = unparsed_corpus_path

        if not fileparse:
            print('Making list of files ... ')

        # now we enter a while loop while not all files are parsed
        #todo: these file lists are not necessary when not parsing

        while REPEAT_PARSE_ATTEMPTS:

            if not parse:
                break

            if not fileparse:
                pp = os.path.dirname(unparsed_corpus_path)
                # if restart mode, the filepaths won't include those already parsed...
                filelist, fs = get_corpus_filepaths(projpath=pp, 
                                                corpuspath=to_parse,
                                                restart=restart,
                                                out_ext=kwargs.get('output_format'))

            else:
                filelist = unparsed_corpus_path.replace('.txt', '-filelist.txt')
                with open(filelist, 'w') as fo:
                    fo.write(unparsed_corpus_path + '\n')

            # split up filelists
            if multiprocess is not False:

                if multiprocess is True:
                    import multiprocessing
                    multiprocess = multiprocessing.cpu_count()
                from joblib import Parallel, delayed
                # split old file into n parts
                data, enc = saferead(filelist)
                fs = [i for i in data.splitlines() if i]
                # if there's nothing here, we're done
                if not fs:
                    # double dutch
                    REPEAT_PARSE_ATTEMPTS = 0
                    break
                if len(fs) <= multiprocess:
                    multiprocess = len(fs)
                # make generator with list of lists
                divl = int(len(fs) / multiprocess)
                filelists = []
                if not divl:
                    filelists.append(filelist)
                else:
                    fgen = chunks(fs, divl)
                
                    # for each list, make new file
                    for index, flist in enumerate(fgen):
                        as_str = '\n'.join(flist) + '\n'
                        new_fpath = filelist.replace('.txt', '-%s.txt' % str(index).zfill(4))
                        filelists.append(new_fpath)
                        with codecs.open(new_fpath, 'w', encoding='utf-8') as fo:
                            fo.write(as_str.encode('utf-8'))
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
                         'stdout': stdout,
                         'outname': outname,
                         'coref': coref,
                         'output_format': kwargs.get('output_format', 'xml')
                        }
                    ds.append(d)

                res = Parallel(n_jobs=multiprocess)(delayed(parse_corpus)(**x) for x in ds)
                if len(res) > 0:
                    newparsed = res[0]
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
                newparsed = parse_corpus(proj_path=project_path, 
                                         corpuspath=to_parse,
                                         filelist=filelist,
                                         corenlppath=corenlppath,
                                         nltk_data_path=nltk_data_path,
                                         operations=operations,
                                         copula_head=cop_head,
                                         root=root,
                                         note=note,
                                         stdout=stdout,
                                         fileparse=fileparse,
                                         outname=outname,
                                         output_format=kwargs.get('output_format', 'conll'))

            if not restart:
                REPEAT_PARSE_ATTEMPTS = 0
            else:
                REPEAT_PARSE_ATTEMPTS -= 1
                print('Repeating parsing due to missing files. '\
                      '%d iterations remaining.' % REPEAT_PARSE_ATTEMPTS)

        if parse and not newparsed:
            return 
        if parse and all(not x for x in newparsed):
            return

        if parse and fileparse:
            # cleanup mistakes :)
            if isfile(splitext(unparsed_corpus_path)[0]):
                os.remove(splitext(unparsed_corpus_path)[0])
            if isfile(unparsed_corpus_path.replace('.txt', '-filelist.txt')):
                os.remove(unparsed_corpus_path.replace('.txt', '-filelist.txt'))
            return unparsed_corpus_path + '.conll'

        if parse:
            move_parsed_files(project_path, to_parse, newparsed,
                          ext=kwargs.get('output_format', 'conll'), restart=restart)

            if speaker_segmentation and kwargs.get('output_format', 'conll') == 'conll':
                add_ids_to_xml(newparsed, originalname=to_parse)
            if kwargs.get('output_format') == 'conll':
                #from corpkit.build import add_deps_to_corpus_path
                from corpkit.conll import convert_json_to_conll
                coref = False
                if operations is False:
                    coref = True
                elif 'coref' in operations or 'dcoref' in operations:
                   coref = True

                convert_json_to_conll(newparsed, speaker_segmentation=speaker_segmentation,
                                      coref=coref, metadata=metadata)

        try:
            os.remove(filelist)
        except:
            pass

    if not parse and tokenise:
        #todo: outname
        newparsed = to_parse.replace('-stripped', '-tokenised')
        from corpkit.tokenise import plaintext_to_conll
        newparsed = plaintext_to_conll(to_parse,
                                    postag=postag,
                                    lemmatise=lemmatise,
                                    lang=lang,
                                    metadata=metadata,
                                    nltk_data_path=nltk_data_path,
                                    speaker_segmentation=speaker_segmentation,
                                    outpath=newparsed)

        if outname:
            if not os.path.isdir(outname):
                outname = os.path.join('data', os.path.basename(outdir))
            import shutil
            shutil.copytree(newparsed, outname)
            newparsed = outname
        if newparsed is False:
            return
        else:
            return newparsed

    rename_all_files(newparsed)

    print('Done!\n')
    return newparsed
