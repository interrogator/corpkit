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

def query_test(query, have_ipython = False, on_cloud = False):
    """make sure a tregex query works, and provide help if it doesn't"""

    import re
    import subprocess

    # define error searches 
    tregex_error = re.compile(r'^Error parsing expression')
    regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')

    #define command and run it
    if have_ipython:
        if on_cloud:
            tregex_command = 'sh tregex.sh \'%s\' 2>&1' % (query)
        else:
            tregex_command = 'tregex.sh \'%s\' 2>&1' % (query)
        testpattern = get_ipython().getoutput(tregex_command)
    else:
        if on_cloud:
            tregex_command = ['sh', 'tregex.sh', '%s' % (query)]
        else:
            tregex_command = ['tregex.sh', '%s' % (query)]
        try:
            testpattern = subprocess.check_output(tregex_command, 
                                    stderr=subprocess.STDOUT).split('\n')
        except Exception, e:
            testpattern = str(e.output).split('\n')

    # if tregex error, give general error message
    if re.match(tregex_error, testpattern[0]):
        tregex_error_output = "Error parsing Tregex expression. Check for balanced parentheses and boundary delimiters."
        raise ValueError(tregex_error_output) 
    
    # if regex error, try to help
    if re.match(regex_error, testpattern[0]):
        info = testpattern[0].split(':')
        index_of_error = re.findall(r'index [0-9]+', info[1])
        justnum = index_of_error[0].split('dex ')
        spaces = ' ' * int(justnum[1])
        remove_start = query.split('/', 1)
        remove_end = remove_start[1].split('/', -1)
        regex_error_output = 'Error parsing regex inside Tregex query:%s'\
        '. Best guess: \n%s\n%s^' % (str(info[1]), str(remove_end[0]), spaces)
        raise ValueError(regex_error_output)
    