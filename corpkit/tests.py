def check_pytex():
    """checks for pytex, i hope"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if 'pythontex' in as_string:
        return True
    else:
        return False

def check_t_kinter():
    """checks for tkinter i hope"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if 'Tkinter' in as_string:
        return True
    else:
        return False

def check_spider():
    """checks for spyder, i hope"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if 'spyder' in as_string:
        return True
    else:
        return False

def check_dit():
    """checks if we're on the cloud ... bad way to do it..."""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if '/opt/python/lib' in as_string:
        return True
    else:
        return False
 
def check_tex(have_ipython = True):
    import os
    if have_ipython:
        checktex_command = 'which latex'
        o = get_ipython().getoutput(checktex_command)[0]
        if o.startswith('which: no latex in'):
            have_tex = False
        else:
            have_tex = True
    else:
        import subprocess
        FNULL = open(os.devnull, 'w')
        checktex_command = ["which", "latex"]
        try:
            o = subprocess.check_output(checktex_command, stderr=FNULL)
            have_tex = True
        except subprocess.CalledProcessError:
            have_tex = False
    return have_tex
