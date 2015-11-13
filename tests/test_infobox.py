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

import mwparserfromhell

from wikipediabase.article import get_article
from wikipediabase.infobox import Infobox, InfoboxBuilder, InfoboxUtil, \
    MetaInfoboxBuilder, RenderedInfoboxBuilder, get_infoboxes, \
    get_meta_infobox, get_rendered_infoboxes
from wikipediabase.util import tostring


class TestInfobox(unittest.TestCase):

    def test_markup(self):
        ibox = get_infoboxes("Led Zeppelin")[0]
        self.assertEqual(ibox.markup[:9], "{{Infobox")
        self.assertIn("| name = Led Zeppelin", ibox.markup)

    def test_html_items(self):
        ibox = get_rendered_infoboxes("AC/DC")[0]
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
        ibox = get_rendered_infoboxes("The Rolling Stones")[0]
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
        self.assertEqual(map(lambda i: i.cls, infoboxes), classes)

    def test_classes_with_subtemplates(self):
        infoboxes = get_infoboxes("IS (manga)")
        classes = [
            'wikipedia-animanga/header',
            'wikipedia-animanga/print',
            'wikipedia-animanga/video',
            'wikipedia-animanga/footer',
        ]
        self.assertEqual(map(lambda i: i.cls, infoboxes), classes)

    @unittest.expectedFailure
    def test_html_attributes(self):
        # TODO: we're not getting all rendered attributes, see issue #70
        ibox = get_infoboxes("BBC News")[0]
        self.assertEqual("Owner", ibox.attributes.get("owner"))

    def test_no_clashes_with_multiple_infoboxes(self):
        officeholder_ibox, martial_artist_ibox = \
            get_rendered_infoboxes('Vladimir Putin')
        self.assertEqual(officeholder_ibox.cls,
                         'wikipedia-officeholder')
        self.assertEqual(martial_artist_ibox.cls,
                         'wikipedia-martial-artist')
        self.assertEqual(officeholder_ibox.get('image'),
                         'Vladimir Putin 12023 (cropped).jpg')
        self.assertEqual(martial_artist_ibox.get('image'),
                         'Vladimir Putin in Japan 3-5 September 2000-22.jpg')

    def test_get_infoboxes(self):
        symbol = "Led Zeppelin"
        self.assertIs(list, type(get_infoboxes(symbol)))
        self.assertIs(Infobox, type(get_infoboxes(symbol)[0]))

    def test_illegal_meta_infobox(self):
        ibox = get_infoboxes('Chickasaw County, Iowa')[0]
        ibox.markup = mwparserfromhell.parse(
            '{{Infobox rubbish made up template\n |foo = bar\n}}')
        # even if the MetaInfobox is illegal, attributes should be parsed
        self.assertIn("foo", ibox.attributes)


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


