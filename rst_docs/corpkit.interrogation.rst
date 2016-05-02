Interrogation classes
============================

Once you have searched a ``Corpus`` object, you'll want to be able to edit, visualise and store results. Remember that upon importing *corpkit*, any ``pandas.DataFrame`` or ``pandas.Series`` object is monkey-patched with ``save``, ``edit`` and ``visualise`` methods.

`Interrogation`
---------------------
.. autoclass:: corpkit.interrogation.Interrogation
    .. autoinstanceattribute:: interrogation.Interrogation.query
    .. autoinstanceattribute:: interrogation.Interrogation.results
    .. autoinstanceattribute:: interrogation.Interrogation.totals
    .. autoinstanceattribute:: interrogation.Interrogation.concordance

`Interrodict`
---------------------
.. autoclass:: corpkit.interrogation.Interrodict
    :members:
    :undoc-members:
    :show-inheritance:

`Concordance`
---------------------
.. autoclass:: corpkit.interrogation.Concordance
    :members:
    :undoc-members:
    :show-inheritance: