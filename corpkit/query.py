
#!/usr/local/bin/ipython

#   Interrogating parsed corpora and plotting the results: interrogator
#   for ResBaz NLTK stream
#   Author: Daniel McDonald

def interrogator(path, options, query, lemmatise = False, 
    dictionary = 'bnc.p', titlefilter = False, lemmatag = False, 
    usa_english = True, phrases = False, dep_type = 'basic-dependencies'):
    
    """
    Interrogate a parsed corpus using Tregex queries, dependencies, or for
    keywords/ngrams

    path: path to corpus
    options: 
            Tregex output options: -t, -c, -u, -o,
            dependency options: depnum, govrole, funct
    query: 
            a Tregex query
            'keywords'
            'ngrams'
            a regex to match a word for dependencies

    lemmatise: Do lemmatisation on results?
    titlefilter: strip 'mr, 'the', 'president' etc from results (this turns 'phrases' on)
    lemmatag: explicitly pass pos to lemmatiser: 'n', 'v', 'a' or 'r'
    usa_english: convert all to U.S. English
    phrases: turn on if your expected results are multiword and thus need tokenising
    dictionary: the name of a dictionary made with dictmaker for use with keyword query
    dep_type: the kind of stanford dependency parses you want to use:
            'basic-dependencies' * best lemmatisation
            'collapsed-dependencies'
            'collapsed-ccprocessed-dependencies'
    """
    
    import os
    import re
    import signal
    import collections
    from collections import Counter
    from time import localtime, strftime

    import nltk
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass

    from corpkit.query import query_test
    from corpkit.progressbar import ProgressBar
    import dictionaries

    if lemmatise:
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()
        # location of words for manual lemmatisation
        from dictionaries.word_transforms import wordlist, usa_convert
        from dictionaries.manual_lemmatisation import wordlist, taglemma
    
    # check if we are in ipython
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    def signal_handler(signal, frame):
        """exit on ctrl+c, rather than just stop loop"""
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    def gettag(query):
        import re
        if lemmatag is False:
            # attempt to find tag from tregex query
            # currently this will fail with a query like r'/\bthis/'
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)') 
            tagchecker = re.compile(r'^[A-Z]{2,4}$')
            tagfinder = re.compile(r'^[^A-Za-z]*([A-Za-z]*)')
            treebank_tag = re.findall(tagfinder, query)
            if re.match(tagchecker, treebank_tag[0]):
                if treebank_tag[0].startswith('J'):
                    tag = 'a'
                elif treebank_tag[0].startswith('V'):
                    tag = 'v'
                elif treebank_tag[0].startswith('N'):
                    tag = 'n'
                elif treebank_tag[0].startswith('R'):
                    tag = 'r'
            else:
                tag = 'n' # default to noun tag---same as lemmatiser does with no tag
        if lemmatag:
            tag = lemmatag
            tagchecker = re.compile(r'^[avrn]$')
            if not re.match(tagchecker, lemmatag):
                raise ValueError("WordNet POS tag not recognised. Must be 'a', 'v', 'r' or 'n'.")
        return tag
    
    def processwords(list_of_matches):
        """edit matches from interrogations"""

        # make everything unicode, lowercase and sorted
        list_of_matches = [unicode(w, 'utf-8', errors = 'ignore') for w in list_of_matches]
        list_of_matches = [w.lower() for w in list_of_matches]
        list_of_matches.sort()
        
        # tokenise if multiword:
        if phrases:
            result = [nltk.word_tokenize(i) for i in result]

        if lemmatise:
            tag = gettag(query)
            list_of_matches = lemmatiser(list_of_matches, tag)

        if titlefilter:
            list_of_matches = titlefilterer(list_of_matches)

        if usa_english:
            list_of_matches = usa_english_maker(list_of_matches)
        
        # turn every result into a single string again if need be:
        if phrases:
            output = []
            for res in list_of_matches:
                joined = ' '.join(res)
                output.append(joined)
            return output
        else:
            return list_of_matches

    def lemmatiser(list_of_words, tag):
        """take a list of unicode words and a tag and return a lemmatised list."""
        output = []
        for entry in list_of_words:
            if phrases:
                # just get the rightmost word
                word = entry[-1]
                entry.pop()
            else:
                word = entry
            if 'u' in options:
                if word in taglemma:
                    word = taglemma[word]
            # only use wordnet lemmatiser for -t
            if 't' in options or 'keyword' in query or 'ngram' in query:
                if word in wordlist:
                    word = wordlist[word]
                word = lmtzr.lemmatize(word, tag)
            if phrases:
                entry.append(word)
                output.append(entry)
            else:
                output.append(word)
        return output

    def titlefilterer(list_of_matches):
        from dictionaries.titlewords import titlewords, determiners
        output = []
        for result in list_of_matches:
            head = result[-1]
            non_head = len(result) - 1 # ???
            title_stripped = [token for token in result[:non_head] if token.rstrip('.') not in titlewords and token.rstrip('.') not in determiners]
            title_stripped.append(head)
            output.append(title_stripped)
        return output

    def usa_english_maker(list_of_matches):
        from dictionaries.word_transforms import usa_convert
        output = []
        for result in list_of_matches:
            if phrases:
                for w in result:
                    try:
                        w = usa_convert[w]
                    except KeyError:
                        pass
                output.append(result)
            else:
                try:
                    result = usa_convert[result]
                except KeyError:
                    pass
                output.append(result)
        return output

    def govrole(soup):
        """print funct:gov"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    role = dep.attrs.get('type')
                    gov = dep.find_all('governor')
                    govword = gov[0].get_text()
                    # very messy here, sorry
                    if lemmatise is True:
                        if role in deptags:
                            thetag = deptags[role]
                        else:
                            thetag = None
                        if not thetag:
                            if lemmatag:
                                thetag = lemmatag
                            else:
                                thetag = 'v'
                        if word in wordlist:
                            word = wordlist[word]
                        govword = lmtzr.lemmatize(govword, thetag)
                    colsep = role + u':' + govword
                    result.append(colsep)
        return result

    def funct(soup):
        """"print functional role"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    result.append(dep.attrs.get('type'))
        return result

    def depnum(soup):
        """print dependency number"""
        result = []
        for dep in soup.find_all('dep'):
            for dependent in dep.find_all('dependent'):
                word = dependent.get_text()
                if re.match(regex, word):
                    # get just the number
                    result.append(int(dependent.attrs.get('idx')))
        return result

    def depnum_reorder(results_list, output = 'results'):
        """reorder depnum results and/or generate totals list"""
        yearlist = [[unicode(i[0])] for i in results_list[0][1:]]
        #print yearlist
        totallist = [u'Totals']
        counts = []
        for entry in results_list: # for each depnum:
            depnum = entry[0]
            #print depnum
            count = sum(d[1] for d in entry[1:])
            #print count
            totallist.append([depnum, count])
        for year in yearlist:
            for entry in results_list:
                word = entry[0]
                data = entry[1:]
                #depnum_and_count = [word, sum([d[1] for d in data])] # sum for each depnum
                #totallist.append(depnum_and_count)
                for theyear, count in data:
                    if theyear == int(year[0]):
                        fixed_datum = [word, count]
                        year.append(fixed_datum)
        # this could be done more efficiently earlier:
        for year in yearlist:
            for entry in year[1:]:
                if entry[0] > 50:
                    year.remove(entry)
        for entry in totallist[1:]:
            if entry[0] > 50:
                    totallist.remove(entry)
        if output == 'results':
            return yearlist
        if output == 'totals':
            return totallist

    # a few things are off by default:
    only_count = False
    keywording = False
    n_gramming = False
    dependency = False

    # titlefiltering only works with phrases, so turn it on
    if titlefilter:
        phrases = True

    # parse options
    if options == 'u' or options == 'U':
        optiontext = 'Tags only.'
    elif options == 'o' or options == 'O':
        optiontext = 'Tags and words.'
    elif options == 't' or options == 'T':
        optiontext = 'Words only.'
    elif options == 'c' or options == 'C':
        only_count = True
        options = options.upper()
        optiontext = 'Counts only.'
    elif 'dep' in options:
        dependency = True
        optiontext = 'Number only.'
    elif 'funct' in options:
        dependency = True
        optiontext = 'Functional role only.'
    elif 'gov' in options:
        dependency = True
        optiontext = 'Role and governor.'
    else:
        raise ValueError("'%s' option not recognised. Must be:\n\nFor tree searching:\n    'u', 'o', 'c' or 't'\nFor dependencies searching:\n    'depnum', 'funct' or 'govrole'." % options)
    
    # dependencies can't be phrases
    if dependency:
        import gc
        from bs4 import BeautifulSoup, SoupStrainer
        regex = re.compile(query)
        phrases = False

    # parse query
    if query.startswith('key'):
        keywording = True
        optiontext = 'Words only.'
    elif 'ngram' in query:
        n_gramming = True
        phrases = True
        optiontext = 'Words only.'
    else:
        if not dependency:
            # it's tregex. check if ok
            query_test(query, have_ipython = have_ipython)
        else:
            try:
                re.compile(query)
            except re.error:
                raise ValueError("Regular expression '%s' contains an error." % query)

    # begin interrogation
    time = strftime("%H:%M:%S", localtime())
    print ("\n%s: Beginning corpus interrogation: %s" \
           "\n          Query: '%s'\n          %s" \
           "\n          Interrogating corpus ... \n" % (time, path, query, optiontext) )
    
    # get list of subcorpora and sort them
    sorted_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    sorted_dirs.sort(key=int)
    
    # treat as one large corpus if no subdirs found
    if len(sorted_dirs) == 0:
        import warnings
        warnings.warn('\nNo subcorpora found in %s.\nUsing %s as corpus dir.' % (path, path))
        sorted_dirs = [os.path.basename(path)]
    
    # some empty lists we'll need
    allwords_list = []
    results_list = []
    all_files = [] # dependencies only
    main_totals = [u'Totals']
    
    # make progress bar for each dir
    p = ProgressBar(len(sorted_dirs))

    # if doing dependencies, make list of all files
    if dependency:
        for d in sorted_dirs:
            subcorpus = os.path.join(path, d)
            files = [f for f in os.listdir(subcorpus) if f.endswith('.xml')]
            all_files.append([d, files])
        total_files = len([item for sublist in all_files for item in sublist[1]])
        sorted_dirs = all_files
        c = 0
        p = ProgressBar(total_files)

    # loop through each subcorpus
    for index, d in enumerate(sorted_dirs):
        if not dependency:
            subcorpus_name = d
            p.animate(index)
    
            # get path to corpus/subcorpus
            if len(sorted_dirs) == 1:
                subcorpus = path
            else:
                subcorpus = os.path.join(path,subcorpus_name)
    
            # get keywords and ngrams, rather than tregex:
            if keywording or n_gramming:
                from corpkit import keywords
                keys, ngrams = keywords(subcorpus, dictionary = dictionary, 
                                        printstatus = False, clear = False)
                result = []
    
                # this remains a total hack, and sacrifices a little 
                # bit of accuracy when doing the division. rewrite, one day.
                if keywording:
                    for index, word, score in keys:
                        divided_score = score / 10.0
                        for _ in range(int(divided_score)):
                            result.append(word)
                elif n_gramming:
                    for index, ngram, score in ngrams:
                        for _ in range(int(score)):
                            result.append(ngram)
    
            #if tregex, determine ipython or not and search
            else:
                if have_ipython:
                    tregex_command = 'tregex.sh -o -%s \'%s\' %s 2>/dev/null | grep -vP \'^\s*$\'' %(options, query, subcorpus)
                    result = get_ipython().getoutput(tregex_command)
                else:
                    tregex_command = ["tregex.sh", "-o", "-%s" % options, '%s' % query, "%s" % subcorpus]
                    FNULL = open(os.devnull, 'w')
                    result = subprocess.check_output(tregex_command, stderr=FNULL)
                    result = os.linesep.join([s for s in result.splitlines() if s]).split('\n')
            
                # if just counting matches, just 
                # add subcorpus name and count...
                if only_count:
                    try:
                        tup = [int(d), int(result[0])]
                    except ValueError:
                        tup = [d, int(result[0])]
                    main_totals.append(tup)
                    continue

        if dependency:
            subcorpus_name = d[0]
            fileset = d[1]
            #for f in read_files:
            result = []
            for f in fileset:
                p.animate(c, str(c) + '/' + str(total_files))
                c += 1
                with open(os.path.join(path, subcorpus_name, f), "rb") as text:
                    data = text.read()
                    just_good_deps = SoupStrainer('dependencies', type=dep_type)
                    soup = BeautifulSoup(data, "lxml", parse_only=just_good_deps)
                    if options == 'govrole':
                        result_from_file = govrole(soup)
                    if options == 'funct':
                       result_from_file = funct(soup)
                    if options == 'depnum':
                      result_from_file = depnum(soup)
                if result_from_file is not None:
                    for entry in result_from_file:
                        result.append(entry)

                # attempt to stop memory issues:
                soup.decompose()
                soup = None
                data = None
                gc.collect()

        result.sort()

        # add subcorpus name and total count to totals
        try:
            main_totals.append([int(subcorpus_name), len(result)])
        except ValueError:
            main_totals.append([subcorpus_name, len(result)])

        # lowercaseing, encoding, lemmatisation, 
        # titlewords removal, usa_english, etc.
        processed_result = processwords(result)

        # add results master list and to results list
        allwords_list.append(processed_result)
        results_list.append([subcorpus_name, processed_result])

    # 100%
    p.animate(len(sorted_dirs))
    if not have_ipython:
        print '\n'
    
    # if only counting, get total total and finish up:
    if only_count:
        total = sum([i[1] for i in main_totals[1:]])
        main_totals.append([u'Total', total])
        # no results branch:
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        query_options = [path, query, options] 
        output = outputnames(query_options, main_totals)
        if have_ipython:
            clear_output()
        return output

    # flatten and sort master list
    allwords = [item for sublist in allwords_list for item in sublist]
    allwords.sort()
    unique_words = set(allwords)
    list_words = []
    for word in unique_words:
        list_words.append([word])

    # make dictionary of every subcorpus and store in dicts
    dicts = []
    p = ProgressBar(len(results_list))
    for index, subcorpus in enumerate(results_list):
        subcorpus_name = subcorpus[0]
        subcorpus_data = subcorpus[1]
        p.animate(index)
        dictionary = Counter(subcorpus_data)
        dicts.append(dictionary)
        for word in list_words:
            getval = dictionary[word[0]]
            try:
                word.append([int(subcorpus_name), getval])
            except ValueError:
                word.append([subcorpus_name, getval])

    # 100%            
    p.animate(len(results_list))

    # do totals (and keep them), then sort list by total
    for word in list_words:
        total = sum([i[1] for i in word[1:]])
        word.append([u'Total', total])
    list_words = sorted(list_words, key=lambda x: x[-1], reverse = True) # does this need to be int!?
    
    # reconstitute keyword scores, because we earlier
    # did / 100 to save memory and time
    if keywording:
        for res in list_words:
            for datum in res[1:]:
                datum[1] = datum[1] * 10

    # add total to main_total
    total = sum([i[1] for i in main_totals[1:]])
    main_totals.append([u'Total', total])

    #make results into named tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    query_options = [path, query, options] 
    output = outputnames(query_options, list_words, main_totals)
    if have_ipython:
        clear_output()
    return output



