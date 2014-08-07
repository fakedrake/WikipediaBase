import MySQLdb as mdb

from wikipediabase.fetcher import BaseFetcher

class DBFetcher(BaseFetcher):

    _default_conn = {
        'user': "csail",
        'passwd': "pass",
        'port': 3307,
        'db': "bitnami_mediawiki",
        'host': 'futuna.csail.mit.edu'
    }

    def __init__(self, **kw):
        self._setup(**kw)

    def _setup(self, **kw):
        self.db = mdb.connect(**dict(self._default_conn, **kw))
        self.cur = self.db.cursor()

    def _query_one_raw(self, cmd):
        self.cur.execute(cmd)
        return self.cur.fetchone()

    def _query_raw(self, cmd):
        self.cur.execute(cmd)
        return self.cur.fetchall()

    def tables(self):
        return [i[0] for i in self._query_raw("show tables;")]
