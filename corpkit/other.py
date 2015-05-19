def quickview(lst, n = 50):
    """view top n results of lst"""
    import pandas
    for index, w in enumerate(list(lst.columns)[:n]):
        fildex = '% 3d' % index
        print '%s: %s (n=%d)' %(fildex, w, lst[w]['Total'])