def conc(corpus, query, n = 100, random = False, window = 50, trees = False, csvmake = False): 
    """A concordancer for Tregex queries"""
    # add sorting?
    import os
    from random import randint
    import time
    from time import localtime, strftime
    import re
    from collections import defaultdict
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    import pydoc
    from corpkit.query import query_test
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    if csvmake:
        if os.path.isfile(csvmake):
            raise ValueError("CSV error: " + csvmake + " already exists in current directory. Move it, delete it, or change the name of the new .csv file.")

    def csvmaker(csvdata, sentences, csvmake):
        """Puts conc() results into tab-separated spreadsheet form"""
        #make data utf 8
        uc_data = []
        uc_sentences = []
        for line in csvdata:
            newline = []
            for part in line:
                newpart = unicode(part, 'utf-8')
                newline.append(newpart)
            uc_data.append(newline)
        for sentence in sentences:
            newsentence = unicode(sentence, 'utf-8')
            uc_sentences.append(newsentence)
        csv = []
        # make first line
        topline = query + '\nTab separated, with window (n=' + str(len(csvdata)) + '):\n'
        midline = '\n\n' + query + '\nEntire sentences (n=' + str(len(sentences)) + '):\n'
        # title then years for top row
        csv.append(topline)
        # for each word
        for entry in uc_data:
            sentence = '\t'.join(entry)
            csv.append(sentence)
        csv.append(midline)
        for entry in uc_sentences:
            csv.append(entry)
        csv = '\n'.join(csv)
        # write the csv file?
        try:
            fo=open(csvmake,"w")
        except IOError:
            print "Error writing CSV file."
        fo.write(csv.encode("UTF-8"))
        fo.close()
        time = strftime("%H:%M:%S", localtime())
        print time + ": " + csvmake + " written to currect directory."
                
    def list_duplicates(seq):
        tally = defaultdict(list)
        for i,item in enumerate(seq):
            tally[item].append(i)
        return ((key,locs) for key,locs in tally.items() 
                        if len(locs)>1)

        ##############################################################

    time = strftime("%H:%M:%S", localtime())
    #if noprint is False:
    print "\n%s: Getting concordances for %s ... \n          Query: %s\n" % (time, corpus, query)
    output = []
    query_test(query)
    if trees:
        options = '-s'
    else:
        options = '-t'
    # tregex_command = "tregex.sh -o -w %s '%s' %s 2>/dev/null | grep -vP '^\s*$'" % (options, query, corpus)
    # replace bracket: '-LRB- ' and ' -RRB- ' ...
    #allresults = !$tregex_command
    #print allresults
    if have_ipython:
        tregex_command = 'tregex.sh -o -w %s \'%s\' %s 2>/dev/null | grep -vP \'^\s*$\'' %(options, query, corpus)
        allresults = get_ipython().getoutput(tregex_command)
    else:
        tregex_command = ["tregex.sh", "-o", "-w", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        allresults = subprocess.check_output(tregex_command, stderr=FNULL)
        allresults = os.linesep.join([s for s in allresults.splitlines() if s]).split('\n')
    results = list(allresults)
    if csvmake: # this is not optimised at all!
        sentences = list(results)
    if have_ipython:
        tregex_command = 'tregex.sh -o %s \'%s\' %s 2>/dev/null | grep -vP \'^\s*$\'' %(options, query, corpus)
        alltresults = get_ipython().getoutput(tregex_command)
    else:
        tregex_command = ["tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        alltresults = subprocess.check_output(tregex_command, stderr=FNULL)
        alltresults = os.linesep.join([s for s in alltresults.splitlines() if s]).split('\n')
    tresults = list(alltresults)
    zipped = zip(allresults, alltresults)
    all_dupes = []
    #for dup in sorted(list_duplicates(results)):
        #index_list = dup[1][1:] # the list of indices for each duplicate, minus the first one, which we still want.
        #for i in index_list:
            #all_dupes.append(i)
    #for i in sorted(all_dupes, reverse = True):
        #print tresults[i]
        #print results[i]
    #n = len(results)
    #for i in xrange(n):
        #print tresults[i]
        #print results[i]
    totalresults = len(zipped)
    if totalresults == 0:
        raise ValueError("No matches found, sorry. I wish there was more I could tell you.") 
    maximum = len(max(tresults, key=len)) # longest result in characters
    csvdata = []
    unique_results = []
    for result in zipped: 
        tree = result[0]

        pattern = result[1]
        if not trees:
            regex = re.compile(r"(\b[^\s]{0,1}.{," + re.escape(str(window)) + r"})(\b" + 
            re.escape(pattern) + r"\b)(.{," + re.escape(str(window)) + r"}[^\s]\b)")
        else:
            regex = re.compile(r"(.{,%s})(%s)(.{,%s})" % (window, re.escape(pattern), window ))
        search = re.findall(regex, tree)
        for result in search:
            unique_results.append(result)
    unique_results = set(sorted(unique_results)) # make unique
    for unique_result in unique_results:
        lstversion = list(unique_result)
        if len(lstversion) == 3:
            # make match red!
            # lstversion[1] = "\x1b[31m%s\x1b[0m" % lstversion[1]
            if csvmake:
                csvdata.append(lstversion)
            whitespace_first = window + 2 - len(lstversion[0])
            whitespace_second = maximum - len(lstversion[1])
            lstversion[0] = ' ' * whitespace_first + lstversion[0]
            lstversion[1] = lstversion[1] + ' ' * whitespace_second
            output.append(lstversion)
    formatted_output = []
    for index, row in enumerate(output):
        formatted_output.append(" ".join(row))
        #if noprint is False:
        if not random:
            if index < n:
                print '% 4d' % index, " ".join(row)
    if csvmake:
        csvmaker(csvdata, sentences, csvmake)
    if not random:
        return formatted_output
    if random:
        outnum = len(output)
        if n > outnum:
            n = outnum
        rand_out = []
        while len(rand_out) < n:
            randomnum = randint(0,outnum - 1)
            possible = output[randomnum]
            if possible not in rand_out:
                rand_out.append(possible)
        formatted_random_output = []
        for index, row in enumerate(rand_out):
            formatted_random_output.append(" ".join(row))
            print '% 4d' % index, " ".join(row)
        return formatted_random_output



def multiquery(corpus, query, sort_by = 'total'):
    """Creates a named tuple for a list of named queries to count.

    Pass in something like:

    [[u'NPs in corpus', r'NP'], [u'VPs in corpus', r'VP']]"""

    import collections
    from corpkit.query import interrogator
    from corpkit.edit import resorter
    from corpkit.edit import merger
    results = []
    for name, pattern in query:
        result = interrogator(corpus, '-C', pattern)
        result.totals[0] = name # rename count
        results.append(result.totals)
    if sort_by:
        results = resorter(results, sort_by = sort_by)
    tot = merger(results, r'.*', newname = 'Totals', printmerge = False)
    #print tot
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    output = outputnames(query, results, tot.totals)
    return output



def topix_search(topic_subcorpora, options, query, **kwargs):
    """Interrogates each topic subcorpus."""
    fullqueries = []
    results = [] # make empty list of results and totals
    totals = []
    for topic in topic_subcorpora: # for topic name
        result = interrogator(topic, options, query, **kwargs)
        fullqueries.append(result.query)
        try:
            results.append(result.results) # add to results
        except:
            results.append([])
        totals.append(result.totals)
    # now we should have 3x results and 3x totals, and a query
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals']) 
    output = outputnames(fullqueries, results, totals)
    return output

def query_test(query, have_ipython = False):
    import re
    import subprocess
    # define error searches 
    tregex_error = re.compile(r'^Error parsing expression')
    regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')
    #define command and run it
    if have_ipython:
        tregex_command = 'tregex.sh \'%s\' 2>&1' % (query)
        testpattern = get_ipython().getoutput(tregex_command)
    else:
        tregex_command = ['tregex.sh', '%s' % (query)]
        try:
            testpattern = subprocess.check_output(tregex_command, stderr=subprocess.STDOUT).split('\n')
        except Exception, e:
            testpattern = str(e.output).split('\n')
            print testpattern

    # if tregex error, give general error message
    if re.match(tregex_error, testpattern[0]):
        tregex_error_output = "Error parsing Tregex expression. Check for balanced parentheses and boundary delimiters."
        raise ValueError(tregex_error_output) 
    # if regex error, try to help
    if re.match(regex_error, testpattern[0]):
        info = testpattern[0].split(':')
        index_of_error = re.findall(r'index [0-9]+', info[1])
        justnum = index_of_error[0].split('dex ')
        spaces = ' ' * int(justnum[1])
        remove_start = query.split('/', 1)
        remove_end = remove_start[1].split('/', -1)
        regex_error_output = 'Error parsing regex inside Tregex query:%s'\
        '. Best guess: \n%s\n%s^' % (str(info[1]), str(remove_end[0]), spaces)
        raise ValueError(regex_error_output)
    # if nothing, the query's fine! 

def interroplot(path, query):
    from corpkit import interrogator, plotter
    quickstart = interrogator(path, 't', query)
    plotter(str(path), quickstart.results, fract_of = quickstart.totals)
