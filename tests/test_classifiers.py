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

    def test_static(self):
        c = cls.StaticClassifier()
        self.assertItemsEqual(c('Bill Clinton'),
                              ['wikibase-term', 'wikibase-paragraphs'])
        self.assertItemsEqual(c('Massachusetts Institute of Technology'),
                              ['wikibase-term', 'wikibase-paragraphs'])

if __name__ == '__main__':
    unittest.main()
