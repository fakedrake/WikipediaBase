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

from wikipediabase import fetcher
from wikipediabase.infobox import Infobox, get_infoboxes


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.fetcher = fetcher.get_fetcher()

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
        ibox = get_infoboxes("Led Zeppelin")[0]
        self.assertEqual(ibox.markup_source()[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup_source())

    def test_infobox_markup_raw(self):
        ibox = get_infoboxes("Winston Churchill")[0]
        self.assertIn("|death_place ", ibox.markup_source())

    def test_infobox_html_raw(self):
        ibox = get_infoboxes("Led Zeppelin")[0]
        self.assertIn("Origin\nLondon, England", ibox.rendered())

    def test_infobox_html_parsed(self):
        ibox = get_infoboxes("AC/DC")[0]
        self.assertIn(("Origin", "Sydney, Australia"), ibox.html_parsed())

    def test_rendered_attributes(self):
        clinton = get_infoboxes("Winston Churchill")[0]
        self.assertEqual("Died",
                         clinton.rendered_attributes().get("death_place"))

        bridge = get_infoboxes("Brooklyn Bridge")[0]
        self.assertEqual("Maintained by",
                         bridge.rendered_attributes().get("maint"))

    def test_get(self):
        ibox = get_infoboxes("The Rolling Stones")[0]
        self.assertEqual(ibox.get("origin"), "London, England")

    def test_attributes(self):
        ibox = get_infoboxes("Winston Churchill")[0]
        self.assertIn("death-place",
                      [k for k, v in ibox.markup_parsed_iter()])

    def test_templates(self):
        infoboxes = get_infoboxes("Vladimir Putin")
        templates = ["Template:Infobox officeholder",
                     "Template:Infobox martial artist"]
        self.assertItemsEqual(map(lambda i: i.template(), infoboxes),
                              templates)

    def test_classes(self):
        infoboxes = get_infoboxes("Vladimir Putin")
        classes = ["wikipedia-officeholder", "wikipedia-martial-artist"]
        self.assertItemsEqual(map(lambda i: i.wikipedia_class(), infoboxes),
                              classes)

    def test_html_attributes(self):
        ibox = get_infoboxes("BBC News")[0]
        self.assertEqual("Owners", ibox.rendered_attributes().get("owners"))

    def test_no_clashes_with_multiple_infoboxes(self):
        officeholder_ibox, martial_artist_ibox = get_infoboxes('Vladimir Putin')
        self.assertEqual(officeholder_ibox.wikipedia_class(),
                         'wikipedia-officeholder')
        self.assertEqual(martial_artist_ibox.wikipedia_class(),
                         'wikipedia-martial-artist')
        self.assertEqual(officeholder_ibox.get('image'),
                         'Vladimir Putin 12023 (cropped).jpg')
        self.assertEqual(martial_artist_ibox.get('image'),
                         'Vladimir Putin in Japan 3-5 September 2000-22.jpg')

    def test_get_infoboxes(self):
        symbol = "Led Zeppelin"
        self.assertIs(list, type(get_infoboxes(symbol)))
        self.assertIs(Infobox, type(get_infoboxes(symbol)[0]))

if __name__ == '__main__':
    unittest.main()
