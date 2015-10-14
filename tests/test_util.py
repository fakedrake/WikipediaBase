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
from wikipediabase.infobox import Infobox, InfoboxScraper
from wikipediabase.article import Article


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.symbol = "Led Zeppelin"

    def test_fromstringtotext(self):
        self.assertEqual(util.totext(util.fromstring("hello<br/>")), "hello")
        self.assertEqual(util.totext(util.fromstring("<br/>", True)), "\n")

    def test_infoboxes(self):
        c = InfoboxScraper(self.symbol)
        self.assertIs(list, type(util.get_infoboxes(self.symbol)))
        self.assertIs(Infobox, type(util.get_infoboxes(self.symbol)[0]))
        self.assertIs(list, type(util.get_infoboxes(c)))

    def test_article(self):
        art = Article(self.symbol)
        self.assertIs(Article, type(util.get_article(self.symbol)))
        self.assertIs(Article, type(util.get_article(art)))

    side = 1
    def test_memoized(self):
        @util.memoized
        def side_effect(dc):
            self.side += 1
            return self.side + 2

        self.assertEqual(side_effect(1), 4)
        # Should have been 5 if not memoized
        self.assertEqual(side_effect(1), 4)
        # Also nothng was called so side should remain the same
        self.assertEqual(self.side, 2)

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
