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
from wikipediabase import persistentkv as pkv

DATABASE = "/tmp/remove-me.db"

class TestPersistentkv(unittest.TestCase):

    def setUp(self):
        pass

    def test_non_persist(self):
        ps = pkv.PersistentDict(DATABASE)
        ps['hello'] = "yes"
        ps["bye"] = "no"
        ps['\xe2\x98\x83snowman'.decode('utf8')] = "well"
        self.assertEqual(ps['hello'], "yes")
        self.assertEqual(ps['bye'], "no")
        del ps

        # Test persistence
        ps = pkv.PersistentDict(DATABASE)
        self.assertEqual(ps['hello'], "yes")
        self.assertEqual(ps['bye'], "no")
        self.assertEqual(ps['\xe2\x98\x83snowman'.decode('utf8')], "well")
        del ps

        # Test file dependency
        os.remove(DATABASE)
        ps = pkv.PersistentDict(DATABASE)
        with self.assertRaises(KeyError):
            bo = ps['hello'] == "yes"

    def tearDown(self):
        os.remove(DATABASE)

if __name__ == '__main__':
    unittest.main()
