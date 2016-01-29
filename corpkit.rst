---------------------------
Classes
---------------------------

`Corpus`
=================

.. autoclass:: corpkit.corpus.Corpus
    :members:
    :undoc-members:
    :show-inheritance:

`Corpora`
=================
.. autoclass:: corpkit.corpus.Corpora
    :members:
    :undoc-members:
    :show-inheritance:

`Subcorpus`
=================
.. autoclass:: corpkit.corpus.Subcorpus
    :members:
    :undoc-members:
    :show-inheritance:

`File`
=================
.. autoclass:: corpkit.corpus.File
    :members:
    :undoc-members:
    :show-inheritance:

`Datalist`
=================
.. autoclass:: corpkit.corpus.Datalist
    :members:
    :undoc-members:
    :show-inheritance:



`Interrogation`
=================
.. autoclass:: corpkit.interrogation.Interrogation
    :members:
    :undoc-members:
    :show-inheritance:

`Interrodict`
=================
.. autoclass:: corpkit.interrogation.Interrodict
    :members:
    :undoc-members:
    :show-inheritance:


----------------------
Functions
----------------------

`as_regex`
=================
.. autofunction:: corpkit.other.as_regex

`load`
=================
.. autofunction:: corpkit.other.load

`load_all_results`
===================
.. autofunction:: corpkit.other.load_all_results

`new_project`
=================
.. autofunction:: corpkit.other.new_project

----------------------
Wordlists
----------------------

.. autodata:: corpkit.dictionaries.wordlists.wordlists
   :annotation: Various wordlists. `wordlists.closedclass`, `wordlists.pronouns`, etc.

.. autodata:: corpkit.dictionaries.process_types.processes
   :annotation: Process type wordlists. `processes.relational`, `processes.mental`, `processes.verbal`

.. data:: corpkit.dictionaries.stopwords.stopwords
   :annotation: A list of stopwords (or, use `wordlists.closedclass`)
   
.. autodata:: corpkit.dictionaries.roles.roles
   :annotation: Translate systemic-functional to dependency roles. roles.actor, roles.predicator, roles.epithet

.. data:: corpkit.dictionaries.bnc.bnc
   :annotation: BNC word frequency list

.. data:: corpkit.dictionaries.word_transforms.usa_convert
   :annotation: A dict with U.S. English words as keys, U.K. words as values.
