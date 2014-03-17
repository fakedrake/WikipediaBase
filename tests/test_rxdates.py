#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rxdates
----------------------------------

Tests for `rxdates` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import re

from wikipediabase import rxdates as rd
from wikipediabase.rxbuilder import fuzzy_match

class TestRxdates(unittest.TestCase):

    def setUp(self):
        pass

    def test_months(self):
        self.assertEqual(rd.MONTH_NAMES.search("22 jun", name="month", flags=re.I), 'Jun')

    def test_fuzzy_match(self):
        dates = [(i.meta[1], str(i)) for i in fuzzy_match("I shall come on 10|10|2001", rd.DATE_RATINGS)]
        self.assertEqual(dates, str(rd.DMY))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
