import re

import cachetools.func
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request

app = Flask(__name__)

URL = 'https://news.ycombinator.com'
PATTERN = r'\b\w{6}\b'
REPLACEMENT = r'\g<0>™'
ROOT_PATH = '/'


@app.route(ROOT_PATH, defaults={'path': ''})
@app.route('/<path:path>')
@cachetools.func.ttl_cache(maxsize=128, ttl=10)
def proxy(path):
    """Main proxy view function"""
    url = '{}/{}'.format(URL, path)
    params = request.args
    response = requests.get(url, params)
    html = response.text
    modified_html = modify_html_page(html)
    headers = {'Access-Control-Allow-Origin': '*'}
    return Response(str(modified_html),
                    content_type=response.headers['content-type'],
                    headers=headers)


def trademark_words(soup):
    """Changes each 6-letter word by adding trademark"""
    for tag in soup.find_all(string=True):
        if tag.parent.name not in ['style', 'script', 'head', 'title']:
            tag.replace_with(re.sub(PATTERN, REPLACEMENT, tag.string))


def change_style_links_to_absolute(soup):
    """Changes href in links with absolute links"""
    for link in soup.find_all('link'):
        if 'href' in link.attrs:
            link.attrs['href'] = '{}/{}'.format(URL, link.attrs['href'])


def replace_source_links_with_proxy(soup, path=None):
    """Replace source links in hyperlink tag to proxy links """
    if not path:
        path = ROOT_PATH
    for a in soup.find_all('a'):
        if 'href' in a.attrs and a.attrs['href'] == URL:
            a.attrs['href'] = path


def change_img_links_to_proxy(soup):
    """Changes href in img with absolute links"""
    for img in soup.find_all('img'):
        if 'src' in img.attrs and not img.attrs['src'].startswith('http'):
            img.attrs['src'] = '{}/{}'.format(URL, img.attrs['src'])


def modify_html_page(html):
    """
    Modify page by adding trademarks,
    changing stylesheet links and hrefs
    """
    soup = BeautifulSoup(html, 'html.parser')
    trademark_words(soup)
    change_style_links_to_absolute(soup)
    replace_source_links_with_proxy(soup)
    change_img_links_to_proxy(soup)
    return soup


if __name__ == '__main__':
    app.run(port=8232)
