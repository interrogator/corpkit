---
title: "Changelog"
tags: [changelog]
keywords: interrogation, gui, corpkit, CHANGELOG
summary: "A changelog for the GUI."
last_updated: 2016-04-26
---
{% include linkrefs.html %}

# Change log

All notable changes to the *corpkit* GUI will be documented in this file.
This project does not yet adhere to strict [Semantic Versioning](http://semver.org/). It will once the first major release is a bit more stable.

## 2016-04-01

### Fixed

Fixed unused import in download_large_file, used when getting CoreNLP

## 2016-03-27

### Fixed

* matplotlib figures with non-numerical axes


## 2016-03-25

### Changed

* Better handling of multiple criteria
* use vidiris as colour scheme
* A lot of backend updates

## 2016-02-05

### Added

* Calculate stats from concordance lines

### Fixed

* Dictionary savename
* Various bugs

## 2016-02-04

### Changed

Serious changes with this revision. Most notably, the concordancer and interrogator have in many respects merged. When you interrogate the corpus, concordance lines are automatically generated. The main benefit of this is that the user can now search much more complex things, and have more crossover with things in the interrogation tab.

This major change may have caused some breakages that remain to be seen.

### Improved

* Under the hood, many modules have been upgraded to the latest versions. Most things are now also Python 3 compatible, but there's still more to be done on that front.
* The show and return options have been expanded significantly
* Lemmatisation is improved/streamlined
* Minor GUI interface tweaks

## 2015-12-11

### Improved

* App upgraded to use matplotlib 1.5.0, newest numpy, pandas, etc. This should improve stability for now, and will make it possible to do cool new things in the future

### Added

* Plotting colour schemes: 'viridis', 'magma', 'plasma', 'inferno'

### Fixed

* Editing and plotting errors if editing/plotting totals, rather than results

## 2015-11-16

### Fixed

* Preset queries fixed now, with ability to still customise return values
* Interrogate interface improved

## 2015-11-15

### Added

* Multiple exclude patterns
* Exclude with wordlists

### Improved

* Bugs in interrogation interface


## 2015-11-13

### Improved

* Interrogation update: there's no more function filter and POS filter options. These have been replaced by 'Refine' and 'Exclude', which are much more flexible.

### Fixed

* Progress on getting more features to work with every data type. Still some bugs though.

## 2015-11-11

### Improved

* This version has a new way of selecting search types and what to return. This allows much greater flexibility, and is more readily comprehensible. It was a major change, so some thing may have broken. Some documentation might also need updating.
* Bugfixing for multiquery (i.e. selecting 'ALL' as speaker)

## 2015-11-05

### Improved

* Single entry/subcorpus switched from 'None' to 'All'
* If you delete num_to_plot, it comes back as '7' on plot
* Minor button moving

### Fixed

* Stopped some bad parser path and most recent project settings from leaking into the distributed app

## 2015-11-04

### Added

* Visualisation: *filled*, which makes all entries sum to 100% for bar and area charts
* Partial pie: allow non-circular pie charts when values don't sum to 1
* Layout: if using subplots, specify the grid shape for the chart

### Fixed

* General UI tweaks, so that you can't press Edit/Plot when there's nothing to edit/plot
* Regex error messages (still need to be more specific)
* Closer to Linux compatibility
* Area plot legends don't duplicate, and go where they are supposed to

## 2015-10-19

### Added

* Preferences popup that exports to tool preferences, alongside some new options:
  * Spreadsheet cell width
  * Spreadsheet row header width
  * Number at which to truncate conc/spreadsheet
  * p value
  * Disable update checks
  * Parser memory allocation
* More plotting styles from seaborn

### Fixed

* Edit: Merge entries with wordlist
* Better edit spreadsheet positioning
* No scientific notation in axis ticks when plotting
* Force English locale

### Updated

* New version of matplotlib

## 2015-10-15

### Fixed

* Hopefully fixed a matplotlib error that made corpkit break on startup
* Fixed broken concordancer (sorry!)

## 2015-10-13

### Fixed

* Auto update won't keep asking you to update anymore

### Added

* Single subcorpus plotting

### Improved

* enable/disables

## 2015-10-12

### Improved

* Put panels of buttons into frames so they don't jump around
* Merge saved conc lines with those on screen if only one selected
* More helpful regular expression errors
* Scrollbars for visualisations
* More verbose log output
* Dictionary, update and prev/next buttons don't wait until interrogating/editing before showing up
* More things are disabled when unavailable

### Added

* Single entry option for Visualise

## 2015-10-10

### Added

* Split sentences option controls truncation of conc lines at sent boundaries

### Improved

* GUI tweaks: various widget weights were changed to fit better
* Manage moved to menu bar
* Speaker segmentation is now an option after pressing 'parse'
* Clearing of old project corpora
* More options disabled when not helpful

### Fixed

* Plaintext and token based concordancing
* A few plaintext searching errors, both for simple and regex-based

## 2015-10-08

### Fixed

* If you make a large figure in Visualise, it won't mess up the grid
* Cumulative option
* Editing sorting for certain operations
* No extra printing of path on open

### Added

* New visualise option: stacked plot
* New visualise styles: matplotlib, mpl-white
* Visualise: toggle grid
* Seaborn run on plots now by default
* Better help links

## 2015-10-07

### Fixed

* Error message when concordancing by function that isn't recognised
* No system dirs in recent projects

## 2015-10-06

### Fixed

* Included matplotlib without any compression so that it works properly
* Can concordance unstructured corpora
* Build windows refresh properly
* Fixed bug where you couldn't parse immediately after downloading CoreNLP
* Fixed auto update for major and minor updates
* Added Scipy. It's half the app size, though!

### Disabled

* TeX is disabled for now, due to an error. Those who want it can probably run from .py, which enables it again.

## 2015-10-05

### Added

* Readded updating, via download of the Unix executable
* Fixed error when trying to parse caused by inability to reload sys module

### Changed

* Made the app resizable
* Now using requests module for large file download
* chmod the downloaded executable for minor updates
* Fixing paths to NLTK resources and CoreNLP downloader

## 2015-10-04

### Changed

* Because of some underlying issues with SSL, I've ended up using PyInstaller as the app builder. This should allow the splash screen, too. For now, though, there could be some little bugs, and the code needs a bit of a clean up

### Disabled

* Checking for updates has been disabled, because I don't know if I can patch the binary file.

## 2015-10-03

### Issues

The app is failing to load on many other machines at the moment. I can't reproduce the problem, making it hard to diagnose. I'm working on it.

### Added

* Bundled md5 into app

## 2015-09-30

### Added

* Minor versioning system: if corpkit-gui.py is updated in the corpkit-app submodule, user can quickly patch the tool. Major updates will be those where re-download of the .tar.gz is necessary. This will allow quick patching.
* There's a nice splash screen, but it may not work inside the .app. Low priority.
* Ability to select certain CoreNLP annotators

### Fixed

* Fixed error when keywording caused by no IPython installation

## 2015-09-28

### Added

* You can now select parts of the wordlists and get inflections for just the part
* Linear regression reenabled now that it's down to a managable size
* A number of backend features regarding multiprocessing that aren't yet enabled in the GUI
* Option to select annotations before parsing (probably needs further testing)

### Fixed

* Better handling of corenlp path variable: user should be able to select either the dir containing the jars or the dir containing the dir containing the jars.

## 2015-09-12

### Changed

Removed impossible kinds of search from options, depending on name of corpus. This should reduce your chance of getting errors from trying to search tokens for trees, etc.

## 2015-09-10

Likely final update from HK, so broken things may remain so for a few days.

### Fixed

* Inflection buttons working properly
* Better clearing of previous interrogation spreadsheet

### Added

* Prompt user when there's an unsaved wordlist when pressing 'Done'
* Split or don't split contractions when doing ngrams

### To do

I think opening a new project while in a project does not start cleanly, but keeps a few old variables. I don't think any users have multiple projects yet, though, so it shouldn't be a huge problem.

## 2015-09-09

### Added

* Open recent project option
* Auto selection of appropriate kind of search based on corpus name

### Fixed

* Deleting of custom wordlists
* Tool preferences file contains recent projects

## 2015-09-08

### Added

* Custom queries: make custom wordlists with inflections, save to json in project dir
* Schemes menu for this and the colour coder
* A tool preferences file, currently just containing the corenlp path, but in future, corenlp options, appearance, and so on

### Improved

* Reducing size of the app by taking out unused bits from libraries

## 2015-09-08

### Fixed

* The auto-update feature was struggling a little. It should work properly now.
* PIL was not bundled with the app, so you could not view saved images. That's corrected now.

### Added

* In the Plot tab, 'Explode' lets you explode an entry for a pie chart, or a list of entries using the [first,second] syntax

## 2015-09-03

### Added
Created this repository, a *corpkit* submodule