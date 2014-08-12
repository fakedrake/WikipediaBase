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

from common import TEST_FETCHER_SETUP

from wikipediabase.article import Article
from wikipediabase import fetcher

class TestArticle(unittest.TestCase):

    def setUp(self):
        self.ftchr = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)
        self.rtcl = Article("Astaroth", self.ftchr)

    def test_html(self):
        self.assertIn("<body", self.rtcl.html_source())
        self.assertIn("Crowned Prince", self.rtcl.html_source())

    def test_paragraphs(self):
        self.assertEqual(len(list(self.rtcl.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.rtcl.headings())), 5)
        self.assertIn("Appearances in literature",
                      self.rtcl.headings())

    def test_complex(self):
        rtcl = Article("Baal", self.ftchr)
        self.assertEqual(rtcl.headings()[-1], "External links")
        self.assertEqual(len(list(rtcl.headings())), 15)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
