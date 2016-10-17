"""
A toolkit for corpus linguistics
"""

from __future__ import print_function

#metadata
__version__ = "2.3.5"
__author__ = "Daniel McDonald"
__license__ = "MIT"

# probably not needed, anymore but adds corpkit to path for tregex.sh
import sys
import os
import inspect

from corpkit.constants import LETTERS

# asterisk import
__all__ = [
    "load",
    "loader",
    "load_all_results",
    "as_regex",
    "new_project",
    "Corpus",
    "File",
    "Corpora",
    "gui"] + LETTERS

corpath = inspect.getfile(inspect.currentframe())
baspat = os.path.dirname(corpath)
#dicpath = os.path.join(baspat, 'dictionaries')
for p in [corpath, baspat]:
    if p not in sys.path:
        sys.path.append(p)
    if p not in os.environ["PATH"].split(':'): 
        os.environ["PATH"] += os.pathsep + p

# import classes
from corpkit.corpus import Corpus, File, Corpora
#from corpkit.model import MultiModel

from corpkit.other import (load, loader, load_all_results, 
                           quickview, as_regex, new_project)

from corpkit.lazyprop import lazyprop
#from corpkit.dictionaries.process_types import Wordlist
from corpkit.process import gui

# monkeypatch editing and plotting to pandas objects
from pandas import DataFrame, Series

# monkey patch functions
def _plot(self, *args, **kwargs):
    from corpkit.plotter import plotter
    return plotter(self, *args, **kwargs)

def _edit(self, *args, **kwargs):
    from corpkit.editor import editor
    return editor(self, *args, **kwargs)

def _save(self, savename, **kwargs):
    from corpkit.other import save
    save(self, savename, **kwargs)

def _quickview(self, n=25):
    from corpkit.other import quickview
    quickview(self, n=n)

def _format(self, *args, **kwargs):
    from corpkit.other import concprinter
    concprinter(self, *args, **kwargs)

def _texify(self, *args, **kwargs):
    from corpkit.other import texify
    texify(self, *args, **kwargs)

def _calculate(self, *args, **kwargs):
    from corpkit.process import interrogation_from_conclines
    return interrogation_from_conclines(self)

def _multiplot(self, leftdict={}, rightdict={}, **kwargs):
    from corpkit.plotter import multiplotter
    return multiplotter(self, leftdict=leftdict, rightdict=rightdict, **kwargs)

def _perplexity(self):
    """
    Pythonification of the formal definition of perplexity.

    input:  a sequence of chances (any iterable will do)
    output: perplexity value.

    from https://github.com/zeffii/NLP_class_notes
    """
    def _perplex(chances):
        import math
        chances = [i for i in chances if i] 
        N = len(chances)
        product = 1
        for chance in chances:
            product *= chance
        return math.pow(product, -1/N)

    return self.apply(_perplex, axis=1)

def _entropy(self):
    """
    entropy(pos.edit(merge_entries=mergetags, sort_by='total').results.T
    """
    from scipy.stats import entropy
    import pandas as pd
    escores = entropy(self.edit('/', SELF).results.T)
    ser = pd.Series(escores, index=self.index)
    ser.name = 'Entropy'
    return ser

def _shannon(self):
    from corpkit.stats import shannon
    return shannon(self)


def _shuffle(self, inplace=False):
    import random
    index = list(self.index)
    random.shuffle(index)
    shuffled = self.ix[index]
    shuffled.reset_index()
    if inplace:
        self = shuffled
    else:
        return shuffled

def _top(self):
    """Show as many rows and cols as possible without truncation"""
    import pandas as pd
    max_row = pd.options.display.max_rows
    max_col = pd.options.display.max_columns
    return self.iloc[:max_row, :max_col]

def _tabview(self, **kwargs):
    import pandas as pd
    import tabview
    tabview.view(self, **kwargs)

def _rel(self, denominator='self', **kwargs):
    from corpkit.editor import editor
    return editor(self, '%', denominator, **kwargs)

def _keyness(self, measure='ll', denominator='self', **kwargs):
    from corpkit.editor import editor
    return editor(self, 'k', denominator, **kwargs)

# monkey patching things

DataFrame.entropy = _entropy
DataFrame.perplexity = _perplexity
DataFrame.shannon = _shannon

DataFrame.edit = _edit
Series.edit = _edit

DataFrame.rel = _rel
Series.rel = _rel

DataFrame.keyness = _keyness
Series.keyness = _keyness

DataFrame.visualise = _plot
Series.visualise = _plot

DataFrame.tabview = _tabview

DataFrame.multiplot = _multiplot
Series.multiplot = _multiplot

DataFrame.save = _save
Series.save = _save

DataFrame.quickview = _quickview
Series.quickview = _quickview

DataFrame.format = _format
Series.format = _format

Series.texify = _texify

DataFrame.calculate = _calculate
Series.calculate = _calculate

DataFrame.shuffle = _shuffle

DataFrame.top = _top

# Defining letters
module = sys.modules[__name__]
for letter in LETTERS:
    if not letter.isalpha():
        trans = letter.replace('A', '-', 1).replace('Z', '+', 1).lower()
    else:
        trans = letter.lower()
    setattr(module, letter, trans)
    # other methods:
    # globals()[letter] = letter.lower()
    # exec('%s = "%s"' % (letter, letter.lower()))

ANYWORD = r'[A-Za-z0-9:_]'
