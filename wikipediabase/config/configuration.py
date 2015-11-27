from random import random


class Configuration(object):
    """
    A transparent dict that falls back to parent configurations in
    case of missing keys.
    """

    def __init__(self, local=None, parent=None):
        self._local = local or {}
        self._parent = parent
        self._id = random()
        self.frozen = False

        from .ref import ConfigRef
        self.ref = ConfigRef(self)

    def freeze(self):
        self.frozen = True
        return self

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
