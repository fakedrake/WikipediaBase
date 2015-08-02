"""
Basically a tree of dicts whereby you can access all children from
a root dict. Children are prioritized by the order they are added.
"""

from random import random
from itertools import chain

class Configuration(object):
    """
    A configuration is a key-value container that can have
    children. The local config has precedence over children. A later
    child gets prescedence over a previous child.
    """

    def __init__(self, local=None):
        self.local = local or {}
        self.children = []
        self.id = random()

    def __hash__(self):
        return self.id

    def remove_child(self, child_conf):
        self.children = [c for c in self.children if c is not child_conf]
        return self.children

    def add_child(self, child_conf):
        self.children.insert(0, child_conf)
        return self.children

    def keys(self):
        return list(chain.from_iterable((c.keys for c in self.children)))

    def __setitem__(self, key, val):
        self.local[key] = val

    def get(self, key, default=None, blacklist=None):

        # Make sure we have not been seached before
        if blacklist is None:
            blacklist = set([self])
        else:
            if self in blacklist:
                return default

            blacklist.add(self)

        ret = self.local.get(key, None)
        if ret is not None:
            return ret

        for c in self.children:
            if isinstance(c, Configuration):
                val = c.get(key, None, blacklist)
            else:
                val = c.get(key, None)

            if val:
                return val

        return default

    def __getitem__(self, key):
        ret = self.get(key, None)
        if ret is None:
            raise KeyError()

        return ret


class MethodConfiguration(Configuration):
    """
    If a value of a key is a method then we should call the method
    itself.
    """

    def __init__(self, *args, **kwargs):
        super(MethodConfiguration, self).__init__(*args, **kwargs)
        class Local(dict):
            def get(self, key, default=None):
                val = dict.get(self, key, default)
                if hasattr(val, '__call__'):
                    return val()

                return val

        self.local = Local()

class SubclassesFactory(object):
    """
    A factory for subclasses. The point of this is that imported
    modules may create subclasses that implementa basic interfaces. We
    want to include those on demand.
    """

    def __init__(self, cls, instantiate=True):
        """
        Provide the class that we will on-demand get the subclasses of. If
        instantate is true. Get instances of that class. Instances are
        created once and cached.
        """

        self.cls = cls
        self.instantiate = instantiate
        self.instances_dict = {}

    def all_subclasses(self, cls, including=True):
        """
        Recursively get all subclasses of this including this one or not
        depending on the including keyword argument.
        """

        return ([cls] if including else []) + \
            list(chain.from_iterable((self.all_subclasses(c) for
                                      c in cls.__subclasses__())))

    def get_instance(self, cls, **kw):
        """
        Create an instance of a class and cache it.
        """
        ret = self.instances_dict.get(cls, None)
        if ret is not None:
            return ret

        ret = cls(**kw)
        self.instances_dict[cls] = ret
        return ret


    def __call__(self, **kw):
        """
        Do the actual work of getting what was defined in init.
        """

        # Get all subclasses but not the root as it is just a dummy
        # baseclass
        rcls = self.all_subclasses(self.cls, including=False)

        # Make sure priorities are defined and sort the subclasses
        for c in rcls:
            assert isinstance(c.priority, int), \
                "type(%s . priority) = %s != int" % (repr(c), type(c.priority.name))

        clss = sorted(rcls, key=lambda c: c.priority, reverse=True)

        if not self.instantiate:
            return [C for C in clss
                    if not C.__name__.startswith("_")]

        return [self.get_instance(C, **kw) for C in clss
                if not C.__name__.startswith("_")]

# A global configuration that everyone can use
configuration = Configuration()

# Register all interfaces. See the test for how to do it.
interfaces = MethodConfiguration()
configuration.add_child(interfaces)
__all__ = ['configuration', 'interfaces']
