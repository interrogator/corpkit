def configurations(corpus, search, **kwargs):
    """Get behaviour of a word"""
    import corpkit
    from collections import OrderedDict
    from dictionaries.wordlists import wordlists
    from interrogation import Interrodict
    from interrogator import interrogator

    root = kwargs.get('root')
    note = kwargs.get('note')

    queries = {'participant': 

                {'left_participant_in':             
                  {'d': search.get('w'),
                   'df': r'^.subj.*',
                   'f': 'root'},

                'right_participant_in':
                  {'d': search.get('w'),
                   'df': r'^[di]obj',
                   'f': 'root'},

                'modified_by':
                  {'f': r'^amod', 
                   'g': search.get('w')},
                },

               'process':

                {'has_subject':
                  {'f': r'^.subj.*',
                   'g': search.get('w')},

                 'has_object':
                  {'f': r'^[di]obj',
                   'g': search.get('w')},

                 'modalised_by':
                  {'f': r'aux',
                   'w': wordlists.modals,
                   'g': search.get('w')},

                 'has_circumstance':
                  {'f': 'nmod.*'},
              
                },

               'modifier':

                {'modifies_noun':
                  {'df': 'a(dv)?mod', 
                   'd': search.get('w')},
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
    return data

