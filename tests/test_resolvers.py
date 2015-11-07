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

import logging

from wikipediabase import resolvers
from wikipediabase.frontend import Frontend

from wikipediabase.util import get_knowledgebase

from wikipediabase.resolvers.person import first_paren

from tests.examples import *

ARTICLE_BODY = u"""A ninja (忍者?) or shinobi (忍び?) was a covert agent or mercenary
in feudal Japan. The functions of the ninja included espionage,
sabotage, infiltration, and assassination, and open combat in certain
situations.[1] Their covert methods of waging war contrasted the ninja
with the samurai, who observed strict rules about honor and combat.[2]
The shinobi proper, a specially trained group of spies and
mercenaries, appeared in the Sengoku or \"warring states\" period, in
the 15th century,[3] but antecedents may have existed in the 14th
century,[4] and possibly even in the 12th century (Heian or early
Kamakura era).[5][6]"""

DISABLE_ALL_EXCEPT_JUST = False


class All(object):

    def __contains__(self, _):
        return True


class TestResolvers(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("resolver-testing")
        self.fe = Frontend()
        self.kb = get_knowledgebase()
        self.term_resolver = resolvers.TermResolver()

    def test_word_count(self):
        self.assertEqual(len(self.term_resolver._words(ARTICLE_BODY)), 100)

    def test_url(self):
        url = self.term_resolver.resolve('wikibase-term', 'Barack Obama', 'url')
        self.assertEquals('https://en.wikipedia.org/wiki/Barack_Obama', url.val)

    def test_infobox(self):
        band_name = self.fe.eval('(get "wikipedia-album" "%s" "Name")' %
                                 "The Def Leppard E.P.")
        self.assertEqual(band_name, '((:html "The Def Leppard E.P."))')

    def test_get(self):
        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES):
            self.assertEqual(ans, rx, msg=msg)

    def test_strangeness(self):
        for ans, rx, msg in self._ans_match(DEGENERATE_EXAMPLES, All()):
            self.assertEqual(ans, rx, msg=msg)

    def test_get_not(self):
        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_NOT):
            self.assertNotEqual(ans, rx, msg=msg)

    def test_get_rx(self):
        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_RX):
            self.assertRegexpMatches(ans, rx, msg=msg)

    def test_get_not_rx(self):
        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_NOT_RX):
            self.assertNotRegexpMatches(ans, rx, msg=msg)

    def test_first_paren(self):
        query = "I (Joe (sir) doe) am here (an0other paren here) and text"
        self.assertEqual(first_paren(query), "Joe (sir) doe")

        txt = "Hello (dr. hello 2000-2012) I like bananas." \
              "Of couse i do (they are the begist)"
        # First paren will stop at the first sentence.
        txt_none = "Hello. My name is Bond (James Bond)"
        self.assertEqual(first_paren(txt), "dr. hello 2000-2012")
        self.assertIs(first_paren(txt_none), None)

    def test_error_resolver(self):
        alive_err = '((:error attribute-value-not-found :reply '\
            '"Currently alive"))'
        err = self.kb.get('wikipedia-president', 'Bill Clinton', 'death-date')
        self.assertEqual(str(err), alive_err)
        err = self.kb.get('wikibase-person', 'Barack Obama', 'death-date')
        self.assertEqual(str(err), alive_err)

    def _ans_match(self, lst, just=None):
        """
        From a list of queries (query, ans-matcher[, message]) extract the
        answer that the frontend asked for, the matcher and the
        message or None. This is a generator. Just is a list of the
        ones to test
        """

        if not DISABLE_ALL_EXCEPT_JUST or just:
            full = len(lst)
            for completion, entry in enumerate(lst):
                if just is not None and completion not in just:
                    continue

                try:
                    q, m = entry
                    msg = ""
                except ValueError:
                    q, m, msg = entry

                self.log.info("\n\tQuery: '%s'\n\tMatcher: '%s'\n\tComp: %d\%d"
                              % (q, m, completion + 1, full))

                ans = self.fe.eval(q) or ""

                msg += "\n\tQuery: '%s'\n\tAnswer: '%s'\n\tMatcher: '%s'\n\tCompletion: %d\%d" \
                    % (q, ans, m, completion + 1, full)

                yield ans, m, msg

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
