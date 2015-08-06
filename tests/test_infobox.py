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

from wikipediabase.util import get_infobox
from wikipediabase import fetcher


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.WIKIBASE_FETCHER

    def test_markup(self):
        ibox = get_infobox("Led Zeppelin", self.fetcher)
        self.assertEqual(ibox.markup_source()[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup_source())

    def test_infobox_markup_raw(self):
        ibox = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("|death_place ", ibox.markup_source())

    def test_infobox_html_raw(self):
        ibox = get_infobox("Led Zeppelin", self.fetcher)
        self.assertIn("Origin\nLondon, England", ibox.rendered())

    def test_infobox_html_parsed(self):
        ibox = get_infobox("AC/DC", self.fetcher)
        self.assertIn(("Origin", "Sydney, Australia"), ibox.html_parsed())

    def test_rendered_keys(self):
        ibox = get_infobox("Brooklyn Bridge", self.fetcher)
        self.assertEqual("Maintained by", ibox.rendered_keys().get("maint"))

    def test_get(self):
        ibox = get_infobox("The Rolling Stones", self.fetcher)
        self.assertEqual(ibox.get("origin"), "London, England")

    def test_attributes(self):
        ibox = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("death-place",
                      [k for k, v in ibox.markup_parsed_iter()])

    def test_types(self):
        ibox = get_infobox("Vladimir Putin", self.fetcher)
        expected = ["Template:Infobox officeholder",
                    "Template:Infobox martial artist"]

        expected_extended = ["Template:Infobox officeholder",
                             "Template:Infobox martial artist"]

        expected_start = ["wikipedia-officeholder",
                          "wikipedia-martial-artist",
                          "wikipedia-person",
                          "wikipedia-sportsperson",
                          "wikipedia-other-sportsperson"]

        self.assertItemsEqual(ibox.types(), expected)
        self.assertItemsEqual(ibox.types(extend=True), expected_extended)
        self.assertEqual(ibox.start_types(), expected_start)

    def test_types_redirect(self):
        ibox = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("wikipedia-president", ibox.start_types())

    def test_html_keys(self):
        ibox = get_infobox("BBC News", self.fetcher)
        self.assertEquals("Owners", ibox.rendered_keys().get("owners"))

if __name__ == "__main__":
    unittest.main()
