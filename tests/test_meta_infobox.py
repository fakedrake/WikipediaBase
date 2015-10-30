#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_meta_infobox
----------------------------------

Tests for `meta_infobox` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.meta_infobox import get_meta_infobox, MetaInfoboxBuilder


class TestMetaInfobox(unittest.TestCase):

    def setUp(self):
        self.builder = MetaInfoboxBuilder('Template:Infobox person')
        self.ibx = self.builder.build()

    def test_clean_attribute(self):
        dirty = "  attr12 "
        self.assertEqual(self.builder._clean_attribute(dirty), "attr")

    def test_newlines(self):
        ibx = get_meta_infobox('Template:Infobox weapon')
        attr = ibx.rendered_attributes()['secondary_armament']
        self.assertEqual(attr, "Secondary armament")

    def test_musician(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.rendered_attributes()['origin'], "Origin")

    def test_regression_officeholder(self):
        mibx = get_meta_infobox('Template:Infobox officeholder')
        self.assertEqual("Died", mibx.rendered_attributes().get("death_place"))

    def test_getting_by_symbol(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.symbol, "Template:Infobox musical artist")
        self.assertEqual(di.title, "Infobox musical artist")

    def test_getting_by_title(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.symbol, "Template:Infobox musical artist")
        self.assertEqual(di.title, "Infobox musical artist")

    def test_attributes(self):
        self.assertIn((u'Native\xa0name', '!!!!!native_name!!!!!'),
                      self.builder.html_parsed())

    def test_rendered_attributes(self):
        self.assertEqual(self.ibx.rendered_attributes()['native_name'],
                         u'Native\xa0name')

if __name__ == '__main__':
    unittest.main()
