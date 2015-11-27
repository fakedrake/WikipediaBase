#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_persistentkv
----------------------------------

Tests for `persistentkv` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os
import common
from wikipediabase import persistentkv as pkv

DATABASE = "/tmp/remove-me.db"

class TestPersistentkv(unittest.TestCase):

    def setUp(self):
        pass

    def test_non_persist(self):
        ps = pkv.DbmPersistentDict(DATABASE)
        ps['hello'] = "yes"
        ps["bye"] = "no"
        ps['\xe2\x98\x83snowman'.decode('utf8')] = "well"
        self.assertEqual(ps['hello'], "yes")
        self.assertEqual(ps['bye'], "no")
        del ps

        # Test persistence
        ps = pkv.DbmPersistentDict(DATABASE)
        self.assertEqual(ps['hello'], "yes")
        self.assertEqual(ps['bye'], "no")
        self.assertEqual(ps['\xe2\x98\x83snowman'.decode('utf8')], "well")
        del ps

        # Test file dependency
        pkv.DbmPersistentDict(DATABASE).remove_db()
        ps = pkv.DbmPersistentDict(DATABASE)
        with self.assertRaises(KeyError):
            self.assertNotEqual(ps['test'], "yes")

        with self.assertRaises(KeyError):
            self.assertNotEqual(ps['hello'], "yes")

    def internal_test_database(self, pkv_type, filename):
        # TODO:
        # Create a dbm database with a config pointing to data
        # Check that the file was created.
        # Destroy and reopen and see that the values were kept
        # Call this from test_* functions to test
        pass

    def tearDown(self):
        pkv.DbmPersistentDict(DATABASE).remove_db()

if __name__ == '__main__':
    unittest.main()
