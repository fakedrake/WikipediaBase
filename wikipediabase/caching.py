from wikipediabase.config import Configurable, configuration

class cached(object):
    """
    Decorator that will persistently memoize the function. Used mainly
    on functions with internet access.
    """

    def __init__(self, *local_keys):
        """
        Pass the local keys that define the state that this function
        depends on.
        """

        self.method = CachedMethod(local_keys)

    def __call__(self, func):
        """
        Pass the function.
        """
        return self.method.function(func)

class CachedMethod(object):
    def __init__(self, local_keys_used=None, function=None, _self=None):
        """
        :param local_keys_used: The attributes of self that the underlying
        method uses. They are used to create separate entries based on
        the self object's state.
        :param function: The underlying function.
        """
        self._local_keys_used = local_keys_used
        self._function = function
        self._self = _self

    def copy(self, **kw):
        return CachedMethod(
            local_keys_used=kw.get("local_keys_used", self._local_keys_used),
            function=kw.get("function", self.function),
            _self=kw.get("_self", self._self))

    def function(self, function):
        return self.copy(function=function)

    def local_keys(self, local_keys_used):
        return self.copy(local_keys_used=local_keys_used)

    def __get__(self, instance, owner):
        # We mutate instead of creating a new one each time so that
        #    a.cachedmethod is a.cachedmethod
        # succeeds
        self._self = instance
        assert isinstance(self._self, Caching), \
            "Only caching objects can have cached methods"

        return self

    def __call__(self, *args, **kw):
        local_state = [(k, getattr(self._self, k)) for k in self._local_keys_used]
        func = self._function
        return self._self.cache_manager.maybe_call(func, (args, kw),
                                                   state=local_state,
                                                   _self=self._self)

class CacheKey(object):
    def __init__(self, func, args, kwargs, local_state):
        self.local_state = tuple(local_state)
        self.args = tuple(args)
        self.kwargs = tuple(kwargs.items())
        self.func = func

    def __hash__(self):
        return hash((self.local_state,
                     self.args,
                     self.kwargs,
                     self.func))

class Caching(Configurable):
    def __init__(self, configuration=configuration):
        self.cache_manager = configuration.ref.cache.cache_manager

class NoCacheManager(Configurable):
    """
    A cache manager that does not cache anything.
    """
    def __init__(self, configuration):
        pass

    def maybe_call(self, func, (args, kw), state, _self):
        return func(_self, *args, **kw)


class DictCacheManager(NoCacheManager):
    """
    A cache manager that uses a simple dict-like object to cache.
    """

    def __init__(self, dict_like=None):
        self.cache = dict_like or {}

    def maybe_call(self, func, (args, kw), state, _self):
        key = hash(CacheKey(func, args, kw, state))
        if key in self.cache:
            return self.cache[key]

        ret = super(DictCacheManager, self).maybe_call(func, (args, kw),
                                                       state=state,
                                                       _self=_self)
        self.cache[key] = ret
        return ret
