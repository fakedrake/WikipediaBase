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

import re, logging

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

    # ============================================
    # tests for 'get' -- attributes from infoboxes
    # ============================================

    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     '((:html "8848"))'),
    ('(get "wikipedia-officeholder" "Bill Clinton" (:code "SUCCESSOR"))',
     '((:html "George W. Bush"))'),

    # ==============================================================
    # tests for 'get' -- attributes from infoboxes -or- article text
    # ==============================================================

    ('(get "wikipedia-person" "Barack Obama" (:ID "BIRTH-DATE"))',
     '((:yyyymmdd 19610804))'),
    ('(get "wikipedia-person" "Bill Clinton" "BIRTH-DATE")',
     '((:yyyymmdd 19460819))'),
    ('(get "wikipedia-person" "Klaus Barbie" "BIRTH-DATE")',
     '((:yyyymmdd 19131025))'),
    ('(get "wikipedia-person" "Klaus Barbie" "DEATH-DATE")',
     '((:yyyymmdd 19910925))'),
    ('(get "wikipedia-person" "Paul Shardlow" "BIRTH-DATE")',
     '((:yyyymmdd 19430429))'),
    ('(get "wikipedia-person" "Paul Shardlow" "DEATH-DATE")',
     '((:yyyymmdd 19681014))'),
    ('(get "wikipedia-person" "Napoleon" "BIRTH-DATE")',
     '((:yyyymmdd 17690815))'),
    ('(get "wikipedia-person" "Napoleon" "DEATH-DATE")',
     '((:yyyymmdd 18210505))'),
    ('(get "wikipedia-person" "Stephen Gray (scientist)" "DEATH-DATE")',
     '((:yyyymmdd 17360207))'),
    ('(get "wikipedia-person" "Jesus" "BIRTH-DATE")',
     '((:yyyymmdd -00040000))'),
    ('(get "wikipedia-person" "Jesus" "DEATH-DATE")',
     '((:yyyymmdd 00330000))'), # Used to be '((:yyyymmdd 00300000))'),
    # But both are equally correct i think.
    ('(get "wikipedia-person" "Albert Einstein" "BIRTH-DATE")',
     '((:yyyymmdd 18790314))'),
    ('(get "wikipedia-person" "Albert Einstein" "DEATH-DATE")',
     '((:yyyymmdd 19550418))'),
    ('(get "wikipedia-person" "Barack Obama" "BIRTH-DATE")',
     '((:yyyymmdd 19610804))'),
    ('(get "wikipedia-person" "Barack Obama" "DEATH-DATE")',
     '(((error attribute-value-not-found :reply "Currently alive")))'),
    ('(get "wikipedia-person" "Jamie Glover" "BIRTH-DATE")',
     '((:yyyymmdd 19690710))'),
    ('(get "wikipedia-person" "Jamie Glover" "DEATH-DATE")',
     '(((error attribute-value-not-found :reply "Currently alive")))'),
    ('(get "wikipedia-person" "John Lennon" "BIRTH-DATE")',
     '((:yyyymmdd 19401009))'),
    ('(get "wikipedia-person" "John Lennon" "DEATH-DATE")',
     '((:yyyymmdd 19801208))'),
    ('(get "wikipedia-person" "Jean Ferrat" "BIRTH-DATE")',
     '((:yyyymmdd 19301226))'),
    ('(get "wikipedia-person" "Jean Ferrat" "DEATH-DATE")',
     '((:yyyymmdd 20100313))'),
    ('(get "wikipedia-person" "Al Babartsky" "BIRTH-DATE")',
     '((:yyyymmdd 19150419))'),
    ('(get "wikipedia-person" "Al Babartsky" "DEATH-DATE")',
     '((:yyyymmdd 20021229))'),
    ('(get "wikipedia-person" "Martin Iti" "BIRTH-DATE")',
     '((:yyyymmdd 19830228))'),
    ('(get "wikipedia-person" "Edward Michael S." "BIRTH-DATE")',
     '((:yyyymmdd 19210000))'),
    ('(get "wikipedia-person" "Edward Michael S." "DEATH-DATE")',
     '((:yyyymmdd 20060000))'),
    ('(get "wikipedia-person" "Herbert Allan Fogel" "BIRTH-DATE")',
     '((:yyyymmdd 19290000))'),
    ('(get "wikipedia-person" "Marcos Angeleri" "BIRTH-DATE")',
     '((:yyyymmdd 19830407))'),
    ('(get "wikipedia-person" "Samantha Cristoforetti" "BIRTH-DATE")',
     '((:yyyymmdd 19770426))'),
    ('(get "wikipedia-person" "William Shakespeare" "BIRTH-DATE")',
     '((:yyyymmdd 15640400))'),
    ('(get "wikipedia-person" "William Shakesppeare" "BIRTH-DATE")',
     '#f'),
    ('(get "wikipedia-person" "Mary Shakespeare" "BIRTH-DATE")',
     '((:yyyymmdd 15370000))',
     'Person without infobox -- get birth date from first paragraph'),
    ('(get "wikipedia-person" "Mary Shakespeare" "DEATH-DATE")',
     '((:yyyymmdd 16080000))',
     'Person without infobox -- get death date from first paragraph'),
    ('(get "wikipedia-person" "John Shakespeare" "DEATH-DATE")',
     '((:yyyymmdd 16010907))',
     'Person without infobox -- get death date from first paragraph'),
    ('(get "wikipedia-person" "Violet Markham" "BIRTH-DATE")',
     '((:yyyymmdd 18720000))'),
    ('(get "wikipedia-person" "Stephen Gray (scientist)" "BIRTH-DATE")',
     '((:yyyymmdd 16660000))'),

    # DEGENERATE CASES

    ('(get "wikipedia-person" "Barack Obama" "DEATH-DATE")',
     '(((error attribute-value-not-found :reply "Currently alive")))'),

    # Resolved from text
    ('(get "wikipedia-person" "Violet Markham" "DEATH-DATE")',
     '((:yyyymmdd 19590202))'),
    ('(get "wikipedia-person" "Manno Wolf-Ferrari" "BIRTH-DATE")',
     '((:yyyymmdd 19110000))'),
    ('(get "wikipedia-person" "Manno Wolf-Ferrari" "DEATH-DATE")',
     '((:yyyymmdd 19940000))'),
    ('(get "wikipedia-person" "Freidun Aghalyan" "BIRTH-DATE")',
     '((:yyyymmdd 18761120))'),
    ('(get "wikipedia-person" "Freidun Aghalyan" "DEATH-DATE")',
     '((:yyyymmdd 19440201))'),

    # Dates can now be evaluated
    ('(get "wikipedia-person" "Plato" "BIRTH-DATE")',
     # '((:html "ca. 428 BC/427 BC"))'  XXX: Wikipedia was updated it seems
     '((:html "428/427 or 424/423 BC"))'),

    # =====================================
    # tests for 'get' -- special attributes
    # =====================================

    ('(get "wikipedia-term" "Sium sisarum" (:code "IMAGE-DATA")',
     '((0 "illustration_Sium_sisarum0.jpg" "<i>Sium sisarum</i>"))'),

    # Next three tests copied from old tests that asserted that each
    # coordinate was within a small delta (.1) of the tested value, to
    # allow for minor edits to Wikipedia articles.
    ('(get "wikipedia-term" "Black Sea" "COORDINATES")',
     '((:coordinates 44 35))'),
    ('(get "wikipedia-term" "Eiffel Tower" "COORDINATES")',
     '((:coordinates 48.8583, 2.2945))'),
    ('(get "wikipedia-term" "Caracas" "COORDINATES")',
     '((:coordinates 10.5, -66.916664))'),

    ('(get "wikipedia-person" "Bill Clinton" (:code "URL"))',
     '((:url "http://en.wikipedia.org/wiki/Bill_Clinton"))'),

    ('(get "wikipedia-person" "Bill Clinton" (:code "GENDER"))',
     ':MASCULINE'),
    ('(get "wikipedia-person" "William Shakespeare" "GENDER")',
     ':MASCULINE'),
    ('(get "wikipedia-person" "Sacagawea" "GENDER")',
     ':FEMININE'),
    ('(get "wikipedia-person" "Mary Shakespeare" (:calculated "GENDER"))',
     ':FEMININE'),

    ('(get "wikipedia-term" "Bill Clinton" (:calculated "PROPER"))',
     '#t'),
    ('(get "wikipedia-term" "North American Free Trade Agreement" (:calculated "PROPER"))',
     '#t'),
    ('(get "wikipedia-term" "Purchasing power parity" (:calculated "PROPER"))',
     '#f'),

    ('(get "wikipedia-term" "Bill Clinton" (:calculated "NUMBER"))',
     '#f'),
    ('(get "wikipedia-term" "The Beatles" (:calculated "NUMBER"))',
     '#t'),
]

