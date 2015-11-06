from .item import BaseItem, VersionedItem

class ConfigRef(object):
    """
    Convenience class to provide configurations that change
    dynamically. Basically a reference to a configuration ref that is
    dereferenced on the fly. To evaluate something over the return
    value (eg. clear whitespaces) each time the ref is taken use
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
        Get a new ConfigRef that can be dereferenced.
        """
        if key.startswith('_'):
            return self.__dict__[key]

        return ConfigRef(config=self._config, path=self._path + [key])

    def __setattr__(self, key, val):
        """
        Realize the reference path so far, creating empty dicts where
        necessary and set the value to the final key.
        """

        if key.startswith('_'):
            return super(ConfigRef, self).__setattr__(key, val)

        tip = self._config
        for k in self._path:
            if k not in tip.keys():
                tip[k] = {}

            tip = tip[k]

        tip[key] = val


    def __and__(self, argument):
        """
        Return a multilens that will pass argument as an extra argument to
        the lens. Argument will be derefernced if it is a reference
        before being passed.
        """

        return MultiLensConfigRef([self, argument])

    def lens(self, lens):
        """
        Return a ConfigRef that when checked will use the provided
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

        If you need a closure pass them as args, kwargs and the lens
        will be evaluated like so:

           lens_callback(config_item, *args, **kwargs)

        """

        return LensConfigRef(self, lens)

    def with_args(self, *args, **kwargs):
        def maybe_with_args(x):
            if isinstance(x, VersionedItem):
                return x.with_args(*args, **kwargs)

            return x

        return ShallowLensConfigRef(self, maybe_with_args)

    def deref(self, eval_items=True):
        """
        Dereference the config ref that acts like a pointer. If it's a
        lazy ref evaluate it first.
        """

        # Each config ref knows it's path and the config that path
        # refers to so just follow the path starting from the config
        # object. Remember that the config object is just a dict of
        # dicts.

        ret = None
        try:
            ret = reduce(lambda obj, key: obj[key],
                         self._path,
                         self._config)

        except KeyError, e:
            raise KeyError("%s" % '.'.join(self._path))

        if isinstance(ret, BaseItem) and eval_items:
            return ret.eval()

        return ret

class LensConfigRef(ConfigRef):
    """
    Here is a demostrative example on how this is used:

    >>> Configuration({'hello': {'there': 2}}).ref.hello
    <__main__.ConfigRef object at 0x1074dfb50>
    >>> Configuration({'hello': 1}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2).deref()
    4
    >>> Configuration({'hello': 1}).ref.hello.lens(lambda x: x+1).lens(lambda x: x+2)
    <__main__.LensConfigRef object at 0x1074dfb10>
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

    def deref(self, eval_item=True):
        return self._lens(self._parent.deref(eval_item))

class ShallowLensConfigRef(LensConfigRef):
    """
    For internal use. Like a lens only it does not deref before
    applying lens.

    Note the case where the underlying ConfigItem changes and the lens
    will now raise an error. This case happens here:

    class A(object):
        hello = 'hello'

    cfg = Configuration({'hello': A()})
    ref = ConfigRef(cfg, ['a'])
    sref = ShallowLensConfigRef(ref, lambda a: a.hello)
    print sref.deref()
    cfg['a'] = 1
    print sref.deref() # error
    """
    def deref(self, eval_item=True):
        item = self._lens(self._parent.deref(False))

        if eval_item and isinstance(item, BaseItem):
            return item.eval()

        return item


class MultiLensConfigRef(ConfigRef):
    """
    Many arguments to a lens
    """

    def __init__(self, arguments, lens=None):
        self._lens = lens
        self._arguments = arguments

    def __and__(self, arg):
        return MultiLensConfigRef(self._arguments + [arg])

    def lens(self, lens):
        if self._lens is not None:
            return super(MultiLensConfigRef, self).lens(lens)

        return MultiLensConfigRef(self._arguments, lens=lens)

    def eval_argument(self, argument, eval_item):
        if isinstance(argument, ConfigRef):
            return argument.deref(eval_item)

        return argument

    def deref(self, eval_item=True):
        if self._lens is None:
            raise Exception("Did not define lens.")

        return self._lens(*[self.eval_argument(p, eval_item)
                            for p in self._arguments])
