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

from common import MockUrlFd, testcfg
from wikipediabase.article import Article
from wikipediabase import fetcher


class TestArticle(unittest.TestCase):

    def setUp(self):
        self.ftchr = fetcher.CachingSiteFetcher(testcfg)
        self.rtcl = Article("Astaroth", testcfg)

    def test_html(self):
        self.assertIn("<body", self.rtcl.html_source())
        self.assertIn("Crowned Prince", self.rtcl.html_source())

    def test_fetcher(self):
        from wikipediabase.fetcher import BaseFetcher
        self.assertIsInstance(self.rtcl.fetcher, BaseFetcher)

    def test_paragraphs(self):
        self.assertEqual(len(list(self.rtcl.paragraphs())), 7)

    def test_headings(self):
        self.assertEqual(len(list(self.rtcl.headings())), 5)
        self.assertIn("Appearances in literature",
                      self.rtcl.headings())

    def test_infobox(self):
        self.assertEqual(self.rtcl.infobox().types(), [])

    def test_complex(self):
        rtcl = Article("Baal", configuration=testcfg)
        self.assertEqual(rtcl.headings()[-1], "External links")
        self.assertGreaterEqual(len(list(rtcl.headings())), 15)

    # XXX: symbols are not used anyway but here is the test.
    # The symbols work, mocking
    def _test_symbol(self):
        art = Article("Baal", configuration=testcfg)
        self.assertEqual(art.symbol(), "Baal")

        redir = "http://fake_wikipedia.c0m/w/index.php?title=han_solo"
        with MockURLOpen(redir, "Han solo is a bitch."):
            self.assertEqual(Article("Han Solo").symbol(), 'han_solo')

        redir = "http://fake_wikipedia.c0m/w/han_solo"
        with MockURLOpen(redir, "NOONE CALL HAN SOLO A BITCH."):
            self.assertEqual(Article("Han Solo", configuration=testcfg).symbol(), 'han_solo')

        # Test that we are back to normal
        art = Article("Astaroth")
        self.assertEqual(art.symbol(), "astaroth")

    def test_redirect(self):
        # Actually redirects the source
        self.assertGreater(len(Article("Barack Hussein Obama", configuration=testcfg).
                               markup_source()),
                           30000)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