WIKI_EXAMPLES_NOT =[

    # =====================================
    # tests for 'get' -- special attributes
    # =====================================

    ('(get "wikipedia-term" "Mother\'s Day" (:CODE "SHORT-ARTICLE"))',
     '((:html ""))'),

    # ==============================================================
    # tests for 'get' -- attributes from infoboxes -or- article text
    # ==============================================================

    ('(get "wikipedia-person" "Jesus" "BIRTH-DATE")',
     '((:yyyymmdd -000200007))',
     'Don\'t absurdly return range of years as year and day.'),

    # ============================================
    # tests for 'get' -- attributes from infoboxes
    # ============================================

    ('(get "wikipedia-aircraft-type" "General Dynamics F-16 Fighting Falcon" (:code "UNIT-COST"))',
     '((:html "F-16A/B: (1998 dollars) F-16C/D: (1998 dollars)"))',
     'tests the retrieval of infobox attributes that contain the {{US#|...}} template'),
    # Tests that infobox attributes that aren't dates but may contain
    # dates aren't returned in yyyymmdd format
    ('(get "wikipedia-military-conflict" "2006 Lebanon War" (:code "RESULT"))',
     '((:yyyymmdd 20060814))',
     '2006 Lebanon War RESULT is not just a date')
]

WIKI_EXAMPLES_RX =[

    # =====================
    # tests for get-classes
    # =====================

    # Would be clearer as something like:
    #   (assert-member 'wikipedia-term' '(get-classes \"Bill Clinton\")')
    ('(get-classes \"Bill Clinton\")',
     r'wikipedia-president',
     'All Wikipedia symbols have calculated class wikipedia-term'),
    ('(get-classes \"Bill Clinton\")',
     r'wikipedia-president',
     'All Wikipedia symbols have calculated class wikipedia-paragraphs'),
    ('(get-classes \"Bill Clinton\")',
     r'wikipedia-person',
     'All people have calculated class wikipedia-person'),
    ('(get-classes \"Bill Clinton\")',
     r'wikipedia-president'),
    ('(get-classes \"Ada (programming language)\")',
     r'wikipedia-programming-language'),
    ('(get-classes \"Mary Shakespeare\")',
     r'wikipedia-person',
     'Person without infobox'),

    # ========================
    # tests for get-attributes
    # ========================

    ('(get-attributes "wikipedia-film" "Gone with the Wind (film)")',
     r':code \"DIRECTOR\"'),
    # Instead of the next dozen tests, should have an assert-subset operator.
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"KEY-PEOPLE\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r'(:code \"OWNER\" :rendered \"Owner\(s\)\")'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r'(:code \"SERVICES\" :rendered \"Services\")'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"AREA-SERVED\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"LOCATION-COUNTRY\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"NAME\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"LOGO\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"LOCATION-CITY\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r'(:code \"TYPE\" :rendered \"Former type\")'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"INTL\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r':code \"NUM-EMPLOYEES\"'),
    ('(get-attributes "wikipedia-company" "BBC News")',
     r'(:code \"INDUSTRY\" :rendered \"Industry\"'),
    ('(get-attributes "wikipedia-bridge" "Brooklyn Bridge")',
     r':code \"OPEN\"'),

    # =====================================
    # tests for 'get' -- special attributes
    # =====================================

    ('(get "wikipedia-term" "Alexander Pushkin" "SHORT-ARTICLE")',
     r'Russian literature'),
    ('(get "wikipedia-term" "North America" "SHORT-ARTICLE")',
     r'It is bordered to the north'),
    ('(get "wikipedia-term" "Mother\'s Day" (:CODE "SHORT-ARTICLE"))'
     r'influence of mothers in society'),

    ('(get "wikipedia-term" "Bill Clinton" (:code "IMAGE-DATA")',
     '((0 "Bill_Clinton.jpg"'),

    # ============================================
    # tests for 'get' -- attributes from infoboxes
    # ============================================

    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     r'^\(\(:html "8848"\)\)$'),
    ('(get "wikipedia-military-conflict" "American Civil War" (:code "RESULT"))',
     re.compile(r'<ul>.*<li>.*<\/ul>', re.DOTALL),
     'Parse wiki-style list correctly in American Civil War RESULT'),
    ('(get "wikipedia-weapon" "M1 Abrams" (:code "WARS"))',
     re.compile(r'Gulf War\s*<br\s*\/>\s*War in Afghanistan', re.DOTALL),
     'Parse <br/>-separated list correctly in M1 Abrams WARS'),
    ('(get "wikipedia-film" "Gone with the Wind (film)" (:code "DIRECTOR"))',
     re.compile(r'<li>Victor Fleming/', re.DOTALL),
     r'Parse {{plainlist|...}} template correctly in GWTW DIRECTOR'),

    # Next few test the retrieval of infobox attributes that contain the
    # {{convert|..}} template
    ('(get "wikipedia-ocean" "Sea of Azov" (:CODE "LENGTH"))',
     r'360.*km.*220.*mi'),
    ('(get "wikipedia-ocean" "Sea of Azov" (:CODE "WIDTH"))',
     r'180.*km.*110.*mi'),
    ('(get "wikipedia-ocean" "Sea of Azov" (:CODE "AREA"))',
     r'39.?000.*km.*2.*15.?000.*sq.*mi'),
    ('(get "wikipedia-ocean" "Sea of Azov" (:CODE "DEPTH"))',
     r'7.*met.*23.*ft'),
    ('(get "wikipedia-ocean" "Sea of Azov" (:CODE "MAX-DEPTH"))',
     r'14.*m.*46.*ft'),

    ('(get "wikipedia-sea" "Sea of Azov" (:CODE "VOLUME"))',
     r'290.*km.*3'),

    ('(get "wikipedia-military-conflict" "American Civil War" (:code "RESULT"))',
     re.compile(r'Union victory.*Slavery abolished.*Territorial integrity.*Lincoln assassinated.*Reconstruction', re.DOTALL)),
    ('(get "wikipedia-weapon" "M1 Abrams" (:code "WARS"))',
     r'Persian',
     'Returns link text, not link target'),

    # Tests that infobox attributes that aren't dates but may contain
    # dates aren't returned in yyyymmdd format
    ('(get "wikipedia-military-conflict" "World War I" (:code "DATE"))',
     re.compile(r'1918.*Treaty.*signed', re.DOTALL),
     'World War I DATE returns end as well as start date'),
]

