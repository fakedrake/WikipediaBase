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

from wikipediabase.article import Article


class TestArticle(unittest.TestCase):

    def setUp(self):
        self.article = Article("Astaroth")

    def test_html(self):
        self.assertIn("<body", self.article.html_source())
        self.assertIn("demonology", self.article.html_source())

    def test_paragraphs(self):
        self.assertEqual(len(list(self.article.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.article.headings())), 5)
        self.assertIn("Appearances in literature", self.article.headings())

    def test_complex(self):
        article = Article("Baal")
        self.assertEqual(article.headings()[-1], "External links")
        # TODO : is this a good test? The number of headings keeps changing
        self.assertEqual(len(list(article.headings())), 21)

    def test_redirects_live(self):
        markup = Article("Barack Hussein Obama").markup_source(force_live=True)
        self.assertGreater(len(markup), 30000)

if __name__ == '__main__':
    unittest.main()
