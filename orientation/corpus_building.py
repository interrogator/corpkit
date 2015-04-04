# <headingcell level=1>
# *corpkit*: a Python-based toolkit for working with parsed linguistic corpora
# <headingcell level=2>

# <markdowncell>
# [Daniel McDonald](mailto:mcdonaldd@unimelb.edu.au?Subject=corpkit)**
#---------------------------
# <markdowncell>
# <br>

# > **SUMMARY:** This *IPython Notebook* shows you how to use `corpkit` to build a parsed corpus.

# Sophisticated corpora can't be built without a little bit of coding. The functions here aim to simplify the process as much as possible, however.

# <codecell>
import corpkit
from corpkit import x, y, z

# <headingcell level=2>
# Getting raw data

# <markdowncell>
# The function below will get all URLs listed on a webpage. You can use a `criteria` regex and `remove` to get 
# <codecell>
urls = get_urls(url, criteria = False, remove = True):

# <markdowncell>
# You could, of course, do this recursively...

# <codecell>
bigger_list = []
for index, url in enumerate(urls):
    bigger_list.append(url)
    print 'Doing %d/%d...' % (index + 1, len(urls))
    more_urls = get_urls(url)
    for u in more_urls:
        bigger_list.append(u)
print len(bigger_list)

# <headingcell level=2>
# Downloading files

# <markdowncell>
# So long as space isn't an issue, it's probably better to download the HTML, as the page could vanish one day. Also, one of `corpkit`'s cool features is connecting HTML to concordance lines. This makes that much easier.

# <codecell>
downloader(urls, new_path = 'downloaded', wait = 5)

# <markdowncell>
# You'll now have a 'downloaded' folder in the current directory.

# <headingcell level=2>
# Getting text from files

# <markdowncell>
# There are two major approaches. One is to use a heuristic approach to get anything in the HTML that looks like natural language. This option is most useful for people who are either very new to programming, or seeking to make larger, more general corpora. The second option is to traverse the HTML, and pull out the exact things we want. This can't be fully automated, because it's very different for everyone.

# <headingcell level=3>
# via JusText

# <headingcell level=3>
# via Beautiful Soup

# <markdowncell>
# This method is more complicated, but is superior. If we want to make a corpus with structure, we want to attach metadata to every extracted text, so that we can then structure according to the metadata attribute.

# <headingcell level=2>
# Structuring the data

# <headingcell level=2>
# Parsing the data

# <markdowncell>
# We need to instal CoreNLP and a Python wrapper for it:

# <codecell>
# sudo pip install pexpect unidecode
# get the wrapper
! git clone git://github.com/arne-cl/stanford-corenlp-python.git
# go to wrapper dir
! cd stanford-corenlp-python
# get stanford corenlp
! wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip
# unzip it
! unzip stanford-corenlp-full-2014-08-27.zip
# install the wrapper, which installs corenlp too
! sudo python setup.py install
# go back to original dir and delete everything we no longer need
! cd ..
! rm -f -R stanford-corenlp-python

# <codecell>
corpus_path = 'data/structured_corpus'
stanford_parse(corpus_path)

# <markdowncell>
# Assuming everything went smoothly, you should now be able to interrogate the corpus. For documentation on this subject, head over to `orientation.ipynb`.