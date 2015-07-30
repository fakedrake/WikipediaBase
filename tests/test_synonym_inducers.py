#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_synonym_inducers
----------------------------------

Tests for `synonym_inducers` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import synonym_inducers as si


class TestSynonymInducers(unittest.TestCase):

    def setUp(self):
        pass

    def test_reduce(self):
        self.assertEqual(si.string_reduce("An awesome \"thing\""),
                         "awesome thing")

    def test_forward_redirect(self):
        fr = si.ForwardRedirectInducer()
        self.assertIn('barack obama', fr.induce("Barack Hussein Obama"))

    def test_lexical(self):
        fl = si.LexicalInducer()
        self.assertIn('awesome', fl.induce('awesome (singer)'))


if __name__ == '__main__':
    unittest.main()
