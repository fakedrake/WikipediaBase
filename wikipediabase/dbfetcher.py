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

    def _query_single(self, cmd):
        return int(self._query_one_raw(cmd)[0])

    def _query_single_list(self, cmd):
        return (i[0] for i in self._query_raw(cmd))

    def tables(self):
        return list(self._query_single_list("show tables;"))

    def columns(self, table):
        return list(self._query_single_list("show columns from %s;" % table))

    def n_categories(self):
        cmd = "select count(*) from page where page_namespace = 14;"
        return int(self._query_single(cmd))

    def categories(self):
        cmd = "select page_id, page_title from page where page_namespace = 14;"
        return ({'id': id, 'name': title} for id, title
                in self._query_raw(cmd))

    def article_id(self, title):
        cmd = "select page_id from page where page_title = '%s'" % title
        return int(self._query_single(cmd))

    def article_title(self, id):
        cmd = "select page_title from page where page_id = '%s'" % id
        return self._query_single(cmd)

    def article_categories(self, article):
        pass

def get_dbfetcher(new=False, **kw):
    try:
        if not new:
            return get_dbfetcher._fetcher
    except AttributeError:
        pass

    get_dbfetcher._fetcher = DBFetcher(**kw)
    return get_dbfetcher(**kw)
