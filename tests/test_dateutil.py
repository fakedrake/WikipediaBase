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

class TestDateUtil(unittest.TestCase):

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
        self.assertEqual(parse("22/7/1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("22 July 1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("22nd of July 1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse(" July the 22nd 1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("July 22nd 1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("07|22|1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("22|07|1991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("07221991")[0][1], (22, 7, 1991))
        self.assertEqual(parse("1991")[0][1], (0, 0, 1991))
        self.assertEqual(parse("live in 1991")[0][1], (0, 0, 1991))
        self.assertEqual(parse("199 BC")[0][1], (0, 0, -199))
        self.assertEqual(parse("January 2005")[0][1], (0, 1, 2005))
        self.assertEqual(parse("January, 2005")[0][1], (0, 1, 2005))
        self.assertEqual(parse("January of 2005")[0][1], (0, 1, 2005))

    def test_multiple_dates(self):
        self.assertIn((22, 7, 1991), parse("1991 22/7/1991")[0])
        self.assertIn((0, 0, 1991), parse("22/7/1991 1991")[1])

        # 22 july 1991 is more probable date that's why we expect to see it first
        self.assertIn((22, 7, 1991), list(parse("1100 22 july 1991"))[0])

    def test_favor(self):
        d = dict([(d,w) for w,d in parse("16 Jul 1991 17 March 1992",
                                         favor='end')])
        self.assertGreater(d[(17, 3, 1992)], d[(16, 7, 1991)])

    def test_almost_overlap(self):
        self.assertEqual(parse("|1991|09|25|1913|10|25", favor='start')[0][1], (25, 9, 1991))

    def test_parsed_obj(self):
        txt = "I was born in 22.7.1991, That means i have lived 1991 - 2014 and also 1998 to 2010 was a golden era"
        po = DateParsed(parse(txt, yield_position=True), txt)

        self.assertEqual(po.dates(ratings=False), [(22, 7, 1991),
                                                   (0, 0, 1991),
                                                   (0, 0, 2014),
                                                   (0, 0, 1998),
                                                   (0, 0, 2010)])
        self.assertEqual(len(po.dategroups()), 2)
        self.assertEqual(po.dategroups(ratings=False)[0][1],
                         [(0, 0, 1991), (0, 0, 2014)])
        self.assertEqual(po.dategroups(ratings=False)[1][1],
                         [(0, 0, 1998), (0, 0, 2010)])

        self.assertEqual(po.dategroups(ratings=False, grp_yield_position=True)[1][0],
                        (70, 82))

    def test_ranges(self):
        txt = "lives 22.7.1991-"
        po = DateParsed(parse(txt, yield_position=True), txt)
        self.assertIn([(22, 7, 1991), (0, 0, 0)], po.dategroups(ratings=False)[0])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
