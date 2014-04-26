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

import re

from wikipediabase.knowledgebase import KnowledgeBase
from wikipediabase.provider import Acquirer, Provider

CLINTON_ATTRS = \
re.sub("\s+", " ",
       """(:code "NAME") (:code "IMAGE") (:code "ORDER") (:code "OFFICE")
(:code "VICEPRESIDENT") (:code "TERM-START") (:code "TERM-END") (:code
"PREDECESSOR") (:code "SUCCESSOR") (:code "BIRTH-NAME") (:code
"BIRTH-DATE") (:code "BIRTH-PLACE") (:code "DEATH-DATE") (:code
"DEATH-PLACE") (:code "PARTY") (:code "SPOUSE") (:code "CHILDREN")
(:code "ALMA-MATER") (:code "RELIGION") (:code "SIGNATURE") (:code
"SIGNATURE-ALT")""")

class TestKnowledgebase(unittest.TestCase):
    def setUp(self):
        self.fe = Acquirer()     # A dumb frontend
        self.kb = KnowledgeBase(frontend=self.fe)
        self.att_res = Provider(resources={'status': lambda art,attr: "unknown"},
                                acquirer=self.kb.resolvers_acquirer)

    def test_get(self):
        self.assertEquals(self.fe.resources()['get'], self.kb.get)

    def test_get_attributes(self):
        self.assertIn("BIRTH-DATE",
                      self.fe.resources()['get-attributes']("wikipedia-person",
                                                            "Bill Clinton"))

    def test_attributes_format(self):
        self.assertEqual(self.fe.resources()['get-attributes']("Bill Clinton"),
                         CLINTON_ATTRS)

    def test_classes(self):
        self.assertIn("wikipedia-president", str(self.fe.resources()['get-classes']("Bill Clinton")))


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