class TestInfoboxSubTemplates(unittest.TestCase):

    def test_group_infobox_sub_templates_animanga(self):
        # The article 'IS (manga)' contains 4 infoboxes that are sub-templates
        # of infobox animanga. Sub-templates are defined using a slash and a
        # suffix (e.g. 'Infobox animanga/Header')

        # These 4 templates (defined in markup as separate infoboxes) are
        # rendered into one single HTML infobox.

        symbol = 'IS (manga)'
        animanga_templates = [
            'Template:Infobox animanga/Header',
            'Template:Infobox animanga/Print',
            'Template:Infobox animanga/Video',
            'Template:Infobox animanga/Footer'
        ]

        markup_infoboxes = get_infoboxes(symbol)
        builder = RenderedInfoboxBuilder(symbol, markup_infoboxes)
        groups = builder._group_infobox_sub_templates(markup_infoboxes)

        # tests that the 4 sub-templates are grouped into one common prefix
        self.assertEquals(['Template:Infobox animanga'], groups.keys())

        # tests that the correct 4 sub-templates are retrieved
        animanga_infoboxes = groups['Template:Infobox animanga']
        templates = [ibox.template for ibox in animanga_infoboxes]
        self.assertItemsEqual(animanga_templates, templates)

        # checks that markup segments are partitioned correctly
        # each substring below is unique to different sub-templates
        infoboxes = [ibox.markup for ibox in animanga_infoboxes]
        self.assertIn('image', infoboxes[0])
        self.assertIn('volume_list', infoboxes[1])
        self.assertIn('episode_list', infoboxes[2])
        self.assertIn('/Footer}}', infoboxes[3])

    def test_group_infobox_sub_templates_ship(self):
        # The article 'USS Pueblo (AGER-2)' contains 4 infoboxes that are
        # sub-templates of infobox ship. Sub-templates are defined by
        # appending a suffix (e.g. "Infobox ship characteristics")

        # These 4 templates (defined in markup as separate
        # infoboxes) are rendered into one single HTML infobox.

        symbol = 'USS Pueblo (AGER-2)'
        ship_templates = [
            'Template:Infobox ship begin',
            'Template:Infobox ship image',
            'Template:Infobox ship career',
            'Template:Infobox ship characteristics',
        ]

        markup_infoboxes = get_infoboxes(symbol)
        builder = RenderedInfoboxBuilder(symbol, markup_infoboxes)
        groups = builder._group_infobox_sub_templates(markup_infoboxes)

        # tests that the 4 sub-templates are grouped into one common prefix
        self.assertEquals(['Template:Infobox ship'], groups.keys())

        # tests that the correct 4 sub-templates are retrieved
        ship_infoboxes = groups['Template:Infobox ship']
        templates = [ibox.template for ibox in ship_infoboxes]
        self.assertItemsEqual(ship_templates, templates)

        # checks that markup segments are partitioned correctly
        # each substring below is unique to different sub-templates
        infoboxes = [ibox.markup for ibox in ship_infoboxes]
        self.assertIn('caption', infoboxes[0])
        self.assertIn('Ship image', infoboxes[1])
        self.assertIn('Ship commissioned', infoboxes[2])
        self.assertIn('Ship displacement', infoboxes[3])

    def test_group_subtemplates(self):
        # made-up, complex markup consisting of infobox templates and
        # sub-templates
        markup = '\n'.join([
            '{{Infobox officeholder}}',
            '{{Infobox martial artist}}',
            '{{Infobox martial artist/Footer}}',
            '{{Infobox person}}',
            '{{Infobox ship begin}}',
            '{{Infobox ship characteristics}}',
        ])

        symbol = 'Foo'
        builder = InfoboxBuilder(symbol)
        markup_infoboxes, _ = builder._markup_infoboxes(markup)

        infoboxes = [Infobox(symbol, m['template'], m['cls'], m['markup'])
                     for m in markup_infoboxes]
        rendered_builder = RenderedInfoboxBuilder('Foo', infoboxes)
        groups = rendered_builder._group_infobox_sub_templates(infoboxes)

        expected = {
            'Template:Infobox officeholder': [
                'Template:Infobox officeholder',
            ],
            'Template:Infobox martial artist': [
                'Template:Infobox martial artist',
                'Template:Infobox martial artist/Footer',
            ],
            'Template:Infobox person': [
                'Template:Infobox person',
            ],
            'Template:Infobox ship': [
                'Template:Infobox ship begin',
                'Template:Infobox ship characteristics',
            ]
        }

        result = {g: [x.template for x in groups[g]] for g in groups}
        self.assertEquals(expected, result)

    def test_split_html_infobox_animanga(self):
        # The article 'IS (manga)' contains 4 infoboxes that are sub-templates
        # of infobox animanga. These 4 templates (defined in markup as separate
        # infoboxes) are rendered into one single HTML infobox.

        # The HTML infobox can be split into 4 logical partitions by looking
        # at <td> or <th> elements with a light-purple background
        symbol = 'IS (manga)'
        html = get_article(symbol).html_source()
        infoboxes = get_infoboxes(symbol)

        builder = RenderedInfoboxBuilder(symbol, infoboxes)
        html_infobox = builder._html_infoboxes(html)[0]
        split_html = builder._split_html_infobox(html_infobox, 4)
        split_html = [tostring(ibox) for ibox in split_html]

        # each split infobox should be in its own <table> element
        for ibox in split_html:
            self.assertIn('<table class="infobox', ibox)

        # checks that HTML infoboxes are partitioned correctly
        # each substring below is unique to different sub-templates
        self.assertIn('Genre', split_html[0])
        self.assertIn('Manga', split_html[1])
        self.assertIn('Television drama', split_html[2])
        self.assertIn('Anime and Manga portal', split_html[3])

    def test_split_html_infobox_person(self):
        # The article 'Bill Clinton' contains one HTML infobox. The HTML
        # infobox can be split into 4 logical partitions by looking
        # at <td> or <th> elements with a light-purple background

        # Note that this is just a test. Bill Clinton's infobox doesn't
        # actually need to be split because it comes from one single
        # markup infobox
        symbol = 'Bill Clinton'
        html = get_article(symbol).html_source()
        infoboxes = get_infoboxes(symbol)

        builder = RenderedInfoboxBuilder(symbol, infoboxes)
        html_infobox = builder._html_infoboxes(html)[0]
        split_html = builder._split_html_infobox(html_infobox, 4)
        split_html = [tostring(ibox) for ibox in split_html]

        # each split infobox should be in its own <table> element
        for ibox in split_html:
            self.assertIn('<table class="infobox', ibox)

        # checks that HTML infoboxes are partitioned correctly
        # each substring below is unique to different sub-templates
        self.assertIn('George W. Bush', split_html[0])
        self.assertIn('Jim Guy Tucker', split_html[1])
        self.assertIn('Steve Clark', split_html[2])
        self.assertIn('William Jefferson Blythe III', split_html[3])

    def test_unsuccessful_infobox_split(self):
        # The article 'LTV L450F' contains 2 infoboxes that are sub-templates
        # of infobox aircraft. These 2 templates (defined in markup as separate
        # infoboxes) are rendered into one single HTML infobox.

        # The HTML infobox cannot be split into 2 logical partitions because
        # there are no logical headers (<td>/<th> elements with a background)
        symbol = 'LTV L450F'
        infoboxes = get_infoboxes(symbol)
        builder = RenderedInfoboxBuilder(symbol, infoboxes)
        html = get_article(symbol).html_source()
        html_infobox = builder._html_infoboxes(html)[0]
        self.assertRaises(ValueError, builder._split_html_infobox,
                          html_infobox, 4)

    def test_handle_sub_templates(self):
        # An end-to-end test of our capacity to handle infobox sub-templates
        # The article 'IS (manga)' contains 4 infoboxes that are sub-templates
        # of infobox animanga. These 4 templates (defined in markup as separate
        # infoboxes) are rendered into one single HTML infobox.

        infoboxes = get_rendered_infoboxes('IS (manga)')
        self.assertEqual(4, len(infoboxes))

        classes = [
            'wikipedia-animanga/header',
            'wikipedia-animanga/print',
            'wikipedia-animanga/video',
            'wikipedia-animanga/footer',
        ]

        self.assertItemsEqual(classes, map(lambda ibox: ibox.cls, infoboxes))

        ibox_print, ibox_video = infoboxes[1:3]

        # test for correct rendered attributes
        self.assertEquals(u'Published\xa0by',
                          ibox_print.attributes['publisher'])
        self.assertEquals(u'Produced\xa0by',
                          ibox_video.attributes['producer'])

        # test for no clashes in get
        self.assertEquals('manga', ibox_print.get('type'))
        self.assertEquals('drama', ibox_video.get('type'))


if __name__ == '__main__':
    unittest.main()
