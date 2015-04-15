# so far pretty much untested

def searchtree(tree, query):
    "Searches a tree with Tregex and returns matching terminals"
    import os
    from corpkit.query import query_test, check_dit, check_pytex
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    on_cloud = check_dit()
    fo = open('tree.tmp',"w")
    fo.write(tree + '\n')
    fo.close()
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh -o -t \'%s\' tree.tmp 2>/dev/null' % query
        else:
            tregex_command = 'tregex.sh -o -t \'%s\' tree.tmp 2>/dev/null' % query
        result_with_blank = get_ipython().getoutput(tregex_command)
        result = [r for r in result_with_blank if r]
    else:
        if on_cloud:
            tregex_command = ["sh", "tregex.sh", "-o", "-t", '%s' % query, "tree.tmp"]
        else:
            tregex_command = ["tregex.sh", "-o", "-t", '%s' % query, "tree.tmp"]
        FNULL = open(os.devnull, 'w')
        result = subprocess.check_output(tregex_command, stderr=FNULL)
        result = os.linesep.join([s for s in result.splitlines() if s]).split('\n')
    tregex_command = 'sh ./tregex.sh -o -t \'' + query + '\' tmp.tree 2>/dev/null'
    os.remove("tree.tmp")
    return result

def quicktree(sentence):
    """Parse a sentence and return a visual representation in IPython"""
    import os
    from nltk import Tree
    from nltk.draw.util import CanvasFrame
    from nltk.draw import TreeWidget
    try:
        from stat_parser import Parser
    except:
        raise ValueError('PyStatParser not found.')
    try:
        from IPython.display import display
        from IPython.display import Image
    except:
        pass
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False
    parser = Parser()
    parsed = parser.parse(sentence)
    cf = CanvasFrame()
    tc = TreeWidget(cf.canvas(),parsed)
    cf.add_widget(tc,10,10) # (10,10) offsets
    cf.print_to_file('tree.ps')
    cf.destroy()
    if have_ipython:
        tregex_command = 'convert tree.ps tree.png'
        result = get_ipython().getoutput(tregex_command)
    else:
        tregex_command = ["convert", "tree.ps", "tree.png"]
        result = subprocess.check_output(tregex_command)    
    os.remove("tree.ps")
    return Image(filename='tree.png')
    os.remove("tree.png")
