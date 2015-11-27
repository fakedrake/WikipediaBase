#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_infobox_tree
----------------------------------

Tests for `infobox_tree` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import util
from wikipediabase import infobox_tree
from .common import read_data, testcfg

MU = read_data("dummy_ibox_tree.txt")


class TestInfoboxTree(unittest.TestCase):

    def setUp(self):
        self.src = """
        Body 0

        = Head 1 =

        Body 1
        == Head 1.1 ==
        Body 1.1
        = Head 2=
        == Head 2.1 ==
        = Head 3 =
        == Head 3.1 ==
        === Head 3.1.1 ===
        Body 3.1.1
        === Head 3.1.2 ===
        Body 3.1.2
        = Head 4 =
        ==== Head 4.1.1.1 ====
        Body 4.1.1.1
        """
        self.ibx = infobox_tree.InfoboxSuperclasses(configuration=testcfg)

    def test_header_levels(self):
        self.assertEqual(list(self.ibx.header_levels("")), [(0, None, '')])
        self.assertEqual(list(self.ibx.header_levels("hello")), [(0, None, "hello")])
        levels =  [(0, None, 'Body 0'),
                   (1, 'Head 1', 'Body 1'),
                   (2, 'Head 1.1', 'Body 1.1'),
                   (1, 'Head 2', ''),
                   (2, 'Head 2.1', ''),
                   (1, 'Head 3', ''),
                   (2, 'Head 3.1', ''),
                   (3, 'Head 3.1.1', 'Body 3.1.1'),
                   (3, 'Head 3.1.2', 'Body 3.1.2'),
                   (1, 'Head 4', ''),
                   (4, 'Head 4.1.1.1', 'Body 4.1.1.1')]

        self.assertEqual(list(self.ibx.header_levels(self.src)), levels)

    def test_header_lists(self):
        lists = [([], 'Body 0'),
                 (['Head 1'], 'Body 1'),
                 (['Head 1', 'Head 1.1'], 'Body 1.1'),
                 (['Head 2'], ''),
                 (['Head 2', 'Head 2.1'], ''),
                 (['Head 3'], ''),
                 (['Head 3', 'Head 3.1'], ''),
                 (['Head 3', 'Head 3.1', 'Head 3.1.1'], 'Body 3.1.1'),
                 (['Head 3', 'Head 3.1', 'Head 3.1.2'], 'Body 3.1.2'),
                 (['Head 4'], ''),
                 (['Head 4', None, None, 'Head 4.1.1.1'], 'Body 4.1.1.1')]

        self.assertEqual(list(self.ibx.header_lists(self.src)), lists)

    def test_infobox_list(self):

        src = """
        ==Arts and culture==

===Award===
* [[Template:Infobox actor awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_actor_awards&namespace=10 Transclusion count]: 56)
* [[Template:Infobox award]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_award&namespace=10 Transclusion count]: 3,574)
** [[Template:Infobox British Academy video games awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_British_Academy_video_games_awards&namespace=10 Transclusion count]: 10)
* [[Template:Infobox beauty pageant]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_beauty_pageant&namespace=10 Transclusion count]: 1,268)
        """
        res = [(['actor awards'], 'actor awards'),
               (['award'], 'award'),
               (['award',
                 'British Academy video games awards'],
                'British Academy video games awards'),
               (['beauty pageant'], 'beauty pageant')]
        self.assertEqual(list(self.ibx.infobox_lists(src)), res)

    # def test_ibx_tree(self):
    #     tree = infobox_tree.ibx_tree(MU, ["Artsy stuff"])
    #     self.assertIn("award", tree[0])
    #     self.assertIn("Artsy stuff", tree[0][1])
    #     self.assertEqual(len(tree[1][1]), 4, msg=tree[0])
    #     self.assertEqual(len(tree[0][1]), 3, msg=",".join(tree[0][1]))

    # def test_ibx_type_tree(self):
    #     tree = infobox_tree.ibx_type_tree()
    #     self.assertEqual(len(tree['California State Legislature']),
    #                      3, msg=repr(tree['California State Legislature']))
    #     self.assertNotIn("party", tree["state gun laws"])
    #     self.assertIn(u'Other politics and government', tree["state gun laws"])
    #
    def test_company(self):
        ibx = util.get_meta_infobox('Template:Infobox_company')
        self.assertEqual(ibx.rendered_keys()['rating'], 'Rating')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
