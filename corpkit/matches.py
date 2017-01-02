import pandas as pd

import functools

@functools.total_ordering
class Match(object):
    """
    Store a single search result, with everything needed to generate views
    """

    def __init__(self, filepath, subcorpora, sent, tok, sent_id, tok_id):
        self.file = filepath
        self.subcorpora = subcorpora
        self.sent = sent
        self.tok = tok
        self.sent_id = sent_id
        self.tok_id = tok_id
        super(Match, self).__init__()

    def __eq__(self, other):
        attrs = ['file', 'subcorpora', 'sent_id', 'tok_id']
        return all([getattr(self, a) == getattr(other, a) for a in attrs])

    def _is_valid_operand(self, other):
        samefile = self.file == other.file
        return (hasattr(other, 'tok_id') and hasattr(other, 'sent_id') and samefile)

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            raise NotImplementedError("Matches do not come from the same file, so they cannot be compared.")
        return ((self.sent_id, self.tok_id) < (other.sent_id, other.tok_id))

class Matches(object):
    """
    Store search results in an abstract, intermediate way
    """

    def __init__(self, data, corpus, **kwargs):

        self.data = data
        self.corpus = corpus

        super(Matches, self).__init__()

    def record(self):
        import pandas as pd
        from corpkit.build import get_all_metadata_fields
        record_data = []
        fields = list(sorted(['parse'] + get_all_metadata_fields(self.corpus.path, include_speakers=True)))
        for k, v in self.data.items():
            line = [k.metadata.get(key, 'none') for key in fields]
            line += [k, v]
            record_data.append(line)
        column_names = fields + ['entry', 'count']

        df = pd.DataFrame(record_data)
        df.columns = column_names
        return df

        df = df.groupby(df.index).sum()
        df = df[df.sum().sort_values(ascending=False).index]
        return df

    def table(self, subcorpora=False, preserve_case=False, show=['w']):
        import pandas as pd
        if not subcorpora:
            ser = pd.Series(self.data)
            ser.index = [k.display(show) for k in ser.index]
            return ser.groupby(ser.index).sum().sort_values(ascending=False)
        else:
            df = self.record()
            # should be apply
            df['entry'] = [x.display(show, preserve_case=preserve_case) for x in df['entry']]
            df = df.pivot_table(columns='entry', values='count', index=subcorpora)
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
        rec = rec.drop(['count', 'parse'], axis=1)
        rec.rename(columns = {'entry':'m'}, inplace=True)
        clines = rec.apply(_concer, show=show, axis=1)
        return Concordance(clines)

from corpkit.lazyprop import lazyprop

class Token(object):
    """
    Model a token in the corpus
    """

    def __init__(self, idx, sent, sent_id, path, metadata):
        self.idx = idx
        self.sent = sent
        self.sent_id = sent_id
        self.path = path
        self.metadata = metadata
        if self.idx != 0:
            self.word = self.getter('w')
            self.lemma = self.getter('l')
            self.function = self.getter('f')
            self.ner = self.getter('e')
            self.is_root = False
        else:
            self.word =  None
            self.lemma =  None
            self.function = None
            self.is_root = True

        self._w = self.word
        self._l = self.lemma
        self._f = self.function
        self._e = self.ner
        self._s = sent_id
        self._i = idx

        super(Token, self).__init__()

    def getter(self, att):
        try:
            return self.sent.ix[self.idx][att]
        except:
            return 'stripped'

    @lazyprop
    def governor(self):
        new_idx = self.sent.ix[self.idx]['g']
        return Token(new_idx, self.sent, self.sent_id, self.path, self.metadata)

    @lazyprop
    def dependents(self):
        pass

    def __hash__(self):
        return hash((self.idx, self.sent_id, self.path))
    
    def __eq__(self, other):
        attrs = ['path', 'sent_id', 'idx']
        return all([getattr(self, a) == getattr(other, a) for a in attrs])

    def display(self, show=['w'], preserve_case=False):
        """
        Show token in a certain way
        """
        from corpkit.interrogator import fix_show
        from corpkit.constants import transshow
        show = fix_show(show, 1)
        out = []
        # todo
        for bit in show:
            obj, att = bit[-2], bit[-1]
            if obj == 'g':
                tok = self.governor
            elif obj == 'm':
                tok = self
            out.append(getattr(tok, '_' + att, 'none'))
        out = '/'.join(out)

        if preserve_case:
            return out
        else:
            return out.lower()

    def __str__(self):
        return self.word if self.word else '<root>'


def _concer(record, show):
    """
    to use in a pandas apply function to make a concordance line
    """
    tok = record['m']
    sent, s, i = tok.sent, tok._s, tok._i
    record['m'] = tok.display(show)
    start = ' '.join(sent['w'].loc[:i-1].values)
    end = ' '.join(sent['w'].loc[i+1:].values)
    record['r'] = end
    record['l'] = start 
    return record