__all__ = ["wordlists", "roles", "bnc", "processes", "verbs", 
           "uktous", "tagtoclass", "queries", "mergetags"]

import corpkit
from dictionaries.bnc import _get_bnc
from dictionaries.process_types import processes
from dictionaries.process_types import verbs
from dictionaries.roles import roles
from dictionaries.wordlists import wordlists
from dictionaries.queries import queries
from dictionaries.word_transforms import taglemma
from dictionaries.word_transforms import mergetags
from dictionaries.word_transforms import usa_convert

roles = roles
wordlists = wordlists
processes = processes
bnc = _get_bnc
queries = queries
tagtoclass = taglemma
uktous = usa_convert
mergetags = mergetags
verbs = verbs