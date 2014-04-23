#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dates
----------------------------------

Tests for `dates` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.dates import EnchantedDate

JESUS_BIRTHDAY = """
7–2 BC{{efn|John P. Meier writes that Jesus' birth year is ''c.'' 7/6 BC.<ref name=Meier1991>{{cite book|last=Meier|first=John P.|title=A Marginal Jew: The roots of the problem and the person|year=1991|publisher=Yale University Press|isbn=978-0-300-14018-7|page=407}}</ref> Rahner states that the consensus among historians is ''c.'' 4 BC.{{sfn|Rahner|2004|p=732}} Sanders favors ''c.'' 4 BC, and refers to the general consensus.{{sfn|Sanders|1993|pp=10–11}} Finegan supports ''c.'' 3/2 BC, defending it comprehensively according to early Christian traditions.<ref name=Finegan>{{cite book|first=Jack |last=Finegan|title= Handbook of Biblical Chronology, rev. ed.|year=1998|publisher=Hendrickson Publishers| isbn= 978-1-56563-143-4|page=319}}</ref>
"""

class TestDates(unittest.TestCase):

    def setUp(self):
        self.ed = EnchantedDate("yyyymmdd", JESUS_BIRTHDAY)

    def test_jeezes(self):
        self.assertEqual(str(self.ed), "((:yyyymmdd -00040000))",
                         msg="You should find 4 BC because it is found alone.")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
