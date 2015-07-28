#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_article
----------------------------------

Tests for `article` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from common import MockURLOpen

from wikipediabase.article import Article
from wikipediabase import fetcher


class TestArticle(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.Fetcher()
        self.article = Article("Astaroth", self.fetcher)

    def test_html(self):
        self.assertIn("<body", self.article.html_source())
        self.assertIn("Crowned Prince", self.article.html_source())

    def test_paragraphs(self):
        self.assertEqual(len(list(self.article.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.article.headings())), 5)
        self.assertIn("Appearances in literature",
                      self.article.headings())

    def test_infobox(self):
        self.assertEqual(self.article.infobox().types(), [])

    def test_complex(self):
        article = Article("Baal", self.fetcher)
        self.assertEqual(article.headings()[-1], "External links")
        self.assertEqual(len(list(article.headings())), 17)

    # XXX: symbols are not used anyway but here is the test.
    # The symbols work, mocking
    def _test_symbol(self):
        article = Article("Baal")
        self.assertEqual(article.symbol(), "Baal")

        redir = "http://fake_wikipedia.c0m/w/index.php?title=han_solo"
        with MockURLOpen(redir, "Han solo is a bitch."):
            self.assertEqual(Article("Han Solo").symbol(), 'han_solo')

        redir = "http://fake_wikipedia.c0m/w/han_solo"
        with MockURLOpen(redir, "NOONE CALL HAN SOLO A BITCH."):
            self.assertEqual(Article("Han Solo").symbol(), 'han_solo')

        # Test that we are back to normal
        article = Article("Astaroth")
        self.assertEqual(article.symbol(), "astaroth")

    def test_redirect(self):
        # Actually redirects the source
        self.assertGreater(len(Article("Barack Hussein Obama").markup_source()),
                           30000)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
