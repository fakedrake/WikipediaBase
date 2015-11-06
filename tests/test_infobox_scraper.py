#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox_scraper
----------------------------------

Tests for `infobox_scraper` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from common import testcfg
from wikipediabase.infobox_scraper import MetaInfobox
import wikipediabase.fetcher as fetcher
from wikipediabase.util import get_meta_infobox

class TestMetaInfobox(unittest.TestCase):

    def setUp(self):
        self.ibx = MetaInfobox('infobox_person', configuration=testcfg)

    def test_newlines(self):
        weapon = get_meta_infobox('Template:Infobox weapon',
                                  configuration=testcfg).rendered_keys()
        self.assertIn('secondary_armament', weapon)
        self.assertEqual(weapon.get('secondary_armament'), "Secondary armament")

    def test_musician(self):
        di = get_meta_infobox('Template:Infobox musical artist',
                              configuration=testcfg)

        self.assertIsInstance(di.fetcher, fetcher.StaticFetcher)
        self.assertIn("origin", di.markup_source())
        self.assertIn("Origin", di.html_source().text())
        self.assertIn("origin", di.rendered_keys())
        self.assertEqual(di.rendered_keys().get('origin'), "Origin")

    def test_regression_officeholder(self):
        mibx = get_meta_infobox('Template:Infobox officeholder',
                                configuration=testcfg)
        self.assertEqual("Died", mibx.rendered_keys().get("death_place"))

    def test_getting_by_symbol(self):
        di = get_meta_infobox('Template:Infobox musical artist',
                              configuration=testcfg)
        self.assertEqual(di.title(), "Infobox musical artist")
        self.assertEqual(di.symbol.url_friendly(), "Template:Infobox_musical_artist")

    def test_getting_by_title(self):
        di = get_meta_infobox('Infobox musical artist', configuration=testcfg)
        self.assertEqual(di.symbol.url_friendly(), "Template:Infobox_musical_artist")
        self.assertEqual(di.title(), "Infobox musical artist")


    def test_attributes(self):
        self.assertIn((u'Native\xc2\xa0name', '!!!!!native_name!!!!!'),
                      [(k.text(), v.text()) for k, v in self.ibx.html_parsed()])

    def test_rendered_keys(self):
        self.assertEqual(self.ibx.rendered_keys().get('native_name'),
                         u'Native\xc2\xa0name', self.ibx.rendered_keys())

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
