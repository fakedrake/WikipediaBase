"""
Some persistent maps (gdbm) require special encoding of keys
and/or values. This is an abstraction for these kinds of quirks.
"""

from itertools import imap

import collections
import dumbdbm as dbm
import json
from sqlitedict import SqliteDict
import os

from wikipediabase.config import Configurable, configuration

class EncodedDict(collections.MutableMapping, Configurable):
    """
    Subclass this and provide any of the following (see
    implementatiokn for signatures)

    - db
    - _init()
    - _encode_key
    - _decode_key.
    """

    def __init__(self, wrapped=None, configuration=configuration):
        self.db = wrapped if wrapped is not None else dict()
        self.transactions = 0
        self.sync_period = configuration.ref.cache.sync_period

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
        self.sync()
        del self.db

    def __setitem__(self, key, val):
        self.transactions += 1
        if self.transactions % self.sync_period:
            self.sync()

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

    def sync(self):
        pass


class JsonPersistentDict(EncodedDict):
    """
    Persistent dict using dbm. Will open or create filename.
    """

    def __init__(self, filename, configuration=configuration):
        if not filename.endswith('.json'):
            filename += '.json'

        self.filename = filename
        self.dirty = False
        fd = None
        try:
            fd = open(self.filename)
        except:
            pass

        super(JsonPersistentDict, self).__init__(json.load(fd) if fd else {})

    def sync(self):
        print "Dumping:", len(self.db.keys())
        if self.dirty:
            json.dump(self.db, open(self.filename, 'w'))


        super(JsonPersistentDict, self).sync()

    def __setitem__(self, key, val):
        self.dirty = True
        return super(JsonPersistentDict, self).__setitem__(key, val)

    def _encode_key(self, key):
        if isinstance(key, unicode):
            return key.encode('unicode_escape')

        return str(key)

    def _decode_key(self, key):
        return key.decode('unicode_escape')

class DbmPersistentDict(EncodedDict):
    """
    Persistent dict using dbm. Will open or create filename.
    """

    def __init__(self, filename=None, configuration=configuration):
        self.filename = configuration.ref.cache.path.lens(lambda x: x + (filename or 'default.dbm'))
        flag = 'w' if os.path.exists(filename) else 'n'

        try:
            database = dbm.open(filename, flag)
        except:
            raise IOError("Failed dbm.open('%s', '%s')" % (filename, flag))

        super(DbmPersistentDict, self).__init__(database, configuration=configuration)

    def _encode_key(self, key):
        # Asciify
        if isinstance(key, unicode):
            return key.encode('unicode_escape')

        return str(key)

    def _decode_key(self, key):
        # Unicodify
        return key.decode('unicode_escape')


class SqlitePersistentDict(EncodedDict):
    def __init__(self, filename, configuration=configuration):
        if not filename.endswith('.sqlite'):
            filename += '.sqlite'

        db = SqliteDict(filename)
        super(SqlitePersistentDict, self).__init__(db)

    def sync(self):
        self.db.close()
        super(SqlitePersistentDict, self).sync()


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
