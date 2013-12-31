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

from wikipediabasepy.provider import Provider
from wikipediabasepy.frontend import Frontend


def get_attribute(x, y):
    return "%s of %s" % (repr(y), repr(x))

class TestFrontend(unittest.TestCase):

    def setUp(self):
        self.simple_fe = Frontend(providers=[Provider(
            resources={"get": get_attribute})])

    def test_simple(self):
        self.assertEqual(self.simple_fe.eval("(get \"article\" words)"),
                         "Symbol(words) of 'article'")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
