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

from wikipediabase import fetcher

class TestFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.CachingSiteFetcher()

    def test_html(self):
        # Remember, this probably needs internet.
        html = self.fetcher.download("Led Zeppelin")
        self.assertIn("wikipedia", html)

    def test_source(self):
        src = self.fetcher.source("Led Zeppelin")
        self.assertIn("{{Infobox", src)

    def test_infobox(self):
        infobox = self.fetcher.infobox("Led Zeppelin")
        self.assertEqual(infobox[:9], "{{Infobox")

    def test_infobox_html_raw(self):
        ibrp = self.fetcher.infobox("Led Zeppelin", rendered=True, parsed=False)
        self.assertIn("Origin\nLondon, England", ibrp)

    def test_infobox_source_raw(self):
        ibrp = self.fetcher.infobox("Led Zeppelin", rendered=False, parsed=False)
        self.assertIn("| name = Led Zeppelin", ibrp)


    def test_infobox_html_parsed(self):
        ibrp = self.fetcher.infobox("Led Zeppelin", rendered=True, parsed=True)
        self.assertIn((u'Origin', u'London, England'), ibrp)

    def test_infobox_source_parsed(self):
        ibrp = self.fetcher.infobox("Led Zeppelin", rendered=False, parsed=True)
        self.assertIn(('name ', 'Led Zeppelin'), ibrp)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
