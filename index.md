---
layout: default
title: "corpkit"
---

corpkit
=======

`corpkit` is a tool for doing corpus linguistics. It does a lot of the usual things, like parsing, concordancing and keywording, but also extends their potential significantly: you can concordance by searching for combinations of lexical and grammatical features, and can do keywording of lemmas, of subcorpora compared to corpora, or of words in certain positions within clauses. Interrogations can be quickly edited and visualised in complex ways, or saved and loaded within projects, or exported to formats that can be handled by other tools.

## Screenshots

<figure> <center>
  <a href="https://raw.githubusercontent.com/interrogator/risk/master/images/interro.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/interro.png" alt="Interrogating" width="600" height="300"></a>
  <figcaption>Searching a corpus using constituency parses</figcaption> </center> 
</figure> 

<figure><center>
  <a href="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" alt="Editing" width="600" height="300"></a>
  <figcaption>Making relative frequencies, skipping subcorpora</figcaption>
</figure></center> 

<figure><center>
  <a href="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" alt="Visualising" width="600" height="300"></a>
  <figcaption>Visualising results</figcaption> 
</figure></center>

<figure><center>
  <a href="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" alt="Concordancing" width="560" height="300"></a>
  <figcaption>Concordancing with constituency queries, manually coding results</figcaption></center>
</figure> 

## Key features

The main difference from other tools is that `corpkit` is designed to look at **combinations of lexical and grammatical features** in **structured corpora**. You can easily count or concordance the subjects of passive clauses, or the verbal groups that occur when a participant is pronominal. Furthermore, you can do this for every subcorpus in your dataset in turn, in order to understand how language might be similar or different across the different parts of your dataset.

Also unique to `corpkit` are:

* Sophisticated editing and plotting tools (via *pandas* and *matplotlib*)
* Immediately editable results (via *tkintertable*)
* Thematic coding and colouring of concordance lines
* Auto-storage of results from investigations, as well as all the options used to generate them

The final key difference between `corpkit` and most current corpus linguistic software (*AntConc*, *WMatrix*, *Sketch Engine*, *UAM Corpus Tool*, *Wordsmith Tools*, etc.), `corpkit` is **free and open-source**, hackable, and provides both graphical and command-line interfaces, so that it may be useful for geek and non-geek alike. 

If you're interested in the command line interface, head to the [`corpkit repository`](https://www.github.com/interrogator/corpkit) for documentation and code. If you're interested in the graphical interface, you're in the right place. **From here on out, this document focusses on the graphical, not the command-line version of the tool.**

## Download

Currently, `corpkit` works for Mac, and presumably Linux. Windows support is coming soon.

To download, head to `corpkit`'s [**GitHub page**](https://github.com/interrogator/corpkit) and click `Download Zip`. 

Head to the [Setup page](doc/setup.html) for (very simple) installation instructions.

## Cite

If you want to cite `corpkit`, please use:

> `McDonald, D. (2015). corpkit: a toolkit for corpus linguistics. Retrieved from https://www.github.com/interrogator/corpkit. DOI: http://doi.org/10.5281/zenodo.28361`