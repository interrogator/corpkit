
try:
    from corpkit.lazyprop import lazyprop
except:
    import corpkit
    from lazyprop import lazyprop

class Queries(object):

    def __init__(self):
        import corpkit
        from corpkit.dictionaries import roles, processes
        self.sayer = {'f': roles.participant1, 'gl': processes.verbal.lemmata, 'gf': roles.event}
        self.verbiage = {'f': roles.participant2, 'gl': processes.verbal.lemmata, 'gf': roles.event}
        self.senser = {'f': roles.participant1, 'gl': processes.mental.lemmata, 'gf': roles.event}
        self.phenomenon = {'f': roles.participant2, 'gl': processes.mental.lemmata, 'gf': roles.event}
        self.token = {'f': roles.participant1, 'gl': processes.relational.lemmata, 'gf': roles.event}
        self.value = {'f': roles.participant2, 'gl': processes.relational.lemmata, 'gf': roles.event}
        self.agent = {'f': roles.participant1}

queries = Queries()