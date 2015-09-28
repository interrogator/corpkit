# This file translates CoreNLP labels into SFL categories

def translator():
    from collections import namedtuple
    # currently not getting finite!
    roledict = {
            'acomp': ['participant', 'goal', 'complement', 'participant2'],
            'advcl': ['adjunct', 'circumstance'],
            'advmod': ['adjunct', 'circumstance'],
            'amod': ['epithet'],
            'appos': ['thing', 'participant'],
            'aux': ['auxiliary', 'modal'],
            'agent': ['actor', 'participant1', 'adjunct', 'participant', 'thing'],
            'auxpass': ['auxiliary', 'modal'],
            'ccomp': ['process', 'event'],
            'cop': ['process', 'event'],
            'csubj': ['participant', 'thing', 'subject', 'actor', 'participant1'],
            'csubjpass': ['participant', 'thing', 'subject', 'goal', 'participant2'],
            'det': ['deictic'],
            'dobj': ['participant', 'thing', 'complement', 'goal', 'participant2'],
            'iobj': ['participant', 'thing', 'complement', 'goal', 'participant2'],
            'neg': ['polarity'],
            'nn': ['classifier'],
            'compound': ['classifier'],
            'nsubj': ['participant', 'thing', 'subject', 'actor', 'participant1'],
            'nsubjpass': ['participant', 'thing', 'subject', 'goal', 'participant2'],
            'predet': ['deictic'],
            # 'prep': ['thing', 'circumstance', 'adjunct'], # must be as regex
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
            'prep_meaning': ['thing', 'circumstance', 'adjunct'],
            'prep_down': ['thing', 'circumstance', 'adjunct'],
            'prep_below': ['thing', 'circumstance', 'adjunct'],
            'prep_despite': ['thing', 'circumstance', 'adjunct'],
            'prep_during': ['thing', 'circumstance', 'adjunct'],
            'prep_throughout': ['thing', 'circumstance', 'adjunct'],
            'prep_as_of': ['thing', 'circumstance', 'adjunct'],
            'prep_about': ['thing', 'circumstance', 'adjunct'],
            'prep_because_of': ['thing', 'circumstance', 'adjunct'],
            'prep_out': ['thing', 'circumstance', 'adjunct'],
            'prep_though': ['thing', 'circumstance', 'adjunct'],
            'prep_unlike': ['thing', 'circumstance', 'adjunct'],
            'prep_over': ['thing', 'circumstance', 'adjunct'],
            'prep_vs.': ['thing', 'circumstance', 'adjunct'],
            'prep_beside': ['thing', 'circumstance', 'adjunct'],
            'prep_next_to': ['thing', 'circumstance', 'adjunct'],
            'prep_inside': ['thing', 'circumstance', 'adjunct'],
            'prep_throught': ['thing', 'circumstance', 'adjunct'],
            'prep_onto': ['thing', 'circumstance', 'adjunct'],
            'prep_@': ['thing', 'circumstance', 'adjunct'],
            'prep_apart_from': ['thing', 'circumstance', 'adjunct'],
            'prep_while': ['thing', 'circumstance', 'adjunct'],
            'prep_untill': ['thing', 'circumstance', 'adjunct'],
            'prep_but': ['thing', 'circumstance', 'adjunct'],
            'prep_post': ['thing', 'circumstance', 'adjunct'],
            'prep_ahead_of': ['thing', 'circumstance', 'adjunct'],
            'prep_abput': ['thing', 'circumstance', 'adjunct'],
            'prep_of': ['thing', 'circumstance', 'adjunct'],
            'prep_afer': ['thing', 'circumstance', 'adjunct'],
            'prep_toward': ['thing', 'circumstance', 'adjunct'],
            'prep_instead_of': ['thing', 'circumstance', 'adjunct'],
            'prep_since': ['thing', 'circumstance', 'adjunct'],
            'prep_by': ['thing', 'circumstance', 'adjunct'],
            'prep_with': ['thing', 'circumstance', 'adjunct'],
            'prep_whether': ['thing', 'circumstance', 'adjunct'],
            'prep_across': ['thing', 'circumstance', 'adjunct'],
            'prep_within': ['thing', 'circumstance', 'adjunct'],
            'prep_that': ['thing', 'circumstance', 'adjunct'],
            'prep_along': ['thing', 'circumstance', 'adjunct'],
            'prep_atleast': ['thing', 'circumstance', 'adjunct'],
            'prep_as_per': ['thing', 'circumstance', 'adjunct'],
            'prep_than': ['thing', 'circumstance', 'adjunct'],
            'prep_aside_from': ['thing', 'circumstance', 'adjunct'],
            'prep_aftre': ['thing', 'circumstance', 'adjunct'],
            'prep_on': ['thing', 'circumstance', 'adjunct'],
            'prep_starting': ['thing', 'circumstance', 'adjunct'],
            'prep_notwithstanding': ['thing', 'circumstance', 'adjunct'],
            'prep_pursuant_to': ['thing', 'circumstance', 'adjunct'],
            'prep_w/out': ['thing', 'circumstance', 'adjunct'],
            'prep_because': ['thing', 'circumstance', 'adjunct'],
            'prep_till': ['thing', 'circumstance', 'adjunct'],
            'prep_for': ['thing', 'circumstance', 'adjunct'],
            'prep_away_from': ['thing', 'circumstance', 'adjunct'],
            'prep_on_top_of': ['thing', 'circumstance', 'adjunct'],
            'prep_as': ['thing', 'circumstance', 'adjunct'],
            'prep_at': ['thing', 'circumstance', 'adjunct'],
            'prep_worth': ['thing', 'circumstance', 'adjunct'],
            'prep_whilst': ['thing', 'circumstance', 'adjunct'],
            'prep_theya': ['thing', 'circumstance', 'adjunct'],
            'prep_per': ['thing', 'circumstance', 'adjunct'],
            'prep_around': ['thing', 'circumstance', 'adjunct'],
            'prep_aabout': ['thing', 'circumstance', 'adjunct'],
            'prep_past': ['thing', 'circumstance', 'adjunct'],
            'prep_like': ['thing', 'circumstance', 'adjunct'],
            'prep_throughtout': ['thing', 'circumstance', 'adjunct'],
            'prep_following': ['thing', 'circumstance', 'adjunct'],
            'prep_in': ['thing', 'circumstance', 'adjunct'],
            'prep_underneath': ['thing', 'circumstance', 'adjunct'],
            'prep_being': ['thing', 'circumstance', 'adjunct'],
            'prep_above': ['thing', 'circumstance', 'adjunct'],
            'prep_if': ['thing', 'circumstance', 'adjunct'],
            'prep_against': ['thing', 'circumstance', 'adjunct'],
            'prep_a.k.a.': ['thing', 'circumstance', 'adjunct'],
            'prep_although': ['thing', 'circumstance', 'adjunct'],
            'prep_via': ['thing', 'circumstance', 'adjunct'],
            'prep_among': ['thing', 'circumstance', 'adjunct'],
            'prep_up': ['thing', 'circumstance', 'adjunct'],
            'prep_inside_of': ['thing', 'circumstance', 'adjunct'],
            'prep_considering': ['thing', 'circumstance', 'adjunct'],
            'prep_without': ['thing', 'circumstance', 'adjunct'],
            'prep_in_accordance_with': ['thing', 'circumstance', 'adjunct'],
            'prep_under': ['thing', 'circumstance', 'adjunct'],
            'prep_after': ['thing', 'circumstance', 'adjunct'],
            'prep_due_to': ['thing', 'circumstance', 'adjunct'],
            'prep_anfd': ['thing', 'circumstance', 'adjunct'],
            'prep_out_of': ['thing', 'circumstance', 'adjunct'],
            'prep_aboard': ['thing', 'circumstance', 'adjunct'],
            'prep_as_for': ['thing', 'circumstance', 'adjunct'],
            'prep_alot': ['thing', 'circumstance', 'adjunct'],
            'prep_besides': ['thing', 'circumstance', 'adjunct'],
            'prep_outside': ['thing', 'circumstance', 'adjunct'],
            'prep_including': ['thing', 'circumstance', 'adjunct'],
            'prep_except_for': ['thing', 'circumstance', 'adjunct'],
            'prep_along_with': ['thing', 'circumstance', 'adjunct'],
            'prep_between': ['thing', 'circumstance', 'adjunct'],
            'prep_near': ['thing', 'circumstance', 'adjunct'],
            'prep_before': ['thing', 'circumstance', 'adjunct'],
            'prep_next': ['thing', 'circumstance', 'adjunct'],
            'prep_andall': ['thing', 'circumstance', 'adjunct'],
            'prep_amongst': ['thing', 'circumstance', 'adjunct'],
            'prep_off_of': ['thing', 'circumstance', 'adjunct'],
            'prep_through': ['thing', 'circumstance', 'adjunct'],
            'prep_thisss': ['thing', 'circumstance', 'adjunct'],
            'prep_in_addition_to': ['thing', 'circumstance', 'adjunct'],
            'prep_except': ['thing', 'circumstance', 'adjunct'],
            'prep_regardless_of': ['thing', 'circumstance', 'adjunct'],
            'prep_prior_to': ['thing', 'circumstance', 'adjunct'],
            'prep_such_as': ['thing', 'circumstance', 'adjunct'],
            'prep_thru': ['thing', 'circumstance', 'adjunct'],
            'prep_concerning': ['thing', 'circumstance', 'adjunct'],
            'prep_to': ['thing', 'circumstance', 'adjunct'],
            'prep_into': ['thing', 'circumstance', 'adjunct'],
            'prep_from': ['thing', 'circumstance', 'adjunct'],
            'prep_based_on': ['thing', 'circumstance', 'adjunct'],
            'prep_beyond': ['thing', 'circumstance', 'adjunct'],
            'prep_abut': ['thing', 'circumstance', 'adjunct'],
            'prep_with_respect_to': ['thing', 'circumstance', 'adjunct'],
            'prep_far_from': ['thing', 'circumstance', 'adjunct'],
            'prep_close_to': ['thing', 'circumstance', 'adjunct'],
            'prep_outside_of': ['thing', 'circumstance', 'adjunct'],
            'prep_en': ['thing', 'circumstance', 'adjunct'],
            'prep_abt': ['thing', 'circumstance', 'adjunct'],
            'prep_in_spite_of': ['thing', 'circumstance', 'adjunct'],
            'prep_going': ['thing', 'circumstance', 'adjunct'],
            'prep_behind': ['thing', 'circumstance', 'adjunct'],
            'prep_testing': ['thing', 'circumstance', 'adjunct'],
            'prep_unless': ['thing', 'circumstance', 'adjunct'],
            'prep_upon': ['thing', 'circumstance', 'adjunct'],
            'prep_b/c': ['thing', 'circumstance', 'adjunct'],
            'prep_towards': ['thing', 'circumstance', 'adjunct'],
            'prep_thanks_to': ['thing', 'circumstance', 'adjunct'],
            'prep_regarding': ['thing', 'circumstance', 'adjunct'],
            'prep_alongside': ['thing', 'circumstance', 'adjunct'],
            'prep_off': ['thing', 'circumstance', 'adjunct'],
            'prep_in_front_of': ['thing', 'circumstance', 'adjunct'],
            'prep_until': ['thing', 'circumstance', 'adjunct'],

            'nmod:meaning': ['thing', 'circumstance', 'adjunct'],
            'nmod:down': ['thing', 'circumstance', 'adjunct'],
            'nmod:below': ['thing', 'circumstance', 'adjunct'],
            'nmod:despite': ['thing', 'circumstance', 'adjunct'],
            'nmod:during': ['thing', 'circumstance', 'adjunct'],
            'nmod:throughout': ['thing', 'circumstance', 'adjunct'],
            'nmod:as_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:about': ['thing', 'circumstance', 'adjunct'],
            'nmod:because_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:out': ['thing', 'circumstance', 'adjunct'],
            'nmod:though': ['thing', 'circumstance', 'adjunct'],
            'nmod:unlike': ['thing', 'circumstance', 'adjunct'],
            'nmod:over': ['thing', 'circumstance', 'adjunct'],
            'nmod:vs.': ['thing', 'circumstance', 'adjunct'],
            'nmod:beside': ['thing', 'circumstance', 'adjunct'],
            'nmod:next_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:inside': ['thing', 'circumstance', 'adjunct'],
            'nmod:throught': ['thing', 'circumstance', 'adjunct'],
            'nmod:onto': ['thing', 'circumstance', 'adjunct'],
            'nmod:@': ['thing', 'circumstance', 'adjunct'],
            'nmod:apart_from': ['thing', 'circumstance', 'adjunct'],
            'nmod:while': ['thing', 'circumstance', 'adjunct'],
            'nmod:untill': ['thing', 'circumstance', 'adjunct'],
            'nmod:but': ['thing', 'circumstance', 'adjunct'],
            'nmod:post': ['thing', 'circumstance', 'adjunct'],
            'nmod:ahead_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:abput': ['thing', 'circumstance', 'adjunct'],
            'nmod:of': ['thing', 'circumstance', 'adjunct'],
            'nmod:afer': ['thing', 'circumstance', 'adjunct'],
            'nmod:toward': ['thing', 'circumstance', 'adjunct'],
            'nmod:instead_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:since': ['thing', 'circumstance', 'adjunct'],
            'nmod:by': ['thing', 'circumstance', 'adjunct'],
            'nmod:with': ['thing', 'circumstance', 'adjunct'],
            'nmod:whether': ['thing', 'circumstance', 'adjunct'],
            'nmod:across': ['thing', 'circumstance', 'adjunct'],
            'nmod:within': ['thing', 'circumstance', 'adjunct'],
            'nmod:that': ['thing', 'circumstance', 'adjunct'],
            'nmod:along': ['thing', 'circumstance', 'adjunct'],
            'nmod:atleast': ['thing', 'circumstance', 'adjunct'],
            'nmod:as_per': ['thing', 'circumstance', 'adjunct'],
            'nmod:than': ['thing', 'circumstance', 'adjunct'],
            'nmod:aside_from': ['thing', 'circumstance', 'adjunct'],
            'nmod:aftre': ['thing', 'circumstance', 'adjunct'],
            'nmod:on': ['thing', 'circumstance', 'adjunct'],
            'nmod:starting': ['thing', 'circumstance', 'adjunct'],
            'nmod:notwithstanding': ['thing', 'circumstance', 'adjunct'],
            'nmod:pursuant_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:w/out': ['thing', 'circumstance', 'adjunct'],
            'nmod:because': ['thing', 'circumstance', 'adjunct'],
            'nmod:till': ['thing', 'circumstance', 'adjunct'],
            'nmod:for': ['thing', 'circumstance', 'adjunct'],
            'nmod:away_from': ['thing', 'circumstance', 'adjunct'],
            'nmod:on_top_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:as': ['thing', 'circumstance', 'adjunct'],
            'nmod:at': ['thing', 'circumstance', 'adjunct'],
            'nmod:worth': ['thing', 'circumstance', 'adjunct'],
            'nmod:whilst': ['thing', 'circumstance', 'adjunct'],
            'nmod:theya': ['thing', 'circumstance', 'adjunct'],
            'nmod:per': ['thing', 'circumstance', 'adjunct'],
            'nmod:around': ['thing', 'circumstance', 'adjunct'],
            'nmod:aabout': ['thing', 'circumstance', 'adjunct'],
            'nmod:past': ['thing', 'circumstance', 'adjunct'],
            'nmod:like': ['thing', 'circumstance', 'adjunct'],
            'nmod:throughtout': ['thing', 'circumstance', 'adjunct'],
            'nmod:following': ['thing', 'circumstance', 'adjunct'],
            'nmod:in': ['thing', 'circumstance', 'adjunct'],
            'nmod:underneath': ['thing', 'circumstance', 'adjunct'],
            'nmod:being': ['thing', 'circumstance', 'adjunct'],
            'nmod:above': ['thing', 'circumstance', 'adjunct'],
            'nmod:if': ['thing', 'circumstance', 'adjunct'],
            'nmod:against': ['thing', 'circumstance', 'adjunct'],
            'nmod:a.k.a.': ['thing', 'circumstance', 'adjunct'],
            'nmod:although': ['thing', 'circumstance', 'adjunct'],
            'nmod:via': ['thing', 'circumstance', 'adjunct'],
            'nmod:among': ['thing', 'circumstance', 'adjunct'],
            'nmod:up': ['thing', 'circumstance', 'adjunct'],
            'nmod:inside_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:considering': ['thing', 'circumstance', 'adjunct'],
            'nmod:without': ['thing', 'circumstance', 'adjunct'],
            'nmod:in_accordance_with': ['thing', 'circumstance', 'adjunct'],
            'nmod:under': ['thing', 'circumstance', 'adjunct'],
            'nmod:after': ['thing', 'circumstance', 'adjunct'],
            'nmod:due_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:anfd': ['thing', 'circumstance', 'adjunct'],
            'nmod:out_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:aboard': ['thing', 'circumstance', 'adjunct'],
            'nmod:as_for': ['thing', 'circumstance', 'adjunct'],
            'nmod:alot': ['thing', 'circumstance', 'adjunct'],
            'nmod:besides': ['thing', 'circumstance', 'adjunct'],
            'nmod:outside': ['thing', 'circumstance', 'adjunct'],
            'nmod:including': ['thing', 'circumstance', 'adjunct'],
            'nmod:except_for': ['thing', 'circumstance', 'adjunct'],
            'nmod:along_with': ['thing', 'circumstance', 'adjunct'],
            'nmod:between': ['thing', 'circumstance', 'adjunct'],
            'nmod:near': ['thing', 'circumstance', 'adjunct'],
            'nmod:before': ['thing', 'circumstance', 'adjunct'],
            'nmod:next': ['thing', 'circumstance', 'adjunct'],
            'nmod:andall': ['thing', 'circumstance', 'adjunct'],
            'nmod:amongst': ['thing', 'circumstance', 'adjunct'],
            'nmod:off_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:through': ['thing', 'circumstance', 'adjunct'],
            'nmod:thisss': ['thing', 'circumstance', 'adjunct'],
            'nmod:in_addition_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:except': ['thing', 'circumstance', 'adjunct'],
            'nmod:regardless_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:prior_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:such_as': ['thing', 'circumstance', 'adjunct'],
            'nmod:thru': ['thing', 'circumstance', 'adjunct'],
            'nmod:concerning': ['thing', 'circumstance', 'adjunct'],
            'nmod:to': ['thing', 'circumstance', 'adjunct'],
            'nmod:into': ['thing', 'circumstance', 'adjunct'],
            'nmod:from': ['thing', 'circumstance', 'adjunct'],
            'nmod:based_on': ['thing', 'circumstance', 'adjunct'],
            'nmod:beyond': ['thing', 'circumstance', 'adjunct'],
            'nmod:abut': ['thing', 'circumstance', 'adjunct'],
            'nmod:with_respect_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:far_from': ['thing', 'circumstance', 'adjunct'],
            'nmod:close_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:outside_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:en': ['thing', 'circumstance', 'adjunct'],
            'nmod:abt': ['thing', 'circumstance', 'adjunct'],
            'nmod:in_spite_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:going': ['thing', 'circumstance', 'adjunct'],
            'nmod:behind': ['thing', 'circumstance', 'adjunct'],
            'nmod:testing': ['thing', 'circumstance', 'adjunct'],
            'nmod:unless': ['thing', 'circumstance', 'adjunct'],
            'nmod:upon': ['thing', 'circumstance', 'adjunct'],
            'nmod:b/c': ['thing', 'circumstance', 'adjunct'],
            'nmod:towards': ['thing', 'circumstance', 'adjunct'],
            'nmod:thanks_to': ['thing', 'circumstance', 'adjunct'],
            'nmod:regarding': ['thing', 'circumstance', 'adjunct'],
            'nmod:alongside': ['thing', 'circumstance', 'adjunct'],
            'nmod:off': ['thing', 'circumstance', 'adjunct'],
            'nmod:in_front_of': ['thing', 'circumstance', 'adjunct'],
            'nmod:until': ['thing', 'circumstance', 'adjunct']
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
    participant1s = []
    participant2s = []
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
            if v == 'participant1':
                participant1s.append(k)
            if v == 'participant2':
                participant2s.append(k)
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
    outputnames = namedtuple('roles', ['actor', 'adjunct', 'auxiliary', 'circumstance', 'classifier', 'complement', 'deictic', 'epithet', 'event', 'existential', 'goal', 'modal', 'numerative', 'participant', 'participant1', 'participant2', 'polarity', 'predicator', 'process', 'qualifier', 'subject', 'textual', 'thing'])
    output = outputnames(sorted(actors), sorted(adjuncts), sorted(auxiliarys), 
                         sorted(circumstances), sorted(classifiers), sorted(complements), 
                         sorted(deictics), sorted(epithets), sorted(events), 
                         sorted(existentials), sorted(goals), sorted(modals), 
                         sorted(numeratives), sorted(participants), sorted(participant1s), sorted(participant2s), sorted(polaritys), 
                         sorted(predicators), sorted(processs), sorted(qualifiers), 
                         sorted(subjects), sorted(textuals), sorted(things))
    return output

roles = translator()
