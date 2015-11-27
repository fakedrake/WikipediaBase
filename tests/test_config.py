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

from wikipediabase.config import *

class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        conf = Configuration()
        conf['a'] = 1
        self.assertEqual(conf['a'], 1)
        self.assertEqual(conf.get('a', 3), 1)
        self.assertEqual(conf.get('b', 3), 3)

    def test_parent_setting(self):
        cfg = Configurable()
        cfgr = ConfigRef()
        cfgr.deref = lambda : "hello"
        cfg.ref = cfgr
        self.assertEqual(cfg.ref, "hello")

    def test_children(self):
        root = Configuration({'isroot': True})
        default = root.child({'isroot': False})
        test = default.child({'type': 'test'})
        libconfig = default.child({'type': 'lib'})
        appconfig = libconfig.child({'type': 'app'})

        self.assertEqual(libconfig['type'], 'lib')
        self.assertEqual(appconfig['type'], 'app')
        self.assertEqual(test['type'], 'test')
        self.assertEqual(test['isroot'], False)
        self.assertEqual(appconfig['isroot'], False)
        self.assertEqual(root['isroot'], True)

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

        sf = SubclassesItem(A)
        self.assertEqual([i.name for i in sf.eval()], ['B', 'C'])

        # Also classes defined later
        class E(B):
            def __init__(self):
                self.name = 'E'

        # And one with a higher priority
        class F(B):
            priority = 10
            def __init__(self):
                self.name = 'F'

        self.assertEqual([i.name for i in sf.eval()], ['F', 'B', 'C', 'E'])

        # Also caching: we wont get a new instance each time:
        sf.eval()[0].name = 'new_name'
        self.assertEqual([i.name for i in sf.eval()], ['new_name', 'B', 'C', 'E'])

    def test_subclass_methods(self):
        this = self
        class A(Configurable):
            def __init__(self, config):
                self.hello = config.ref.hello

            def top_method(self):
                return 0xdeadbeef

        class B(A): pass
        b = B(Configuration({'hello': 1}))
        self.assertEqual(b.top_method(), 0xdeadbeef)

    def test_references(self):
        this = self
        class A(Configurable):
            def __init__(self, config):
                self.hello = config.ref.hello

            def top_method(self):
                return 0xdeadbeef


        cfg = Configuration().freeze()
        a = A(cfg)

        with self.assertRaises(KeyError):
            tmp = a.hello + 1

        cfg['hello'] = 1
        self.assertIn('hello', a.local_config_scope)
        self.assertEqual(a.hello, 1)
        a.hello = 2
        self.assertNotIn('hello', a.local_config_scope)
        self.assertEqual(a.hello, 2)

        cfg = cfg.child()
        cfg.ref.hello = 3
        cfg.freeze()
        self.assertEqual(a.hello, 2,
                         "The attribute is no longer a reference to config")


    def test_refsetting(self):
        cfg = Configuration()

        cfg.ref.hello.there.guvnah = 3
        cfg.ref.hello.there.chris = 4
        self.assertEqual(cfg['hello']['there']['guvnah'], 3)
        self.assertEqual(cfg['hello']['there']['chris'], 4)

    def test_lenses(self):
        # Multiple lenses can be stacked
        cfg = Configuration({'hello': 1}).freeze()
        self.assertEqual(cfg.ref.hello.lens(lambda x: x+1).lens(lambda x: x+2).deref(), 4)

        # Lenses do not affect the ability to create further
        # references
        cfg = Configuration({'hello': 1, 'hi': {'there': 0}}).freeze()
        lens1 = cfg.ref.hi.there.lens(lambda x: x+1)
        lens2 = lens1.lens(lambda x: x+2)
        self.assertEqual(lens2.deref(), 3)

        # Non lensed stuff still works
        self.assertEqual(Configuration({'hello': 1}). \
                         freeze().ref.hello.deref(), 1)

        # Lens closure with extra args
        conf = Configuration({'num': 1, 'subtract': 1}).freeze()
        self.assertEqual((conf.ref.num & 1).lens(lambda n, s: n-s).deref(), 0)

    def test_multilenses(self):
        cfg = Configuration({'a': 1, 'b':2, 'c':3}).freeze()
        multilens = (cfg.ref.a & cfg.ref.b & cfg.ref.c).lens(lambda a, b, c: a+b+c)
        self.assertEqual(multilens.deref(), 6)

    def test_versioned_items(self):
        def constructor(x):
            constructor.times_called += 1
            return "Item:" + x

        # Side effect to keep track of how often this is called.
        constructor.times_called = 0

        # Creates an item that is constructed by calling the
        # constructor
        item = VersionedItem(constructor, 'first')
        self.assertEqual(item.eval(), "Item:first")
        self.assertEqual(constructor.times_called, 1)

        # Calling with the same args just returns the original
        item2 = item.with_args('first')
        self.assertEqual(item2.eval(), "Item:first")
        self.assertEqual(constructor.times_called, 1)

        # We can actually have multiple (more than one) versions of an
        # object
        item3 = item.with_args('second')
        self.assertEqual(item3.eval(), "Item:second")
        self.assertEqual(constructor.times_called, 2)

        # Versions of the item are also versioned items
        item31 = item3.with_args('3.1')
        self.assertEqual(item31.eval(), "Item:3.1")
        self.assertEqual(constructor.times_called, 3)

        # All this time the original item did not change it's state
        self.assertEqual(item.eval(), "Item:first")
        self.assertEqual(constructor.times_called, 3)
        self.assertEqual(item3.eval(), "Item:second")
        self.assertEqual(constructor.times_called, 3)
        self.assertEqual(item.eval(), "Item:first")
        self.assertEqual(constructor.times_called, 3)

        # references
        cfg = Configuration()
        class A(Configurable):
            pass

        # We can configure configurables
        cfg.ref.item = item3
        cfg.freeze()

        a = A()
        a.item = cfg.ref.item
        self.assertEqual(a.item, "Item:second")
        self.assertEqual(constructor.times_called, 3)

        # And get new versions of the items
        a.item = cfg.ref.item.with_args('third')
        self.assertEqual(a.item, "Item:third")
        self.assertEqual(constructor.times_called, 4)

        # Or assert that we use already existing ones
        a.item = cfg.ref.item.with_args('second')
        self.assertEqual(a.item, "Item:second")
        self.assertEqual(constructor.times_called, 4)

        # Get versioned from other configs
        child = cfg.child()
        child.ref.item = cfg.ref.item.with_args('third').deref()
        child.freeze()
        a.deep = child.ref.item
        self.assertEqual(a.deep, "Item:third")
        self.assertEqual(constructor.times_called, 4)

        ### Configurations are not mutable anymore.
        # # And when we change the config to a non-versioned item that
        # # is handled accordingly
        # cfg.ref.item = 'hello'
        # self.assertEqual(a.item, "hello")
        # self.assertEqual(constructor.times_called, 4)

        # # A 'downside' of versioned items is that the configurable now
        # # has a reference to an item that is not directly accessible
        # # by the configuration. Therefore changing the configuration
        # # will have no effect on the configurable's percieved
        # # state.
        # cfg.ref.item = item
        # self.assertEqual(a.item, "Item:second")
        # self.assertEqual(constructor.times_called, 4)
        ###

        # For this reason, and in general to avoid state handling and
        # sharing, the user is strongly discouraged from editing the
        # configuration. Instead you are advised to create config
        # children and create from scratch. (A case where the
        # configuration is passed to the configurable would be much
        # more demostrative)
        cfg1 = cfg.child().freeze()
        a1 = A()
        self.assertEqual(a.item, "Item:second")
        a1.item = cfg1.ref.item.with_args('first')
        self.assertEqual(a.item, "Item:second")
        self.assertEqual(a1.item, "Item:first")
        self.assertEqual(constructor.times_called, 5)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
