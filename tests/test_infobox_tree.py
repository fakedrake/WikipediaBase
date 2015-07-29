#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox_tree
----------------------------------

Tests for `infobox_tree` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import infobox_tree
from .common import read_data

MU = read_data("dummy_ibox_tree.txt")


class TestInfoboxTree(unittest.TestCase):

    def setUp(self):
        pass

    def test_ibx_tree(self):
        tree = infobox_tree.ibx_tree(MU, ["Artsy stuff"])
        self.assertIn("award", tree[0])
        self.assertIn("Artsy stuff", tree[0][1])
        self.assertEqual(len(tree[1][1]), 4, msg=tree[0])
        self.assertEqual(len(tree[0][1]), 3, msg=",".join(tree[0][1]))

    def test_ibx_type_tree(self):
        tree = infobox_tree.ibx_type_tree()
        self.assertEqual(
            len(tree['California State Legislature district']),
            3,
            msg=repr(tree['California State Legislature district'])
        )
        self.assertNotIn("party", tree["state gun laws"])
        self.assertIn(u'Other politics and government', tree["state gun laws"])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