WIKI_EXAMPLES_NOT_RX =[

    # ========================
    # tests for get-attributes
    # ========================

    # Tests that infobox attributes that aren't dates but may contain
    # dates aren't returned in yyyymmdd format
    ('(get-attributes "wikipedia-military-conflict" "2006 Lebanon War")',
     r'result[^)]*yyyymmdd',
     "2006 Lebanon War RESULT attribute is not yyyymmdd"),

    # =====================================
    # tests for 'get' -- special attributes
    # =====================================

    ('(get "wikipedia-term" "Alexander Pushkin" "SHORT-ARTICLE")',
     r'Watchlist'),
    ('(get "wikipedia-term" "North America" "SHORT-ARTICLE")',
     r'Uploads'),

    # ============================================
    # tests for 'get' -- attributes from infoboxes
    # ============================================

    ('(get "wikipedia-mountain" "Mount Everest" (:code "ELEVATION_M"))',
     r':code'),
    ('(get "wikipedia-film" "Gone with the Wind (film)" (:code "DIRECTOR"))',
     r'George CukorSam Wood',
     "Names not run together in GWTW DIRECTOR"),
    ('(get "wikipedia-military-conflict" "American Civil War" (:code "RESULT"))',
     r'Abolition',
     'Returns link text, not link target: Abolition'),
    ('(get "wikipedia-military-conflict" "American Civil War" (:code "RESULT"))',
     r'Reconstruction Era of the United States',
     'Returns link text, not link target: Reconstruction...'),
]

