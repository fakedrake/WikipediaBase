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

from common import testcfg
from wikipediabase import classifiers as cls


class TestClassifiers(unittest.TestCase):

    def setUp(self):
        pass

    def test_person(self):
        c = cls.PersonClassifier(testcfg)
        self.assertIn('wikipedia-person', c('Bill Clinton'))
        self.assertIn('wikipedia-male', c('Bill Clinton'))
        self.assertIn('wikipedia-person', c('Mary Shakespeare'))
        self.assertIn('wikipedia-female', c('Mary Shakespeare'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
