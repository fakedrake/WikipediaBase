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
from wikipediabase.enchantments import EnchantedList

CLINTON_ATTRS = \
                re.sub("\s+", " ",
                       """(:code "NAME") (:code "IMAGE") (:code "ORDER") (:code "OFFICE")
(:code "VICEPRESIDENT") (:code "TERM-START") (:code "TERM-END") (:code
"PREDECESSOR") (:code "SUCCESSOR") (:code "BIRTH-NAME") (:code
"BIRTH-DATE") (:code "BIRTH-PLACE") (:code "DEATH-DATE") (:code
"DEATH-PLACE") (:code "PARTY") (:code "SPOUSE") (:code "CHILDREN")
(:code "ALMA-MATER") (:code "RELIGION") (:code "SIGNATURE") (:code
"SIGNATURE-ALT")""")


def _as(atrrs_string):
    """
    Split attributes string so we can compare lists
    """

    return atrrs_string.split(") (")


class TestKnowledgebase(unittest.TestCase):

    def setUp(self):
        self.fe = Acquirer()     # A dumb frontend
        self.kb = KnowledgeBase(frontend=self.fe)

    def test_get(self):
        self.assertEquals(self.fe.resources()['get'], self.kb.get)

    def test_get_attributes(self):
        self.assertIn("BIRTH-DATE",
                      self.fe.resources()['get-attributes']("wikipedia-person",
                                                            "Bill Clinton"))

    def test_attributes_format(self):
        result_attrs = _as(
            self.fe.resources()['get-attributes']("Bill Clinton"))

        for a in _as(CLINTON_ATTRS):
            self.assertIn(a, result_attrs)

    def test_classes(self):
        self.assertIn("wikipedia-president",
                      str(self.fe.resources()['get-classes']("Bill Clinton")))

    def test_sort_symbols(self):
        ench = self.fe.resources()['sort-symbols']("Mary Shakespeare", "Batman")
        self.assertIs(type(ench), EnchantedList)
        self.assertEqual(ench.val, ["Batman", "Mary Shakespeare"])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
