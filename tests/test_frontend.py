#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_frontend
----------------------------------

Tests for `frontend` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.provider import Provider
from wikipediabase.frontend import Frontend


def get_attribute(x, y):
    return "%s of %s" % (repr(y), repr(x))


class TestFrontend(unittest.TestCase):

    def setUp(self):
        self.simple_fe = Frontend(providers=[Provider(
            resources={"get": get_attribute})])
        self.fe = Frontend()

    def test_simple(self):
        self.assertEqual(self.simple_fe.eval("(get \"article\" words)"),
                         "Symbol(words) of 'article'")

    def test_unicode(self):
        date = self.fe.eval(
            '(get "wikipedia-military-conflict" "World War I" (:code "DATE"))')
        self.assertEqual(date, '((:yyyymmdd 19140728))')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
