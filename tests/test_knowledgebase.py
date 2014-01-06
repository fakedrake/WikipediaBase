#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_knowledgebase
----------------------------------

Tests for `knowledgebase` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.knowledgebase import KnowledgeBase
from wikipediabase.provider import Acquirer, Provider


class TestKnowledgebase(unittest.TestCase):
    def setUp(self):
        self.fe = Acquirer()     # A dumb frontend
        self.kb = KnowledgeBase(frontend=self.fe)
        self.att_res = Provider(resources={'status': lambda art,attr: "unknown"},
                                acquirer=self.kb.resolvers_acquirer)

    def test_get(self):
        self.assertEquals(self.fe.resources()['get'], self.kb.get)

    def test_get_attributes(self):
        self.assertIn("birth-date",
                      self.fe.resources()['get-attributes']("wikipedia-person", "Bill Clinton"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
