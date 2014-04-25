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

from common import data, TEST_FETCHER_SETUP

import re, logging

from wikipediabase import resolvers
from wikipediabase import fetcher
from wikipediabase.frontend import Frontend
from wikipediabase.knowledgebase import KnowledgeBase

from tests.examples import *

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


class TestResolvers(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("resolver-testing")
        self.simple_resolver = resolvers.StaticResolver()
        self.ibresolver = resolvers.InfoboxResolver(
            fetcher=fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP))

        self.fe = Frontend()
        self.kb = KnowledgeBase(frontend=self.fe,
                                resolvers=[self.simple_resolver, self.ibresolver])

    def test_resolver(self):
        self.assertEqual(self.simple_resolver.resolve(ARTICLE, "word-count"), \
                         100)

    def test_random_attributes(self):
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\" \"word-count\")"), '3')
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\n\" (:code \"word-count\"))"), '3')

    def test_infobox(self):
        # Disable compatibility mode: no extra tag info on result.
        self.ibresolver.compat = False

        band_name = self.fe.eval('(get "%s" "Name")' % "Def_Leppard_EP")
        self.assertEqual(band_name, '((:html "The Def Leppard E.P."))')

    def test_compat(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES):
            self.assertEqual(ans, rx, msg=msg)

    def test_compat_not(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_NOT):
            self.assertNotEqual(ans, rx, msg=msg)

    def test_compat_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_RX):
            self.assertRegexpMatches(ans, rx, msg=msg)

    def test_compat_not_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher(**TEST_FETCHER_SETUP)

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_NOT_RX):
            self.assertNotRegexpMatches(ans, rx, msg=msg)


    def _ans_match(self, lst):
        """
        From a list of queries (query, ans-matcher[, message]) extract the
        answer that the frontend asked for, the matcher and the
        message or None. This is a generator.
        """

        full = len(lst)
        for completion, entry in enumerate(lst):
            try:
                q, m = entry
                msg = ""
            except ValueError:
                q, m, msg = entry

            self.log.info("\n\tQuery: '%s'\n\tMatcher: '%s'\n\tComp: %d\%d" \
                          % (q, m, completion+1, full))

            ans = self.fe.eval(q) or ""

            msg += "\n\tQuery: '%s'\n\tAnswer: '%s'\n\tMatcher: '%s'\n\tCompletion: %d\%d" \
                      % (q, ans, m, completion+1, full)

            yield ans, m, msg

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
