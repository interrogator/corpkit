#!/usr/bin/python

#   dictionaries: process type wordlists
#   Author: Daniel McDonald

# make regular expressions and lists of inflected words from word lists
try:
    from corpkit.lazyprop import lazyprop
except:
    import corpkit
    from lazyprop import lazyprop

def _verbs():
    import corpkit
    from dictionaries.verblist import allverbs
    verblist = [i for i in allverbs if '_' not in i]
    return Wordlist(verblist)

def load_verb_data():
    """load the verb lexicon"""

    def resource_path(relative):
        """seemingly not working"""
        import os
        return os.path.join(os.environ.get("_MEIPASS2", os.path.abspath(".")), relative)

    import os
    import corpkit
    import pickle
    from corpkit.process import get_gui_resource_dir
    corpath = os.path.dirname(corpkit.__file__)
    baspat = os.path.dirname(corpath)
    dicpath = os.path.join(baspat, 'dictionaries')
    lastpath = os.path.join(baspat, 'corpkit', 'dictionaries')
    
    paths_to_check = [resource_path('eng_verb_lexicon.p'),
                      os.path.join(dicpath, 'eng_verb_lexicon.p'),
                      os.path.join(get_gui_resource_dir(), 'eng_verb_lexicon.p'),
                      os.path.join(lastpath, 'eng_verb_lexicon.p')]

    for p in paths_to_check:
        try:
            return pickle.load(open(p, 'rb'))
        except:
            pass

    return

def find_lexeme(verb):
    """ For a regular verb (base form), returns the forms using a rule-based approach.
    
    taken from pattern.en, because it wouldn't go into py2app properly
    """
    vowels = ['a', 'e', 'i', 'o', 'u']
    v = verb.lower()
    if len(v) > 1 and v.endswith("e") and v[-2] not in vowels:
        # Verbs ending in a consonant followed by "e": dance, save, devote, evolve.
        return [v, v, v, v+"s", v, v[:-1]+"ing"] + [v+"d"]*6
    if len(v) > 1 and v.endswith("y") and v[-2] not in vowels:
        # Verbs ending in a consonant followed by "y": comply, copy, magnify.
        return [v, v, v, v[:-1]+"ies", v, v+"ing"] + [v[:-1]+"ied"]*6
    if v.endswith(("ss", "sh", "ch", "x")):
        # Verbs ending in sibilants: kiss, bless, box, polish, preach.
        return [v, v, v, v+"es", v, v+"ing"] + [v+"ed"]*6
    if v.endswith("ic"):
        # Verbs ending in -ic: panic, mimic.
        return [v, v, v, v+"es", v, v+"king"] + [v+"ked"]*6
    if len(v) > 1 and v[-1] not in vowels and v[-2] not in vowels:
        # Verbs ending in a consonant cluster: delight, clamp.
        return [v, v, v, v+"s", v, v+"ing"] + [v+"ed"]*6
    if (len(v) > 1 and v.endswith(("y", "w")) and v[-2] in vowels) \
    or (len(v) > 2 and v[-1] not in vowels and v[-2] in vowels and v[-3] in vowels) \
    or (len(v) > 3 and v[-1] not in vowels and v[-3] in vowels and v[-4] in vowels):
        # Verbs ending in a long vowel or diphthong followed by a consonant: paint, devour, play.
        return [v, v, v, v+"s", v, v+"ing"] + [v+"ed"]*6
    if len(v) > 2 and v[-1] not in vowels and v[-2] in vowels and v[-3] not in vowels:
        # Verbs ending in a short vowel followed by a consonant: chat, chop, or compel.
        return [v, v, v, v+"s", v, v+v[-1]+"ing"] + [v+v[-1]+"ed"]*6
    return [v, v, v, v+"s", v, v+"ing"] + [v+"ed"]*6

def get_both_spellings(verb_list):
    """add alternative spellings to verb_list"""
    from corpkit.dictionaries.word_transforms import usa_convert
    uk_convert = {v: k for k, v in usa_convert.items()}
    to_add_to_verb_list = []
    for w in verb_list:
        if w in usa_convert.keys():
          to_add_to_verb_list.append(usa_convert[w])
    for w in verb_list:
        if w in uk_convert.keys():
          to_add_to_verb_list.append(uk_convert[w])
    verb_list = sorted(list(set(verb_list + to_add_to_verb_list)))
    return verb_list

