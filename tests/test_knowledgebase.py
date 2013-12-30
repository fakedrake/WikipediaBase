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

from wikipediabasepy.knowledgebase import KnowledgeBase
from wikipediabasepy.provider import Aquirer, Provider


class TestKnowledgebase(unittest.TestCase):
    def setUp(self):
        self.fe = Aquirer()     # A dumb frontend
        self.kb = KnowledgeBase(frontend=self.fe)
        self.att_res = Provider(resources={'status': lambda art,attr: "unknown"},
                                aquirer=self.kb.resolvers_aquirer)

    def test_get(self):
        self.assertEquals(self.fe.resources()['get'], self.kb.get)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
