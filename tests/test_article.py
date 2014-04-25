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
from wikipediabase import fetcher

class TestArticle(unittest.TestCase):

    def setUp(self):
        self.ftchr = fetcher.CachingSiteFetcher()
        self.rtcl = Article("Astaroth", self.ftchr)

    def test_html(self):
        self.assertIn("<body", self.rtcl.html_source())
        self.assertIn("Crowned Prince", self.rtcl.html_source())

    def test_paragraphs(self):
        self.assertEqual(len(list(self.rtcl.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.rtcl.headings())), 5)
        self.assertIn("Appearances in literature",
                         map(lambda x: x.name(), self.rtcl.headings()))

    def test_complex(self):
        rtcl = Article("Baal", self.ftchr)
        self.assertEqual(len(list(rtcl.headings())), 15)

    def tearDown(self):
        pass

class TestHeading(unittest.TestCase):

    def setUp(self):
        ftchr = fetcher.CachingSiteFetcher()
        rtcl = Article("Led Zeppelin", ftchr)
        self.h = rtcl._primary_heading()

    def test_subheadings(self):
        topmost = [h.tag.text for h in self.h.subheadings()]
        self.assertIn("History", topmost)
        self.assertNotIn("Post-breakup", topmost)
        self.assertEqual(len(list(self.h.subheadings())), 9)
        self.assertIn("Formation", [h.name() for h in
                                    list(self.h.subheadings())[0].subheadings()])

    def test_paragraphs(self):
        self.assertIn("Led Zeppelin were an English rock band",
                      self.h.paragraphs()[0].text)


if __name__ == '__main__':
    unittest.main()
