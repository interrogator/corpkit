__all__ = ["wordlists", "roles", "bnc", "processes", "verbs", 
           "uktous", "tagtoclass", "queries", "mergetags"]

from corpkit.dictionaries.bnc import _get_bnc
from corpkit.dictionaries.process_types import processes
from corpkit.dictionaries.process_types import verbs
from corpkit.dictionaries.roles import roles
from corpkit.dictionaries.wordlists import wordlists
from corpkit.dictionaries.queries import queries
from corpkit.dictionaries.word_transforms import taglemma
from corpkit.dictionaries.word_transforms import mergetags
from corpkit.dictionaries.word_transforms import usa_convert

roles = roles
wordlists = wordlists
processes = processes
bnc = _get_bnc
queries = queries
tagtoclass = taglemma
uktous = usa_convert
mergetags = mergetags
verbs = verbs