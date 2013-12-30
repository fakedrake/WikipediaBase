from itertools import chain


class Aquirer(object):
    def __init__(self, providers=None):
        self._providers = providers or []

    def iter_resources(self):
        for p in self._providers:
            for r in p.iter_resources():
                yield r

    def resources(self):
        """
        Get a dict of all the resources from all providers.
        """

        return dict(chain(*[p._resources.items() for p in self._providers]))

    def aquire_from(self, provider, name=None):
        """
        Register 'provider' as provider of resources under 'name'.
        """

        self._providers.append(provider)

def provide(name=None):
    """
    Decorator for methods of providers to be automagically provided.
    """

    def wrap(fn):
        fn._provided = name
        return fn

    return wrap



class ProviderMeta(type):
    def __new__(meta, clsname, bases, clsDict):
        """
        Create pw_<name> for each resource that is to be provided. 'pw' is
        provide wrapped.
        """

        provided = []
        newDict = clsDict.copy()

        for k,v in clsDict.iteritems():
            if hasattr(v, "_provided"):
                provided.append((v._provided or k, k))

        newDict["meta_resources"] = provided
        return type.__new__(meta, clsname, bases, newDict)



class Provider(object):
    """
    Can provide a dictionary of resources managed by name. Resources
    can be anything but most of the time they will be callables.
    """

    __metaclass__ = ProviderMeta

    def __init__(self, resources={}, aquirer=None, *args, **kwargs):
        self._resources = {}

        for k,f in self.meta_resources:
            self._resources[k] = getattr(self, f)

        self._resources.update(resources)

        if aquirer:
            self.provide_to(aquirer)

    def provide(self, name, resource):
        """
        Provide 'resource' under name.
        """

        self._resources[name] = resource

    def provide_to(self, aquirer):
        return aquirer.aquire_from(self)
