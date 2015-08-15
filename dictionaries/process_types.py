#!/usr/bin/python

#   dictionaries: process type wordlists
#   Author: Daniel McDonald

# This code used to make a regular expression to match the words
# That's been commented out. Now, you get a word list. This can still be passed
# to interrogator(), however, which will make the regex. 

def process_types(regex = False):
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

    def regex_or_list_maker(verb_list):
        """makes a regex from the list of words passed to it"""
        # add alternative spellings
        from dictionaries.word_transforms import usa_convert
        # try doing with pattern again one more time.
        
        def find_lexeme(verb):
            """ For a regular verb (base form), returns the forms using a rule-based approach.
            taken from pattern
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
          forms = list(set([form.replace("n't", "").replace(" not", "") for form in find_lexeme(w)]))
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
        
        to_add = []
        for w in verbforms:
            if w in usa_convert.keys():
              to_add.append(usa_convert[w])
        for w in verbforms:
            if w in uk_convert.keys():
              to_add.append(uk_convert[w])
        verbforms = sorted(list(set(verbforms + to_add)))
        t = []

        # ensure unicode
        for w in verbforms:
            if type(w) != unicode:
                t.append(unicode(w, 'utf-8', errors = 'ignore'))
            else:
                t.append(w)
        verbforms = t
        
        if not regex:
            return verbforms
        else:
            return r'(?i)\b(' + r'|'.join(verbforms) + r')\b'
    
    list_of_regexes = []

    for process_type in [relational, mental, verbal]:
        # replace handles lemmata ending in e
        as_list_or_regex = regex_or_list_maker(process_type)
        list_of_regexes.append(as_list_or_regex)

        #regex_list = [regex_or_list_maker(process_type) for process_type in [relational_processes, mental_processes, verbal_processes]]
        # implement material process as any word not on this list?

    outputnames = collections.namedtuple("processes", ['relational', 'mental', 'verbal'])
    output = outputnames(list_of_regexes[0], list_of_regexes[1], list_of_regexes[2])
    return output

processes = process_types(regex = False)
