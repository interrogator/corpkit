def configurations(corpus, search, **kwargs):
    """Get behaviour of a word---see corpkit.corpus.Corpus.configurations() for docs"""

    import corpkit
    from dictionaries.wordlists import wordlists
    from dictionaries.roles import roles
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
        word_or_token = search.get('l')
    else:
        if search.get('w'):
            dep_word_or_lemma = 'd'
            gov_word_or_lemma = 'g'
            word_or_token = search.get('w')

    queries = {'participant': 

                {'left_participant_in':             
                  {dep_word_or_lemma: word_or_token,
                   'df': r'^.subj.*',
                   'f': roles.event},

                'right_participant_in':
                  {dep_word_or_lemma: word_or_token,
                   'df': r'^[di]obj',
                   'f': roles.event},

                'modified_by':
                  {'f': r'^amod', 
                   gov_word_or_lemma: word_or_token},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   'gf': roles.participant,
                   gov_word_or_lemma: word_or_token},
                },

               'process':

                {'has_subject':
                  {'f': roles.participant1,
                   gov_word_or_lemma: word_or_token},

                 'has_object':
                  {'f': roles.participant2,
                   gov_word_or_lemma: word_or_token},

                 'modalised_by':
                  {'f': r'aux',
                   'w': wordlists.modals,
                   gov_word_or_lemma: word_or_token},

                 'modulated_by':
                  {'f': 'advmod',
                   'gf': roles.event,
                   gov_word_or_lemma: word_or_token},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   'gf': roles.event,                 
                   gov_word_or_lemma: word_or_token},
              
                },

               'modifier':

                {'modifies':
                  {'df': roles.modifier,
                   dep_word_or_lemma: word_or_token},

                 'modulated_by':
                  {'f': 'advmod',
                   'gf': roles.modifier,
                   gov_word_or_lemma: word_or_token},

                 'and_or':
                  {'f': 'conj:(and|or)',
                   'gf': roles.modifier,
                   gov_word_or_lemma: word_or_token},

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
        queries['and_or'] = {'f': 'conj:(and|or)', gov_word_or_lemma: word_or_token},

    total_queries = 0
    for k, v in queries.items():
        for subk, subv in v.items():
            total_queries += 1

    kwargs['search'] = queries
    data = interrogator(corpus, **kwargs)
    for k, v in data.items():
        v.results = v.results.drop(word_or_token, axis = 1, errors = 'ignore')
        v.totals = v.results.sum(axis = 1)
        data[k] = v
    return data

