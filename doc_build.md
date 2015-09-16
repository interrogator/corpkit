---
title: "Build"
tags: [build, parsing, structure, corpus, getting-started]
keywords: interrogation, gui, corpkit
summary: "This tab helps you incorporate, view, edit and parse plain text corpora."
last_updated: 2015-09-01
---
{% include linkrefs.html %}


## What *corpkit* needs from you

All you need to start working with *corpkit* is some plain text. If your data isn't in plain text format (`.txt`), you should turn it into plain text. You can often do this from Microsoft Word, a text editor, or via any of dozens of websites, like [zamzar](http://www.zamzar.com/). It makes no real difference if you have many small text files or a few large large files.

Once you have plain text files, ideally, you'll want to structure them: that is, put bits of text into subfolders representing something meaningful, like different timestamps, websites, books, chapters, etc. Give these subfolders useful names. 

If your corpus is unstructured, *corpkit* will still work, but you'll miss out on some really amazing features.


## Working with dialogue

If your data is dialogue, don't make subfolders for each speaker. Instead, just make sure it's formatted like this:

    USER: Can it handle a billion words?
    DEV: I reckon.

A unique feature of *corpkit* is that it will parse these documents, allowing you to later search by speaker.

## Scale up!

*corpkit* is designed to work with **lots of text**. The more, the better. Don't worry about the upper-limits, either: *corpkit* will not struggle with hundreds of millions of words. The larger the dataset, the more likely you can find significant numbers of even hyperspecific queries.

## Creating a project

Once you have data, you can start up *corpkit* and begin. The best way to begin is by creating a new project, via the menu. This creates a folder, with subfolders for saved interrogations, concordances, images, logs, CSV files and corpus data. You should then be moved to the `Build` tab.

From the `Build` tab, you can use `Add corpus` to copy your structured, plain-text corpus into the project directory. You have to select a directory containing your files, rather than the files themselves. This directory will then be copied into your project's `data/` folder.

Once you have added a corpus to the project, you can select it for viewing, editing and/or parsing. Or, if you want to add another corpus, or select a previously added corpus, you can do that instead.

## Editing your data

With a plain text corpus selected, you can view and edit the text files in your collection. You can make last-minute changes to the corpus now: after the texts are parsed, they are very difficult to change.

{{warning}} This interface is not designed for a serious amount of editing work. For large amounts of editing, use a good text editor, like  <a href="http://www.sublimetext.com"><i>Sublime Text</i></a> or <a href="http://www.barebones.com/products/textwrangler"><i>TextWrangler.</i></a>{{end}}

## Parsing

Parsing requires the one-time installation of the *Stanford CoreNLP* parser, as well as some things needed to run it. Follow the prompts to download and install it. If you want to move or delete the parser, it can be found in your `home` directory as `corenlp`. If you move it, you can manually set the CoreNLP path within *corpkit*.

{{tip}} Some features of <i>corpkit</i> work without parsing, but parsing is the best way to find complex and interesting things in your data. {{end}}

You can then choose to parse your files, or simply tokenise them. Why not do both?

## Speaker segmentation

If you select the speaker segmentation option, parsing will also involve labelling the speaker ID of each sentence.

For this option to work, each text file in your corpus must be formatted with speaker names in capital letters, followed by a colon, like so:

    JOHN: Why did they change the signs above all the bins?
    SPEAKER23: I know why. But I'm not telling.

This will allow you to restrict your interrogations and concordances to specific interlocutors.

{{note}} Speaker IDs don't <i>technically</i> need to denote speakers: timestamps or dates could be formatted in the same way, allowing you to restrict interrogations temporally. {{end}}

## Pressing the button

Parsing is a computationally intensive process. For long sentences, there are thousands of possible parses. The parser has to create them all, and decide which is the most likely. Sit tight and let the parsing happen. It's worth the wait.

## Next steps

Once texts are parsed, there is one more feature you might like to use. If you select a corpus of parsed texts, rather than editing the file contents, you can look at visualisations of the parse trees. This can be helpful in learning how to write a Tregex query.

Any parsed corpus becomes selectable from the menu, or from the `Interrogate` tab. Next, you can move over to the `Interrogate` tab to begin investigating  your data.
