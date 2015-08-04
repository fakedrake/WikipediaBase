#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_settings
----------------------------------

Tests for `settings` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import settings

class TestSettings(unittest.TestCase):

    def setUp(self):
        pass

    def test_keys_exist(self):
        # These are supposed to be changing without breaking the test
        # but make sure they are set
        self.assertEqual(settings.configuration['cache']['rendered_pages'],
                         'rendered')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
