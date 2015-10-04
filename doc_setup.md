---
title: "Setup"
tags: [setup, getting-started, osx]
keywords: setup, corpkit, gui
last_updated: 2015-09-01
---

## Opening the app

All you have to do is open the app to begin using *corpkit*. If you get an "unidentified developer" error when you try to open the app, close the error message, and `control-click`/`right-click` the app and select `Open` that way.

## Extras

Most of the things *corpkit* needs to run are embedded inside the app. A few things, however, might need to installed as you go along. In most cases, *corpkit* will prompt you if it cannot find a resource.

### Java

You'll need Java in order to search constituency trees. Your Mac will pop up a message if you don't have the right Java installed, and will point you to a website where you can get it.

Once it's installed, restart *corpkit* and try again. If the error persists, the reason is that your Mac actually pointed you to the wrong Java distribution. The one you need is [here](https://support.apple.com/downloads/DL1572/en_US/javaforosx.dmg). 

### CoreNLP parser

Parsing files requires the download and installation of the [Stanford CoreNLP parser](http://nlp.stanford.edu/software/corenlp.shtml). *corpkit* will manage this for you, installing the parser to your Home directory. It's pretty large, so if you ever want to remove it, just delete the `corenlp` folder from your `/users/yourname` directory.

{{note}} If you move the `corenlp/` folder somewhere else, *corpkit* won't automatically find it. You can tell *corpkit* where the parser is via the `Set CoreNLP path` option in the menu. {{end}}

### TeX

Finally, when plotting, The `Use TeX` option requires a TeX distribution. TeX is a typesetting system that the *corpkit* plotter can use to generate the text in the plot. It's mostly useful if you're writing up articles using TeX, and would like the fonts in your figures to match. If you don't already have TeX, it's probably not worth downloading TeX just for these images, as TeX installations can be gigabytes in size.

## Settings

*corpkit* stores two kinds of settings. The first are project-specific settings, which are saved to the `settings.ini` file inside each project directory. These include annotation schemes, wordlists, TeX use, etc.

Global settings, such as the path to CoreNLP, recently opened projects, etc., are saved within the tool itself.
