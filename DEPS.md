## corpkit's dependencies

Corpkit leverages several powerful Python libraries.

* [**matplotlib**](http://matplotlib.org) is a tool for generating 2d plots, usually of function graphs. The magic of matplotlib is that it can target different output formats: images, web content, interactive gui and even textual representations for the command-line. It's used for most of the plotting done by *corpkit*.
* [**nltk**](http://www.nltk.org) is a collection of handy little tools for working with natural language datasets. It sometimes handles lemmatisation and tokenisation.
* [**pandas**](http://pandas.pydata.org) is for manipulating data once you've parsed it and tidied it up. Its core object is the DataFrame, which you can think of as a spreadsheet, a table in a database or a mathematical relation. Interrogations and edited results are stored as Pandas objects, so that you can bypass `editor()` if you're a pandas/Python whiz.
* [**mpld3**](http://mpld3.github.io) hooks matplotlib up to [D3](http://d3js.org), a JS framework for data-driven documents. When not using the GUI, mpld3 can be used to provide web-based, interactive visualisations. It's pretty experimental at the moment.
* [**corenlp_xml**](https://github.com/interrogator/corenlp-xml-lib) is used to quickly navigate the XML output of Stanford CoreNLP. It's better to use the forked version, which handles speaker IDs. This is automatically installed 
* [*joblib*](https://pythonhosted.org/joblib/parallel.html) provides multiprocessing for some queries, when not using the GUI.
* [*Scipy*](http://www.scipy.org/)'s linear regression module is used to sort data by increasing or decreasing frequency. It's a big library for just one little function, but you should probably have it anyway.
* [*Jupyter Notebook*](https://jupyter.org/): programmatic web-browser interface
* [*TkInter*](https://wiki.python.org/moin/TkInter): Python GUI tool
* [*tkintertable*](https://github.com/dmnfarrell/tkintertable): show spreadsheets in TkInter GUI

* [*Jekyll*](http://jekyllrb.com/): website generator, used for [GUI website](http://interrogator.github.io/corpkit/)
* [*Jekyll Documentation Theme*](http://idratherbewriting.com/documentation-theme-jekyll/): specific template for the GUI website
