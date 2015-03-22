# WordNet handles most lemmatisation, but it struggles with a few things.

# During lemmatisation, words will be corrected via this list.

# insert the word and what you want it to be turned into.

wordlist = {u"felt": u"feel",
           u"'s": u"is",
           u"'re": u"are",
           u"'m": u"am",
           u"'d": u"had",
           u"'ve": u"have",
           u"n't": u"not",
           u"smelt": u"smell",
           u"others": u"other"}


# this one translates the dependency relationship into a wordnet tag:

deptags = {u'amod': 'n',
           u'nn': 'n',
           u'rcmod': 'n',
           u'dobj': 'v',
           u'nsubj': 'v',
           u'nsubjpass': 'v',
           u'advmod': 'v',
           u'iobj': 'v',
           u'acomp': 'v',
           u'cop': 'v',
           u'advmod': 'v',
           u'iobj': 'v',
           u'xcomp': 'v',
           u'ccomp': 'v'}

