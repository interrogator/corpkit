
def save_result(interrogation, savename, savedir = 'data/saved_interrogations'):
    """Save an interrogation as pickle to savedir"""
    from collections import namedtuple
    import pickle
    import os
    import pandas
    # currently, allow overwrite. if that's not ok:
    #if os.path.isfile(csvmake):
        #raise ValueError("Save error: %s already exists in %s. \
                    #Pick a new name." % (savename, savedir))
    
    # if it's just a table or series
    if type(interrogation) == pandas.core.frame.DataFrame or type(interrogation) == pandas.core.series.Series:
        temp_list = [interrogation]
    elif len(interrogation) == 2:
        temp_list = [interrogation.query, interrogation.totals]
    elif len(interrogation) == 4:
        temp_list = [interrogation.query, interrogation.results, interrogation.totals, interrogation.table]
    else:
        try:
            temp_list = [interrogation.query, interrogation.results, interrogation.totals, interrogation.table]
        except:
            raise ValueError(' %s' % interrogation)
            
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    if not savename.endswith('.p'):
        savename = savename + '.p'
    f = open('%s/%s' % (savedir, savename), 'w')
    pickle.dump(temp_list, f)
    f.close()

def load_result(savename, loaddir = 'data/saved_interrogations'):
    """Reloads a save_result as namedtuple"""
    import collections
    import pickle
    import pandas
    if not savename.endswith('.p'):
        savename = savename + '.p'
    unpickled = pickle.load(open('%s/%s' % (loaddir, savename), 'rb'))
    
    if type(unpickled) == pandas.core.frame.DataFrame or type(unpickled) == pandas.core.series.Series:
        output = unpickled
    elif len(unpickled) == 4:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals', 'table'])
        output = outputnames(unpickled[0], unpickled[1], unpickled[2], unpickled[3])        
    elif len(unpickled) == 3:
        outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
        output = outputnames(unpickled[0], unpickled[1], unpickled[2])
    elif len(unpickled) == 2:
        outputnames = collections.namedtuple('interrogation', ['query', 'totals'])
        output = outputnames(unpickled[0], unpickled[1])
    return output
