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
        self.assertEqual(RxExpr("a", "b", " ", name="yes").render(), "(?P<yes>a b)")
        self.assertEqual(RxExpr(rx, rx_rename, " ", name="yes").render(),
                         "(?P<yes>rx_original (?P<name>rx_original))")

    def test_concat(self):
        self.assertEqual(ConcatRx("a", "b", "c", "d").render(), "abcd")
        self.assertEqual((Regex("a", name="first") + "b" + "c").render(),
                         "(?P<first>a)bc")

        rx = Regex("some_regex", name="rx1")

        self.assertEqual((rx+"a"+"b"+Regex("c", name="rx1")).render(),
                         "some_regexab(?P<rx1>c)")

    def test_or(self):
        self.assertEqual(OrRx("a", "b", "c").render(), "(a|b|c)")
        self.assertEqual(OrRx("a").render(), "(a)")
        self.assertEqual(OrRx("a", "b", name="or").render(), "(?P<or>a|b)")
        self.assertEqual((Regex("a", name="alpha") | "b").render(),
                         "((?P<alpha>a)|b)")

    def test_name_tree(self):
        rx = Regex("\d+", name="num")
        ext_rx = ConcatRx("[+-]",rx, name="num")
        self.assertEqual(rx.render(), r"(?P<num>\d+)")
        self.assertEqual(ext_rx.render(), r"(?P<num>[+-]\d+)")

    def test_matching(self):
        rx = Regex("\d+", name="num")
        self.assertEqual(rx.match("1992", name="num"), "1992")
        self.assertEqual(rx.match("1992").groups("num"), ("1992",))
        self.assertEqual(rx.match("a1992"), None)
        self.assertRaises(IndexError, lambda : rx.match("1992", name="num2"))

    def test_search(self):
        rx = Regex("\d+", name="num")
        self.assertEqual(rx.search("1992", name="num"), "1992")
        self.assertEqual(rx.search("1992").groups("num"), ("1992",))
        self.assertEqual(rx.search("a1992").groups("num"), ("1992",))
        self.assertRaises(IndexError, lambda : rx.search("1992", name="num2"))

    def test_flags(self):
        rx = Regex("july", flags='i', name="m")

        self.assertEqual(rx.render(), '(?P<m>(?i)july)')
        self.assertEqual(rx.match("July", name="m"), "July")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
