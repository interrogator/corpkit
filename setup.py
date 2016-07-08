import setuptools
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from os.path import isfile, isdir, join, dirname

class CustomInstallCommand(install):
    """Customized setuptools install command."""
    def run(self):
        from setuptools.command.install import install
        install.run(self)
        # since nltk may have just been installed
        # we need to update our PYTHONPATH
        import site
        try:
            reload(site)
        except NameError:
            pass
        # Now we can import nltk
        import nltk
        path_to_nltk_f = nltk.__file__
        nltkpath = dirname(path_to_nltk_f)
        punktpath = join(nltkpath, 'tokenizers')
        wordnetpath = join(nltkpath, 'corpora')
        if not isfile(join(punktpath, 'punkt.zip')) \
            and not isdir(join(punktpath, 'punkt')):
            nltk.download('punkt', download_dir=nltkpath)
        if not isfile(join(wordnetpath, 'wordnet.zip')) \
            and not isdir(join(wordnetpath, 'wordnet')):
            nltk.download('wordnet', download_dir=nltkpath)
        nltk.data.path.append(nltkpath)

setup(name='corpkit',
      version='2.2.8',
      description='A toolkit for working with linguistic corpora',
      url='http://github.com/interrogator/corpkit',
      author='Daniel McDonald',
      packages=['corpkit'],
      scripts=['corpkit/new_project'],
      package_dir={'corpkit': 'corpkit'},
      package_data={'corpkit': ['*.jar', 'corpkit/*.jar', '*.sh', 'corpkit/*.sh', 
                                '*.ipynb', 'corpkit/*.ipynb', '*.p', 'dictionaries/*.p',
                                '*.py', 'dictionaries/*.py']},
      author_email='mcdonaldd@unimelb.edu.au',
      license='MIT',
      cmdclass={'install': CustomInstallCommand,},
      keywords=['corpus', 'linguistics', 'nlp'],
      install_requires=["matplotlib>=1.4.3",
                        "nltk>=3.0.0",
                        "joblib",
                        "pandas>=0.16.1",
                        "mpld3>=0.2", 
                        "lxml>=3.4.4",
                        "requests",
                        "chardet",
                        "blessings>=1.6",
                        "traitlets>=4.1.0"],
      dependency_links=['git+https://www.github.com/interrogator/corenlp-xml-lib#egg=corenlp-xml-lib',
                        'git+https://github.com/interrogator/tkintertable.git@e983dea6565d583439cbe04034774944388213ae#egg=tkintertable'])
  
