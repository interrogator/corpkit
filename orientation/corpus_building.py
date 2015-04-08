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
# The function below will get all URLs listed on a webpage. You can use a `criteria` regex and `remove` to remove/keep good URLs.

# <codecell>
% load_ext soup
urls = get_urls('http://www.theage.com.au', r'theage.*political-news', remove = False)
print urls

# <markdowncell>
# You could, of course, do this recursively. It would probably be wise to use `criteria` to restrict the domain:

# <codecell>
bigger_list = []
for index, url in enumerate(urls):
    bigger_list.append(url)
    print 'Doing %d/%d...' % (index + 1, len(urls))
    more_urls = get_urls(url, r'www\.theage\.com\.au', remove = False)
    for u in more_urls:
        bigger_list.append(u)
# we only want unique entries:
unique_urls = sorted(set(bigger_list))
print '%d unique URLs!' len(unique_urls)

# <headingcell level=2>
# Downloading files

# <markdowncell>
# So long as hard disk space isn't an issue, it's better to download the HTML, as the page could vanish one day. Also, one of `corpkit`'s cool features is connecting HTML to concordance lines, which at present works with downloaded HTML only.

# It's bad form to download a lot of URLs without a little but of wait time. Here, it's set to five, which is usually polite enough.

# <codecell>
# we won't use our bigger list...
downloader(urls, new_path = 'html', wait = 5)

# <markdowncell>
# When it's done, there will be an 'html' folder in the current directory.

# <headingcell level=2>
# Making a corpus from the HTML

# <markdowncell>
# Now that we have the HTML files, we can build a corpus.

# To take advantage of all of `corpkit`'s features, we will build a corpus where each file contains:

# 1. The raw text we're interested in
# 2. The spelling corrected version
# 2. The annotated versions of the spelling corrected version
# 3. The original HTML, so that we can reconstitute the text's original context.

# The other thing we'll do is structure the corpus by a metadata attribute. Rather than having a huge set of text files, we'll have a corpus with subcorpora (a folder with subfolders). `corpkit` will then be able to run over each subcorpus with the same query and plot results.

# So, our workflow will be:

# 1. Get the raw text of interest from the HTML and the metadata attribute we'll structure our corpus by
# 2. Normalise the spelling of the texts, to aid parsing
# 3. Parse the spelling corrected version with CoreNLP
# 4. Make subcorpora, and put each text, annotations and html in the right spot

# To make a well-structured corpus, some steps will require some user input, which may in turn mean that you need to write some Python from scratch. Below is a basic guide.

# <headingcell level=3>
# Get raw text and metadata

# <markdowncell>
# This is the most difficult part of the entire process, and it can't be totally automated, since what kind of text you want, and what metadata feature you want to use to structure the corpus, could be almost anything.

# We're going to use Beautiful Soup, an HTML parser, to get what we want from our text. You may well need to use [its documentation](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) to figure out how to extract the right things from your HTML.

# `corpkit`'s functions use [ipython-beautifulsoup](https://github.com/Psycojoker/ipython-beautifulsoup), which very helpfully displays the raw and rendered HTML together.

# What you need to do is define two functions, `get_text` and `get_metadata`:

# <codecell>
def get_text():
	return text

# <codecell>
def get_metadata():
	return metadata

# <codecell>
# attempt

# <markdowncell>
# What you want to end up with is a *tuple* with two parts: the text, and the metadata.

# <codecell>
# real

# <headingcell level=4>
# The simpler approach

# <markdowncell>
# If you're in a hurry to get text from the HTML, and aren't too fussed about exactly what part of the page it comes from, you can use `simple_text_extractor()`, which relies on [justext]():

# <codecell>
simple_text_extractor()

# <headingcell level=3>
# Normalise spelling

# <codecell>
correct_spelling()

# <headingcell level=3>
# Parse normalised texts


# <headingcell level=3>
# Make subcorpora
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