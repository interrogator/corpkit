---
title: "Preferences"
keywords: preferences
summary: "There are a number of useful preferences you might want to customise."
last_updated: 2015-10-20
---
{% include linkrefs.html %}

From the Menu you can access `Preferences`. These are loaded every time you open *corpkit*. Most defaults are sensible, but a part of the philosophy of the tool is that any arbitrary value should be customisable.

<br>

| Name      | Function      |
|--------|--------|
| `Automatically check updates`       | When selected, *corpkit* goes online on startup, looks for newer versions, and requests to install them if available.        |
| `Truncate concordance lines`       |  By default, *corpkit* will ask you to truncate concordance results if there are more than 1000. You can change that number here, or just hit `No` at the prompt to load them all.  |
| `Truncate spreadsheets`      | Unlike concordances, spreadsheets are automatically truncated at 9999 unique results. This value can be altered here. |
| `CoreNLP memory allocation`  | The CoreNLP parser requires a lot of memory, especially if you have very long sentences or if you are using referent tracking in long documents. While the default value should be sufficient for parsing well-edited text, non-standard material might need an increase. Your computer only has finite amounts of memory, however, so performance problems may result if you raise this number.       |
| `Spreadsheet cell width`       | If you have a lot of subcorpora, you may want to reduce the width of spreadsheet cells to see more results.       |
| `Spreadsheet row header width` | If you have long corpus names, you may want to increase this dimension to allow them to be seen |
| `P value` | When editing interrogations, some options (sorting by increase/decrease, or selecting `Keep stats`) will cause p values to be generated, representing the likelihood that variations between subcorpora are caused by chance. If you change this number and use the `Remove above p` option, anything result higher than the threshold will be automatically removed |
| `CoreNLP path`       | *corpkit* will download CoreNLP to your home directory. If you move it, you can tell *corpkit* where you moved it to. |

