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

import common
from wikipediabase.infobox_scraper import MetaInfobox
from wikipediabase.util import get_meta_infobox

class TestMetaInfobox(unittest.TestCase):

    def setUp(self):
        self.ibx = MetaInfobox('infobox_person')

    def test_newlines(self):
        self.assertEqual(get_meta_infobox('Template:Infobox weapon').rendered_keys()['secondary_armament'], "Secondary armament")

    def test_musician(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.rendered_keys()['origin'], "Origin")

    def test_regression_officeholder(self):
        mibx = get_meta_infobox('Template:Infobox officeholder')
        self.assertEqual("Died", mibx.rendered_keys().get("death_place"))

    def test_getting_by_symbol(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.symbol, "Template:Infobox musical artist")
        self.assertEqual(di.title, "Infobox musical artist")

    def test_getting_by_title(self):
        di = get_meta_infobox('Infobox musical artist')
        self.assertEqual(di.symbol, "Template:Infobox musical artist")
        self.assertEqual(di.title, "Infobox musical artist")


    def test_attributes(self):
        self.assertIn((u'Native\xc2\xa0name', '!!!!!native_name!!!!!'),
                      self.ibx.html_parsed())

    def test_rendered_keys(self):
        self.assertEqual(self.ibx.rendered_keys()['native_name'],
                         u'Native\xc2\xa0name')


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
