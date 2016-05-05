{% include linkrefs.html %}

## Overview 

*corpkit* is a tool for doing corpus linguistics. 

It does a lot of the usual things, like parsing, concordancing and keywording, but also extends their potential significantly: you can concordance by searching for combinations of lexical and grammatical features, and can do keywording of lemmas, of subcorpora compared to corpora, or of words in certain positions within clauses. 

Corpus interrogations can be quickly edited and visualised in complex ways, or saved and loaded within projects, or exported to formats that can be handled by other tools.

*corpkit* accomplishes all of this by leveraging a number of sophisticated programming libraries, including *pandas*, *matplotlib*, *scipy*, *Tkinter*, *tkintertable* and *Stanford CoreNLP*.

## Screenshots

<center>

<table width="500" border="0" cellpadding="5">
<tr>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/corpkit/gh-pages/images/interrogate.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/interro.png" alt="Interrogating" width="100" height="50"></a>
</div> <br />
<i>Searching a corpus using constituency parses</i>
</td>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/editing.png" alt="Editing" width="100" height="50"></a>
</div> <br />
<i>Making relative frequencies, skipping subcorpora</i>
</td>
</tr>
<tr>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/plott.png" alt="Visualising" width="100" height="50"></a>
</div> <br />
<i>Visualising results as a line graph</i>
</td>

<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/conc2.png" alt="Concordancing" width="90" height="50"></a>
</div>
<br />
<i>Concordancing with constituency queries, manually coding results</i>
</td>
</tr>
<tr>
<td align="center" valign="bottom">
<div style="width:120px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/corpkit/gh-pages/images/custom_wordlists.png" > <img src="https://raw.githubusercontent.com/interrogator/corpkit/gh-pages/images/custom_wordlists.png" alt="Defining wordlists" width="100" height="50"></a>
</div> <br />
<i>Defining pre-installed and custom wordlists</i>
</td>

<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/corpkit/gh-pages/images/treeview.png" > <img src="https://raw.githubusercontent.com/interrogator/corpkit/gh-pages/images/treeview.png" alt="Building, viewing trees" width="90" height="50"></a>
</div>
<br />
<i>Building corpora, viewing parse tree output</i>
</td>
</tr>
</table>
</center>

## Example figures: *Risk Semantics project*

<center>

<table width="500" border="0" cellpadding="5">
<tr>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk_processes-2.png" alt="Interrogating" width="100" height="50"></a>
</div> <br />
<i>Changing frequencies of risk processes</i>
</td>

<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/nominalisation-of-risk-emphthe-new-york-times-19872014.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/nominalisation-of-risk-emphthe-new-york-times-19872014.png" alt="Editing" width="100" height="50"></a>
</div> <br />
<i>Nominalisation of risk</i>
</td>
</tr>
<tr>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/risk-and-power-2.png" alt="Risk and power" width="90" height="50"></a>
</div>
<br />
<i>How often do certain social actors do risking?</i>
</td>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/pie-chart-of-common-modals-in-the-nyt2.png" alt="Modals" width="100" height="50"></a>
</div> <br />
<i>Modal auxiliaries in the NYT</i>
</td>
</tr>
<tr>

<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/sayers-increasing.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/sayers-increasing.png" alt="Sayers, increasing" width="90" height="50"></a>
</div>
<br />
<i>Sayers in verbal processes, sorted by increasing frequency</i>
</td>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/an-ocean-of-modals2.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/an-ocean-of-modals2.png" alt="Modal ocean" width="100" height="50"></a>
</div> <br />
<i>An ocean of modals in the NYT</i>
</td>
</tr>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/keyness-of-politicians-in-the-nyt.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/keyness-of-politicians-in-the-nyt.png" alt="Keyness" width="100" height="50"></a>
</div> <br />
<i>Using keywording with a list of politicians' names and no external reference corpus</i>
</td>
<td align="center" valign="bottom">
<div style="width:300px;height:180px;overflow:hidden;" >
<a href="https://raw.githubusercontent.com/interrogator/risk/master/images/to-put-at-risk.png" > <img src="https://raw.githubusercontent.com/interrogator/risk/master/images/to-put-at-risk.png" alt="To put at risk" width="90" height="50"></a>
</div><br />
<i>Using subplots to demonstrate the rise of "to put at risk" in U.S. news</i>
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
* Tool for building re-usable wordlists, getting spelling variants and inflections
* Simple integration of wordlists and corpus queries
* Auto-storage of results from investigations, as well as all the options used to generate them

The final key difference between *corpkit* and most current corpus linguistic software (*AntConc*, *WMatrix*, *Sketch Engine*, *UAM Corpus Tool*, *Wordsmith Tools*, etc.), *corpkit* is **free and open-source**, hackable, and provides both graphical and command-line interfaces, so that it may be useful for geek and non-geek alike. 

{{note}} A more detailed overview of features can be found on the <a href="doc_features.html"><i>Features</i></a> page. {{end}}

## Download

To download the most recent OSX version, use the link in the menu bar, or just [click here](https://github.com/interrogator/corpkit-app/raw/master/corpkit-2.0.9.tar.gz). See the [Setup page](doc_setup.html) for (very simple) installation instructions.

Linux users can run the graphical interface by installing *corpkit* with `pip install corpkit` and then open the GUI with `python -m corpkit.gui`.

Windows users will need to get a Python interpreter and *pip* installed, and then run `pip install corpit` and `python -m corpkit.gui`.

## Cite

If you want to cite *corpkit*, please use:

```
McDonald, D. (2015). corpkit: a toolkit for corpus linguistics. Retrieved from
https://www.github.com/interrogator/corpkit. DOI: http://doi.org/10.5281/zenodo.28361
```
