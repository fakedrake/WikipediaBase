from wikipediabase.lispify import lispify, LispType
from wikipediabase.provider import Provider

MIN_PRIORITY = 0


def check_resolver(fn):
    def decorator(self, cls, *args, **kwargs):
        if self._should_resolve(cls):
            return fn(self, cls, *args, **kwargs)
        else:
            return None

    return decorator


class BaseResolver(Provider):

    priority = 1

    def __init__(self, *args, **kwargs):
        super(BaseResolver, self).__init__(*args, **kwargs)

        self._tag = None

    def _custom_resolve_fn(self):
        resolve_fns = [getattr(self, f) for f in dir(self)
                       if f.startswith('resolve_')]
        if resolve_fns:
            if len(resolve_fns) > 1:
                self.log().warn("%s has more than one custom resolve function. "
                                "Choosing '%s'.",
                                self.__class__,
                                resolve_fns[-1].__name__)
            return resolve_fns[-1]

    def _should_resolve(self, cls):
        """
        Checks if this resolver applies to cls

        BaseResolver should always return True
        """
        return True

    @check_resolver
    def resolve(self, cls, symbol, attr):
        """
        Resolve attr using a custom resolve function or provided methods

        Returns None if attr cannot be resolved or if this resolver should not
        resolve (symbol, attr)

        Do NOT override this method when subclassing BaseResolver. Instead,
        define a method prefixed by "resolve_" (e.g. "resolve_infobox).
        """
        custom_resolve = self._custom_resolve_fn()
        if custom_resolve:
            return custom_resolve(cls, symbol, attr)

        if isinstance(attr, LispType):
            attr = attr.val
        else:
            attr = attr

        attr = attr.lower()
        if attr in self._resources:
            return self._resources[attr](symbol, attr)

    @check_resolver
    def attributes(self, cls, symbol):
        """
        Get a list of lispified attributes that the resolver provides
        """
        return lispify([dict(code=a.upper()) for a in self._resources.keys()])
