def configurations(corpus, search, **kwargs):
    """Get behaviour of a word---see corpkit.corpus.Corpus.configurations() for docs"""

    import corpkit
    from dictionaries.wordlists import wordlists
    from interrogation import Interrodict
    from interrogator import interrogator

    from collections import OrderedDict

    root = kwargs.get('root')
    note = kwargs.get('note')

    if search.get('l') and search.get('w'):
        raise ValueError('Search only for a word or a lemma, not both.')

    if search.get('l'):
        dep_word_or_lemma = 'dl'
        gov_word_or_lemma = 'gl'
        byme = search.get('l')
    else:
        if search.get('w'):
            dep_word_or_lemma = 'd'
            gov_word_or_lemma = 'g'
            byme = search.get('w')

    queries = {'participant': 

                {'left_participant_in':             
                  {dep_word_or_lemma: byme,
                   'df': r'^.subj.*',
                   'f': 'root'},

                'right_participant_in':
                  {dep_word_or_lemma: byme,
                   'df': r'^[di]obj',
                   'f': 'root'},

                'modified_by':
                  {'f': r'^amod', 
                   gov_word_or_lemma: byme},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   gov_word_or_lemma: byme},
                },

               'process':

                {'has_subject':
                  {'f': r'^.subj.*',
                   gov_word_or_lemma: byme},

                 'has_object':
                  {'f': r'^[di]obj',
                   gov_word_or_lemma: byme},

                 'modalised_by':
                  {'f': r'aux',
                   'w': wordlists.modals,
                   gov_word_or_lemma: byme},

                 'modulated_by':
                  {'f': 'advmod',
                   gov_word_or_lemma: byme},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   gov_word_or_lemma: byme},
              
                },

               'modifier':

                {'modifies':
                  {'df': 'a(dv)?mod', 
                   dep_word_or_lemma: byme},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   gov_word_or_lemma: byme},

                }
            }

    if search.get('f'):
        if search.get('f').lower().startswith('part'):
            queries = queries['participant']
        elif search.get('f').lower().startswith('proc'):
            queries = queries['process']
        elif search.get('f').lower().startswith('mod'):
            queries = queries['modifier']
    else:
        newqueries = {}
        for k, v in queries.items():
            for name, pattern in v.items():
                newqueries[name] = pattern
        queries = newqueries

    total_queries = 0
    for k, v in queries.items():
        for subk, subv in v.items():
            total_queries += 1

    kwargs['search'] = queries
    data = interrogator(corpus, **kwargs)
    for k, v in data.items():
        v.results = v.results.drop(byme, axis = 1, errors = 'ignore')
        v.totals = v.results.sum(axis = 1)
        data[k] = v
    return data

