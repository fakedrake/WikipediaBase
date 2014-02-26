#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rxdates
----------------------------------

Tests for `rxdates` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import rxdates

class TestRxdates(unittest.TestCase):

    def setUp(self):
        pass

    def test_months(self):
        self.assertEqual(MONTH_NAMES.search("22 jun", name="month", flags=re.I), 'jun')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
