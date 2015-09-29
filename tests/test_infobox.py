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
from wikipediabase.infobox import Infobox


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.WIKIBASE_FETCHER

    def test_class(self):
        self.assertEqual(Infobox._to_class("Template:Infobox martial artist"),
                         "wikipedia-martial-artist")

    def test_type(self):
        self.assertEqual(Infobox._to_type("Template:Infobox martial artist"),
                         "martial artist")

    def test_markup(self):
        ibox = get_infobox("Led Zeppelin", self.fetcher)
        self.assertEqual(ibox.markup_source()[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup_source())

    def test_infobox_markup_raw(self):
        ibox = get_infobox("Winston Churchill", self.fetcher)
        self.assertIn("|death_place ", ibox.markup_source())

    def test_infobox_html_raw(self):
        ibox = get_infobox("Led Zeppelin", self.fetcher)
        self.assertIn("Origin\nLondon, England", ibox.rendered())

    def test_infobox_html_parsed(self):
        ibox = get_infobox("AC/DC", self.fetcher)
        self.assertIn(("Origin", "Sydney, Australia"), ibox.html_parsed())

    def test_rendered_attributes(self):
        clinton = get_infobox("Winston Churchill", self.fetcher)
        self.assertEqual("Died",
                         clinton.rendered_attributes().get("death_place"))

        bridge = get_infobox("Brooklyn Bridge", self.fetcher)
        self.assertEqual("Maintained by",
                         bridge.rendered_attributes().get("maint"))

    def test_get(self):
        ibox = get_infobox("The Rolling Stones", self.fetcher)
        self.assertEqual(ibox.get("origin"), "London, England")

    def test_attributes(self):
        ibox = get_infobox("Winston Churchill", self.fetcher)
        self.assertIn("death-place",
                      [k for k, v in ibox.markup_parsed_iter()])

    def test_templates(self):
        ibox = get_infobox("Vladimir Putin", self.fetcher)
        templates = ["Template:Infobox officeholder",
                     "Template:Infobox martial artist"]
        self.assertItemsEqual(ibox.templates(), templates)

    def test_classes(self):
        ibox = get_infobox("Vladimir Putin", self.fetcher)
        classes = ["wikipedia-officeholder", "wikipedia-martial-artist"]
        self.assertItemsEqual(ibox.classes(), classes)

    def test_types(self):
        ibox = get_infobox("Vladimir Putin", self.fetcher)
        types = ["officeholder", "martial artist", "person", "sportsperson",
                 "other sportsperson"]

        self.assertItemsEqual(ibox.types(), types)

    def test_types_redirect(self):
        ibox = get_infobox("Bill Clinton", self.fetcher)
        self.assertIn("president", ibox.types())

    def test_html_attributes(self):
        ibox = get_infobox("BBC News", self.fetcher)
        self.assertEqual("Owners", ibox.rendered_attributes().get("owners"))

if __name__ == '__main__':
    unittest.main()
