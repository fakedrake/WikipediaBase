#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_symbols
----------------------------------

Tests for `symbols` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.symbols import get_synonyms, reverse_comma, clean_synonym, \
    chop_leading_determiners


class TestSymbols(unittest.TestCase):

    def test_chop_leading_determiners(self):
        self.assertEquals('Symbol', chop_leading_determiners('A Symbol'))
        self.assertEquals('Park', chop_leading_determiners('The Park'))
        self.assertEquals('Animal', chop_leading_determiners('An Animal'))
        self.assertEquals('person', chop_leading_determiners('a person'))

    def test_clean_possesive(self):
        self.assertEquals('John', clean_synonym("John's"))

    def test_reverse_comma(self):
        self.assertEquals('the Golden ratio',
                          reverse_comma('Golden ratio, the'))
        self.assertEquals('a Symbol', reverse_comma('Symbol, a'))
        self.assertEquals('an Animal', reverse_comma('Animal, an'))

    def test_reverse_comma_case_insensitive(self):
        self.assertEquals('Democratic Republic Of The Congo',
                          reverse_comma('Congo, Democratic Republic Of The'))

    def test_synonyms_parens(self):
        symbol = 'A Bill (law)'
        expected = ['Bill (law)', 'Bill']
        self.assertEquals(expected, get_synonyms(symbol))

    def test_synonyms_from_empty_symbol(self):
        self.assertEquals([], get_synonyms('  '))

    def test_synonyms(self):
        symbol = 'Complicated & complex (movie), a'
        expected = ['Complicated & complex (movie)', 'Complicated & complex']
        self.assertEquals(expected, get_synonyms(symbol))
