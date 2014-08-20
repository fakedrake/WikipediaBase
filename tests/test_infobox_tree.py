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

from wikipediabase import infobox_tree

MU = """
==Arts and culture==

===Award===
* [[Template:Infobox award]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_award&namespace=10 Transclusion count]: 3,053)
** [[Template:Infobox British Academy Television Awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_British_Academy_Television_Awards&namespace=10 Transclusion count]: 20)
* [[Template:Infobox British Academy video games awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_British_Academy_video_games_awards&namespace=10 Transclusion count]: 10)
* [[Template:Infobox beauty pageant]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_beauty_pageant&namespace=10 Transclusion count]: 1,257)
* [[Template:Infobox comedian awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_comedian_awards&namespace=10 Transclusion count]: 122)
* [[Template:Infobox film awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_film_awards&namespace=10 Transclusion count]: 692)
** [[Template:Infobox Hong Kong Film Awards]] ([http://toolserver.org/~jarry/templatecount/index.php?lang=en&name=Infobox_Hong_Kong_Film_Awards&namespace=10 Transclusion count]: 29)
"""


class TestInfoboxTree(unittest.TestCase):

    def setUp(self):
        pass

    def test_ibx_tree(self):
        tree = infobox_tree.ibx_tree(MU, ["Artsy stuff"])
        self.assertIn("award", tree[0])
        self.assertIn("Artsy stuff", tree[0][1])
        self.assertEqual(len(tree[1][1]), 4, msg=tree[0])
        self.assertEqual(len(tree[0][1]), 3, msg=",".join(tree[0][1]))

    def test_ibx_type_tree(self):
        tree = infobox_tree.ibx_type_tree()
        self.assertEqual(len(tree['California State Legislature']),
                         3, msg=repr(tree['California State Legislature']))
        self.assertNotIn("party", tree["state gun laws"])
        self.assertIn(u'Other politics and government', tree["state gun laws"])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
