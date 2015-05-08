
def report_display():
    """Displays/downloads the risk report, depending on your browser settings"""
    class PDF(object):
        def __init__(self, pdf, size=(200,200)):
            self.pdf = pdf
            self.size = size
        def _repr_html_(self):
            return '<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)
        def _repr_latex_(self):
            return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)
    return PDF('report/risk_report.pdf',size=(800,650))

def ipyconverter(inputfile, outextension):
    """ipyconverter converts ipynb files to various formats.

    This function calls a shell script, rather than using an API. The first argument is the ipynb file. The second argument is the file extension of the output format, which may be 'py', 'html', 'tex' or 'md'.

    Example usage: ipyconverter('infile.ipynb', 'tex')

    This creates a .tex file called infile-converted.tex
    """
    import os
    if outextension == 'py':
        outargument = '--to python ' # the trailing space is important!
    if outextension == 'tex':
        outargument = '--to latex '
    if outextension == 'html':
        outargument = '--to html '
    if outextension == 'md':
        outargument = '--to md '
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '-converted.' + outextension
    shellscript = 'ipython nbconvert ' + outargument + inputfile + ' --stdout > ' + output
    print "Shell command: " + shellscript
    os.system(shellscript)

def conv(inputfile, loadme = True):
    """A .py to .ipynb converter that relies on old code from IPython.

    You shouldn't use this: I only am while I'm on a deadline.
    """
    import os, sys
    import pycon.current as nbf
    import IPython
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '.ipynb'
    badname = outbasename + '.nbconvert.ipynb'
    print '\nConverting ' + inputfile + ' ---> ' + output + ' ...'
    nb = nbf.read(open(inputfile, 'r'), 'py')
    nbf.write(nb, open(output, 'w'), 'ipynb')
    os.system('ipython nbconvert --to=notebook --nbformat=4 %s' % output)
    os.system('mv %s %s' % (badname, output))
    if loadme:
        os.system('ipython notebook %s' % output)
    #nbnew = open(output, 'r')
    #IPython.nbformat.v4.convert.upgrade(nbnew, from_version=3, from_minor=0)
    print 'Done!\n'

def pytoipy(inputfile):
    """A .py to .ipynb converter.

    This function converts .py files to ipynb, relying on the IPython API. Comments in the .py file can be used to delimit cells, headings, etc. For example:

    # <headingcell level=1>
    # A heading 
    # <markdowncell>
    # *This text is in markdown*
    # <codecell>
    # print 'hello'

    Example usage: pytoipy('filename.py')
    """
    import os
    import IPython.nbformat.current as nbf
    outbasename = os.path.splitext(inputfile)[0]
    output = outbasename + '.ipynb'
    print '\nConverting ' + inputfile + ' ---> ' + output + ' ...'
    nb = nbf.read(open(inputfile, 'r'), 'py')
    nbf.write(nb, open(output, 'w'), 'ipynb')
    print 'Done!\n'

def new_project(name):
    """make a new project in current directory"""
    import os
    import shutil
    import stat
    import platform
    import corpkit

    path_to_corpkit = os.path.dirname(corpkit.__file__)
    thepath, corpkitname = os.path.split(path_to_corpkit)
    
    # make project directory
    os.makedirs(name)
    # make other directories
    dirs_to_make = ['data', 'images']
    subdirs_to_make = ['dictionaries', 'saved_interrogations', 'corpus']
    for directory in dirs_to_make:
        os.makedirs(os.path.join(name, directory))
    for subdir in subdirs_to_make:
        os.makedirs(os.path.join(name, 'data', subdir))
    # copy the bnc dictionary to data/dictionaries
    shutil.copy(os.path.join(thepath, 'dictionaries', 'bnc.p'), os.path.join(name, 'data', 'dictionaries'))
    
    # make a blank ish notebook
    newnotebook_text = open(os.path.join(thepath, corpkitname, 'blanknotebook.ipynb')).read()
    fixed_text = newnotebook_text.replace('blanknotebook', str(name))
    with open(os.path.join(name, name + '.ipynb'), 'wb') as handle:
        handle.write(fixed_text)
        handle.close
    if platform.system() == 'Darwin':
        shtext = '#!/bin/bash\n\npath=$0\ncd ${path%%/*.*}\nipython notebook %s.ipynb\n' % name
        with open(os.path.join(name, 'launcher.sh'), 'wb') as handle:
            handle.write(shtext)
            handle.close
        # permissions for sh launcher
        st = os.stat(os.path.join(name, 'launcher.sh'))
        os.chmod(os.path.join(name, 'launcher.sh'), st.st_mode | 0111)
        print '\nNew project made: %s\nTo begin, either use:\n\n    ipython notebook %s.ipynb\n\nor run launcher.sh.\n\n' % (name, name)
    else:
        print '\nNew project made: %s\nTo begin, either use:\n\n    ipython notebook %s.ipynb\n\n' % (name, name)