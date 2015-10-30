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


class TestLRUCache(unittest.TestCase):

    def test_set_and_get(self):
        cache = util.LRUCache(1)
        cache.set('a', 'foo')
        self.assertEquals(cache.get('a'), 'foo')

    def test_lru(self):
        cache = util.LRUCache(2)
        cache.set('a', 'foo')
        cache.set('b', 'bar')

        # look into the cache to get the lru item
        self.assertEquals('b', cache.cache.keys()[-1])

        cache.get('a')
        self.assertEquals('a', cache.cache.keys()[-1])

    def test_pop_lru_item(self):
        cache = util.LRUCache(3)
        cache.set(1, 'a')
        cache.set(2, 'b')
        cache.set(3, 'c')
        cache.set(4, 'd')
        cache.set(5, 'e')
        cache.set(6, 'f')
        cache.set(7, 'g')

        self.assertEqual(3, len(cache.cache))
        self.assertRaises(KeyError, cache.get, 1)
        self.assertEqual('g', cache.get(7))


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.symbol = "Led Zeppelin"

    def test_fromstringtotext(self):
        self.assertEqual(util.totext(util.fromstring("hello<br/>")), "hello")
        self.assertEqual(util.totext(util.fromstring("<br/>", True)), "\n")

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

if __name__ == '__main__':
    unittest.main()
