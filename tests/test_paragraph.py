#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_paragraph
----------------------------------

Tests for `paragraph` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import wikipediabase


class TestParagraph(unittest.TestCase):

    def setUp(self):
        pass

    def test_first_paren(self):
        self.assertEqual(wikipediabase(
            '(get "wikipedia-person" "Mary Shakespeare" "birth-date")'),
            "((:yyyymmdd 15370000))")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
