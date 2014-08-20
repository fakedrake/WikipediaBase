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

from common import TEST_FETCHER_SETUP

from wikipediabase import fetcher


class TestFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)

    def test_html(self):
        # Remember, this probably needs internet.
        html = self.fetcher.download("Led Zeppelin")
        self.assertIn("wikipedia", html)

    def test_source(self):
        src = self.fetcher.source("Led Zeppelin")
        self.assertIn("{{Infobox", src)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
