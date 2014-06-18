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

    def test_paren(self):
        txt = "Hello (dr. hello 2000-2012) I like bananas. Of couse i do (they are the begist)"

        # First paren will stop at the first sentence.
        txt_none = "Hello. My name is Bond (James Bond)"
        self.assertEqual(util.first_paren(txt), "dr. hello 2000-2012")
        self.assertIs(util.first_paren(txt_none), None)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
