## Contents
* [About MangaScrapper](https://github.com/AnimeshShaw/MangaScrapper#mangascrapper)
* [Help & Usage Instructions](https://github.com/AnimeshShaw/MangaScrapper#help--usage)
* [Example Usage](https://github.com/AnimeshShaw/MangaScrapper#example-usage)
* [Viewing Comic Book Archives (CBR/CBZ/CBT)](https://github.com/AnimeshShaw/MangaScrapper/blob/master/README.md#viewing-comic-book-archives-cbrcbzcbt)
* [Screenshots](https://github.com/AnimeshShaw/MangaScrapper#screenshots)

# MangaScrapper 
===============


	  __  __
	 |  \/  | __ _ _ __   __ _  __ _
	 | |\/| |/ _` | '_ \ / _` |/ _` |
	 | |  | | (_| | | | | (_| | (_| |
	 |_|  |_|\__,_|_| |_|\__, |\__,_|
	  ____               |___/
	 / ___|  ___ _ __ __ _ _ __  _ __   ___ _ __
	 \___ \ / __| '__/ _` | '_ \| '_ \ / _ \ '__|
	  ___) | (__| | | (_| | |_) | |_) |  __/ |
	 |____/ \___|_|  \__,_| .__/| .__/ \___|_|
						  |_|   |_|
			
						  By : Psycho_Coder
			  rC Developers @ rawCoders.com

It is simple, easy, and fast command line tool to download manga's and save them in a directory and as well as save them in different formats like CBR/CBZ/CBT/PDF. [CBR](http://en.wikipedia.org/wiki/Comic_book_archive) is a well known comic book archive format used by many across the Globe. It is compatible with Python 2.7.x+ and Python 3.3.x+.

Manga's are scraped from [MangaPanda](http://www.mangapanda.com/). Complete Manga, or a single chapter or chapters in a range can be downloaded. All these customizations are provided by this tool in addition to several others.

**MangaScrapper** makes use of 3rd party libraries for HTTP Requests and HTML processing. You need to fulfill these requirements before using this tool.

Fulfill the requirements by executing the following in bash shell.
	
	pip install -r requirements.txt

The *requirements.txt* file is present in the repo.

# Help & Usage
==============

	usage: mangascrapper.py [-h] [-b BEGIN] [-e END] [-c CHAPTER] [-l LOCATION]
	                [-lc] [-out OUTFORMAT]
	                manga_name

    MangaScrapper is simple, easy, and fast CLI tool to download manga's and also
    create an ebook in pdf format.

    positional arguments:
      manga_name            Enter the name of the manga.

    optional arguments:
      -h, --help            show this help message and exit
      -b BEGIN, --begin BEGIN
                            Enter the starting chapter. By default its first
                            chapter
      -e END, --end END     Enter the ending chapter. Defaults to the last chapter
                            possible.
      -c CHAPTER, --chapter CHAPTER
                            Give the chapter number if you want to download only
                            one chapter.
      -l LOCATION, --location LOCATION
                            The location where manga has to be downloaded. By
                            default stored in the current directory.
      -lc, --latest         Download the latest Manga chapter
      -out OUTFORMAT, --outformat OUTFORMAT
                            Generated Manga/Comic book output formats. Available
                            formats are cbr, cbz, cbt, & pdf; default is cbz.
							

# Example Usage
===============

#### To download complete Manga

	python mangascrapper.py <manga-name>
	
*Example:-* 	

	python mangascrapper.py "One Piece"

#### To download a particular chapter of Manga

	python mangascrapper.py -c <chapter-number> <manga-name>
						or
	python mangascrapper.py --chapter <chapter-number> <manga-name>
	
*Example:-*

	python mangascrapper.py --chapter 1 "Detective Conan"

#### To download chapters of Manga in a range

	python mangascrapper.py -b <beginning-chapter-number> -e <ending-chapter-number> <manga-name>
						or
	python mangascrapper.py --begin <beginning-chapter-number> --end <ending-chapter-number> <manga-name>
	
*Example:-* 	

	python mangascrapper.py --begin 1 --end 5 "Fairy Tail"

#### To download the latest Manga chapter.

	python mangascrapper.py <manga-name> -lc
	                or
	python mangascrapper.py <manga-name> --latest

*Example:-*

	python mangascrapper.py "One Piece" --latest

#### To download Manga chapters in different formats like CBR/CBZ/CBT/PDF

You can use this argument with any other argument. By default the PDF format is used.

	python mangascrapper.py <manga-name> -out cbr
						or
	python mangascrapper.py <manga-name> --outformat cbr

*Example:-*

	python mangascrapper.py --outformat cbr "Detective Conan"

__More Query Examples__

    python mangascrapper.py --outformat cbr --chapter 1 "Detective Conan"

    python mangascrapper.py --outformat cbr --begin 1 --end 5 "Naruto"

# Viewing Comic Book Archives (CBR/CBZ/CBT)
==============

#### Viewing in Linux

CBR files can be viewed using [Evince](https://wiki.gnome.org/Apps/Evince)

Run Evince from bash shell as :- 
	evince "path-cbr-file.cbr"
	
example :- 
	evince "Fairy Tail Zero - Chapter 9 - Treasure.cbr"

#### Viewing on Windows

The best free software to view CBR/CBZ/CBT comic book archive is [CDisplayex](http://www.cdisplayex.com/). Download and view the CBR files generated by this tool.

## Screenshots

Downloading a single chapter from M\manga Black Magic

![Downloading manga "Black Magic"](http://i.imgur.com/NCK34Ka.png)
---

Help Options

![Help Options](http://i.imgur.com/I6pbdHj.png)
---

Directory structure.

![Usage Demo and Directory Structure made](https://i.imgur.com/W7D4YAL.png)
---

PDF's generated

![A look at the PDF generated](https://i.imgur.com/QiX9wTj.png)
---

![A close look at the PDF generated](https://i.imgur.com/yhN8Rup.png)
---

Opening CBR file in Linux using Elance

![Open CBR files using Evince](http://i.imgur.com/e8McsSF.png)
---
