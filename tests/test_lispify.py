#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lispify
----------------------------------

Tests for `lispify` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.lispify import lispify


class TestLispify(unittest.TestCase):

    def test_string(self):
        self.assertEqual(lispify("foo"), '"foo"')

    def test_string_escaped(self):
        self.assertEqual(lispify('foo \\ "bar"'), '"foo \\ \\"bar\\""')

    def test_unicode_string(self):
        self.assertEqual(lispify(u"föø ” "), u'"föø ” "')

    def test_string_with_typecode(self):
        self.assertEqual(lispify("bar", typecode="html"), '(:html "bar")')

    def test_list(self):
        l = ['wikipedia-class1', 'wikipedia-class2']
        self.assertEqual(lispify(l), '("wikipedia-class1" "wikipedia-class2")')

    def test_list_with_typecode(self):
        l = [44, 35]
        self.assertEqual(lispify(l, typecode='coordinates'),
                         '(:coordinates 44 35)')

    def test_nested_list(self):
        l = [[0, 'foo'], [1, '"bar"']]
        self.assertEqual(lispify(l), '((0 "foo") (1 "\\"bar\\""))')

    def test_double_nested_list(self):
        l = [[0, ['v0', 'foo']], [1, ['v1', 'bar']]]
        self.assertEqual(lispify(l), '((0 ("v0" "foo")) (1 ("v1" "bar")))')

    def test_list_of_dict(self):
        l = [{'foo': 'bar'}, {'foo': 'baz'}]
        self.assertEqual(lispify(l), '((:foo "bar") (:foo "baz"))')

    def test_list_of_dict_with_typecode(self):
        l = [{'foo': 'bar'}, {'foo': 'baz'}]
        self.assertEqual(lispify(l, typecode='html'),
                         '(:html (:foo "bar") (:foo "baz"))')

    def test_date_simple(self):
        ed = lispify("coming on August the 8th", typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 00000808)')

    def test_date_multiple_voting(self):
        ed = lispify("2010 8.8.1991 on August the 8th 1991",
                     typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 20100000)')

    def test_date_with_range(self):
        # 2010 is in the given range, thus it will precede 8,8,1991
        ed = lispify("2010 8.9.1991 - 2012 on August the 8th 1991",
                     typecode="yyyymmdd")
        self.assertEqual(ed, '(:yyyymmdd 20100000)')

    def test_bool(self):
        self.assertEqual(lispify(True), 't')
        self.assertEqual(lispify(False), 'nil')

    def test_bool_with_typecode(self):
        self.assertEqual(lispify(False, typecode='calculated'),
                         '(:calculated nil)')

    def test_keyword(self):
        self.assertEqual(lispify(':feminine'), ":feminine")

    def test_string_not_keyword(self):
        self.assertEqual(lispify(':not a keyword'), '":not a keyword"')

    def test_keyword_with_typecode(self):
        self.assertEqual(lispify(':feminine', typecode='calculated'),
                         '(:calculated :feminine)')

    def test_dict(self):
        self.assertEqual(lispify({'a': 1, 'b': "foo"}),
                         '(:a 1 :b "foo")')

    def test_dict_with_escaped_string(self):
        self.assertEqual(lispify({'a': 1, 'b': '"foo"'}),
                         '(:a 1 :b "\\"foo\\"")')

    def test_dict_with_list(self):
        self.assertEqual(lispify({'a': 1, 'b': ['foo', 'bar']}),
                         '(:a 1 :b ("foo" "bar"))')

    def test_error(self):
        err = lispify({'symbol': 'sym', 'kw': dict(a=1, b=2, c='ha')},
                      typecode='error')
        self.assertEqual(err, '(:error sym :a 1 :b 2 :c "ha")')

    def test_error_from_exception(self):
        err = lispify(ValueError('Wrong thing'))
        self.assertEqual(err, '(:error ValueError :message "Wrong thing")')

    def test_none(self):
        self.assertEqual(lispify(None), 'nil')

    def test_none_with_typecode(self):
        self.assertEqual(lispify(None, typecode='calculated'),
                         '(:calculated nil)')

    def test_number(self):
        self.assertEqual(lispify(5), '5')

    def test_number_with_typecode(self):
        self.assertEqual(lispify(5, typecode='calculated'),
                         '(:calculated 5)')

if __name__ == '__main__':
    unittest.main()
