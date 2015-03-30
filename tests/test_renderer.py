#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_renderer
----------------------------------

Tests for `renderer` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase import renderer
from wikipediabase.util import fromstring

class TestRenderer(unittest.TestCase):

    def setUp(self):
        self.rndr = renderer.SandboxRenderer()

    def test_render(self):
        html_str = self.rndr.render("Bawls of steel")
        self.assertIn(u"Bawls of steel", html_str, "Body not found")
        # If this fails it is possible that wikipedia.org has blocked
        # you. Use a mirror.
        self.assertNotIn(u"wpTextbox1", html_str, "Get just the contents..")

    def test_render_ibox(self):
        ibx_txt ="""{{Infobox person
| name =  Sam Dunn
| birth_date = {{birth date and age|1974|3|20|df=y}}
| birth_place = [[Stroud]], [[England]]
}}"""
        self.assertIn(u"March 1974", self.rndr.render(ibx_txt))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
