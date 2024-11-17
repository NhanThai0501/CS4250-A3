#-------------------------------------------------------------------------
# AUTHOR: Nhan Thai
# FILENAME: crawler.py
# SPECIFICATION: Crawl the CS website until the Permanent Faculty (there are 18 in total) page is found
# FOR: CS 4250 - Assignment #3
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/


import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re 
from collections import deque 

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['cs4250']
collection = db['pages']

# Function to retrieve HTML content from a URL
def retrieveHTML(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        return None

# Function to store the page's HTML into MongoDB
def storePage(url, html):
    if html:
        collection.insert_one({'url': url, 'html': html.decode('utf-8')})

# Function to parse the HTML and find all links
def parse(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if href.endswith('.html') or href.endswith('.shtml'):
            full_url = urllib.parse.urljoin(base_url, href)
            links.append(full_url)
    return links

# Function to check if the target page is found
def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1', {'class': 'cpp-h1'})
    return h1 and h1.get_text().strip() == "Permanent Faculty"

# Main crawler function
def crawlerThread(frontier):
    visited = set()
    while frontier:
        url = frontier.pop(0)
        if url in visited:
            continue
        print(f"Visiting: {url}")
        html = retrieveHTML(url)
        if html is None:
            continue
        storePage(url, html)
        visited.add(url)
        if target_page(html):
            print(f"Target page found: {url}")
            return
        for link in parse(html, url):
            if link not in visited:
                frontier.append(link)

# Main execution
if __name__ == "__main__":
    # Initial frontier with the CS homepage URL
    start_url = "https://www.cpp.edu/sci/computer-science/"
    frontier = [start_url]

    # Run the crawler
    crawlerThread(frontier)
