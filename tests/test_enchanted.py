#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_enchanted
----------------------------------

Tests for `enchanted` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import enchanted

class TestEnchanted(unittest.TestCase):

    def setUp(self):
        pass

    def test_extraction(self):
        self.assertEqual(enchanted.EnchantedDate.extract_date("birth_date", "My birthday 1666 July", result_from="date"), ('yyyymmdd', '16660700'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
