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
import colorama
import codecs
import requests
import sys
import time

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

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


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    session = HTMLSession()
    try:###
        # initialize an HTTP session
        
        # make HTTP request & retrieve response
        response = session.get(url)
        # execute Javascript
        try:
            response.html.render()
        except:
            session.close()
            return urls
        soup = BeautifulSoup(response.html.html, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                # not a valid URL
                continue
            if href in internal_urls:
                # already in the set
                continue
            if url not in href:
                # external link
                if href not in external_urls:
                    print(f"{GRAY}[!] External link: {href}{RESET}")
                    external_urls.add(href)
                    sexternal.write(href+"\n")
                continue
            print(f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            if not href in internal_urls:
                sinternal.write(href+"\n")
            internal_urls.add(href)
    except:
        print("Error: ",sys.exc_info())
        session.close()
        sys.exit()
    session.close()
    return urls


def crawl(url, max_urls=30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        if time.time() > start + maxtime: 
            print("Max time reached!")
            print("[+] Total Internal links:", len(internal_urls))
            print("[+] Total External links:", len(external_urls))
            print("[+] Total URLs:", len(external_urls) + len(internal_urls))
            print("[+] Total crawled URLs:", total_urls_visited)
            sys.exit()
        try:
            crawl(link, max_urls=max_urls)
        except:
            print("ERROR in crawling: ",str(url),"\nTotal urls: ",str(total_urls_visited)+"\n"+str(sys.exc_info()))


#if __name__ == "__main__":
import argparse
parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
parser.add_argument("--url", help="The URL to extract links from.")
parser.add_argument("-m", "--max_urls", help="Number of max URLs to crawl, default is 10000.", default=10000, type=int)
parser.add_argument("-t", "--max_time", help="Max downloading time in hours, default is 1 hour.", default=1, type=float)
parser.add_argument("--min_links", help="Minimun number of internal links. If fewer perform Google search.", default=100, type=int)

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()
url = args.url
max_urls = args.max_urls
min_links=args.min_links
domain_name = urlparse(url).netloc
maxtime=3600*args.max_time

filename=url.replace("/","_")
sinternal=codecs.open(f"{filename}_internal_links.txt", "w",encoding="utf-8")
sexternal=codecs.open(f"{filename}_external_links.txt", "w",encoding="utf-8")
# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
total_urls_visited = 0
if not url.startswith("http"): url="http://"+url
start = time.time()

crawl(url, max_urls=max_urls)

if len(internal_urls)<min_links:
    googlelinks=searchGoogle(url)
    for gl in googlelinks:
        crawl(gl, max_urls=max_urls)

print("[+] Total Internal links:", len(internal_urls))
print("[+] Total External links:", len(external_urls))
print("[+] Total URLs:", len(external_urls) + len(internal_urls))
print("[+] Total crawled URLs:", total_urls_visited)

