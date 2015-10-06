#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_classifiers
----------------------------------

Tests for `classifiers` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import classifiers as cls


class TestClassifiers(unittest.TestCase):

    def test_person(self):
        c = cls.PersonClassifier()
        self.assertIn('wikibase-person', c('Bill Clinton'))
        self.assertIn('wikibase-person', c('Mary Shakespeare'))
        self.assertNotIn('wikibase-person', c('Harvard University'))

    def test_term(self):
        c = cls.TermClassifier()
        self.assertEquals(c('Bill Clinton'), ['wikibase-term'])
        self.assertEquals(c('Harvard University'), ['wikibase-term'])

    def test_sections(self):
        c = cls.SectionsClassifier()
        self.assertEquals(c('Bill Clinton'), ['wikibase-sections'])
        self.assertEquals(c('Harvard University'), ['wikibase-sections'])

if __name__ == '__main__':
    unittest.main()
