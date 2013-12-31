#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_resolvers
----------------------------------

Tests for `resolvers` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from common import data

from wikipediabase import resolvers
from wikipediabase import fetcher
from wikipediabase.frontend import Frontend
from wikipediabase.knowledgebase import KnowledgeBase

ARTICLE = u"""A ninja (忍者?) or shinobi (忍び?) was a covert agent or mercenary
in feudal Japan. The functions of the ninja included espionage,
sabotage, infiltration, and assassination, and open combat in certain
situations.[1] Their covert methods of waging war contrasted the ninja
with the samurai, who observed strict rules about honor and combat.[2]
The shinobi proper, a specially trained group of spies and
mercenaries, appeared in the Sengoku or \"warring states\" period, in
the 15th century,[3] but antecedents may have existed in the 14th
century,[4] and possibly even in the 12th century (Heian or early
Kamakura era).[5][6]"""

# A list of (query, expected-answer) tuples
WIKI_EXAMPLES = [
    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     '((:html "8848"))'),
    ('(get "wikipedia-officeholder" "Bill Clinton" (:code "SUCCESSOR"))',
     '((:html "George W. Bush"))'),
    ('(get "wikipedia-person" "Barack Obama" (:ID "BIRTH-DATE"))',
     '((:yyyymmdd 19610804))')]

WIKI_EXAMPLES_RX =[
    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     r'^\(\(:html "8848"\)\)$')
    ('(get "wikipedia-military-conflict" "American Civil War" (:code "RESULT"))',
     r'<ul>.*<li>.*<\/ul>')]

WIKI_EXAMPLES_NOT_RX =[
    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     r':code')]

class TestResolvers(unittest.TestCase):

    def setUp(self):
        self.simple_resolver = resolvers.StaticResolver()
        self.ibresolver = resolvers.InfoboxResolver(fetcher=fetcher.CachingSiteFetcher())
        self.idr = resolvers.InfoboxDateResolver(fetcher=self.ibresolver.fetcher)

        self.fe = Frontend()
        self.kb = KnowledgeBase(frontend=self.fe,
                                resolvers=[self.simple_resolver, self.idr, self.ibresolver])

    def test_resolver(self):
        self.assertEqual(self.simple_resolver.resolve(ARTICLE, "word-count"), \
                         100)

    def test_integration(self):
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\" \"word-count\")"), 3)
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\" (:code \"word-count\"))"), 3)

    def test_infobox(self):
        band_name = self.fe.eval('(get "%s" "Name")' % "Def_Leppard_EP")
        self.assertEqual(band_name,"The Def Leppard E.P.")

    def test_compat(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for q, r in WIKI_EXAMPLES:
            ans = self.fe.eval(q)
            self.assertEqual(ans, r)

    def test_compat_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for q, r in WIKI_EXAMPLES_RX:
            ans = self.fe.eval(q)
            self.assertRegexpMatches(ans, r)

    def test_compat_not_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for q, r in WIKI_EXAMPLES_NOT_RX:
            ans = self.fe.eval(q)
            self.assertNotRegexpMatches(ans, r)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
