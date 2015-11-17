#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox
----------------------------------

Tests for sort-symbols and sort-symbols-named
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.sort_symbols import sort_by_length, sort_named


class TestSortSymbols(unittest.TestCase):

    def test_sort_cake(self):
        symbols = ["Cake (TV series)", "Cake (firework)", "Cake (2005 film)",
                   "Cake", "Cake (band)", "Cake (advertisement)", "The Cake"]

        expected = ["Cake (band)", "Cake (advertisement)", "Cake",
                    "Cake (TV series)", "The Cake", "Cake (2005 film)",
                    "Cake (firework)"]

        self.assertEquals(expected, sort_by_length(*symbols))

    def test_sort_obama(self):
        symbols = ["Obama (surname)", "Barack Obama"]
        expected = ["Barack Obama", "Obama (surname)"]
        self.assertEquals(expected, sort_by_length(*symbols))


class TestSortSymbolsNamed(unittest.TestCase):

    def test_cake(self):
        symbols = ["Cake (TV series)", "Cake (firework)", "Cake (2005 film)",
                   "Cake", "Cake (band)", "Cake (advertisement)", "The Cake"]

        expected = ["Cake", "Cake (band)", "Cake (advertisement)",
                    "Cake (TV series)", "The Cake", "Cake (2005 film)",
                    "Cake (firework)"]

        self.assertEquals(expected, sort_named("cake", *symbols))
