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

import re
from wikipediabase import fetcher


class TestFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.WIKIBASE_FETCHER

    def test_html(self):
        html = self.fetcher.download("Led Zeppelin")
        self.assertIn("Jimmy Page", html)

    def test_source(self):
        src = self.fetcher.source("Led Zeppelin")
        self.assertIn("{{Infobox musical artist", src)

    def test_unicode_html(self):
        html = self.fetcher.download(u"Rhône")
        self.assertIn("France", html)

    def test_unicode_source(self):
        src = self.fetcher.source("Rhône")
        self.assertIn("Geobox|River", src)

    def test_silent_redirect(self):
        src = self.fetcher.source("Obama")
        self.assertFalse(re.match(fetcher.REDIRECT_REGEX, src))

if __name__ == '__main__':
    unittest.main()
