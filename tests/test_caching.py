#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_caching
----------------------------------

Tests for `caching` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import caching
from wikipediabase.settings import configuration

class TestCaching(unittest.TestCase):

    def setUp(self):
        class A(caching.Caching):
            def __init__(self, a, b, configuration=configuration):
                super(A, self).__init__(configuration=configuration)
                self.a = a
                self.b = b
                self.cached_calls = 0

            @caching.cached('a', 'b')
            def cachedmethod(self, attr):
                self.cached_calls += 1
                return "hello"

        self.cfg = configuration.child()
        self.cfg.ref.cache.cache_manager = caching.DictCacheManager()
        self.CachingClass = A

    def test_dict(self):
        a = self.CachingClass(1,2, self.cfg)
        self.assertEqual(a.cached_calls, 0)
        self.assertEqual(a.cachedmethod(1), "hello")
        self.assertEqual(a.cached_calls, 1, "First call")

        self.assertEqual(a.cachedmethod(1), "hello")
        self.assertEqual(a.cached_calls, 1, "Cached call")

        self.assertEqual(a.cachedmethod(2), "hello")
        self.assertEqual(a.cached_calls, 2, "Changed arguments")

        a.a = 1
        self.assertEqual(a.cachedmethod(2), "hello")
        self.assertEqual(a.cached_calls, 2, "Unchanged internal state")

        a.b = 1
        self.assertEqual(a.cachedmethod(2), "hello")
        self.assertEqual(a.cached_calls, 3, "Changed internal state")

        a.b = 1
        self.assertEqual(a.cachedmethod(2), "hello")
        self.assertEqual(a.cached_calls, 3, "Unchanged internal state again")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
