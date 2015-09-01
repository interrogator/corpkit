---
title: "Discourse-semantics of risk in *The New York Times*, 1963&ndash;2014: a corpus linguistic approach"
tags: [example, tutorial]
keywords: interrogation, gui, corpkit
summary: "This is an ongoing research project using corpkit."
last_updated: 2015-09-01
---

[![DOI](https://zenodo.org/badge/14568/interrogator/risk.svg)](https://zenodo.org/badge/latestdoi/14568/interrogator/risk)

This repository contains much of what was created for our longitudinal analysis of risk language in *The New York Times*. The investigation involves systematic analysis of over 150,000 NYT paragraphs containing a risk token (*risk*, *risking*, *at-risk*, *risk-to-reward*, *risk-laden*, etc). These paragraphs have been parsed with *Stanford CoreNLP*, and are interrogated using [`corpkit`](https://github.com/interrogator/corpkit), which was developed for this project.

Our *IPython Notebook* presents the code used in our analysis side-by-side with our results. It can be viewed via either [*GitHub*](https://github.com/interrogator/risk/blob/master/risk.ipynb) or [*nbviewer*](http://nbviewer.ipython.org/github/interrogator/risk/blob/master/risk.ipynb). Basically, we were interrogating the corpus for lexicogrammatical features of risk, and looking for sites of change. Here are a few examples, made using `corpkit`'s `interrogator()` and `plotter()` functions:

<p align="center">
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" height="230" width="400"/>
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/nominalisation-of-risk-emphthe-new-york-times-19872014.png" height="500" width="400"/>
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" height="200" width="400"/>
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png" width="400"/>
<img style="float:left" src="https://raw.githubusercontent.com/interrogator/risk/master/images/types-of-risk-modifiers.png" height="230" width="400"/>
</p>

Theoretically, our interest is in empirically examining sociological claims about risk made by (e.g.) Beck, Giddens and Luhmann. To do this, we rely on *Systemic Functional Linguistics* (e.g. Halliday & Matthiessen, 2004), with particular focus on experiential meaning. Our report, which contextualises and elaborates on these results, is available [as PDF](https://raw.githubusercontent.com/interrogator/risk/master/risk_report.pdf) and `.tex` source via [Overleaf](https://www.overleaf.com/read/jfyjfkqnztsp).

If you want to download and interrogate the corpus yourself, read on.

## Getting the data and Notebook

Once you've got [IPython](http://ipython.org/install.html) (`pip install ipython[all]` should do it for non-Windows users), you should downlad the contents of this repository. Either download and unzip via 'Download ZIP', or clone the repository with:

```shell
git clone https://github.com/interrogator/risk.git
```

Then, change into the project directory and start the IPython Notebook:

```shell
cd risk
# or, cd risk-master if you downloaded the .zip
ipython notebook risk.ipynb
```

The first few cells in the notebook will then help you:

1. install and import `corpkit`
2. unzip corpus data

The remainder of the notebook demonstrates our methods and findings, which you can freely manipulate if you like.
