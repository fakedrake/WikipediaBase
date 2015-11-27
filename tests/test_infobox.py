#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox
----------------------------------

Tests for `infobox` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from common import testcfg

from wikipediabase.infobox import Infobox
from wikipediabase.util import get_infobox
from wikipediabase import fetcher


class TestInfobox(unittest.TestCase):

    def setUp(self):
        self.ibox = get_infobox("Led Zeppelin", configuration=testcfg)

    def test_getter(self):
        lzi = get_infobox("Led Zeppelin")
        bci = get_infobox("Bill Clinton")
        self.assertEqual(lzi.symbol.raw(), "Led Zeppelin")
        self.assertEqual(bci.symbol.raw(), "Bill Clinton")

    def test_markup(self):
        self.assertEqual(self.ibox.markup_source()[:9], "{{Infobox")

    def test_infobox_html_raw(self):
        self.assertIn("Origin\nLondon, England", self.ibox.rendered())

    def test_infobox_markup_raw(self):
        self.assertIn("| name = Led Zeppelin", self.ibox.markup_source())
        clinton = get_infobox("Bill Clinton", configuration=testcfg)
        self.assertIn("|birth_place ", clinton.markup_source())

    def test_rendered_keys(self):
        clinton = get_infobox("Bill Clinton", configuration=testcfg)
        self.assertEqual(clinton.rendered_keys().get("birth_place"), "Born",
                         clinton.html_source())

    def test_infobox_html_parsed(self):
        self.assertIn((u'Origin', u'London, England'),
                      [(k.text(), v.text()) for k,v in self.ibox.html_parsed()])

    def test_attributes(self):
        self.assertEqual(self.ibox.get("origin"), "London, England")
        clinton = get_infobox("Bill Clinton", configuration=testcfg)

        # XXX: maybe not a good idea to check for missing attributes
        # like 'death-date'. In live wikipedia they are there and
        # empty, on the mirror they are missing.
        self.assertIn("term-start",
                      [k for k, v in clinton.markup_parsed()])

    def test_types(self):
        self.assertEqual(self.ibox.types(), ['Template:Infobox musical artist'])
        self.assertEqual(self.ibox.types(True), ['Template:Infobox musical artist'])
        # self.assertEqual(self.ibox.start_types(), ['wikipedia-musical-artist'])

    def test_types_redirect(self):
        clinton = get_infobox("Bill Clinton", configuration=testcfg)

    def test_html_keys(self):
        # XXX: bbc news was vandalized on the mirror, until this is
        # fixed use live just for this
        bbc = get_infobox("BBC News", configuration=testcfg)
        self.assertEquals("[[BBC]]", dict(bbc.markup_parsed()).get("owner"),
                          list(bbc.html_parsed()))
        self.assertEquals("BBC", bbc.get('Owner'))
        self.assertEquals("BBC", bbc.get('owner'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
