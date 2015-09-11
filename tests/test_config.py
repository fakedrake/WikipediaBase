#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `config` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from wikipediabase.config import Configuration, MethodConfiguration, SubclassesFactory, Configurable

class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        conf = Configuration()
        conf['a'] = 1
        self.assertEqual(conf['a'], 1)
        self.assertEqual(conf.get('a', 3), 1)
        self.assertEqual(conf.get('b', 3), 3)

    def test_children(self):
        conf = Configuration()
        child0 = Configuration({'a':1, 'b': 2})
        child1 = {'a':2, 'c': 3}
        conf['d'] = 4
        conf.add_child(child0)
        conf.add_child(child1)
        self.assertEqual(conf['a'], 2)
        self.assertEqual(conf['b'], 2)
        self.assertEqual(conf['c'], 3)
        self.assertEqual(conf['d'], 4)
        conf.remove_child(child1)
        self.assertEqual(conf['a'], 1)
        self.assertEqual(conf['b'], 2)

    def test_method(self):
        conf = MethodConfiguration()
        conf['a'] = lambda : 1
        conf['b'] = 2

        self.assertEqual(conf['a'], 1)
        self.assertEqual(conf['b'], 2)

    def test_keys(self):
        conf = Configuration({'a': 1, 'b': 2})
        self.assertEqual(conf.keys(), ['a','b'])

    def test_subclass(self):
        class A(object):
            priority = 1

        class B(A):
            def __init__(self):
                self.name = 'B'

        class C(B):
            def __init__(self):
                self.name = 'C'

        class _D(B):
            def __init__(self):
                self.name = 'D'

        sf = SubclassesFactory(A)
        self.assertEqual([i.name for i in sf()], ['B', 'C'])

        # Also classes defined later
        class E(B):
            def __init__(self):
                self.name = 'E'

        # And one with a higher priority
        class F(B):
            priority = 10
            def __init__(self):
                self.name = 'F'

        self.assertEqual([i.name for i in sf()], ['F', 'B', 'C', 'E'])

        # Also caching: we wont get a new instance each time:
        sf()[0].name = 'new_name'
        self.assertEqual([i.name for i in sf()], ['new_name', 'B', 'C', 'E'])

    def test_references(self):
        this = self
        class A(Configurable):
            def __init__(self, config):
                self.hello = config.ref.hello

        cfg = Configuration()
        a = A(cfg)

        with self.assertRaises(KeyError):
            tmp = a.hello + 1

        cfg['hello'] = 1
        self.assertEqual(a.hello, 1)

    def test_refsetting(self):
        cfg = Configuration()

        cfg.ref.hello.there.guvnah = 3
        cfg.ref.hello.there.chris = 4
        self.assertEqual(cfg['hello']['there']['guvnah'], 3)
        self.assertEqual(cfg['hello']['there']['chris'], 4)

    def test_lenses(self):
        # Multiple lenses can be stacked
        self.assertEqual(Configuration({'hello': 1}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2).deref(), 4)

        # Lenses do not affect the abuility to create further
        # references
        self.assertEqual(Configuration({'hello': 1, 'hi': {'there': 0}}).ref.hi.lens(lambda x: x+1).lens(lambda x: x+2).there.deref(), 0)

        # Non lensed stuff still works
        self.assertEqual(Configuration({'hello': 1}).ref.hello.deref(), 1)

        # Lens closure with extra args
        self.assertEqual(Configuration({'num': 1}).subtract.lens(lambda n, s: n-s, 1).deref(), 0)

    def test_multilenses(self):
        cfg = Configuration({'a': 1, 'b':2, 'c':3})
        multilens = (cfg.ref.a & cfg.ref.b & cfg.ref.c).lens(lambda a, b, c: a+b+c)
        self.assertEqual(multilens.deref(), 6)
        cfg.ref.a = 11
        self.assertEqual(multilens.deref(), 16)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
