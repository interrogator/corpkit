
def make_corpus(unparsed_corpus_path,
                project_path = None,
                parse = True,
                tokenise = False,
                corenlppath = False,
                nltk_data_path = False,
                operations = False,
                speaker_segmentation = False,
                root = False,
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
    from corpkit.build import (get_corpus_filepaths, 
                               check_jdk, 
                               add_ids_to_xml, 
                               rename_all_files,
                               make_no_id_corpus)

    if project_path is None:
        project_path = os.getcwd()

    # raise error if no tokeniser
    if tokenise:
        import nltk
        if nltk_data_path:
            if nltk_data_path not in nltk.data.path:
                nltk.data.path.append(nltk_data_path)
        try:
            from nltk import word_tokenize as tokenise
        except:
            print '\nTokeniser not found. Pass in its path as keyword arg "nltk_data_path = <path>".\n'
            raise

    if sys.platform == "darwin":
        if not check_jdk():
            print "Get the latest Java from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html"

    # make absolute path to corpus
    unparsed_corpus_path = os.path.abspath(unparsed_corpus_path)

    # move it into project
    if not root:
        print 'Copying files to project ...'
    shutil.copytree(unparsed_corpus_path, os.path.join(project_path, 'data', os.path.basename(unparsed_corpus_path)))
    unparsed_corpus_path = os.path.join(project_path, 'data', os.path.basename(unparsed_corpus_path))

    if os.path.join('data', 'data') in unparsed_corpus_path:
        unparsed_corpus_path = unparsed_corpus_path.replace(os.path.join('data', 'data'), 'data')

    outpaths = []

    if parse:
        if speaker_segmentation:
            print 'Processing speaker IDs ...'
            make_no_id_corpus(unparsed_corpus_path, unparsed_corpus_path + '-stripped')
            to_parse = unparsed_corpus_path + '-stripped'
        else:
            to_parse = unparsed_corpus_path

        if not root:
            print 'Making list of files ... '
    
        filelist = get_corpus_filepaths(projpath = os.path.dirname(unparsed_corpus_path), 
                                corpuspath = to_parse)
        outpaths.append(to_parse)

        new_parsed_corpus_path = parse_corpus(proj_path = project_path, 
                                   corpuspath = to_parse,
                                   filelist = filelist,
                                   corenlppath = corenlppath,
                                   nltk_data_path = nltk_data_path,
                                   operations = operations)

        if new_parsed_corpus_path is False:
            return 
        
        move_parsed_files(project_path, to_parse, new_parsed_corpus_path)

        outpaths.append(new_parsed_corpus_path)

        if speaker_segmentation:
            add_ids_to_xml(new_parsed_corpus_path)
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
        outpaths.append(new_tokenised_corpus_path)

    rename_all_files(outpaths)
    print 'Done! Created %s' % ', '.join(outpaths)
    return outpaths
