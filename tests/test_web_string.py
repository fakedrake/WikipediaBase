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

import re
from wikipediabase import web_string
from common import testcfg
from wikipediabase import settings

class TestWebString(unittest.TestCase):

    def setUp(self):
        pass

    def test_lxml_string(self):
        lxmlstr = web_string.LxmlString('<a attr="val"><b id="bid">b body</b> after b</a>')
        self.assertEqual(lxmlstr.raw(), '<a attr="val"><b id="bid">b body</b> after b</a>')
        self.assertEqual(lxmlstr.text(), "b body after b")
        self.assertEqual(lxmlstr.get('attr'), "val")
        self.assertEqual(lxmlstr.get('attr1'), None)
        self.assertEqual(lxmlstr.get('attr1', "default"), "default")
        self.assertEqual([e.text() for e in lxmlstr.xpath(".//*[@id='bid']")],
                         ["b body"])
        self.assertEqual(lxmlstr.ignoring(['b']).text(),
                         '<b id="bid">b body</b> after b')

    def test_ignoring_xpath(self):
        lxmlstr = web_string.LxmlString('<a><b>b body<c>c body</c></b></a>')
        # Find results of ignoring should still ignore
        self.assertEqual(next(lxmlstr.ignoring(['c']).xpath('.//b')).text(),
                         'b body<c>c body</c>')
        self.assertEqual(next(lxmlstr.xpath('.//b')).text(),
                         'b bodyc body')

    def test_url_string(self):
        example_url = web_string.UrlString.from_url("example.com/title/a_title")
        title_url = web_string.UrlString.from_url("example.com/title?title=b_title")
        edit_url = web_string.UrlString.from_url("example.com/title?title=b_title&action=edit")
        edit_notitle_url = web_string.UrlString.from_url("example.com/title?action=edit")
        cfg = testcfg.child()
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
        pres = web_string.SymbolString('Template:Infobox president')
        self.assertEqual(sym.synonym().raw(), 'The_Beatles')
        self.assertEqual(sym.reduced(), 'beatles')
        self.assertEqual(sym.url_friendly(), 'The_Beatles')
        self.assertEqual(sym.literal(), 'The Beatles')
        self.assertEqual(url.literal(), 'the Beatles')

        cfg = testcfg.child()
        cfg.ref.remote.url = "example.com"
        cfg.ref.remote.base = "base/index.php"
        self.assertEqual(url.url(configuration=cfg).raw(),
                         "example.com/base/index.php?title=the_Beatles")

    def test_markup_redirect(self):
        markup = web_string.MarkupString('  #redirect [[redirect target]]  \n')
        self.assertEqual(markup.redirect_target().url_friendly(), "redirect_target")
        markup = web_string.MarkupString('#REDIRECT[[redirect target]]')
        self.assertEqual(markup.redirect_target().url_friendly(), "redirect_target")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
