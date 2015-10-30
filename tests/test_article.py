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


class TestArticle(unittest.TestCase):

    def setUp(self):
        self.article = Article("Astaroth")

    def test_html(self):
        self.assertIn("<body", self.article.html_source())
        self.assertIn("Crowned Prince", self.article.html_source())

    def test_paragraphs(self):
        self.assertEqual(len(list(self.article.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.article.headings())), 5)
        self.assertIn("Appearances in literature",
                      self.article.headings())

    def test_complex(self):
        article = Article("Baal")
        self.assertEqual(article.headings()[-1], "External links")
        # TODO : is this a good test? The number of headings keeps changing
        self.assertEqual(len(list(article.headings())), 21)

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

    def test_no_redirects_in_db(self):
        # WikipediaBase assumes that symbols are titles of Wikipedia articles.
        # If symbol is a redirect, the behavior of WikipediaBase is undefined.
        # This is a safe assumption to make. WikipediaBase generates a list of
        # symbols for Omnibase. We make sure that that the list of symbols does
        # not contain redirects. WikipediaBase is only called with symbols from
        # this list.
        article = Article("Barack Hussein Obama")
        self.assertRaises(LookupError, article.markup_source, force_live=False)

    def test_redirects_live(self):
        markup = Article("Barack Hussein Obama").markup_source(force_live=True)
        self.assertGreater(len(markup), 30000)

if __name__ == '__main__':
    unittest.main()
