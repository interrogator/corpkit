import pandas as pd
from functools import total_ordering
from corpkit.lazyprop import lazyprop
from corpkit.constants import STRINGTYPE

def make_ser(row, k=False):
    return row['entry'].display(k)

@total_ordering
class Token(object):
    """
    Model a token in the corpus
    """

    def __init__(self, idx, df, sent_id, fobj, metadata, parent, conc=True, **kwargs):

        self.i = idx
        self.s = sent_id
        self._conc = conc
        self.df = df
        df = None
        self.fobj = fobj
        self.path = fobj.path
        self.metadata = metadata
        self.parent = parent
        from corpkit.constants import CONLL_COLUMNS
        for name in CONLL_COLUMNS[1:]:
            setattr(self, name, kwargs.get(name, 'root'))
        self.is_root = idx == 0
        super(Token, self).__init__()
    
    @lazyprop
    def sent(self):
        return self.df.loc[self.s]

    @lazyprop
    def left(self):
        return ' '.join(self.df['w'].loc[:self.i-1].values)

    @lazyprop
    def right(self):
        return ' '.join(self.df['w'].loc[self.i+1:].values)

    @lazyprop
    def governor(self):
        try:
            row = self.sent.ix[self.g].to_dict() if self.g else {}
        except KeyError:
            return
        return Token(self.g, self.df, self.s, self.fobj, self.metadata, self.parent, **row)

    @lazyprop
    def x(self):
        """Get wordclass"""
        from corpkit.dictionaries.word_transforms import taglemma
        return taglemma.get(self.p.lower(), self.p.lower())

    @lazyprop
    def dependents(self):
        out = []
        new_idxs = [int(i) for i in self.sent.at[self.i, 'd'].split(',')]
        for new_idx in new_idxs:
            try:
                row = self.sent.ix[new_idx].to_dict()
            except KeyError:
                continue
            out.append(Token(new_idx, self.df, self.s, self.fobj, self.metadata, self.parent, **row))
        return out

    @lazyprop
    def ancestors(self):
        out = []
        while True:
            self = self.governor
            if self:
                out.append(self)
            else:
                break
        return out

    @lazyprop
    def descendents(self):
        out = []
        deps = self.dependents
        while deps:
            for d in deps:
                out.append(d)
                deps = d.dependents
        return out

    @lazyprop
    def head(self):
        if self.c.endswith('*'):
            return self
        else:
            to_find = self.c
            matches = self.df[self.df['c'] == to_find]
            if matches:
                m = matches.iloc[0]
                # metadata here is actually wrong!
                return Token(m.name[1], self.df, m.name[0], self.fobj, self.metadata, self.parent, **m.to_dict())
            else:
                return

    @lazyprop
    def corefs(self):
        out = []
        just_same_coref = self.df.loc[self.df['c'] == self.c]
        for (s, i), dat in just_same_coref.iterrows():
            out.append(Token(i, self.df, s, self.fobj, self.metadata, self.parent, **dat.to_dict()))
        return out

    @lazyprop
    def representative(self):
        to_find = self.c.rstrip('*')
        matches = self.df[self.df['c'] == to_find + '*']
        if matches:
            m = matches.iloc[0]
            # metadata here is actually wrong!
            return Token(m.name[1], self.df, m.name[0], self.fobj, self.metadata, self.parent, **m.to_dict())
        else:
            return

    def research(self):
        """
        Search for this token in the corpus
        """
        import re
        return self.parent.corpus.interrogate({'mw': r'^%s$' % re.escape(self.w)})

    def __hash__(self):
        return hash((self.i, self.s, self.path))
    
    def __eq__(self, other):
        attrs = ['path', 's', 'i']
        return all([getattr(self, a) == getattr(other, a) for a in attrs])

    def __lt__(self, other):
        return (self.path, self.s, self.i) < (self.path, other.s, other.i)

    def display(self, show=['mw'], preserve_case=False):
        """
        Show token in a certain way
        """
        out = []
        # todo
        for bit in show:
            obj, att = bit[-2], bit[-1]
            if obj == 'g':
                tok = self.governor
            elif obj == 'm':
                tok = self
            out.append(getattr(tok, att, 'none'))

        out = '/'.join(out)

        if preserve_case:
            return out
        else:
            return out.lower()

    def __str__(self):
        return '<%s>' % self.w

def _concer(record, show):
    """
    to use in a pandas apply function to make a concordance line
    """
    tok = record['m']
    record['m'] = tok.display(show)
    record['r'] = ' '.join(tok.sent['w'].loc[tok.i+1:].values)
    record['l'] = ' '.join(tok.sent['w'].loc[:tok.i-1].values)
    return record

# unused code below!

def add_gov(row,df=False):
    """apply to df to add g rows"""
    from pandas import Series
    if row['g'] == 0:
        r = Series(['root'] * len(row), index=row.index)
    else:
        r = df.ix[row.name[0], row['g']]
    r.index = r.index.str.pad(2, fillchar='g')
    nr = row.append(r)
    return nr

def add_gov_to_f(df):
    """add govs to a df"""
    nrow = df.apply(add_gov, df=df, axis=1)
    return nrow
