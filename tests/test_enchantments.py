#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_enchantments
----------------------------------

Tests for `enchantments` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import enchantments

class TestEnchantments(unittest.TestCase):

    def setUp(self):
        pass

    def test_date_simple(self):
        ed = enchantments.EnchantedDate("yyyymmdd", "coming on August the 8th")
        self.assertEqual(ed.val, (8,8,0))

    def test_date_multiple_voting(self):
        ed = enchantments.EnchantedDateVoting("yyyymmdd", "2010 8.8.1991 on August the 8th 1991")
        self.assertEqual(ed.val, (8,8,1991))

    def test_date_with_rng(self):
        # 2010 is in te given range, thus it wil prescede 8,8,1991
        ed = enchantments.EnchantedDate("yyyymmdd", "2010 8.9.1991 - 2012 on August the 8th 1991")
        self.assertEqual(ed.val, (0,0,2010))

    def test_bool(self):
        self.assertEqual(str(enchantments.enchant(None, True)), '#t')
        self.assertEqual(str(enchantments.enchant(None, False)), '#f')
        self.assertEqual(str(enchantments.enchant('dont matter', False)), '#f')

    def test_keyword(self):
        ret = str(enchantments.enchant(":key", None))
        self.assertEqual(ret, ":key")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
