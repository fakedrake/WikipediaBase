"""
Some persistent maps (gdbm) require special encoding of keys
and/or values. This is an abstraction for these kinds of quirks.
"""

from itertools import imap

import collections
import gdbm as dbm
import os

class EncodedDict(collections.MutableMapping):
    """
    Subclass this and provide _encode_key and maybe a reverse
    _decode_key.
    """

    def __init__(self, wrapped=None):
        self.db = wrapped if wrapped is not None else dict()

    def _encode_key(self, key):
        """
        Override to encode keys coming in.
        """
        return key

    def _decode_key(self, key):
        """
        Override to encode keys going out.
        """
        return key

    def __setitem__(self, key, val):
        file("/tmp/sizes.log", 'a').write('Setting: key: %d, val: %d\n' % (len(key), len(val)))
        self.db[self._encode_key(key)] = val

    def __getitem__(self, key):
        return self.db[self._encode_key(key)]

    def __contains__(self, key):
        return self._encode_key(key) in self.db

    def __delitem__(self, key):
        del self.db[self._encode_key(key)]

    def __iter__(self):
        return imap(self._decode_key, self.db)

    def __len__(self):
        return len(self.db)

    def keys(self):
        return [i for i in self]

    def values(self):
        return self.db.values()

    def items(self):
        return [(self._decode_key(k), v) for key in self.db]


class PersistentDict(EncodedDict):
    """
    Persistent dict using dbm. Will open or create filename.
    """

    def __init__(self, filename):
        flag = 'w' if os.path.exists(filename) else 'n'
        super(PersistentDict, self).__init__(dbm.open(filename, flag))

    def _encode_key(self, key):
        if isinstance(key, unicode):
            return key.encode('unicode_escape')

        return str(key)

    def _decode_key(self, key):
        return key.decode('unicode_escape')
