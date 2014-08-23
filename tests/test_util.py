#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_util
----------------------------------

Tests for `util` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime


from wikipediabase import util
from wikipediabase.infobox import Infobox
from wikipediabase.article import Article


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.symbol = "Led Zeppelin"
        self.side = 0


    def test_infobox(self):
        ibx = Infobox(self.symbol)
        self.assertIs(Infobox, type(util.get_infobox(self.symbol)))
        self.assertIs(Infobox, type(util.get_infobox(ibx)))

    def test_memoizer(self):
        @util.memoized
        def side_effect(a, b=1):
            self.side += 1
            return a*b

        side_effect(1)
        self.assertEqual(self.side, 1)
        side_effect(1)
        self.assertEqual(self.side, 1)
        side_effect(2)
        self.assertEqual(self.side, 2)
        self.assertEqual(side_effect(1), 1)
        self.assertEqual(side_effect(2), 2)
        self.assertEqual(side_effect(2, b=2), 4)
        self.assertEqual(side_effect(2, 3), 6)

    def test_memoized_method(self):
        class A(object):
            def __init__(self, a):
                self.a = a

            @util.memoized
            def sf(self, b):
                return self.a + b

        a = A(1)
        self.assertEqual(a.sf(3), 4)
        b = A(2)
        self.assertEqual(b.sf(3), 5)


    def test_article(self):
        art = Article(self.symbol)
        self.assertIs(Article, type(util.get_article(self.symbol)))
        self.assertIs(Article, type(util.get_article(art)))

    def test_interval(self):
        class DateTime(datetime.datetime):
            x = 0

            @classmethod
            def now(cls):
                return cls.x

        datetime.datetime = DateTime

        util.time_interval("now")
        for i in xrange(20):
            # Increment time between calls
            DateTime.x += 1
            self.assertEqual(util.time_interval("now"), 1)

    def test_html(self):
        html = "<html> <body><p>yes</p> <p> hi</p> <img/> </body> </html>"
        el = util.fromstring(html)
        self.assertEqual("yes  hi", util.totext(el).strip())
        self.assertIn("<p>", util.tostring(el))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
