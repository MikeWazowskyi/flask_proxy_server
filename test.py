import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from main import (ROOT_PATH, STATIC_FOLDER, URL, app,
                  change_img_links_to_proxy,
                  change_style_links_to_absolute,
                  replace_source_links_with_proxy,
                  trademark_words)


class TestProxy(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @patch('main.fetch_url')
    def test_index(self, mock_get):
        mock_get.return_value = {
            'html': '<h1>Hello, World!</h1>',
            'status': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'}
        }
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/login')
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/submit')
        self.assertEqual(response.status_code, 200)

    def test_trademark_words(self):
        html = '<html><body><p>This is native Python™</p></body></html>'
        expected_html = ('<html><body><p>This is native™ Python™'
                         '</p></body></html>')
        soup = BeautifulSoup(html, 'html.parser')
        trademark_words(soup)
        self.assertEqual(str(soup), expected_html)

    def test_change_style_links_to_absolute(self):
        html = ('<html><head><link rel="stylesheet" '
                'href="/style.css"></head></html>')
        expected_html = (
            f'<html><head><link href="{STATIC_FOLDER}/style.css" '
            f'rel="stylesheet"/></head></html>')
        soup = BeautifulSoup(html, 'html.parser')
        change_style_links_to_absolute(soup)
        self.assertEqual(str(soup), expected_html)

    def test_replace_source_links_with_proxy(self):
        html = f'<html><body><a href="{URL}">Hacker News</a></body></html>'
        expected_html = (f'<html><body><a href="{ROOT_PATH}">'
                         f'Hacker News</a></body></html>')
        soup = BeautifulSoup(html, 'html.parser')
        replace_source_links_with_proxy(soup, path=ROOT_PATH)
        self.assertEqual(str(soup), expected_html)

    def test_change_img_links_to_proxy(self):
        html = '<html><body><img src="/image.jpg"></body></html>'
        expected_html = (f'<html><body><img src="{STATIC_FOLDER}'
                         f'/image.jpg"/></body></html>')
        soup = BeautifulSoup(html, 'html.parser')
        change_img_links_to_proxy(soup)
        self.assertEqual(str(soup), expected_html)


if __name__ == '__main__':
    unittest.main()
