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



