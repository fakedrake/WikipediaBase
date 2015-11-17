#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dbutil
----------------------------------

Tests for `symbols` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.dbutil import extract_redirect


class TestDBUtil(unittest.TestCase):

    def test_redirect(self):
        markup = '\n'.join(['#REDIRECT [[Barack Obama]]',
                            '{{R from full name}}',
                            '{{DEFAULTSORT:Obama, Barack Hussein}}'])
        self.assertEquals('Barack Obama', extract_redirect(markup))
