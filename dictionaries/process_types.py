#!/usr/bin/python

#   dictionaries: process type wordlists
#   Author: Daniel McDonald

# This sinister code makes regular expressions to match verbs. You can add to the lists below.

# Thanks to Mick O'Donnell for the initial lists of process types



def process_types():
    """This function takes lists of regular and irregular process verbs
    and turns them into regexes. These can then be piped into Tregex queries, etc."""
    import collections
    
    irregular_relational_processes = ["become",
                                      "becomes",
                                      "became",
                                      "become",
                                      "becoming",
                                      "feel",
                                      "feels",
                                      "felt",
                                      "feeling",
                                      "be",
                                      "was",
                                      "been",
                                      "being",
                                      "are",
                                      "were",
                                      "is",
                                      "am",
                                      "[^a-z]s",
                                      "[^a-z]m",
                                      "[^a-z]re",
                                      "have",
                                      "has",
                                      "had",
                                      "had",
                                      "having",
                                      "[^a-z]d",
                                      "[^a-z]ve"]
    
    regular_relational_processes = ["sound",
                                      "look",
                                      "seem",
                                      "appear",
                                      "smell"]
    
    irregular_verbal_processes = ['forbid',
                                  'forbids',
                                  'forbade',
                                  'forbidden',
                                  'forbidding',
                                  'foretell',
                                  'foretells',
                                  'foretold',
                                  'foretold',
                                  'foretelling',
                                  'forswear',
                                  'forswears',
                                  'forswore',
                                  'forsworn',
                                  'forswearing',
                                  'prophesy',
                                  'prophesies',
                                  'prophesied',
                                  'prophesied',
                                  'prophesying',
                                  'say',
                                  'says',
                                  'said',
                                  'saying',
                                  'swear',
                                  'swears',
                                  'swore',
                                  'sworn',
                                  'swearing',
                                  'tell',
                                  'tells',
                                  'told',
                                  'telling',
                                  'write',
                                  'writes',
                                  'wrote',
                                  'written',
                                  'writing']
    regular_verbal_processes = ['certify', 
                                'deny', 
                                'imply', 
                                'move', 
                                'notify', 
                                'reply', 
                                'specify'
                                'accede',
                                'add',
                                'admit',
                                'advise',
                                'advocate',
                                'allege',
                                'announce',
                                'answer',
                                'apprise',
                                'argue',
                                'ask',
                                'assert',
                                'assure',
                                'attest',
                                'aver',
                                'avow',
                                'bark',
                                'beg',
                                'bellow',
                                'blubber',
                                'boast',
                                'brag',
                                'cable',
                                'call',
                                'claim',
                                'comment',
                                'complain',
                                'confess',
                                'confide',
                                'confirm',
                                'contend',
                                'convey',
                                'counsel',
                                'declare',
                                'demand',
                                'disclaim',
                                'disclose',
                                'divulge',
                                'emphasise',
                                'emphasize',
                                'encourage',
                                'exclaim',
                                'explain',
                                'forecast',
                                'gesture',
                                'grizzle',
                                'guarantee',
                                'hint',
                                'holler',
                                'indicate',
                                'inform',
                                'insist',
                                'intimate',
                                'mention',
                                'moan',
                                'mumble',
                                'murmur',
                                'mutter',
                                'note',
                                'object',
                                'offer',
                                'phone',
                                'pledge',
                                'preach',
                                'predicate',
                                'preordain',
                                'proclaim',
                                'profess',
                                'prohibit',
                                'promise',
                                'propose',
                                'protest',
                                'reaffirm',
                                'reassure',
                                'rejoin',
                                'remark',
                                'remind',
                                'repeat',
                                'report',
                                'request',
                                'require',
                                'respond',
                                'retort',
                                'reveal',
                                'riposte',
                                'roar',
                                'scream',
                                'shout',
                                'signal',
                                'state',
                                'stipulate',
                                'telegraph',
                                'telephone',
                                'testify',
                                'threaten',
                                'vow',
                                'warn',
                                'wire',
                                'reemphasise',
                                'reemphasize',
                                'rumor',
                                'rumour',
                                'yell']

    irregular_mental_processes = ['choose',
                                  'chooses',
                                  'chose',
                                  'chosen',
                                  'choosing',
                                  'feel',
                                  'feels',
                                  'felt',
                                  'feeling',
                                  'find',
                                  'finds',
                                  'found',
                                  'finding',
                                  'forget',
                                  'forgets',
                                  'forgot',
                                  'forgotten',
                                  'forgetting',
                                  'hear',
                                  'hears',
                                  'heard',
                                  'hearing',
                                  'know',
                                  'knows',
                                  'knew',
                                  'known',
                                  'knowing',
                                  'mean',
                                  'means',
                                  'meant',
                                  'meaning',
                                  'overhear',
                                  'overhears',
                                  'overheard',
                                  'overhearing',
                                  'prove',
                                  'proves',
                                  'proved',
                                  'proven',
                                  'proving',
                                  'read',
                                  'reads',
                                  'see',
                                  'sees',
                                  'saw',
                                  'seen',
                                  'seeing',
                                  'think',
                                  'thinks',
                                  'thought',
                                  'thinking',
                                  'understand',
                                  'understands',
                                  'understood',
                                  'understanding']
    
    regular_mental_processes = ['abide',
                                'abominate',
                                'accept',
                                'acknowledge',
                                'acquiesce',
                                'adjudge',
                                'adore',
                                'affirm',
                                'agree',
                                'allow',
                                'allure',
                                'anticipate',
                                'appreciate',
                                'ascertain',
                                'aspire',
                                'assent',
                                'assume',
                                'begrudge',
                                'believe',
                                'calculate',
                                'care',
                                'conceal',
                                'concede',
                                'conceive',
                                'concern',
                                'conclude',
                                'concur',
                                'condone',
                                'conjecture',
                                'consent',
                                'consider',
                                'contemplate',
                                'convince',
                                'crave',
                                'decide',
                                'deduce',
                                'deem',
                                'delight',
                                'desire',
                                'determine',
                                'detest',
                                'discern',
                                'discover',
                                'dislike',
                                'doubt',
                                'dread',
                                'enjoy',
                                'envisage',
                                'estimate',
                                'excuse',
                                'expect',
                                'exult',
                                'fear',
                                'foreknow',
                                'foresee',
                                'gather',
                                'grant',
                                'grasp',
                                'hate',
                                'hope',
                                'hurt',
                                'hypothesise',
                                'hypothesize',
                                'imagine',
                                'infer',
                                'inspire',
                                'intend',
                                'intuit',
                                'judge',
                                'ken',
                                'lament',
                                'like',
                                'loathe',
                                'love',
                                'marvel',
                                'mind',
                                'miss',
                                'need',
                                'neglect',
                                'notice',
                                'observe',
                                'omit',
                                'opine',
                                'perceive',
                                'plan',
                                'please',
                                'posit',
                                'postulate',
                                'pray',
                                'preclude',
                                'prefer',
                                'presume',
                                'presuppose',
                                'pretend',
                                'provoke',
                                'realize',
                                'realise',
                                'reason',
                                'recall',
                                'reckon',
                                'recognise',
                                'recognize',
                                'recollect',
                                'reflect',
                                'regret',
                                'rejoice',
                                'relish',
                                'remember',
                                'resent',
                                'resolve',
                                'rue',
                                'scent',
                                'scorn',
                                'sense',
                                'settle',
                                'speculate',
                                'suffer',
                                'suppose',
                                'surmise',
                                'surprise',
                                'suspect',
                                'trust',
                                'visualise',
                                'visualize',
                                'want',
                                'wish',
                                'wonder',
                                'yearn',
                                'rediscover'
                                'dream',
                                'justify', 
                                'figure', 
                                'smell', 
                                'worry']

    def regex_maker(irregular, regular):
        """makes a regex from the lists of words passed to it"""
        # add alternative spellings
        from dictionaries.word_transforms import usa_convert
        uk_convert = {v: k for k, v in usa_convert.items()}

        sib_ends = ['s', 'ss', 'sh', 'ch', 'x']
        vowels = ['a', 'e', 'i', 'o', 'u']
        non_double_words = ['happen', 'visit']
        t_ends = ['bend', 
                  'build',
                  'burn',
                  'deal',
                  'dream',
                  'dwell',
                  'lean',
                  'leap',
                  'learn',
                  'mean',
                  'send', 
                  'shot',
                  'smell',
                  'spend', 
                  'spill',
                  'spoil']

        to_add_to_regular_list = []
        to_add_to_irregular_list = []

        for w in regular:
            if w in usa_convert.keys():
              to_add_to_regular_list.append(usa_convert[w])
        for w in regular:
            if w in uk_convert.keys():
              to_add_to_regular_list.append(uk_convert[w])
        for w in irregular:
            if w in usa_convert.keys():
              to_add_to_irregular_list.append(usa_convert[w])
        for w in irregular:
            if w in uk_convert.keys():
              to_add_to_irregular_list.append(uk_convert[w])

        regular = sorted(list(set(regular + to_add_to_regular_list)))
        irregular = sorted(list(set(irregular + to_add_to_irregular_list)))

        regular_verbforms = []
        for w in regular:
            # remove entries in there by mistake!
            if w in irregular:
                print "'%s' in both regular and irregular lists." % w
                continue
            # base form
            regular_verbforms.append(w)
            # 3rd singular: 
            # catch -> catches
            if any([w.endswith(sib_end) for sib_end in sib_ends]):
                regular_verbforms.append(w + 'es')
            # buy -> buys
            #elif any([w.endswith('%sy' % v) for v in vowels]):
                #regular_verbforms.append(w + 's')
            # try -> tries
            elif w.endswith('y'):
                if not any([w.endswith('%sy' % v) for v in vowels]):
                    regular_verbforms.append(w[:-1] + 'ies')
                else:
                    regular_verbforms.append(w + 's')
            # bat -> bats, buy -> buys
            else:
                regular_verbforms.append(w + 's')

            # past tense
            # double the last letter if need be:
            if w[-1] not in vowels and w[-1] != 'y':
                if w[-2] in vowels:
                    if w[-3] not in vowels:
                        if w not in non_double_words:
                            if len(w) < 6:
                                w = w + w[-1]

            # try -> tried
            if w.endswith('y'):
                if w[-2] not in vowels:
                    regular_verbforms.append(w[:-1] + 'ied')
                else:
                    regular_verbforms.append(w + 'ed')
            elif w.endswith('e'):
                regular_verbforms.append(w + 'd')
            else:
                regular_verbforms.append(w + 'ed')
                if w in t_ends:
                    if w.endswith('d'):
                        regular_verbforms.append(w[:-1] + 't')
                    elif w.endswith('ll'):
                        regular_verbforms.append(w[:-1] + 't')
                    else:
                        regular_verbforms.append(w + 't')
            # is there a -t rule?

            # 'ing'
            # animate -> animating
            if w.endswith('e'):
                if not any([w.endswith('%se' % v) for v in vowels]):
                    regular_verbforms.append(w[:-1] + 'ing')
                else:
                    pass
            # look -> looking, see -> seeing
            else:
                regular_verbforms.append(w + 'ing')

        verbforms = sorted(list(set(regular_verbforms + irregular)))
        
        to_add_to_verbforms_list = []
        for w in verbforms:
            if w in usa_convert.keys():
              to_add_to_verbforms_list.append(usa_convert[w])
        for w in verbforms:
            if w in uk_convert.keys():
              to_add_to_verbforms_list.append(uk_convert[w])
        verbforms = sorted(list(set(verbforms + to_add_to_verbforms_list)))
        return r'(?i)\b(' + r'|'.join(verbforms) + r')\b'
    
    list_of_regexes = []
    for process_type in [[irregular_relational_processes, 
                         regular_relational_processes], 
                         [irregular_mental_processes, 
                         regular_mental_processes], 
                         [irregular_verbal_processes, 
                         regular_verbal_processes]]:
        # replace handles lemmata ending in e
        as_regex = regex_maker(process_type[0], process_type[1]).replace('e{1,2}', 'e{0,1}')
        list_of_regexes.append(as_regex)

        #regex_list = [regex_maker(process_type) for process_type in [relational_processes, mental_processes, verbal_processes]]
        # implement material process as any word not on this list?

    outputnames = collections.namedtuple('processes', ['relational',
                                  'mental',
                                  'verbal'])
    output = outputnames(list_of_regexes[0], list_of_regexes[1], list_of_regexes[2])
    return output

processes = process_types()


verbforms = []
for w in lst:
    forms = [w.replace("n't", "") for w in lexeme(w)]
    for f in forms:
        verbforms.append(f)

