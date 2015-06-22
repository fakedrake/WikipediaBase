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

import common
from wikipediabase.knowledgebase import KnowledgeBase
from wikipediabase.provider import Acquirer, Provider
from wikipediabase.enchantments import EnchantedList

CLINTON_ATTRS = (
u'(:code "NAME"', u':code "IMAGE"', u':code "ORDER"', u':code "OFFICE"', u':code "VICEPRESIDENT"', u':code "TERM-START"', u':code "TERM-END"', u':code "PREDECESSOR"', u':code "SUCCESSOR"', u':code "ORDER1"', u':code "OFFICE1"', u':code "LIEUTENANT1"', u':code "TERM-START1"', u':code "TERM-END1"', u':code "PREDECESSOR1"', u':code "SUCCESSOR1"', u':code "LIEUTENANT2"', u':code "TERM-START2"', u':code "TERM-END2"', u':code "PREDECESSOR2"', u':code "SUCCESSOR2"', u':code "ORDER3"', u':code "OFFICE3"', u':code "GOVERNOR3"', u':code "TERM-START3"', u':code "TERM-END3"', u':code "PREDECESSOR3"', u':code "SUCCESSOR3"', u':code "BIRTH-NAME"', u':code "BIRTH-DATE"', u':code "BIRTH-PLACE"', u':code "DEATH-DATE" :rendered "Died"', u':code "DEATH-PLACE"', u':code "PARTY" :rendered "Political party"', u':code "PARENTS" :rendered "Parents"', u':code "RELATIONS" :rendered "Relations"', u':code "SPOUSE" :rendered "Spouse(s)"', u':code "CHILDREN" :rendered "Children"', u':code "ALMA-MATER"', u':code "RELIGION" :rendered "Religion"', u':code "SIGNATURE"', u':code "SIGNATURE-ALT")')
# Ommited based on content:
# u':code "PROFESSION" :rendered "Profession"'

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
        result_attrs = self.fe.resources()['get-attributes']("Bill Clinton")

        for a in CLINTON_ATTRS:
            self.assertIn(a, result_attrs)

    def test_classes(self):
        self.assertIn("wikipedia-president",
                      str(self.fe.resources()['get-classes']("Bill Clinton")))
        # The list gets iterated and memoization fails.
        self.assertIn("wikipedia-president",
                      str(self.fe.resources()['get-classes']("Bill Clinton")),
                      "Secnd time failed. Memoization problem")


    def test_sort_symbols(self):
        ench = self.fe.resources()['sort-symbols']("Mary Shakespeare", "Batman")
        self.assertIs(type(ench), EnchantedList)
        self.assertEqual(ench.val, ["Batman", "Mary Shakespeare"])

    def test_synonyms(self):
        self.assertIn("batman", self.kb.synonyms("bat man"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
