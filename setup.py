import setuptools
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from os.path import isfile, isdir, join, dirname

class CustomInstallCommand(install):
    """
    Customized setuptools install command, which installs
    some NLTK data automatically
    """
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
        # install these three resources and add them to path
        install_d = {'tokenizers': 'punkt',
                     'corpora': 'wordnet',
                     'taggers': 'averaged_perceptron_tagger'}
        
        path_to_nltk_f = nltk.__file__
        nltkpath = dirname(path_to_nltk_f)
        for path, name in install_d.items():
            pat = join(nltkpath, path)
            if not isfile(join(pat, '%s.zip' % name)) \
                and not isdir(join(pat, name)):
                nltk.download(name, download_dir=nltkpath)

        nltk.data.path.append(nltkpath)

setup(name='corpkit',
      version='2.3.5',
      description='A toolkit for working with linguistic corpora',
      url='http://github.com/interrogator/corpkit',
      author='Daniel McDonald',
      packages=['corpkit'],
      scripts=['corpkit/new_project', 'corpkit/parse',
               'corpkit/corpkit', 'corpkit/corpkit.1'],
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
                        "pandas>=0.18.1",
                        #"mpld3>=0.2", 
                        "requests",
                        "tabview>=1.4.0",
                        "chardet",
                        "blessings>=1.6",

                        "traitlets>=4.1.0"],
      dependency_links=['git+https://github.com/interrogator/tabview@93644dd1f410de4e47466ea8083bb628b9ccc471#egg=tabview',
                        'git+https://github.com/interrogator/tkintertable.git@e983dea6565d583439cbe04034774944388213ae#egg=tkintertable'])
  
