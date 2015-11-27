from .configuration import Configuration
from .item import BaseItem, VersionedItem

class AttributeFallback(object):
    """
    Python will always try to resolve an attribute traversing the
    class hierarchy until it finds a class that defines __getattr__
    and it will use that.

    In the case of set it first checks the class for a special way of
    setting attributes. That involves traversing the ancenstry tree
    fot a __setattr__ method. If that fails we fallback to
    instance_setattr1 which just sets the attribute in the
    instance (see instance_setattr Cpython's Objects/classobject.c)

    The problem is that with ConfigRefs we need to get the attributes
    we define from memory and when we ask for something we don't know
    about we should create a reference to that.

    As for setting attributes we want to be able to override
    attributes that are already in memory (ie the things we defined
    here) but we need to define new items in the configuration when
    something is not already in memory.

    To solve both these problems we define an ancestor to ConfigRef to
    handle the get/set trickery. This way all ConfigRef (and sons')
    methods will be evaluated before this class is queried. Also
    setting attributes will only be allowed for.

    To define anything that you want to behave in the tranditional way
    you need to define also as a class member. For example

        class A(AttributeFallback):
            nofallback = None
            def __init__(self):
                self.nofallback = "No Fallback"
                self.fallback = "value"
            def _setattr_fallback(self, attr, val):
                print "Setting:", attr, "to", val+"-wrapped"
                self.__dict__[attr] = val+"-wrapped"

         a = A() # Setting: fallback to value-wrapped

    """

    def __getattr__(self, attr):
        return self._getattr_fallback(attr)

    def __setattr__(self, attr, val):
        if hasattr(self.__class__, attr):
            self.__dict__[attr] = val
            return

        self._setattr_fallback(attr, val)

    def _setattr_fallback(self, attr, val):
        raise LookupError("Couldn't set '%s' in %s." % (attr, repr(self)))

    def _getattr_fallback(self, attr):
        raise LookupError("'%s' not found in %s." % (attr, repr(self)))


class WithArgsGenMixin(object):
    def with_args(self, *args, **kwargs):
        """
        For versioned items only. Apply arguments to the versioned
        item. This creates closures instead of explicitly holding the
        arguments.
        """

        def maybe_with_args(x):
            if isinstance(x, VersionedItem):
                return x.with_args(*args, **kwargs)

            return x

        return ShallowLensConfigRef(self, maybe_with_args)

class LensGenMixin(object):
    def lens(self, lens, *args, **kw):
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

        # Multilenses provide extra arguments and make no assumptions
        # about kw.
        def closure(*cargs, **ckw):
            ccargs = cargs + args
            cckw = kw.copy()
            cckw.update(ckw)

            return lens(*ccargs, **cckw)

        return LensConfigRef(self, closure)

    def __and__(self, argument):
        """
        Return a multilens that will pass argument as an extra argument to
        the lens. Argument will be derefernced if it is a reference
        before being passed.
        """

        return MultiLensConfigRef([self, argument])


class ConfigRef(AttributeFallback, WithArgsGenMixin, LensGenMixin):
    """
    Convenience class to provide configurations that change
    dynamically. Basically a reference to a configuration ref that is
    dereferenced on the fly. To evaluate something over the return
    value (eg. clear whitespaces) each time the ref is taken use
    lenses.
    """

    _config = None
    _path = None
    _children = None

    def __init__(self, config=None, path=None):
        """
        Create a reference to a member of a config object. The lens attribute
        """
        self._config = config
        self._path = path or []
        self._children = {}

    def _getattr_fallback(self, key):
        """
        Used as the
        """

        return ConfigRef(config=self._config, path=self._path + [key])

    def _setattr_fallback(self, key, val):
        """
        We can't realize the reference path so far, creating empty dicts
        where necessary and set the value to the final key because
        this way we may end up mutating a parent configuration. We
        need to make sure we are mutating only the local config and no
        parents.

        However this way we may be completely whiting out parents if
        we just put dicts in there. To fix this we will be putting as
        children configurations.
        """

        if self._config.frozen:
            raise TypeError("Can't set to frozen dict. Create child.")

        tip = self._config      # :: Configuration
        for k in self._path:
            if k not in tip._local.keys():
                tip[k] = Configuration(local={}, parent=tip.get(k, None))

            tip = tip[k]

        tip[key] = val

    def deref(self, eval_items=True):
        """
        Dereference the config ref that acts like a pointer. If it's a
        lazy ref evaluate it first.
        """

        if not self._config.frozen:
            raise TypeError("Freeze the underlying config before using.")

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
    _parent = None
    _lens = None

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
    For internal use. Like a lens only it does not eval the underlying
    item before applying lens. This is useful if our lens function
    acts on items instead of their underlying values.

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

    _arguments = None
    _lens = None

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
