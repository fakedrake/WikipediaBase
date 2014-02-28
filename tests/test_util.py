#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_util
----------------------------------

Tests for `util` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.util import paths_to_tree, get_html, article
from .common import data

import os

SAKESPEAR_TITLE = "<title>William Shakespeare"

class TestUtil(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile(data("articles/Shakespere.html")):
            from .data.articles.page_download import main as gethtml
            p = os.path.abspath('.')
            os.chdir(data('articles'))
            gethtml("Shakespere")
            os.chdir(p)

    def test_get_html(self):
        s = get_html(data("articles/Shakespere.html"))
        self.assertIn(SAKESPEAR_TITLE[:500], s)

    def test_tree_parsing(self):
        l = [([], 'z'), ([1], 'a'), ([1, 2], 'b'), ([2], 'c'), ([2], 'w'), ([3], 'l')]

        self.assertEqual(paths_to_tree(l),
                         {'head': None, 'paragraphs': ['z'], 'children': [
                             {'head': 1, 'paragraphs': ['a'], 'children': [
                                 {'head': 2, 'paragraphs': ['b'], 'children':[]}]},
                             {'head': 2, 'paragraphs': ['c', 'w'], 'children': []},
                             {'head': 3, 'paragraphs': ['l'], 'children': []}]})

    def test_article_json(self):
        l =
        article(get_html("http://en.wikipedia.org/wiki/Edgar_Allan_Poe"),
                nwrap=lambda x: x.text, lwrap=lambda x: x.text)
        self.assertEqual(l['children'][0]['head'], 'Early life')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
