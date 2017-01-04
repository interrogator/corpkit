import pandas as pd
from functools import total_ordering

class Matches(list):
    """
    Store search results in an abstract, intermediate way
    """

    def __init__(self, data, corpus, **kwargs):

        from corpkit.corpus import Corpus

        self.data = data
        self.corpus = corpus

        super(Matches, self).__init__(data)

    def record(self):
        import pandas as pd
        from corpkit.build import get_all_metadata_fields
        from corpkit.corpus import Corpora, Corpus, Datalist
        record_data = []
        try:
            all_meta_fields = list(self.corpus.metadata['fields'].keys())
        except:
            all_meta_fields = list(Corpus(self.corpus, print_info=False).metadata['fields'].keys())
        fields = list(sorted(['parse', 'folder', 'file'] + all_meta_fields))
        
        for k in self.data:
            line = [k.metadata.get(key, 'none') for key in fields]
            line += [k.s, k.i, k]
            record_data.append(line)
        column_names = fields + ['s', 'i', 'entry']

        df = pd.DataFrame(record_data)
        df.columns = column_names

        sorts = ['corpus'] if isinstance(self.corpus, Corpora) else []
        if getattr(self.corpus, 'level', 's'):
            sorts.append('folder')
        sorts += ['file', 's', 'i']
        df = df.sort_values(sorts).reset_index(drop=True)
        return df

    def table(self, subcorpora='default', preserve_case=False, show=['w']):

        import pandas as pd
        from corpkit.corpus import Corpora, Datalist, Subcorpus

        # wrong for datalists
        if subcorpora == 'default':

            subcorpora = False
            lev = getattr(self.corpus, 'level', False)
            if isinstance(self.corpus, Corpora):
                subcorpora = 'corpus'
            elif lev == 'd' or isinstance(self.corpus, Datalist):
                if isinstance(self.corpus[0], Subcorpus):
                    subcorpora = 'folder'
                else:
                    subcorpora = 'file'
            elif lev == 'c':
                subcorpora = 'folder'
            elif lev == 's':
                subcorpora = 'file'
    
        from corpkit.interrogator import fix_show
        show = fix_show(show, 1)

        if not subcorpora:
            from collections import Counter
            return pd.Series(Counter([k.display(show) for k in self.data])).sort_values(ascending=False)
        else:
            df = self.record()
            # should be apply
            df['entry'] = [x.display(show, preserve_case=preserve_case) for x in df['entry']]
            df['count'] = [1 for x in df.index]
            df = df.pivot_table(index=subcorpora, columns='entry', values='count', aggfunc=sum)
            df = df.fillna(0.0).astype(int)
            df = df[df.sum().sort_values(ascending=False).index]
            return df

    def conc(self, show=['w']):
        """
        Generate concordance from Matches
        """
        #todo: add index stuff in here
        import pandas as pd
        from corpkit.interrogator import fix_show
        show = fix_show(show, 1)
        from corpkit.interrogation import Concordance
        rec = self.record()
        dummy_ser = pd.Series([0 for i in rec.index])
        loc = list(rec.columns).index('entry')
        rec.insert(loc, 'l', [0 for i in rec.index])
        rec = rec.drop(['parse'], axis=1)
        rec.rename(columns={'entry':'m'}, inplace=True)
        clines = rec.apply(_concer, show=show, axis=1)
        return Concordance(clines)

from corpkit.lazyprop import lazyprop

@total_ordering
class Token(object):
    """
    Model a token in the corpus
    """

    def __init__(self, idx, df, sent_id, fobj, metadata, parent, **kwargs):

        self.i = idx
        self.s = sent_id
        self.df = df
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
        return self.df.ix[self.s]

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
    start = ' '.join(tok.sent['w'].loc[:tok.i-1].values)
    end = ' '.join(tok.sent['w'].loc[tok.i+1:].values)
    record['r'] = end
    record['l'] = start 
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
