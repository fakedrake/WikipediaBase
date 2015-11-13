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
from wikipediabase.lispify import LispList

# TODO: update when issue with rendered attributes is fixed, see #70
CLINTON_ATTRS = (
    '(:code "ALMA-MATER" :rendered "Alma mater")',
    '(:code "BIRTH-DATE" :rendered "Born")',
    '(:code "BIRTH-NAME" :rendered "Born")',
    '(:code "BIRTH-PLACE" :rendered "Born")',
    '(:code "CHILDREN" :rendered "Children")',
    '(:code "GOVERNOR3" :rendered "Governor")',
    '(:code "IMAGE")',
    '(:code "LIEUTENANT1" :rendered "Lieutenant")',
    '(:code "LIEUTENANT2" :rendered "Lieutenant")',
    '(:code "NAME")',
    '(:code "OFFICE")',
    '(:code "OFFICE1")',
    '(:code "OFFICE3")',
    '(:code "ORDER")',
    '(:code "ORDER1")',
    '(:code "ORDER3")',
    '(:code "PARENTS" :rendered "Parents")',
    '(:code "PARTY" :rendered "Political party")',
    '(:code "PREDECESSOR" :rendered "Preceded by")',
    '(:code "PREDECESSOR1" :rendered "Preceded by")',
    '(:code "PREDECESSOR2" :rendered "Preceded by")',
    '(:code "PREDECESSOR3" :rendered "Preceded by")',
    '(:code "PROFESSION" :rendered "Profession")',
    '(:code "RELATIONS" :rendered "Relations")',
    '(:code "RELIGION" :rendered "Religion")',
    '(:code "SIGNATURE")',
    '(:code "SIGNATURE-ALT")',
    '(:code "SPOUSE" :rendered "Spouse(s)")',
    '(:code "SUCCESSOR" :rendered "Succeeded by")',
    '(:code "SUCCESSOR1" :rendered "Succeeded by")',
    '(:code "SUCCESSOR2" :rendered "Succeeded by")',
    '(:code "SUCCESSOR3" :rendered "Succeeded by")',
    '(:code "TERM-END")',
    '(:code "TERM-END1")',
    '(:code "TERM-END2")',
    '(:code "TERM-END3")',
    '(:code "TERM-START")',
    '(:code "TERM-START1")',
    '(:code "TERM-START2")',
    '(:code "TERM-START3")',
    '(:code "VICEPRESIDENT" :rendered "Vice President")',
)


class TestKnowledgebase(unittest.TestCase):

    def setUp(self):
        self.fe = Acquirer()     # A dumb frontend
        self.kb = KnowledgeBase(frontend=self.fe)

    def test_get(self):
        self.assertEquals(self.fe.resources()['get'], self.kb.get)

    def test_get_attributes(self):
        attrs = self.fe.resources()['get-attributes']("wikipedia-president",
                                                      "Bill Clinton")
        for a in CLINTON_ATTRS:
            self.assertIn(a, attrs)

    def test_get_classes(self):
        self.assertIn("wikipedia-president",
                      str(self.fe.resources()['get-classes']("Bill Clinton")))
        # The list gets iterated and memoization fails.
        self.assertIn("wikipedia-president",
                      str(self.fe.resources()['get-classes']("Bill Clinton")),
                      "Second time failed. Memoization problem")

    def test_sort_symbols(self):
        ench = self.fe.resources()['sort-symbols']("Mary Shakespeare", "Batman")
        self.assertIs(type(ench), LispList)
        self.assertEqual(ench.val, ["Batman", "Mary Shakespeare"])

if __name__ == '__main__':
    unittest.main()
