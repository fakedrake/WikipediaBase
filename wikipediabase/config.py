"""
Basically a tree of dicts whereby you can access all children from
a root dict. Children are prioritized by the order they are added.
"""

from random import random
from itertools import chain

class ConfigItem(object):
    """
    Convenience class to provide configurations that change
    dynamically. Basically a reference to a configuration item that is
    dereferenced on the fly. To evaluate something over the return
    value (eg. clear whitespaces) each time the item is taken use
    lenses.
    """

    def __init__(self, config=None, path=None):
        """
        Create a reference to a member of a config object. The lens attribute
        """
        self._config = config
        self._path = path or []

    def __getattr__(self, key):
        """
        Get a new ConfigItem that can be dereferenced.
        """
        if key.startswith('_'):
            return self.__dict__[key]

        return ConfigItem(config=self._config, path=self._path + [key])

    def __setattr__(self, key, val):
        """
        Realize the reference path so far, creating empty dicts where
        necessary and set the value to the final key.
        """

        if key.startswith('_'):
            return super(ConfigItem, self).__setattr__(key, val)

        tip = self._config
        for k in self._path:
            if k not in tip.keys():
                tip[k] = {}

            tip = tip[k]

        tip[key] = val


    def __and__(self, config_item):
        return MultiLensConfigItem([self, config_item])

    def lens(self, lens):
        """
        Return a ConfigItem that when checked will use the provided
        lens function to deref. Eg

        >>> class A(Configurable):
        ...     def __init__(self, cfg):
        ...             self.hello = cfg.ref.hello.lens(lambda x: x+1)
        ...
        >>> cfg = Configuration()
        >>> a = A(cfg)
        >>> cfg['hello'] = 1
        >>> a.hello
        2

        This can be used for example to remove trailing whitespaces
        from config strings.
        """

        return LensConfigItem(parent=self, lens=lens)

    def deref(self, lens=None):
        try:
            return reduce(lambda obj, key: obj[key], self._path, self._config)
        except KeyError, e:
            raise KeyError("%s" % '.'.join(self._path))


class LensConfigItem(ConfigItem):
    """
    Here is a demostrative example on how this is used:

    >>> Configuration({'hello': {'there': 2}}).ref.hello
    <__main__.ConfigItem object at 0x1074dfb50>
    >>> Configuration({'hello': 1}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2).deref()
    4
    >>> Configuration({'hello': 1}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2)
    <__main__.LensConfigItem object at 0x1074dfb10>
    >>> Configuration({'hello': {'there': 2}}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2).there.deref()
    2
    """
    def __init__(self, parent, lens):
        self._parent = parent
        self._lens = lens

    @property
    def _config(self):
        return self._parent._config

    @property
    def _path(self):
        return self._parent._path

    def deref(self):
        return self._lens(self._parent.deref())

class MultiLensConfigItem(ConfigItem):
    """
    Combine many lenses together.
    """

    def __init__(self, parents, lens=None):
        self._lens = lens
        self._parents = parents

    def __and__(self, config_item):
        return MultiLensConfigItem(self._parents + [config_item])

    def lens(self, lens):
        if self._lens is not None:
            return super(MultiLensConfigItem, self).lens(lens)

        return MultiLensConfigItem(self._parents, lens=lens)

    def deref(self):
        if self._lens is None:
            raise Exception("Did not define lens.")

        return self._lens(*[p.deref() for p in self._parents])

class Configurable(object):
    """
    Superclass of an object that can have attributes that are
    references to a configuration object. They are evaluated lazily so
    changing the configuration in runtime will immediately change the
    entire system's behavior.
    """

    def __setattr__(self, attr, val):
        if self.__dict__.get('local_config_scope', None) is None:
            self.__dict__['local_config_scope'] = {}

        lcs = self.__dict__['local_config_scope']
        if isinstance(val, ConfigItem):
            lcs[attr] = val
            return

        super(Configurable, self).__setattr__(key, val)

    def __getattr__(self, attr):
        lcs = self.__dict__.get('local_config_scope', {})
        if attr in lcs:
            return lcs[attr].deref()

        return super(Configurable, self).__getattr__(attr)


class Configuration(object):
    """
    A configuration is a key-value container that can have
    children. The local config has precedence over children. A later
    child gets prescedence over a previous child.
    """

    def __init__(self, local=None):
        self._local = local or {}
        self._children = []
        self._id = random()
        self.ref = ConfigItem(self)

    def __hash__(self):
        return self._id

    def __contains__(self, val):
        return val in list(self.keys())

    def remove_child(self, child_conf):
        self._children = [c for c in self._children if c is not child_conf]
        return self._children

    def add_child(self, child_conf):
        self._children.insert(0, child_conf)
        return self._children

    def keys(self):
        return list(chain.from_iterable((c.keys() for c in self._children))) + \
            self._local.keys()

    def __setitem__(self, key, val):
        self._local[key] = val

    def get(self, key, default=None, blacklist=None):

        # Make sure we have not been seached before
        if blacklist is None:
            blacklist = set([self])
        else:
            if self in blacklist:
                return default

            blacklist.add(self)

        ret = self._local.get(key, None)
        if ret is not None:
            return ret

        for c in self._children:
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

        self._local = Local()

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
