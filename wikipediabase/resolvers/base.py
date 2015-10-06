from wikipediabase.lispify import LispType
from wikipediabase.fetcher import Fetcher
from wikipediabase.provider import Provider

MIN_PRIORITY = 0


def check_resolver(fn):
    def decorator(self, *args, **kwargs):
        if self._should_resolve(*args, **kwargs):
            return fn(self, *args, **kwargs)
        else:
            return None

    return decorator


class BaseResolver(Provider):

    priority = 1

    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or Fetcher()

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

    def _should_resolve(self, symbol, attr, **kw):
        """
        Checks if this resolver applies to (symbol, attr)

        BaseResolver should always return True
        """
        return True

    @check_resolver
    def resolve(self, symbol, attr, **kwargs):
        """
        Resolve attr using a custom resolve function or provided methods

        Returns None if attr cannot be resolved or if this resolver should not
        resolve (symbol, attr)

        Do NOT override this method when subclassing BaseResolver. Instead,
        define a method prefixed by "resolve_" (e.g. "resolve_infobox).
        """
        custom_resolve = self._custom_resolve_fn()
        if custom_resolve:
            return custom_resolve(symbol, attr, **kwargs)

        if isinstance(attr, LispType):
            attr = attr.val
        else:
            attr = attr

        attr = attr.lower()
        if attr in self._resources:
            return self._resources[attr](symbol, attr)
