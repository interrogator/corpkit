from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.install import install as _install  
from setuptools.command.develop import develop as _develop

#def _post_install():  
#
#    def install_with_pip(package_name, package):
#        import importlib
#        try:
#            importlib.import_module(package_name)
#        except ImportError:
#            import pip
#            pip.main(['install', package])
#
#    # since nltk may have just been install
#    # we need to update our PYTHONPATH
#    #import site
#    #reload(site)
#    ## Now we can import nltk
#    #import nltk
#    #import os
#    #path_to_nltk_f = nltk.__file__
#    #nltkpath = os.path.dirname(path_to_nltk_f)
#    #punktpath = os.path.join(nltkpath, 'tokenizers')
#    #wordnetpath = os.path.join(nltkpath, 'corpora')
#    #if not os.path.isfile(os.path.join(punktpath, 'punkt.zip')) \
#    #    and not os.path.isdir(os.path.join(punktpath, 'punkt')):
#    #    nltk.download('punkt', download_dir = nltkpath)
#    #if not os.path.isfile(os.path.join(wordnetpath, 'wordnet.zip')) \
#    #    and not os.path.isdir(os.path.join(wordnetpath, 'wordnet')):
#    #    nltk.download('wordnet', download_dir = nltkpath)
#    #nltk.data.path.append(nltkpath)
#
#    install_with_pip('corenlp_xml', 'git+git://github.com/interrogator/corenlp-xml-lib.git')
#    install_with_pip('tkintertable', 'git+git://github.com/interrogator/tkintertable.git')
#    install_with_pip('PIL', 'http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz')
#
#class my_install(install):  
#    def run(self):
#        _install.run(self)
#
#        # the second parameter, [], can be replaced with a set of parameters if _post_install needs any
#        self.execute(_post_install, [],  
#                     msg="Installing NLTK data, etc.")
#
#class my_develop(develop):  
#    def run(self):
#        self.execute(noop, (self.install_lib,),
#                     msg="Installing ... ")
#        _develop.run(self)
#        self.execute(_post_install, [],
#                     msg="Installing NLTK data, etc.")

setup(name='corpkit',
    version='1.62',
    description='A toolkit for working with linguistic corpora',
    url='http://github.com/interrogator/corpkit',
    author='Daniel McDonald',
    package_data={'corpkit': ['*.jar', 'corpkit/*.jar', '*.sh', 'corpkit/*.sh', 
                                '*.ipynb', 'corpkit/*.ipynb'],
                    'dictionaries': ['*.p', 'dictionaries/*.p']},
    author_email='mcdonaldd@unimelb.edu.au',
    license='MIT',
    #cmdclass={'install': my_install,  # override install
    #              'develop': my_develop},
    packages=['corpkit', 'dictionaries'],
    install_requires=["matplotlib >= 1.4.3",
                        "nltk >= 3.0.0",
                        "joblib",
                        "pandas >= 0.16.1",
                        "mpld3 >= 0.2", 
                        "beautifulsoup4>=4.3.2",
                        "lxml>=3.4.4",
                        "blessings>=1.6"],
                        # PIL, Pillow
                        #"tkintertable>=1.2"],
    zip_safe = False)
