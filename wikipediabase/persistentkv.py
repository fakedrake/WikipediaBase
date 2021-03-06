"""
Some persistent maps (gdbm) require special encoding of keys
and/or values. This is an abstraction for these kinds of quirks.
"""

from itertools import imap

import collections
import gdbm as dbm
import json
from sqlitedict import SqliteDict
import os

class EncodedDict(collections.MutableMapping):
    """
    Subclass this and provide any of the following (see
    implementatiokn for signatures)

    - db
    - _init()
    - _encode_key
    - _decode_key.
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

    def __del__(self):
        del self.db

    def __setitem__(self, key, val):
        self.db[self._encode_key(key)] = val

    def __getitem__(self, key):
        return self.db[self._encode_key(key)]

    def __contains__(self, key):
        return self._encode_key(key) in self.keys()

    def __delitem__(self, key):
        del self.db[self._encode_key(key)]

    def __iter__(self):
        return imap(self._decode_key, self.db.keys())

    def __len__(self):
        return len(self.db)

    def keys(self):
        return list(self)

    def values(self):
        return self.db.values()

    def items(self):
        return [(self._decode_key(key), v) for key,v in self.db.iteritems()]

    def to_json(self, filename):
        json.dump([(k,v) for k,v in self.db.iteritems()],
                  open(filename, 'w'))

    def from_json(self, filename):
        for k,v in json.load(open(filename)):
            self.db[k] = v


class DbmPersistentDict(EncodedDict):
    """
    Persistent dict using dbm. Will open or create filename.
    """

    def __init__(self, filename):
        flag = 'w' if os.path.exists(filename) else 'n'

        super(DbmPersistentDict, self).__init__(dbm.open(filename, flag))

    def _encode_key(self, key):
        # Asciify
        if isinstance(key, unicode):
            return key.encode('unicode_escape')

        return str(key)

    def _decode_key(self, key):
        # Unicodify
        return key.decode('unicode_escape')


class SqlitePersistentDict(EncodedDict):
    def __init__(self, filename):
        if not filename.endswith('.sqlite'):
            filename += '.sqlite'

        db = SqliteDict(filename)
        super(SqlitePersistentDict, self).__init__(db)

    def __del__(self):
        self.db.close()
        super(SqlitePersistentDict, self).__del__()


"""
Some info on performance:

>>> import timeit
>>> sqlkv = SqlitePersistentDict('/tmp/bench1.sqlite')
>>> timeit.timeit(lambda : benchmark_write(sqlkv), number=100)
10.847157955169678
>>> timeit.timeit(lambda : benchmark_read(sqlkv), number=100)
18.88098978996277
>>> dbmkv = DbmPersistentDict('/tmp/bench.dbm')
>>> timeit.timeit(lambda : benchmark_write(dbmkv), number=100)
0.18030309677124023
>>> timeit.timeit(lambda : benchmark_read(dbmkv), number=100)
0.14914202690124512

SqliteDict is a pretty thin wrapper around sqlite, I would probably
not have made it much thinner. Just use Dbm.

Keep this around in case anyone considers changing to sqlite.

XXX: see how gdbm does when data is larger than memory. Also check out
bsddb
"""

# PersistentDict = SqlitePersistentDict
PersistentDict = DbmPersistentDict

def benchmark_write(dic, times=100000):
    for i in xrange(times):
        dic['o' + str(i)] = str(i) * 1000

def benchmark_read(dic, times=100000):
    for i in xrange(times):
        dic['o' + str(i)]
