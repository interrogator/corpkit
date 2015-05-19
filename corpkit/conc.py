
def conc(corpus, query, 
        n = 100, 
        random = False, 
        window = 50, 
        trees = False, 
        csvmake = False): 
    """A concordancer for Tregex queries"""
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
    from corpkit.query import query_test, check_pytex, check_dit
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    on_cloud = check_dit()
    
    def csvmaker(csvdata, sentences, csvmake):
        """Puts conc() results into tab-separated spreadsheet form"""
        # I made this before learning about Pandas etc., so there's
        # probably a much easier way to get the same result ...
        if os.path.isfile(csvmake):
            raise ValueError("CSV error: %s already exists in current directory. Move it, delete it, or change the name of the new .csv file." % csvmake)

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

    # make sure query is valid:
    query_test(query)

    # welcome message
    time = strftime("%H:%M:%S", localtime())
    print "\n%s: Getting concordances for %s ... \n          Query: %s\n" % (time, corpus, query)
    output = []
    if trees:
        options = '-s'
    else:
        options = '-t'

    # get whole sentences:
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh -o -w %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        else:
            tregex_command = 'tregex.sh -o -w %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        whole_results = get_ipython().getoutput(tregex_command)
        result = [line for line in whole_results if line]
    else:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh", "-o", "-w", "%s" % options, '%s' % query, "%s" % corpus]
        else:
            tregex_command = ["tregex.sh", "-o", "-w", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        whole_results = subprocess.check_output(tregex_command, stderr=FNULL)
        whole_results = os.linesep.join([s for s in whole_results.splitlines() if s]).split('\n')
    
    results = list(whole_results)
    
    if csvmake:
        sentences = list(results)
    
    # get just the match of the sentence
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh -o %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        else:
            tregex_command = 'tregex.sh -o %s \'%s\' %s 2>/dev/null' %(options, query, corpus)
        middle_column_result = get_ipython().getoutput(tregex_command)
        result = [line for line in middle_column_result if line]
    else:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % corpus]
        else:
            tregex_command = ["tregex.sh", "-o", "%s" % options, '%s' % query, "%s" % corpus]
        FNULL = open(os.devnull, 'w')
        middle_column_result = subprocess.check_output(tregex_command, stderr=FNULL)
        middle_column_result = os.linesep.join([s for s in middle_column_result.splitlines() if s]).split('\n')
    tresults = list(middle_column_result)
    zipped = zip(whole_results, middle_column_result)
    all_dupes = []

    
    # make sure we have some results
    if len(zipped) == 0:
        raise ValueError("No matches found, sorry. I wish there was more I could tell you.") 

    maximum = len(max(tresults, key=len)) # longest result in characters
    csvdata = []
    unique_results = []
    for result in zipped: 
        tree = result[0]
        pattern = result[1]
        if not trees:
            regex = re.compile(r"(\b[^\s]{0,1}.{," + re.escape(str(window)) + r"})(\b" + re.escape(pattern) + r"\b)(.{," + re.escape(str(window)) + r"}[^\s]\b)")
        else:
            regex = re.compile(r"(.{,%s})(%s)(.{,%s})" % (window, re.escape(pattern), window ))
        search = re.findall(regex, tree)
        for result in search:
            unique_results.append(result)
    unique_results = set(sorted(unique_results)) # make unique
    
    # from here on down needs a major cleanup ...
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
