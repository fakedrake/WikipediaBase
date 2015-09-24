#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_fetcher
----------------------------------

Tests for `fetcher` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.common import MockUrlFd, testcfg

from wikipediabase import fetcher


class TestFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.CachingSiteFetcher(testcfg)

    def test_html(self):
        # Remember, this probably needs internet.
        html = self.fetcher.download("Led Zeppelin")
        self.assertIn("wikipedia", html)

    def test_source(self):
        # This should be cached.
        src = self.fetcher.source("Led Zeppelin")
        self.assertIn("{{Infobox", src)

    def test_redirect(self):
        redir = "http://fake_wikipedia.c0m/w/index.php?title=han_solo"
        with MockUrlFd(redir, "Han solo is a bitch."):
            self.assertEqual(self.fetcher.redirect_url("hansolo"), redir)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
