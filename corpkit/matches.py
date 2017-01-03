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
            line += [k.sent_id, k.idx, k]
            record_data.append(line)
        column_names = fields + ['sent_id', 'tok_id', 'entry']

        df = pd.DataFrame(record_data)
        df.columns = column_names

        sorts = ['corpus'] if isinstance(self.corpus, Corpora) else []
        if getattr(self.corpus, 'level', 's'):
            sorts.append('folder')
        sorts += ['file', 'sent_id', 'tok_id']
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
        rec = rec.drop(['count', 'parse'], axis=1)
        rec.rename(columns = {'entry':'m'}, inplace=True)
        clines = rec.apply(_concer, show=show, axis=1)
        return Concordance(clines)

from corpkit.lazyprop import lazyprop

class Token(object):
    """
    Model a token in the corpus
    """

    def __init__(self, idx, df, sent_id, fobj, metadata, word):
        self.idx = idx
        self.sent_id = sent_id
        self.df = df
        self.fobj = fobj
        self.path = fobj.path
        self.metadata = metadata
        self._w = word
        if self.idx != 0:
            self.is_root = False
        else:
            self.is_root = True

        super(Token, self).__init__()

    def getter(self, att):
        """
        Gets an att (word, lemma, etc) from a token
        """
        try:
            return self.sent.ix[self.idx][att]
        except (IndexError, TypeError, KeyError):
            return 'root'
    
    def _i(self):
        return self.idx

    def _s(self):
        return self.sent_id

    @lazyprop
    def sent(self):
        return self.df.ix[self.sent_id]

    @lazyprop
    def _l(self):
        if self.idx != 0:
            return self.getter('l')
        else:
            return 'root'

    @lazyprop
    def _p(self):
        if self.idx != 0:
            return self.getter('p')
        else:
            return 'root'

    @lazyprop
    def _f(self):
        if self.idx != 0:
            return self.getter('f')
        else:
            return 'root'

    @lazyprop
    def _e(self):
        if self.idx != 0:
            return self.getter('e')
        else:
            return 'root'

    @lazyprop
    def governor(self):
        try:
            new_idx = int(self.sent.ix[self.idx]['g'])
        except:
            print(self.fobj.path)
            raise
        new_word = self.sent.ix[new_idx]['w'] if new_idx else 'root'

        return Token(new_idx, self.sent, self.sent_id, self.fobj, self.metadata, new_word)

    @lazyprop
    def dependents(self):
        pass

    def __hash__(self):
        return hash((self.idx, self.sent_id, self.path))
    
    def __eq__(self, other):
        attrs = ['path', 'sent_id', 'idx']
        return all([getattr(self, a) == getattr(other, a) for a in attrs])

    def display(self, show=['mw'], preserve_case=False):
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