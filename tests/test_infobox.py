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

from wikipediabase.util import get_article, get_infoboxes
from wikipediabase import fetcher
from wikipediabase.infobox import Infobox


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.WIKIBASE_FETCHER

    def test_class(self):
        self.assertEqual(Infobox._to_class("Template:Infobox martial artist"),
                         "wikipedia-martial-artist")

    def test_class_strip(self):
        self.assertEqual(Infobox._to_class("Template:Infobox writer "),
                         "wikipedia-writer")

    def test_class_taxobox(self):
        self.assertEqual(Infobox._to_class("Template:Taxobox"),
                         "wikipedia-taxobox")

    def test_type(self):
        self.assertEqual(Infobox._to_type("Template:Infobox martial artist"),
                         "martial artist")

    def test_type_taxobox(self):
        self.assertIsNone(Infobox._to_type("Template:Taxobox"))

    def test_markup(self):
        ibox = get_infoboxes("Led Zeppelin", fetcher=self.fetcher)[0]
        self.assertEqual(ibox.markup_source()[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup_source())

    def test_infobox_markup_raw(self):
        ibox = get_infoboxes("Winston Churchill", fetcher=self.fetcher)[0]
        self.assertIn("|death_place ", ibox.markup_source())

    def test_infobox_html_raw(self):
        ibox = get_infoboxes("Led Zeppelin", fetcher=self.fetcher)[0]
        self.assertIn("Origin\nLondon, England", ibox.rendered())

    def test_infobox_html_parsed(self):
        ibox = get_infoboxes("AC/DC", fetcher=self.fetcher)[0]
        self.assertIn(("Origin", "Sydney, Australia"), ibox.html_parsed())

    def test_rendered_attributes(self):
        clinton = get_infoboxes("Winston Churchill", fetcher=self.fetcher)[0]
        self.assertEqual("Died",
                         clinton.rendered_attributes().get("death_place"))

        bridge = get_infoboxes("Brooklyn Bridge", fetcher=self.fetcher)[0]
        self.assertEqual("Maintained by",
                         bridge.rendered_attributes().get("maint"))

    def test_get(self):
        ibox = get_infoboxes("The Rolling Stones", fetcher=self.fetcher)[0]
        self.assertEqual(ibox.get("origin"), "London, England")

    def test_attributes(self):
        ibox = get_infoboxes("Winston Churchill", fetcher=self.fetcher)[0]
        self.assertIn("death-place",
                      [k for k, v in ibox.markup_parsed_iter()])

    def test_templates(self):
        infoboxes = get_infoboxes("Vladimir Putin", fetcher=self.fetcher)
        templates = ["Template:Infobox officeholder",
                     "Template:Infobox martial artist"]
        self.assertItemsEqual(map(lambda i: i.template(), infoboxes),
                              templates)

    def test_classes(self):
        infoboxes = get_infoboxes("Vladimir Putin", fetcher=self.fetcher)
        classes = ["wikipedia-officeholder", "wikipedia-martial-artist"]
        self.assertItemsEqual(map(lambda i: i.wikipedia_class(), infoboxes),
                              classes)

    def test_types(self):
        article = get_article("Vladimir Putin", self.fetcher)
        # TODO : fix case inconsistency in infobox_tree
        types = ["officeholder", "martial artist", "Person", "Sportsperson",
                 "Other sportsperson"]

        self.assertItemsEqual(article.types(), types)

    def test_types_redirect(self):
        ibox = get_infoboxes("Bill Clinton", fetcher=self.fetcher)[0]
        self.assertIn("president", ibox.types())

    def test_html_attributes(self):
        ibox = get_infoboxes("BBC News", fetcher=self.fetcher)[0]
        self.assertEqual("Owners", ibox.rendered_attributes().get("owners"))

if __name__ == '__main__':
    unittest.main()
