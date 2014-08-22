from itertools import chain

from log import Logging
from .util import memoized


def provide(name=None, memoize=True):
    """
    Argumented decorator for methods of providers to be automagically
    provided. It also may provide memoization. The returned functions
    are unbound.
    """

    def decorator(fn):
        fn._provided = name.lower() if name else name
        if memoize:
            return memoized(fn)
        else:
            return fn

    return decorator


class ProviderMeta(type):

    def __new__(meta, clsname, bases, clsDict):
        """
        Create pw_<name> for each resource that is to be provided. 'pw' is
        provide wrapped.
        """

        provided = []
        newDict = clsDict.copy()

        # Look for your marked resources
        for k, v in clsDict.iteritems():
            if hasattr(v, "_provided"):
                # pair: resource_name, python_name
                provided.append((v._provided or k, k))

        # Inherit resources from parent
        for b in bases:
            if hasattr(b, 'meta_resources'):
                provided.extend(b.meta_resources)

        newDict["meta_resources"] = provided
        return type.__new__(meta, clsname, bases, newDict)


class Provider(Logging):

    """
    Can provide a dictionary of resources managed by name. Resources
    can be anything but most of the time they will be callables.
    """

    __metaclass__ = ProviderMeta

    def __init__(self, resources={}, acquirer=None, *args, **kwargs):
        self._resources = {}

        for k, f in self.meta_resources:
            self._resources[k] = getattr(self, f)

        self._resources.update(resources)

        if acquirer:
            self.provide_to(acquirer)

    def provide(self, name, resource):
        """
        Provide 'resource' under name.
        """

        self._resources[name] = resource

    def provide_to(self, acquirer):
        return acquirer.acquire_from(self)


class Acquirer(Provider):
    """
    An aquirer is also a provder by default to itself. Any methods an
    acquirer privides are available to itself.
    """


    def __init__(self, providers=None, *arg, **kw):
        super(Acquirer, self).__init__(*arg, **kw)
        self._providers = (providers or []) + [self]

    def iter_resources(self):
        for p in self._providers:
            for r in p.iter_resources():
                yield r

    def resources(self):
        """
        Get a dict of all the resources from all providers.
        """

        return dict(chain(*[p._resources.items() for p in self._providers]))

    def acquire_from(self, provider, name=None):
        """
        Register 'provider' as provider of resources under 'name'.
        """

        self._providers.append(provider)
