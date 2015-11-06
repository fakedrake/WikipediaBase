from random import random

from .ref import ConfigRef

class Configuration(object):
    """
    A configuration is a key-value container that can have
    children. The local config has precedence over children. A later
    child gets prescedence over a previous child.
    """

    def __init__(self, local=None, parent=None):
        self._local = local or {}
        self._parent = parent
        self._id = random()
        self.ref = ConfigRef(self)

    def __hash__(self):
        return self._id

    def __contains__(self, val):
        return val in list(self.keys())

    def child(self, data=None):
        return Configuration(local=data or {}, parent=self)

    def keys(self):
        return list(set((self._parent.keys() if self._parent else []) + \
                        self._local.keys()))

    def __setitem__(self, key, val):
        self._local[key] = val

    def get(self, key, default=None):
        if key in self._local:
            return self._local[key]

        if self._parent:
            return self._parent.get(key, default)

        return default


    def __getitem__(self, key):
        ret = self.get(key, None)
        if ret is None:
            raise KeyError()

        return ret
