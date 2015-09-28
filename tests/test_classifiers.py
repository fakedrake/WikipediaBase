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

import common
from wikipediabase import classifiers as cls


class TestClassifiers(unittest.TestCase):

    def setUp(self):
        pass

    def test_person(self):
        c = cls.PersonClassifier()
        self.assertIn('wikibase-person', c('Bill Clinton'))
        self.assertIn('wikibase-male', c('Bill Clinton'))
        self.assertIn('wikibase-person', c('Mary Shakespeare'))
        self.assertIn('wikibase-female', c('Mary Shakespeare'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
