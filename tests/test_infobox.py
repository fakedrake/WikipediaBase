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

from wikipediabase.infobox import Infobox, MetaInfoboxBuilder, InfoboxUtil, \
    get_infoboxes, get_meta_infobox


class TestInfobox(unittest.TestCase):

    def test_markup(self):
        ibox = get_infoboxes("Led Zeppelin")[0]
        self.assertEqual(ibox.markup[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup)

    def test_html_items(self):
        ibox = get_infoboxes("AC/DC")[0]
        self.assertIn(("Origin", "Sydney, Australia"), ibox._html_items())

    def test_attributes(self):
        churchill = get_infoboxes("Winston Churchill")[0]
        self.assertIn("death-place", churchill.attributes)
        self.assertEqual("Died", churchill.attributes.get("death-place"))

        bridge = get_infoboxes("Brooklyn Bridge")[0]
        self.assertIn("maint", bridge.attributes)
        self.assertEqual("Maintained by", bridge.attributes.get("maint"))

        bbc = get_infoboxes("BBC News")[0]
        self.assertEqual("Number of employees",
                         bbc.attributes.get("num-employees"))

    def test_get(self):
        # TODO: test use of :code and :rendered typecodes
        ibox = get_infoboxes("The Rolling Stones")[0]
        self.assertEqual(ibox.get("origin"), "London, England")
        self.assertIn("Mick Jagger", ibox.get("current-members"))

    def test_templates(self):
        infoboxes = get_infoboxes("Vladimir Putin")
        templates = ["Template:Infobox officeholder",
                     "Template:Infobox martial artist"]
        self.assertItemsEqual([i.template for i in infoboxes], templates)

    def test_classes(self):
        infoboxes = get_infoboxes("Vladimir Putin")
        classes = ["wikipedia-officeholder", "wikipedia-martial-artist"]
        self.assertEqual(map(lambda i: i.wikipedia_class, infoboxes), classes)

    @unittest.expectedFailure
    def test_html_attributes(self):
        # TODO: we're not getting all rendered attributes, see issue #70
        ibox = get_infoboxes("BBC News")[0]
        self.assertEqual("Owner", ibox.attributes.get("owner"))

    def test_no_clashes_with_multiple_infoboxes(self):
        officeholder_ibox, martial_artist_ibox = get_infoboxes('Vladimir Putin')
        self.assertEqual(officeholder_ibox.wikipedia_class,
                         'wikipedia-officeholder')
        self.assertEqual(martial_artist_ibox.wikipedia_class,
                         'wikipedia-martial-artist')
        self.assertEqual(officeholder_ibox.get('image'),
                         'Vladimir Putin 12023 (cropped).jpg')
        self.assertEqual(martial_artist_ibox.get('image'),
                         'Vladimir Putin in Japan 3-5 September 2000-22.jpg')

    def test_get_infoboxes(self):
        symbol = "Led Zeppelin"
        self.assertIs(list, type(get_infoboxes(symbol)))
        self.assertIs(Infobox, type(get_infoboxes(symbol)[0]))


class TestMetaInfobox(unittest.TestCase):

    def test_newlines(self):
        ibx = get_meta_infobox('Template:Infobox weapon')
        attr = ibx.attributes['secondary-armament']
        self.assertEqual(attr, "Secondary armament")

    def test_musician(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.attributes['origin'], "Origin")

    def test_regression_officeholder(self):
        mibx = get_meta_infobox('Template:Infobox officeholder')
        self.assertEqual("Died", mibx.attributes.get("death-place"))

    def test_symbol(self):
        di = get_meta_infobox('Template:Infobox musical artist')
        self.assertEqual(di.symbol, "Template:Infobox musical artist")

    def test_attributes(self):
        builder = MetaInfoboxBuilder('Template:Infobox person')
        self.assertIn((u'Native\xa0name', '!!!!!native_name!!!!!'),
                      builder.html_parsed())

    def test_rendered_attributes(self):
        ibx = get_meta_infobox('Template:Infobox person')
        self.assertEqual(ibx.attributes['native-name'], u'Native\xa0name')


class TestInfoboxUtil(unittest.TestCase):

    def test_class(self):
        self.assertEqual(InfoboxUtil.to_class("Template:Infobox martial artist"),
                         "wikipedia-martial-artist")

    def test_class_strip(self):
        self.assertEqual(InfoboxUtil.to_class("Template:Infobox writer "),
                         "wikipedia-writer")

    def test_class_taxobox(self):
        self.assertEqual(InfoboxUtil.to_class("Template:Taxobox"),
                         "wikipedia-taxobox")

    def test_clean_attribute(self):
        dirty = "  attr12 "
        self.assertEqual(InfoboxUtil.clean_attribute(dirty), "attr")


if __name__ == '__main__':
    unittest.main()
