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

from wikipediabase.infobox_scraper import DummyInfobox
from wikipediabase.util import get_dummy_infobox

class TestDummyInfobox(unittest.TestCase):

    def setUp(self):
        self.ibx = DummyInfobox('infobox_person')

    def test_musician(self):
        di = get_dummy_infobox('Template:Infobox musical artist')
        self.assertEqual(di.rendered_keys()['origin'], "Origin")


    def test_attributes(self):
        self.assertIn((u'Native\xa0name', '!!!!!native_name!!!!!'),
                      self.ibx.html_parsed())

    def test_rendered_keys(self):
        self.assertEqual(self.ibx.rendered_keys()['native_name'],
                         u'Native\xa0name')


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()