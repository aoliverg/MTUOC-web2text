# MTUOC-web2text
Scripts and programs for creating corpora from websites. The process of creation of the corpus from the web is divided into two steps:

* Detecting all the internal links from the website. This action is performed with the script: ```MTUOC-link-extractor.py```
* Getting all the text from the detected links, segmenting the text and detecting the language. This action is performed with the script ```MTUOC-links2text.py```

As a result of this process, we will get a text file for each language in the website containing all the text for the language segmented using a SRX file. Once performed this action, we can try to align the segmented text files using [MTUOC-aligner](https://github.com/aoliverg/MTUOC-aligner) using the SBERT strategy.

## MTUOC-link-extractor.py

This script gets all the internal links from a website and stores the links into a text file, one link per line. You can use the -h option to get the help:

```
python3 MTUOC-link-extractor.py -h
usage: MTUOC-link-extractor.py [-h] --url URL -o OUTPUT [-m MAX_URLS] [-t MAX_TIME]
                               [--min_links MIN_LINKS]

Link Extractor Tool with Python

optional arguments:
  -h, --help            show this help message and exit
  --url URL             The URL to extract links from.
  -o OUTPUT, --output OUTPUT
                        The output file that will contain the links.
  -m MAX_URLS, --max_urls MAX_URLS
                        Number of max URLs to crawl, default is 10000.
  -t MAX_TIME, --max_time MAX_TIME
                        Max downloading time in hours, default is 1 hour.
  --min_links MIN_LINKS
                        Minimun number of internal links (default 10). If fewer perform
                        Google search.
```

For example, to get all the links from the http://www.foo.com website, we can write, and stori the list in the links-foo.txt file:

```
python3 MTUOC-link-extractor.py --url http://www.foo.com --o links-foo.txt
```

It will detect 10000 links maximum in 1 hour. After that the process will end. We can modify these parameters with the -t and --min_links. If less of a minimum number of links (by default 10) is obtained, a search to Google is performed to try to find more.

## MTUOC-links2text.py

This program gets the text from the links. Once obtained the text, the language is detected and the text is segmented. One file for each language is created. To get the help the option -h can be used:

```
ython3 MTUOC-links2text.py -h
usage: MTUOC-links2text.py [-h] -i INPUT -o OUTPUT [-s SRXFILE] [-m LDMODEL]

Script to download a list of links, convert to text, segment and classify by language.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The input file.
  -o OUTPUT, --output OUTPUT
                        The suffix for the output file.
  -s SRXFILE, --srxfile SRXFILE
                        The SRX file to segment the texts. Default: segment.srx
  -m LDMODEL, --ldmodel LDMODEL
                        The fast_text model to detect the languages. Default: lid.176.bin

```

To convert all the links in the file links-foo.txt, we can write:

```
python3 MTUOC-links2text.py -i links-foo.txt -o text-foo
```
I http://www.foo.com contains texts in English, Spanish and Frech, the following files will be created: text-foo-en.txt, text-foo-es.txt and text-foo-fr.txt

To run the program you need a language model for fast_text. By default it uses lid.176.bin, that can be obtained from:[https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin](https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin]. This file should be located in the same direcory as MTUOC-links2text.py

By default the program uses the SRX file segment.srx that is distributed along with the program, but any other SRX file can be specified usint the -s option.

