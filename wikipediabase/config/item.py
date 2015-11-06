from itertools import chain

class BaseItem(object):
    def eval(self):
        raise NotImplementedError("Subclass this")

class LazyItem(BaseItem):
    """
    An ref that is not evaluated until it's first dereference. Then
    you can call it with with_args
    """

    def __init__(self, constructor, *args, **kwargs):
        """
        The consgructor is called once when the ref is first
        dereferenced. the dereferenced attribute is false and will be
        true when the item is realized. Set it to a callable to make
        ypur own deref policy.
        """

        self.constructor = constructor
        self.value = None
        self._dereferenced = False
        self.value_args = self.immutable_args(*args, **kwargs)

    def dereferenced(self):
        return self._dereferenced

    @staticmethod
    def immutable_args(*args, **kw):
        """
        Immutable and hashable versions of arguments. For objects this
        only keeps references.
        """
        return (tuple(args), tuple(kw.iteritems()))

    def eval(self):
        if self.dereferenced():
            return self.value

        args, kwargs = self.value_args
        args = list(args)
        kwargs = dict(kwargs)

        self.value = self.constructor(*args, **kwargs)
        self._dereferenced = True
        return self.value

class VersionedItem(LazyItem):
    """
    A LazyItem that can create and remember different versions of
    itself with with_args. This is also useful as an object cache.

    Versioned items are sort of like tree structures
    """
    def __init__(self, constructor, *args, **kwargs):
        super(VersionedItem, self).__init__(constructor, *args, **kwargs)
        self.cache = {}

    def new_item(self, *args, **kw):
        ret = VersionedItem(self.constructor, *args, **kw)
        ret.cache = self.cache
        return ret

    def with_args(self, *args, **kw):
        """
        If there is no change in the arguments return self, otherwise
        create a new LazyItem.
        """

        new_args = self.immutable_args(*args, **kw)
        # It's a common case that we ask the same object over and
        # over.
        if self.value_args == new_args:
            return self

        # We have created this object again
        if new_args in self.cache:
            return self.cache[new_args]

        # We have to create the object from scratch
        ret = VersionedItem(self.constructor, *args, **kw)
        ret.cache = self.cache
        self.cache[new_args] = ret
        return ret


class SubclassesItem(VersionedItem):
    """
    A factory for subclasses. The point of this is that imported
    modules may create subclasses that implementa basic interfaces. We
    want to include those on demand.
    """

    def __init__(self, cls, instantiate=True, **kw):
        """
        Provide the class that we will on-demand get the subclasses of. If
        instantate is true. Get instances of that class. Instances are
        created once and cached.
        """

        super(SubclassesItem, self).__init__(self._constructor, **kw)
        self.cls = cls
        self.instantiate = instantiate
        self.instance_dict = {}

    def all_subclasses(self, cls, including=True):
        """
        Recursively get all subclasses of this including this one or not
        depending on the including keyword argument.
        """

        return ([cls] if including else []) + \
            list(chain.from_iterable((self.all_subclasses(c) for
                                      c in cls.__subclasses__())))

    def get_instance(self, cls, *args, **kw):
        if cls in self.instance_dict:
            return self.instance_dict[cls]

        ret = cls(*args, **kw)
        self.instance_dict[cls] = ret
        return ret

    def dereferenced(self):
        return set(self.all_subclasses(self.cls)) == set(self.instance_dict.keys())

    def _constructor(self, *args, **kwargs):
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

        # Return the list
        if not self.instantiate:
            return [C for C in clss
                    if not C.__name__.startswith("_")]

        return [self.get_instance(C, *args, **kwargs) for C in clss
                if not C.__name__.startswith("_")]
