# WordNet handles most lemmatisation, but it struggles with a few things.

# During lemmatisation, words will be corrected via this list.

# insert the word and what you want it to be turned into. 
# This also includes POS tags.

wordlist = {u"felt": u"feel",
           u"'s": u"is",
           u"'re": u"are",
           u"'m": u"am",
           u"'d": u"had",
           u"'ve": u"have",
           u"n't": u"not",
           u"smelt": u"smell",
           u"people": u"person",
           u"others": u"other"}

taglemma = {u"cc": u"Coordinating conjunction",
           u"cd": u"Cardinal number",
           u"dt": u"Determiner",
           u"ex": u"Ex. there",
           u"fw": u"Foreign word",
           u"in": u"Preposition",
           u"ls": u"List item marker",
           u"md": u"Modal",
           u"pdt": u"Predeterminer",
           u"pos": u"Possessive ending",
           u"rp": u"Particle",
           u"sym": u"Symbol",
           u"to": u"to",
           u"uh": u"Interjection",
           u"wdt": u"Wh-determiner",
           u"wp": u"Wh-pronoun",
           u"wp$": u"Possessive wh-pronoun",
           u"wrb": u"Wh-adverb",
           u"vbp": u"Verb",
           u"vbz": u"Verb",
           u"vbn": u"Verb",
           u"vbd": u"Verb",
           u"vbg": u"Verb",
           u"vb": u"Verb",
           u"nnp": u"Noun",
           u"nns": u"Noun",
           u"nnps": u"Noun",
           u"nn": u"Noun",
           u"prp": u"Pronoun",
           u"prp$": u"Pronoun",
           u"jj": u"Adjective",
           u"jjr": u"Adjective",
           u"jjs": u"Adjective",
           u"rb": u"Adverb",
           u"rbr": u"Adverb",
           u"rbs": u"Adverb",
           u"wp": u"Wh- pronoun",
           u"wp$": u"Wh- pronoun"}

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



