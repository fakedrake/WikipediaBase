#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_util
----------------------------------

Tests for `util` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import util
from wikipediabase.infobox import Infobox
from wikipediabase.article import Article

class TestUtil(unittest.TestCase):

    def setUp(self):
        self.symbol = "Led Zeppelin"

    def test_infobox(self):
        ibx = Infobox(self.symbol)
        self.assertIs(Infobox, type(util.get_infobox(self.symbol)))
        self.assertIs(Infobox, type(util.get_infobox(ibx)))

    def test_article(self):
        art = Article(self.symbol)
        self.assertIs(Article, type(util.get_article(self.symbol)))
        self.assertIs(Article, type(util.get_article(art)))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
