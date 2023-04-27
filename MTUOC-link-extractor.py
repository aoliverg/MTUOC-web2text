#    MTUOC-link-extractor
#    Copyright: Antoni Oliver (2023) - Universitat Oberta de Catalunya - aoliverg@uoc.edu
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import sys
import time
import codecs


from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import argparse

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(browser,url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    urls = set()
    try:
        try:
            browser.get(url)
        except:
            print("ERROR:",sys.exc_info())
        source=browser.page_source
        
        elems = browser.find_elements_by_xpath("//a[@href]")
        urls=set()
        for elem in elems:
            href=elem.get_attribute("href")
            if is_valid(href):
                urls.add(href)
    except:
        print("Error: ",sys.exc_info())       
    return urls

def searchGoogle(query):

    headers = {
        'User-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    params = {
      'q': 'site:'+query,
      #'gl': 'us',
      #'hl': 'en',
    }
    links=[]
    html = requests.get('https://www.google.com/search', headers=headers, params=params)
    soup = BeautifulSoup(html.text, 'lxml')

    for result in soup.select('.tF2Cxc'):
      #title = result.select_one('.DKV0Md').text
        link = result.select_one('.yuRUbf a')['href']
      #print(title, link, sep='\n')
        links.append(link)
    return(links)

parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
parser.add_argument("--url", help="The URL to extract links from.",required=True)
parser.add_argument("-o","--output", help="The URL to extract links from.",required=True)

parser.add_argument("-m", "--max_urls", help="Number of max URLs to crawl, default is 10000.", default=10000, type=int)
parser.add_argument("-t", "--max_time", help="Max downloading time in hours, default is 1 hour.", default=1, type=float)
parser.add_argument("--min_links", help="Minimun number of internal links. If fewer perform Google search.", default=10, type=int)

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()
url = args.url
output=args.output
max_urls = args.max_urls
min_links=args.min_links
domain_name = urlparse(url).netloc
maxtime=3600*args.max_time

toinspect=set()
alreadydone=set()


opts = Options()
opts.add_argument('-headless')
opts.accept_untrusted_certs = True
browser = webdriver.Firefox(options=opts)
browser.set_page_load_timeout(8)

sortida=codecs.open(output,"w",encoding="utf-8")
start = time.time()

toinspect.add(url)
continua=True
while continua:
    URL=toinspect.pop()
    if not URL in alreadydone:
        print(URL,len(alreadydone),len(toinspect))
        sortida.write(URL+"\n")
        links = get_all_website_links(browser,URL)
        for link in links:
            link = urljoin(url, link)
            parsed_href = urlparse(link)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if url in href and not link in alreadydone:
                toinspect.add(link)
        alreadydone.add(URL)
    if time.time() > start + maxtime: 
        continua=False
    if len(alreadydone)>=max_urls:
        continua=False
        
if len(alreadydone)<min_links:
    googlelinks=searchGoogle(url)
    for gl in googlelinks:
        toinspect.add(gl)

continua=True
while continua:
    URL=toinspect.pop()
    if not URL in alreadydone:
        print(URL,len(alreadydone),len(toinspect))
        sortida.write(URL+"\n")
        links = get_all_website_links(browser,URL)
        for link in links:
            link = urljoin(url, link)
            parsed_href = urlparse(link)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if url in href and not link in alreadydone:
                toinspect.add(link)
        alreadydone.add(URL)
    if time.time() > start + maxtime: 
        continua=False
    if len(alreadydone)>=max_urls:
        continua=False

sortida.close()
