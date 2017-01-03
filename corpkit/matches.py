import pandas as pd

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
        from corpkit.corpus import Corpora, Datalist

        # wrong for datalists
        if subcorpora == 'default':
            if isinstance(self.corpus, Corpora):
                subcorpora = 'corpus'
            if getattr(self.corpus, 'level', 'c') and not isinstance(self.corpus, Datalist):
                subcorpora = 'folder'
            elif getattr(self.corpus, 'level', 's') or isinstance(self.corpus, Datalist):
                subcorpora = 'file'
            else:
                subcorpora = False

        from corpkit.interrogator import fix_show
        show = fix_show(show, 1)

        if not subcorpora:
            ser = pd.Series(self.data)
            ser.index = [k.display(show) for k in ser.index]
            return ser.groupby(ser.index).sum().sort_values(ascending=False)
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
        rec.rename(columns = {'entry':'m'}, inplace=True)
        clines = rec.apply(_concer, show=show, axis=1)
        return Concordance(clines)

from corpkit.lazyprop import lazyprop

class Token(object):
    """
    Model a token in the corpus
    """

    def __init__(self, idx, df, sent_id, fobj, metadata, **kwargs):

        kwargs['i'] = idx
        kwargs['s'] = sent_id
        
        self.df = df
        self.fobj = fobj
        self.path = fobj.path
        self.metadata = metadata

        from corpkit.constants import CONLL_COLUMNS
        for name in ['s'] + CONLL_COLUMNS:
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
        return Token(self.g, self.df, self.s, self.fobj, self.metadata, **row)

    @lazyprop
    def dependents(self):
        out = []
        new_idxs = [int(i) for i in self.sent.ix[self.i]['d'].split(',')]
        for new_idx in new_idxs:
            try:
                row = self.sent.ix[new_idx].to_dict()
            except KeyError:
                continue
            out.append(Token(new_idx, self.df, self.s, self.fobj, self.metadata, **row))
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

    def __hash__(self):
        return hash((self.i, self.s, self.path))
    
    def __eq__(self, other):
        attrs = ['path', 's', 'idx']
        return all([getattr(self, a) == getattr(other, a) for a in attrs])

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
        return self._w


def _concer(record, show):
    """
    to use in a pandas apply function to make a concordance line
    """
    tok = record['m']
    record['m'] = tok.display(show)
    start = ' '.join(tok.sent['w'].loc[:tok.idx-1].values)
    end = ' '.join(tok.sent['w'].loc[tok.idx+1:].values)
    record['r'] = end
    record['l'] = start 
    return record