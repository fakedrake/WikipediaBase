#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_log
----------------------------------

Tests for `log` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os

from wikipediabasepy import log

class TestLog(unittest.TestCase):

    def setUp(self):
        self.log = log.Logger("test.log")

    def test_filelogging(self):
        self.log.info("Information")
        self.log.warning("Warning")
        self.log.error("Error")

        with open("test.log") as fd:
            cntents = fd.read()
            self.assertIn("INFO -         Information", cntents)
            self.assertIn("WARNING -         Warning", cntents)
            self.assertIn("ERROR -         Error", cntents)

    def tearDown(self):
        os.remove("test.log")

if __name__ == '__main__':
    unittest.main()
