#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dateutil
----------------------------------

Tests for `dateutil` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.dateutil import *

class TestDateutil(unittest.TestCase):

    def setUp(self):
        pass

    def test_day(self):
        self.assertEqual(day('22'), 22)
        self.assertEqual(day('07'), 7)
        self.assertEqual(day('7'), 7)

    def test_month(self):
        self.assertEqual(month("July"), 7)
        self.assertEqual(month("Jul"), 7)
        self.assertEqual(month("7"), 7)
        self.assertEqual(month("07"), 7)

    def test_year(self):
        self.assertEqual(year("1991"), 1991)
        self.assertEqual(year('7 AD'), 7)
        self.assertEqual(year('8  B.c.'), 8)

    def test_dates(self):
        self.assertEqual(next(parse("22/7/1991")), (22, 7, 1991))
        self.assertEqual(next(parse("22 July 1991")), (22, 7, 1991))
        self.assertEqual(next(parse("22nd of July 1991")), (22, 7, 1991))
        self.assertEqual(next(parse("July 22nd 1991")), (22, 7, 1991))
        self.assertEqual(next(parse("07|22|1991")), (22, 7, 1991))
        self.assertEqual(next(parse("1991")), (0, 0, 1991))
        self.assertEqual(next(parse("199 BC")), (0, 0, -199))

    def test_multiple_dates(self):
        self.assertEqual(list(parse("22/7/1991")), [(22, 7, 1991)])
        self.assertEqual(list(parse("1100 22 july 1991")),
                         [(22, 7, 1991), (0, 0, 1100)])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
