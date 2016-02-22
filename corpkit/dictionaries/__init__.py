all = ["wordlists", "roles", "bnc", "processes"]

from dictionaries.bnc import _get_bnc
from dictionaries.process_types import processes
from dictionaries.roles import roles
from dictionaries.wordlists import wordlists
from dictionaries.queries import queries

roles = roles
wordlists = wordlists
processes = processes
bnc = _get_bnc
queries = queries