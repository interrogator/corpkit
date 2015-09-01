{% include linkrefs.html %}

## Overview 

*corpkit* is a tool for doing corpus linguistics. It does a lot of the usual things, like parsing, concordancing and keywording, but also extends their potential significantly: you can concordance by searching for combinations of lexical and grammatical features, and can do keywording of lemmas, of subcorpora compared to corpora, or of words in certain positions within clauses. 

Interrogations can be quickly edited and visualised in complex ways, or saved and loaded within projects, or exported to formats that can be handled by other tools.

*corpkit* accomplishes all of this by leveraging a number of sophisticated programming libraries, including *pandas*, *matplotlib*, *scipy*, *Tkinter*, *tkintertable* and *Stanford CoreNLP*.

## Screenshots

<center>
<table width="500" border="0" cellpadding="5">
<tr>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/interro.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/interro.png" alt="Interrogating" width="100" height="50"></a>
</div> <br />
Searching a corpus using constituency parses
</td>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" alt="Editing" width="100" height="50"></a>
</div> <br />
Making relative frequencies, skipping subcorpora
</td>
</tr>
<tr>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" alt="Visualising" width="100" height="50"></a>
</div> <br />
Visualising results as a line graph, using TeX
</td>

<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" alt="Concordancing" width="90" height="50"></a>
</div>
<br />
Concordancing with constituency queries, manually coding results
</td>
</tr>
</table>
</center>

## Example figures

<center>
<table width="500" border="0" cellpadding="5">

<tr>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" alt="Interrogating" width="100" height="50"></a>
</div> <br />
Changing frequencies of risk processes
</td>

<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/nominalisation-of-risk-emphthe-new-york-times-19872014.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/nominalisation-of-risk-emphthe-new-york-times-19872014.png" alt="Editing" width="100" height="50"></a>
</div> <br />
Nominalisation of risk
</td>
</tr>
<tr>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" alt="Risk and power" width="90" height="50"></a>
</div>
<br />
How often do certain social actors do risking?
</td>
<td align="center" valign="center">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png" alt="Visualising" width="100" height="50"></a>
</div> <br />
Modal auxiliaries in the NYT
</td>
</tr>
</table>
</center>

## Key features

The main difference from other tools is that *corpkit* is designed to look at **combinations of lexical and grammatical features** in **structured corpora**. You can easily count or concordance the subjects of passive clauses, or the verbal groups that occur when a participant is pronominal. Furthermore, you can do this for every subcorpus in your dataset in turn, in order to understand how language might be similar or different across the different parts of your dataset.

Also unique to *corpkit* are:

* Sophisticated editing and plotting tools (via *pandas* and *matplotlib*)
* Immediately editable results (via *tkintertable*)
* Thematic coding and colouring of concordance lines
* Auto-storage of results from investigations, as well as all the options used to generate them

The final key difference between *corpkit* and most current corpus linguistic software (*AntConc*, *WMatrix*, *Sketch Engine*, *UAM Corpus Tool*, *Wordsmith Tools*, etc.), *corpkit* is **free and open-source**, hackable, and provides both graphical and command-line interfaces, so that it may be useful for geek and non-geek alike. 

A more detailed overview of features can be found on the [Features page](doc_features.html).

## Download

Currently, *corpkit* works for Mac, and presumably Linux. Windows support is coming soon.

To download, head to *corpkit*'s [**GitHub page**](https://github.com/interrogator/corpkit) and click `Download Zip`. 

Head to the [Setup page](doc_setup.html) for (very simple) installation instructions.

## Cite

If you want to cite *corpkit*, please use:

```
McDonald, D. (2015). corpkit: a toolkit for corpus linguistics. 
Retrieved from https://www.github.com/interrogator/corpkit. DOI: http://doi.org/10.5281/zenodo.28361
```
