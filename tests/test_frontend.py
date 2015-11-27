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

from .common import testcfg
from wikipediabase.provider import Provider
from wikipediabase.frontend import Frontend


def get_attribute(x, y):
    return "%s of '%s'" % (str(repr(y)), str(x))


class TestFrontend(unittest.TestCase):

    def setUp(self):
        self.fakekb = Provider(resources={"get": get_attribute})
        self.cfg = testcfg.child({'knowledgebase': self.fakekb}).freeze()
        self.simple_fe = Frontend(self.cfg)
        self.fe = Frontend(configuration=testcfg)

    def test_simple(self):
        self.assertEqual(str(self.simple_fe.eval("(get \"article\" words)")),
                         str("Symbol(words) of 'article'"))

    def test_unicode(self):
        date = self.fe.eval(
            '(get "wikipedia-military-conflict" "World War I" (:code "DATE"))')
        self.assertEqual(date, '((:yyyymmdd 19140728))', "Response was: " + date)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