def add_verb_inflections(verb_list):
    """add verb inflections to verb_list"""
    from corpkit.dictionaries.word_transforms import usa_convert
    uk_convert = {v: k for k, v in usa_convert.items()}

    # get lexemes
    lexemes = load_verb_data()
    verbforms = []
    
    # for each verb, get or guess the inflections
    # make list of ALL VERBS IN ALL INFLECTIONS
    all_lists = [lst for lst in lexemes.values()]
    allverbs = []
    for lst in all_lists:
        for v in lst:
            if v:
                allverbs.append(v)
    allverbs = list(set(allverbs))
    # use dict first
    for w in verb_list:
        verbforms.append(w)
        try:
            wforms = lexemes[w]
        except KeyError:
            # if not in dict, if it's an inflection, forget it
            if w in allverbs:
                continue
            if "'" in w:
                continue
            # if it's a coinage, guess
            else:
                wforms = find_lexeme(w)
        # get list of unique forms
        forms = list(set([form.replace("n't", "").replace(" not", "") for form in wforms if form]))
      
        for f in forms:
            verbforms.append(f)
      
      # deal with contractions
        if w == 'be':
            be_conts = [r"'m", r"'re", r"'s"]
            for cont in be_conts:
                verbforms.append(cont)
        if w == "have":
            have_conts = [r"'d", r"'s", r"'ve"]
            for cont in have_conts:
                verbforms.append(cont)
    
    # go over again, and add both possible spellings
    to_add = []
    for w in verbforms:
        if w in usa_convert.keys():
            to_add.append(usa_convert[w])
    for w in verbforms:
        if w in uk_convert.keys():
            to_add.append(uk_convert[w])
    verbforms = sorted(list(set(verbforms + to_add)))

    # ensure unicode
    t = []
    for w in verbforms:
        try:
            t.append(unicode(w, errors='ignore'))
        except:
            t.append(w)
    return t

# using 'list' keeps compatibility---change to object with no super call soon

class Wordlist(list):
    """A list of words, containing a `words` attribute and a `lemmata` attribute"""
    
    def __init__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs
        super(Wordlist, self).__init__(self.data)

    @lazyprop
    def words(self):
        """get inflections"""
        if not self.kwargs.get('single'):
            return Wordlist(add_verb_inflections(get_both_spellings(self.data)), single=True)
        else:
            return

    @lazyprop
    def lemmata(self):
        """show base forms of verbs"""
        if not self.kwargs.get('single'):
            return Wordlist(get_both_spellings(self.data), single=True)
        else:
            return

    def as_regex(self, boundaries='w', case_sensitive=False, inverse=False):
        """turn list into regular expression matching any item in list"""
        if self.kwargs.get('single'):
            from corpkit import as_regex
            return as_regex(get_both_spellings(self.data),
                            boundaries=boundaries,
                            case_sensitive=case_sensitive,
                            inverse=inverse
                           )

