#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_provider
----------------------------------

Tests for `provider` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import common
from wikipediabase.provider import Acquirer, Provider


class TestProvider(unittest.TestCase):

    def setUp(self):
        # WTF: how does knowledge base get in here??
        self.aq = Acquirer()
        self.double = lambda x: 2 * x
        self.prov = Provider(
            resources={"string": "Just a string", "func": self.double},
            acquirer=self.aq)

    def test_provision(self):
        self.assertEqual(
            self.aq.resources(),
            {"string": "Just a string", "func": self.double})

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
