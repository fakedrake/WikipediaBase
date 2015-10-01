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
from wikipediabase.provider import Acquirer
from wikipediabase.enchantments import EnchantedList

CLINTON_ATTRS = ('(:code "NAME")', '(:code "IMAGE")', '(:code "ORDER")', '(:code "OFFICE")', '(:code "VICEPRESIDENT" :rendered "Vice President")', '(:code "TERM-START")', '(:code "TERM-END")', '(:code "PREDECESSOR")', '(:code "SUCCESSOR")', '(:code "ORDER1")', '(:code "OFFICE1")', '(:code "LIEUTENANT1")', '(:code "TERM-START1")', '(:code "TERM-END1")', '(:code "PREDECESSOR1")', '(:code "SUCCESSOR1")', '(:code "LIEUTENANT2")', '(:code "TERM-START2")', '(:code "TERM-END2")', '(:code "PREDECESSOR2")', '(:code "SUCCESSOR2")', '(:code "ORDER3")', '(:code "OFFICE3")', '(:code "GOVERNOR3")', '(:code "TERM-START3")', '(:code "TERM-END3")', '(:code "PREDECESSOR3")', '(:code "SUCCESSOR3")', '(:code "BIRTH-NAME" :rendered "Born")', '(:code "BIRTH-DATE" :rendered "Born")', '(:code "BIRTH-PLACE" :rendered "Born")', '(:code "PARTY" :rendered "Political party")', '(:code "PROFESSION" :rendered "Profession")', '(:code "PARENTS" :rendered "Parents")', '(:code "RELATIONS" :rendered "Relations")', '(:code "SPOUSE" :rendered "Spouse(s)', ')', '(:code "CHILDREN" :rendered "Children")', '(:code "ALMA-MATER" :rendered "Alma mater")', '(:code "RELIGION" :rendered "Religion")', '(:code "SIGNATURE")', '(:code "SIGNATURE-ALT")')


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
                      "Second time failed. Memoization problem")

    def test_types(self):
        types = self.fe.resources()['get-types']("Bill Clinton")
        self.assertIn('officeholder', types)
        self.assertIn('president', types)

    def test_categories(self):
        self.assertIn("Presidents of the United States",
                      self.fe.resources()['get-categories']("Bill Clinton"))

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
