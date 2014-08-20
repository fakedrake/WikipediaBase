#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox
----------------------------------

Tests for `infobox` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from common import TEST_FETCHER_SETUP

from wikipediabase.infobox import Infobox
from wikipediabase import fetcher


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)
        self.ibox = Infobox("Led Zeppelin", self.fetcher)

    def test_markup(self):
        self.assertEqual(self.ibox.markup_source()[:9], "{{Infobox")

    def test_infobox_html_raw(self):
        self.assertIn("Origin\nLondon, England", self.ibox.rendered())

    def test_infobox_markup_raw(self):
        self.assertIn("| name = Led Zeppelin", self.ibox.markup_source())

    def test_infobox_html_parsed(self):
        self.assertIn((u'Origin', u'London, England'), self.ibox.html_parsed())

    def test_attributes(self):
        self.assertEqual(self.ibox.get("origin"), "London, England")

    def test_types(self):
        self.assertEqual(self.ibox.start_types(), ['wikipedia-musical-artist'])

    def test_types_redirect(self):
        clinton = Infobox("Bill Clinton", self.fetcher)
        self.assertIn('wikipedia-president', clinton.start_types())

    def test_html_keys(self):
        bbc = Infobox("BBC News", self.fetcher)
        self.assertEquals("Owner(s)", bbc.rendered_key("owner"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