class TestResolvers(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("resolver-testing")
        self.simple_resolver = resolvers.StaticResolver()
        self.ibresolver = resolvers.InfoboxResolver(fetcher=fetcher.CachingSiteFetcher())

        self.fe = Frontend()
        self.kb = KnowledgeBase(frontend=self.fe,
                                resolvers=[self.simple_resolver, self.ibresolver])

    def test_resolver(self):
        self.assertEqual(self.simple_resolver.resolve(ARTICLE, "word-count"), \
                         100)

    def test_integration(self):
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\" \"word-count\")"), '3')
        self.assertEqual(self.fe.eval("(get \"doctor ninja batman\n\" (:code \"word-count\"))"), '3')

    def test_infobox(self):
        # Disable compatibility mode: no extra tag info on result.
        self.ibresolver.compat = False

        band_name = self.fe.eval('(get "%s" "Name")' % "Def_Leppard_EP")
        self.assertEqual(band_name, '((:html "The Def Leppard E.P."))')

    def test_compat(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES):
            self.assertEqual(ans, rx, msg=msg)

    def test_compat_not(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_NOT):
            self.assertNotEqual(ans, rx, msg=msg)

    def test_compat_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

        for ans, rx, msg in self._ans_match(WIKI_EXAMPLES_RX):
            self.assertRegexpMatches(ans, rx, msg=msg)

    def test_compat_not_rx(self):
        self.ibresolver.fetcher = fetcher.CachingSiteFetcher()

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
                msg = None
            except ValueError:
                q, m, msg = entry

            self.log.info("\n\tQuery: '%s'\n\tMatcher: '%s'\n\tComp: %d\%d" \
                          % (q, m, completion+1, full))

            ans = self.fe.eval(q) or ""

            if msg is None:
                msg = "\n\tQuery: '%s'\n\tAnswer: '%s'\n\tMatcher: '%s'\n\tComp: %d\%d" \
                      % (q, ans, m, completion+1, full)

            yield ans, m, msg

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
