def _get_bnc():
    """Load the BNC"""
    import corpkit
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    import os
    fullpaths = [os.path.join(os.path.dirname(corpkit.__file__), 'corpkit', 'dictionaries', 'bnc.p'),
                 os.path.join(os.path.dirname(corpkit.__file__), 'dictionaries', 'bnc.p'),
                 os.path.join(os.path.dirname(corpkit.__file__), 'bnc.p'),
                 os.path.join(os.path.dirname(os.path.dirname(corpkit.__file__)), 'bnc.p')]
    fullpath = next(x for x in fullpaths if os.path.isfile(x))
    with open(fullpath, 'rb') as fo:
        data = pickle.load(fo)
    return data

bnc = _get_bnc()