class Processes(object):
    """Process types: relational, verbal, mental, material"""
    def __init__(self):
        relational = ["become",
                      "feel",
                      "be",
                      "have",
                      "sound",
                      "look",
                      "seem",
                      "appear",
                      "smell"
                     ]

        verbal =     ["forbid",
                    "forswear",
                    "prophesy",
                    "say",
                    "swear",
                    "tell",
                    "write",
                    "certify", 
                    "deny", 
                    "imply", 
                    "move", 
                    "notify", 
                    "reply", 
                    "specify",
                    "accede",
                    "add",
                    "admit",
                    "advise",
                    "advocate",
                    "allege",
                    "announce",
                    "answer",
                    "apprise",
                    "argue",
                    "ask",
                    "assert",
                    "assure",
                    "attest",
                    "aver",
                    "avow",
                    "bark",
                    "beg",
                    "bellow",
                    "blubber",
                    "boast",
                    "brag",
                    "cable",
                    "call",
                    "claim",
                    "comment",
                    "complain",
                    "confess",
                    "confide",
                    "confirm",
                    "contend",
                    "convey",
                    "counsel",
                    "declare",
                    "demand",
                    "disclaim",
                    "disclose",
                    "divulge",
                    "emphasise",
                    "emphasize",
                    "encourage",
                    "exclaim",
                    "explain",
                    "forecast",
                    "gesture",
                    "grizzle",
                    "guarantee",
                    "hint",
                    "holler",
                    "indicate",
                    "inform",
                    "insist",
                    "intimate",
                    "mention",
                    "moan",
                    "mumble",
                    "murmur",
                    "mutter",
                    "note",
                    "object",
                    "offer",
                    "phone",
                    "pledge",
                    "preach",
                    "predicate",
                    "preordain",
                    "prescribe",
                    "proclaim",
                    "profess",
                    "prohibit",
                    "promise",
                    "propose",
                    "protest",
                    "reaffirm",
                    "reassure",
                    "rejoin",
                    "remark",
                    "remind",
                    "repeat",
                    "report",
                    "request",
                    "require",
                    "respond",
                    "retort",
                    "reveal",
                    "riposte",
                    "roar",
                    "scream",
                    "shout",
                    "signal",
                    "state",
                    "stipulate",
                    "telegraph",
                    "telephone",
                    "testify",
                    "threaten",
                    "vow",
                    "warn",
                    "wire",
                    "reemphasise",
                    "reemphasize",
                    "rumor",
                    "rumour",
                    "yell",
                    # added manually:
                    'tell',
                     'say',
                     'call',
                     'vent',
                     'talk',
                     'ask',
                     'prescribe',
                     'diagnose',
                     'speak',
                     'suggest',
                     'mention',
                     'recommend',
                     'add',
                     'discuss',
                     'agree',
                     'contact',
                     'refer',
                     'explain',
                     'write',
                     'consult',
                     'advise',
                     'insist',
                     'perscribe',
                     'warn',
                     'offer',
                     'inform',
                     'question',
                     'describe',
                     'convince',
                     'order',
                     'report',
                     'lie',
                     'address',
                     'ring',
                     'state',
                     "pray",
                     'phone',
                     'share',
                     'beg',
                     'blame',
                     'instruct',
                     'chat',
                     'email',
                     'assure',
                     'dx',
                     'recomend',
                     'prescibe',
                     'promise',
                     'communicate',
                     'notify',
                     'claim',
                     'convince',
                     'page',
                     'wish',
                     'post',
                     'complain',
                     'swear']

        behavioural = ['laugh', 'cry', 'listen', 'look', 'hear', 'wake', 'awaken', ]

        mental =      ["choose",
                       "feel",
                       "find",
                       "forget",
                       "hear",
                       "know",
                       "mean",
                       "overhear",
                       "prove",
                       "read",
                       "see",
                       "think",
                       "understand",
                       "abide",
                       "abominate",
                       "accept",
                       "acknowledge",
                       "acquiesce",
                       "adjudge",
                       "adore",
                       "affirm",
                       "agree",
                       "allow",
                       "allure",
                       "anticipate",
                       "appreciate",
                       "ascertain",
                       "aspire",
                       "assent",
                       "assume",
                       "begrudge",
                       "believe",
                       "calculate",
                       "care",
                       "conceal",
                       "concede",
                       "conceive",
                       "concern",
                       "conclude",
                       "concur",
                       "condone",
                       "conjecture",
                       "consent",
                       "consider",
                       "contemplate",
                       "convince",
                       "crave",
                       "decide",
                       "deduce",
                       "deem",
                       "delight",
                       "desire",
                       "determine",
                       "detest",
                       "discern",
                       "discover",
                       "dislike",
                       "doubt",
                       "dread",
                       "enjoy",
                       "envisage",
                       "estimate",
                       "excuse",
                       "expect",
                       "exult",
                       "fear",
                       "foreknow",
                       "foresee",
                       "gather",
                       "grant",
                       "grasp",
                       "hate",
                       "hope",
                       "hurt",
                       "hypothesise",
                       "hypothesize",
                       "imagine",
                       "infer",
                       "inspire",
                       "intend",
                       "intuit",
                       "judge",
                       "ken",
                       "lament",
                       "like",
                       "loathe",
                       "love",
                       "marvel",
                       "mind",
                       "miss",
                       "need",
                       "neglect",
                       "notice",
                       "observe",
                       "omit",
                       "opine",
                       "perceive",
                       "plan",
                       "please",
                       "posit",
                       "postulate",
                       "pray",
                       "preclude",
                       "prefer",
                       "presume",
                       "presuppose",
                       "pretend",
                       "provoke",
                       "realize",
                       "realise",
                       "reason",
                       "recall",
                       "reckon",
                       "recognise",
                       "recognize",
                       "recollect",
                       "reflect",
                       "regret",
                       "rejoice",
                       "relish",
                       "remember",
                       "resent",
                       "resolve",
                       "rue",
                       "scent",
                       "scorn",
                       "sense",
                       "settle",
                       "speculate",
                       "suffer",
                       "suppose",
                       "surmise",
                       "surprise",
                       "suspect",
                       "trust",
                       "visualise",
                       "visualize",
                       "want",
                       "wish",
                       "wonder",
                       "yearn",
                       "rediscover",
                       "dream",
                       "justify", 
                       "figure", 
                       "smell", 
                       "worry",
                       'know',
                       'think',
                       'feel',
                       'want',
                       'hope',
                       'find',
                       'guess',
                       'love',
                       'wish',
                       'like',
                       'understand',
                       'wonder',
                       'believe',
                       'hate',
                       'remember',
                       'agree',
                       'notice',
                       'learn',
                       'realize',
                       'miss',
                       'appreciate',
                       'decide',
                       'suffer',
                       'deal',
                       'forget',
                       'care',
                       'imagine',
                       'relate',
                       'worry',
                       'figure',
                       'handle',
                       'struggle',
                       'pray',
                       'consider',
                       'enjoy',
                       'expect',
                       'plan',
                       'suppose',
                       'trust',
                       'bother',
                       'blame',
                       'accept',
                       'admit',
                       'assume',
                       'remind',
                       'seek',
                       'bet',
                       'refuse',
                       'cope',
                       'choose',
                       'freak',
                       'fear',
                       'question',
                       'recall',
                       'doubt',
                       'suspect',
                       'focus',
                       'calm'
                      ]
 
        can_be_material = ['bother', 'find']

        self.relational = Wordlist(relational)
        self.verbal = Wordlist(verbal)
        self.mental = Wordlist(mental)
        self.behavioural = Wordlist(behavioural)
        from corpkit.dictionaries.verblist import allverbs
        nonmat = set(self.relational + self.verbal + self.behavioural + self.mental)
        vbs = [i for i in allverbs if i not in nonmat and '_' not in i]
        self.material = Wordlist(vbs + can_be_material)

processes = Processes()

verbs = _verbs()
