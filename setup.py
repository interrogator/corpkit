from setuptools import setup, find_packages
from setuptools.command.install import install

class install_with_nltk_extras(install):
    """Customized setuptools install command that adds nltk data and a slightly
       modified version of corenlp_xml, with speakername added in. this only
       works in install mode, not develop mode."""
    def run(self):
        install.run(self)
        import nltk
        import os
        path_to_nltk_f = nltk.__file__
        nltkpath = os.path.dirname(path_to_nltk_f)
        nltk.download('punkt', download_dir = nltkpath)
        nltk.download('wordnet', download_dir = nltkpath)
        nltk.data.path.append(nltkpath)
        def install_with_pip(package):
            import importlib
            try:
                importlib.import_module(package)
            except ImportError:
                import pip
                pip.main(['install', package])
        install_with_pip('git+git://github.com/interrogator/corenlp-xml-lib.git')
        install_with_pip('git+git://github.com/interrogator/tkintertable.git')

setup(name='corpkit',
      version='1.59',
      description='A toolkit for working with linguistic corpora',
      url='http://github.com/interrogator/corpkit',
      author='Daniel McDonald',
      package_data={'corpkit': ['*.jar', 'corpkit/*.jar', '*.sh', 'corpkit/*.sh', 
                                '*.ipynb', 'corpkit/*.ipynb'],
                    'dictionaries': ['*.p', 'dictionaries/*.p']},
      author_email='mcdonaldd@unimelb.edu.au',
      license='MIT',
      cmdclass={'install': install_with_nltk_extras},
      packages=['corpkit', 'dictionaries'],
      install_requires=["matplotlib >= 1.4.3",
                        "nltk >= 3.0.0",
                        "joblib",
                        "pandas >= 0.16.1",
                        "mpld3 >= 0.2", 
                        "beautifulsoup4>=4.3.2",
                        "lxml>=3.4.4",
                        "blessings>=1.6",
                        "PIL>=1.1.7"],
                        #"tkintertable>=1.2"],
      zip_safe = False)
