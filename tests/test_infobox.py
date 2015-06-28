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
from wikipediabase.util import get_infobox
from wikipediabase import fetcher


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)
        self.ibox = get_infobox("Led Zeppelin", self.fetcher)

    def test_markup(self):
        self.assertEqual(self.ibox.markup_source()[:9], "{{Infobox")

    def test_infobox_html_raw(self):
        self.assertIn("Origin\nLondon, England", self.ibox.rendered())

    def test_infobox_markup_raw(self):
        self.assertIn("| name = Led Zeppelin", self.ibox.markup_source())
        clinton = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("|death_place ", clinton.markup_source())

    def test_rendered_keys(self):
        clinton = get_infobox("Bill Clinton", self.fetcher)
        self.assertEqual("Died", clinton.rendered_keys().get("death_place"))

    def test_infobox_html_parsed(self):
        self.assertIn((u'Origin', u'London, England'), self.ibox.html_parsed())

    def test_attributes(self):
        self.assertEqual(self.ibox.get("origin"), "London, England")
        clinton = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("death-place",
                      [k for k, v in clinton.markup_parsed_iter()])

    def test_types(self):
        self.assertEqual(self.ibox.types(), ['Template:Infobox musical artist'])
        self.assertEqual(self.ibox.types(True), ['Template:Infobox musical artist'])
        self.assertEqual(self.ibox.start_types(), ['wikipedia-musical-artist'])

    def test_types_redirect(self):
        clinton = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn('wikipedia-president', clinton.start_types())

    def test_html_keys(self):
        bbc = get_infobox("BBC News", self.fetcher)
        self.assertEquals("Owner(s)", bbc.rendered_keys().get("owner"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
