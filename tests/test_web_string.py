#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_web_string
----------------------------------

Tests for `web_string` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import web_string
from wikipediabase.config import configuration
from wikipediabase import settings

class TestWebString(unittest.TestCase):

    def setUp(self):
        pass

    def test_lxml_string(self):
        lxmlstr = web_string.LxmlString('<a><b id="bid">b body</b> after b</a>')
        self.assertEqual(lxmlstr.raw(), '<a><b id="bid">b body</b> after b</a>')
        self.assertEqual(lxmlstr.text(), "b body after b")
        self.assertEqual([e.text() for e in lxmlstr.xpath(".//*[@id='bid']")],
                         ["b body"])

    def test_url_string(self):
        example_url = web_string.UrlString.from_url("example.com/title/a_title")
        title_url = web_string.UrlString.from_url("example.com/title?title=b_title")
        edit_url = web_string.UrlString.from_url("example.com/title?title=b_title&action=edit")
        edit_notitle_url = web_string.UrlString.from_url("example.com/title?action=edit")
        cfg = configuration.child()
        cfg.ref.remote.url = "example.com"
        cfg.ref.remote.base = "base/index.php"
        symbol_url = web_string.UrlString('sym', cfg)
        self.assertEqual(symbol_url.raw(),
                         "example.com/base/index.php?action=edit&title=sym")
        self.assertEqual(str(example_url.symbol()), "a title")
        self.assertEqual(str(title_url.symbol()), "b title")
        self.assertEqual(str(edit_url.symbol()), "b title")
        self.assertEqual(edit_url.edit, True)

    def test_symbol_string(self):
        sym = web_string.SymbolString('The Beatles')
        url = web_string.SymbolString('the Beatles')
        self.assertEqual(sym.reduced(), 'beatles')
        self.assertEqual(sym.url_friendly(), 'the_beatles')
        self.assertEqual(sym.literal(), 'The Beatles')
        self.assertEqual(url.literal(), 'the Beatles')

        cfg = configuration.child()
        cfg.ref.remote.url = "example.com"
        cfg.ref.remote.base = "base/index.php"
        self.assertEqual(url.url(configuration=cfg).raw(),
                         "example.com/base/index.php?title=the_beatles")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
