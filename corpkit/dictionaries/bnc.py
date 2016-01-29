def _get_bnc():
    """Load the BNC"""
    import corpkit
    import pickle
    import os
    fullpath = os.path.join(os.path.dirname(corpkit.__file__), 'dictionaries', 'bnc.p')
    with open(fullpath, 'rb') as fo:
        data = pickle.load(fo)
    return data

bnc = _get_bnc()