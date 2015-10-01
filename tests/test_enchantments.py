#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_enchantments
----------------------------------

Tests for `enchantments` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.enchantments import enchant


class TestEnchantments(unittest.TestCase):

    def test_string(self):
        self.assertEqual(enchant("foo"), '"foo"')

    def test_unicode_string(self):
        self.assertEqual(enchant(u"föø"), '"foo"')

    def test_string_escaped(self):
        self.assertEqual(enchant('foo "bar"'), '"foo \\"bar\\""')

    def test_string_with_typecode(self):
        self.assertEqual(enchant("bar", typecode="html"), '(:html "bar")')

    def test_list(self):
        l = ['wikipedia-class1', 'wikipedia-class2']
        self.assertEqual(enchant(l), '("wikipedia-class1" "wikipedia-class2")')

    def test_list_with_typecode(self):
        l = [44, 35]
        self.assertEqual(enchant(l, typecode='coordinates'),
                         '(:coordinates 44 35)')

    def test_nested_list(self):
        l = [[0, 'foo'], [1, '"bar"']]
        self.assertEqual(enchant(l), '((0 "foo") (1 "\\"bar\\""))')

    def test_double_nested_list(self):
        l = [[0, ['v0', 'foo']], [1, ['v1', 'bar']]]
        self.assertEqual(enchant(l), '((0 ("v0" "foo")) (1 ("v1" "bar")))')

    def test_date_simple(self):
        ed = enchant("coming on August the 8th", typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 00000808)')

    def test_date_multiple_voting(self):
        ed = enchant("2010 8.8.1991 on August the 8th 1991",
                     typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 20100000)')

    def test_date_with_range(self):
        # 2010 is in the given range, thus it wil precede 8,8,1991
        ed = enchant("2010 8.9.1991 - 2012 on August the 8th 1991",
                     typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 20100000)')

    def test_bool(self):
        self.assertEqual(enchant(True), '#t')
        self.assertEqual(enchant(False), '#f')

    def test_bool_with_typecode(self):
        self.assertEqual(enchant(False, typecode='calculated'),
                         '(:calculated #f)')

    def test_keyword(self):
        self.assertEqual(enchant(':feminine'), ":feminine")

    def test_string_not_keyword(self):
        self.assertEqual(enchant(':not a keyword'), '":not a keyword"')

    def test_keyword_with_typecode(self):
        self.assertEqual(enchant(':feminine', typecode='calculated'),
                         '(:calculated :feminine)')

    def test_dict(self):
        self.assertEqual(enchant({'a': 1, 'b': "foo"}),
                         '(:b "foo" :a "1")')

    def test_dict_with_escaped_string(self):
        self.assertEqual(enchant({'a': 1, 'b': '"foo"'}),
                         '(:b "\\"foo\\"" :a "1")')

    def test_error(self):
        err = enchant({'symbol': 'sym', 'kw': dict(a=1, b=2, c='ha')},
                      typecode='error')
        self.assertEqual(err, '(error sym :a "1" :c "ha" :b "2")')

    def test_error_from_exception(self):
        err = enchant(ValueError('Wrong thing'))
        self.assertEqual(err, '(error ValueError :reply "Wrong thing")')

    def test_none(self):
        self.assertEqual(enchant(None), 'nil')

    def test_none_with_typecode(self):
        self.assertEqual(enchant(None, typecode='calculated'),
                         '(:calculated nil)')

    def test_number(self):
        self.assertEqual(enchant(5), '5')

    def test_number_with_typecode(self):
        self.assertEqual(enchant(5, typecode='calculated'),
                         '(:calculated 5)')

if __name__ == '__main__':
    unittest.main()
