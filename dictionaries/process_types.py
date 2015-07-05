#!/usr/bin/python

#   dictionaries: process type wordlists
#   Author: Daniel McDonald

# This sinister code makes regular expressions to match verbs. You can add to the lists below.

# Thanks to Mick O'Donnell for the initial lists of process types



def process_types():
    """Make a named tuple for each process type (no material yet)"""
    import collections
    
    relational = ["become",
                  "feel",
                  "be",
                  "have",
                  "sound",
                  "look",
                  "seem",
                  "appear",
                  "smell"]

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
                  "yell"]

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
                   "worry"]

    def regex_maker(verb_list):
        """makes a regex from the list of words passed to it"""
        # add alternative spellings
        from dictionaries.word_transforms import usa_convert
        from pattern.en import lexeme
        uk_convert = {v: k for k, v in usa_convert.items()}
        to_add_to_verb_list = []
        for w in verb_list:
            if w in usa_convert.keys():
              to_add_to_verb_list.append(usa_convert[w])
        for w in verb_list:
            if w in uk_convert.keys():
              to_add_to_verb_list.append(uk_convert[w])
        verb_list = sorted(list(set(verb_list + to_add_to_verb_list)))

        verbforms = []
        for w in verb_list:
          forms = [form.replace("n't", "").replace(" not", "") for form in lexeme(w)]
          for f in forms:
              verbforms.append(f)
          # deal with contractions
          if w == 'be':
              be_conts = [r'[^a-z]m', r'[^a-z]re', r'[^a-z]s']
              for cont in be_conts:
                  verbforms.append(cont)
          if w == 'have':
              have_conts = [r'^[a-z]d', r'[^a-z]s', r'[^a-z]ve']
              for cont in have_conts:
                  verbforms.append(cont)
        
        to_add = []
        for w in verbforms:
            if w in usa_convert.keys():
              to_add.append(usa_convert[w])
        for w in verbforms:
            if w in uk_convert.keys():
              to_add.append(uk_convert[w])
        verbforms = sorted(list(set(verbforms + to_add)))
        return r'(?i)\b(' + r'|'.join(verbforms) + r')\b'
    
    list_of_regexes = []

    for process_type in [relational, mental, verbal]:
        # replace handles lemmata ending in e
        as_regex = regex_maker(process_type)
        list_of_regexes.append(as_regex)

        #regex_list = [regex_maker(process_type) for process_type in [relational_processes, mental_processes, verbal_processes]]
        # implement material process as any word not on this list?

    outputnames = collections.namedtuple("processes", ['relational', 'mental', 'verbal'])
    output = outputnames(list_of_regexes[0], list_of_regexes[1], list_of_regexes[2])
    return output

processes = process_types()
