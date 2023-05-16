import re
from functools import wraps

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request

app = Flask(__name__)

URL = 'https://news.ycombinator.com'
PATTERN = r'\b\w{6}(?!™)\b'
REPLACEMENT = r'\g<0>™'
ROOT_PATH = '/'
PORT = 8232
STATIC_FOLDER = '/static/'


def modify_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        html = response.get('html')
        if isinstance(html, str):
            modified_html = modify_html_page(html)
            response['html'] = modified_html
        return response

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
        change_links_to_script(soup)
        return soup

    return wrapper


@modify_response
def fetch_url(url):
    response = requests.request(request.method, url,
                                params=request.args,
                                data=request.form.to_dict())
    return {'html': response.text,
            'status': response.status_code,
            'headers': response.headers}


@app.route(ROOT_PATH, defaults={'path': ''}, )
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    """Main proxy view function"""
    url = '{}/{}'.format(URL, path)
    response = fetch_url(url)
    return Response(str(response.get('html')),
                    content_type=response.get('headers').get(
                        'content-type'), status=response.get('status'))


def trademark_words(soup):
    """Changes each 6-letter word by adding trademark"""
    for tag in soup.find_all(string=True):
        if tag.parent.name not in ['style', 'script', 'head', 'title']:
            tag.replace_with(re.sub(PATTERN, REPLACEMENT, tag.string))


def change_style_links_to_absolute(soup):
    """Changes href in links with absolute links"""
    for link in soup.find_all('link'):
        if 'href' in link.attrs:
            match = re.search(r'^([^?]+)', link.attrs['href'])
            if match:
                link.attrs['href'] = STATIC_FOLDER + match.group(1)
            else:
                link.attrs['href'] = STATIC_FOLDER + link.attrs['href']


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
        if 'src' in img.attrs:
            img.attrs['src'] = STATIC_FOLDER + img.attrs['src']


def change_links_to_script(soup):
    """Changes href in img with absolute links"""
    for script in soup.find_all('script'):
        if 'src' in script.attrs:
            match = re.search(r'^([^?]+)', script.attrs['src'])
            if match:
                script.attrs['src'] = STATIC_FOLDER + match.group(1)
            else:
                script.attrs['src'] = STATIC_FOLDER + script.attrs['src']


if __name__ == '__main__':
    app.run(port=PORT)
