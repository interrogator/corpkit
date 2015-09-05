---
title: Troubleshooting
tags: [errors, troubleshooting, help, python, code]
keywords: trouble, problems, support, error messages, problems, failure, error, #fail
last_updated: 2015-09-01
summary: "This page lists common errors and the steps needed to troubleshoot them."
---
{% include linkrefs.html %} 

### Unidentified developer message

If you can't open *corpkit* because it is from an unidentified developer, simply `control-click` or `right-click` it and select open that way. There's a little more information about this weirdness on the [Apple website](https://support.apple.com/kb/PH14369?locale=en_US)

### Missing dependencies: Java, CoreNLP, TeX

*corenlp* sometimes needs things that it doesn't come bundled with. Most of the time, you'll be prompted when this happens, but things can sometimes still go wrong.

For example, when searching parse trees, your Mac will pop up a message if you don't have the right Java installed, and will point you to a website where you can get it. Once it's installed, restart *corpkit* and try again. If the error persists, the reason is that your Mac actually pointed you to the wrong Java distribution. The one you need is [here](https://support.apple.com/downloads/DL1572/en_US/javaforosx.dmg). This, unfortunately, is an error that's pretty much out of *corpkit*'s hands.