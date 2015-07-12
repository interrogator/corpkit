# This file translates CoreNLP labels into SFL categories

def translator():
    from collections import namedtuple
    roledict = {
            'acomp': ['participant', 'goal'],
            'advcl': ['adjunct', 'circumstance'],
            'advmod': ['adjunct', 'circumstance'],
            'amod': ['epithet'],
            'appos': ['thing', 'participant'],
            'aux': ['auxiliary', 'modal'],
            'auxpass': ['auxiliary', 'modal'],
            'ccomp': ['process', 'event'],
            'cop': ['participant', 'thing'],
            'csubj': ['participant', 'thing', 'subject', 'actor'],
            'csubjpass': ['participant', 'thing', 'subject', 'goal'],
            'det': ['deictic'],
            'dobj': ['participant', 'thing', 'complement', 'goal'],
            'iobj': ['participant', 'thing', 'complement', 'goal'],
            'neg': ['polarity'],
            'nn': ['classifier'],
            'nsubj': ['participant', 'thing', 'subject', 'actor'],
            'nsubjpass': ['participant', 'thing', 'subject', 'goal'],
            'predet': ['deictic'],
            'prep': ['thing', 'circumstance'], # must be as regex
            'quantmod': ['numerative'],
            'root': ['process', 'event', 'predicator'],
            'number': ['numerative'],
            'cc': ['textual'],
            'expl': ['existential'],
            'pobj': ['circumstance', 'thing'],
            'preconj': ['deictic'],
            'vmod': ['qualifier'], # non-finite
            'mark': ['textual'],
            'rcmod': ['qualifier'],
            'tmod': ['adjunct', 'circumstance', 'thing'],
            'poss': ['deictic'],
            'possessive': ['deictic'],
            'prt': ['process'], 
            'ref': ['textual'],
            'xsubj': ['participant'],
            'prep_meaning': ['thing', 'circumstance'],
            'prep_down': ['thing', 'circumstance'],
            'prep_below': ['thing', 'circumstance'],
            'prep_despite': ['thing', 'circumstance'],
            'prep_during': ['thing', 'circumstance'],
            'prep_throughout': ['thing', 'circumstance'],
            'prep_as_of': ['thing', 'circumstance'],
            'prep_about': ['thing', 'circumstance'],
            'prep_because_of': ['thing', 'circumstance'],
            'prep_out': ['thing', 'circumstance'],
            'prep_though': ['thing', 'circumstance'],
            'prep_unlike': ['thing', 'circumstance'],
            'prep_over': ['thing', 'circumstance'],
            'prep_vs.': ['thing', 'circumstance'],
            'prep_beside': ['thing', 'circumstance'],
            'prep_next_to': ['thing', 'circumstance'],
            'prep_inside': ['thing', 'circumstance'],
            'prep_throught': ['thing', 'circumstance'],
            'prep_onto': ['thing', 'circumstance'],
            'prep_@': ['thing', 'circumstance'],
            'prep_apart_from': ['thing', 'circumstance'],
            'prep_while': ['thing', 'circumstance'],
            'prep_untill': ['thing', 'circumstance'],
            'prep_but': ['thing', 'circumstance'],
            'prep_post': ['thing', 'circumstance'],
            'prep_ahead_of': ['thing', 'circumstance'],
            'prep_abput': ['thing', 'circumstance'],
            'prep_of': ['thing', 'circumstance'],
            'prep_afer': ['thing', 'circumstance'],
            'prep_toward': ['thing', 'circumstance'],
            'prep_instead_of': ['thing', 'circumstance'],
            'prep_since': ['thing', 'circumstance'],
            'prep_by': ['thing', 'circumstance'],
            'prep_with': ['thing', 'circumstance'],
            'prep_whether': ['thing', 'circumstance'],
            'prep_across': ['thing', 'circumstance'],
            'prep_within': ['thing', 'circumstance'],
            'prep_that': ['thing', 'circumstance'],
            'prep_along': ['thing', 'circumstance'],
            'prep_atleast': ['thing', 'circumstance'],
            'prep_as_per': ['thing', 'circumstance'],
            'prep_than': ['thing', 'circumstance'],
            'prep_aside_from': ['thing', 'circumstance'],
            'prep_aftre': ['thing', 'circumstance'],
            'prep_on': ['thing', 'circumstance'],
            'prep_starting': ['thing', 'circumstance'],
            'prep_notwithstanding': ['thing', 'circumstance'],
            'prep_pursuant_to': ['thing', 'circumstance'],
            'prep_w/out': ['thing', 'circumstance'],
            'prep_because': ['thing', 'circumstance'],
            'prep_till': ['thing', 'circumstance'],
            'prep_for': ['thing', 'circumstance'],
            'prep_away_from': ['thing', 'circumstance'],
            'prep_on_top_of': ['thing', 'circumstance'],
            'prep_as': ['thing', 'circumstance'],
            'prep_at': ['thing', 'circumstance'],
            'prep_worth': ['thing', 'circumstance'],
            'prep_whilst': ['thing', 'circumstance'],
            'prep_theya': ['thing', 'circumstance'],
            'prep_per': ['thing', 'circumstance'],
            'prep_around': ['thing', 'circumstance'],
            'prep_aabout': ['thing', 'circumstance'],
            'prep_past': ['thing', 'circumstance'],
            'prep_like': ['thing', 'circumstance'],
            'prep_throughtout': ['thing', 'circumstance'],
            'prep_following': ['thing', 'circumstance'],
            'prep_in': ['thing', 'circumstance'],
            'prep_underneath': ['thing', 'circumstance'],
            'prep_being': ['thing', 'circumstance'],
            'prep_above': ['thing', 'circumstance'],
            'prep_if': ['thing', 'circumstance'],
            'prep_against': ['thing', 'circumstance'],
            'prep_a.k.a.': ['thing', 'circumstance'],
            'prep_although': ['thing', 'circumstance'],
            'prep_via': ['thing', 'circumstance'],
            'prep_among': ['thing', 'circumstance'],
            'prep_up': ['thing', 'circumstance'],
            'prep_inside_of': ['thing', 'circumstance'],
            'prep_considering': ['thing', 'circumstance'],
            'prep_without': ['thing', 'circumstance'],
            'prep_in_accordance_with': ['thing', 'circumstance'],
            'prep_under': ['thing', 'circumstance'],
            'prep_after': ['thing', 'circumstance'],
            'prep_due_to': ['thing', 'circumstance'],
            'prep_anfd': ['thing', 'circumstance'],
            'prep_out_of': ['thing', 'circumstance'],
            'prep_aboard': ['thing', 'circumstance'],
            'prep_as_for': ['thing', 'circumstance'],
            'prep_alot': ['thing', 'circumstance'],
            'prep_besides': ['thing', 'circumstance'],
            'prep_outside': ['thing', 'circumstance'],
            'prep_including': ['thing', 'circumstance'],
            'prep_except_for': ['thing', 'circumstance'],
            'prep_along_with': ['thing', 'circumstance'],
            'prep_between': ['thing', 'circumstance'],
            'prep_near': ['thing', 'circumstance'],
            'prep_before': ['thing', 'circumstance'],
            'prep_next': ['thing', 'circumstance'],
            'prep_andall': ['thing', 'circumstance'],
            'prep_amongst': ['thing', 'circumstance'],
            'prep_off_of': ['thing', 'circumstance'],
            'prep_through': ['thing', 'circumstance'],
            'prep_thisss': ['thing', 'circumstance'],
            'prep_in_addition_to': ['thing', 'circumstance'],
            'prep_except': ['thing', 'circumstance'],
            'prep_regardless_of': ['thing', 'circumstance'],
            'prep_prior_to': ['thing', 'circumstance'],
            'prep_such_as': ['thing', 'circumstance'],
            'prep_thru': ['thing', 'circumstance'],
            'prep_concerning': ['thing', 'circumstance'],
            'prep_to': ['thing', 'circumstance'],
            'prep_into': ['thing', 'circumstance'],
            'prep_from': ['thing', 'circumstance'],
            'prep_based_on': ['thing', 'circumstance'],
            'prep_beyond': ['thing', 'circumstance'],
            'prep_abut': ['thing', 'circumstance'],
            'prep_with_respect_to': ['thing', 'circumstance'],
            'prep_far_from': ['thing', 'circumstance'],
            'prep_close_to': ['thing', 'circumstance'],
            'prep_outside_of': ['thing', 'circumstance'],
            'prep_en': ['thing', 'circumstance'],
            'prep_abt': ['thing', 'circumstance'],
            'prep_in_spite_of': ['thing', 'circumstance'],
            'prep_going': ['thing', 'circumstance'],
            'prep_behind': ['thing', 'circumstance'],
            'prep_testing': ['thing', 'circumstance'],
            'prep_unless': ['thing', 'circumstance'],
            'prep_upon': ['thing', 'circumstance'],
            'prep_b/c': ['thing', 'circumstance'],
            'prep_towards': ['thing', 'circumstance'],
            'prep_thanks_to': ['thing', 'circumstance'],
            'prep_regarding': ['thing', 'circumstance'],
            'prep_alongside': ['thing', 'circumstance'],
            'prep_off': ['thing', 'circumstance'],
            'prep_in_front_of': ['thing', 'circumstance'],
            'prep_until': ['thing', 'circumstance']
            # but not event?
            #'punct': ['xxx'],
            #'dep': ['xxx'],
            #'arg': ['xxx'],
            #'conj': ['xxx'],
            #'npadvmod': ['xxx'],
    }

    actors = []
    adjuncts = []
    auxiliarys = []
    circumstances = []
    classifiers = []
    complements = []
    deictics = []
    epithets = []
    events = []
    existentials = []
    goals = []
    modals = []
    numeratives = []
    participants = []
    polaritys = []
    predicators = []
    processs = []
    qualifiers = []
    subjects = []
    textuals = []
    things = []

    roles = []
    for k, vs in roledict.items():
        for v in vs:
            if v == 'actor':
                actors.append(k)
            if v == 'adjunct':
                adjuncts.append(k)
            if v == 'auxiliary':
                auxiliarys.append(k)
            if v == 'circumstance':
                circumstances.append(k)
            if v == 'classifier':
                classifiers.append(k)
            if v == 'complement':
                complements.append(k)
            if v == 'deictic':
                deictics.append(k)
            if v == 'epithet':
                epithets.append(k)
            if v == 'event':
                events.append(k)
            if v == 'existential':
                existentials.append(k)
            if v == 'goal':
                goals.append(k)
            if v == 'modal':
                modals.append(k)
            if v == 'numerative':
                numeratives.append(k)
            if v == 'participant':
                participants.append(k)
            if v == 'polarity':
                polaritys.append(k)
            if v == 'predicator':
                predicators.append(k)
            if v == 'process':
                processs.append(k)
            if v == 'qualifier':
                qualifiers.append(k)
            if v == 'subject':
                subjects.append(k)
            if v == 'textual':
                textuals.append(k)
            if v == 'thing':
                things.append(k)

            #if v not in roles:
                #roles.append(v)
    #roles.sort()
    #closedclass = sorted(list(set(pronouns + articles + determiners + prepositions + connectors + modals)))
    outputnames = namedtuple('roles', ['actor', 'adjunct', 'auxiliary', 'circumstance', 'classifier', 'complement', 'deictic', 'epithet', 'event', 'existential', 'goal', 'modal', 'numerative', 'participant', 'polarity', 'predicator', 'process', 'qualifier', 'subject', 'textual', 'thing'])
    output = outputnames(sorted(actors), sorted(adjuncts), sorted(auxiliarys), 
                         sorted(circumstances), sorted(classifiers), sorted(complements), 
                         sorted(deictics), sorted(epithets), sorted(events), 
                         sorted(existentials), sorted(goals), sorted(modals), 
                         sorted(numeratives), sorted(participants), sorted(polaritys), 
                         sorted(predicators), sorted(processs), sorted(qualifiers), 
                         sorted(subjects), sorted(textuals), sorted(things))
    return output

roles = translator()
