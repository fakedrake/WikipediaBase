#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rxbuilder
----------------------------------

Tests for `rxbuilder` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.rxbuilder import RxExpr, Regex, ConcatRx, OrRx

class TestRegex(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_concat(self):
        rx  = Regex("rx_original", "name")
        rx_rename = Regex(rx, "name")
        self.assertEqual(RxExpr("a", "b", " ", name="yes").render(), "(?<yes>a b)")
        self.assertEqual(RxExpr(rx, rx_rename, " ", name="yes").render(),
                         "(?<yes>rx_original (?<name>rx_original))")

    def test_concat(self):
        self.assertEqual(ConcatRx("a", "b", "c", "d").render(), "abcd")
        self.assertEqual((Regex("a", name="first") + "b" + "c").render(),
                         "(?<first>a)bc")

        rx = Regex("some_regex", name="rx1")

        self.assertEqual((rx+"a"+"b"+Regex("c", name="rx1")).render(),
                         "some_regexab(?<rx1>c)")

    def test_or(self):
        self.assertEqual(OrRx("a", "b", "c").render(), "(a|b|c)")
        self.assertEqual(OrRx("a", "b", name="or").render(), "(?<or>a|b)")
        self.assertEqual((Regex("a", name="alpha") | "b").render(),
                         "((?<alpha>a)|b)")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
