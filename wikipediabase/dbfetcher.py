import sys
import threading
import datetime

from itertools import chain

import mysql.connector as mdb

from wikipediabase.util import time_interval


class DBFetcher(object):
    _default_conn = {
        'user': "csail",
        'passwd': "pass",
        'port': 3307,
        'db': "bitnami_mediawiki",
        'host': 'ashmore.csail.mit.edu',
    }
    msg = "<No message emited>"

    def message(self, msg):
        self.msg = "[ %s ] %s" % (datetime.datetime.now(), msg)

    def __init__(self, **kw):
        self.retries = 10
        self.conn_props = kw
        self._setup(**kw)

    def _setup(self, **kw):
        if kw:
            self.conn_props = kw
        else:
            kw = self.conn_props

        self.db = mdb.MySQLConnection()
        self.db._raw = True
        # self.db._connection_timeout = 30
        # self.db.raise_on_warnings = True
        self.db.connect(**dict(self._default_conn, **kw))
        self.cur = self.db.cursor()

    def _query_one_raw(self, cmd=None):
        self.cur.execute(self.cmd)
        return self.cur.fetchone()

    def _query_raw_iter(self, cmd=None, size=None):
        self.cur.execute(self.cmd)
        retries = self.retries
        while retries > 0:
            try:

                if size is None:
                    ret = iter(self.cur.fetchone, None)
                else:
                    ret = iter(lambda: self.cur.fetchmany(size), None)

                for i in ret:
                    self.message("Just got %s\n" % i[0])
                    yield i
                    self.message("Getting after %s\n" % i[0])

            except mdb.errors.OperationalError:
                retries -= 1
                sys.stderr.write("Connection timed out. Retrying...\n")

                self._setup
            else:
                break

    def _query_raw(self, cmd=None):
        self.cur.execute(self.cmd)
        return self.cur.fetchall()

    def _query_single(self, cmd=None):
        return self._query_one_raw(self.cmd)[0]

    def _query_single_list(self, cmd=None):
        return (i[0] for i in self._query_raw(self.cmd))

    def tables(self):
        return list(self._query_single_list("show tables;"))

    def columns(self, table):
        return list(self._query_single_list("show columns from %s;" % table))

    def n_categories(self):
        self.cmd = "select count(*) from page where page_namespace = 14;"
        return int(self._query_single())

    def categories(self):
        self.cmd = "select page_id, page_title from page where \
        page_namespace = 14;"
        return self._query_raw_iter()

    def article_id(self, title):
        self.cmd = "select page_id from page where page_title = '%s'" % title
        return int(self._query_single())

    def article_title(self, id):
        self.cmd = "select page_title from page where page_id = '%s'" % id
        return self._query_single()

    def article_ns(self, id):
        self.cmd = "select page_namespace from page where page_id = '%s'" % id
        return int(self._query_single())

    def all_articles(self, limit=None, ns=0):
        """
        Get an iterator over of tuples (page_id, page_text)
        """

        where = ("where page_namespace=%d" % ns if ns is not None else "")
        lmt = ("limit %d" % limit if limit is not None else "")
        self.cmd = "select page_title, old_text from text " \
                   "join revision on rev_text_id = old_id " \
                   "join page on page_id = rev_page " \
                   "%s %s;" % (where, lmt)
        return self._query_raw_iter()

    # XXX: there is no obvious way to just get the category ids
    # traight from the data base so you might want to do you training
    # with the strings.
    def article_categories(self, article):
        """
        Find in the article text [[Category:.*]]
        """

        self.message("Parsing: %s" % article)
        ret = self._categories(self.article_text(article))
        self.message("Finished: %s" % article)
        return ret

    def all_article_categories(self, limit=None, namespace=0):
        """
        Stream (article_id, category) tuples.
        """

        id_cat = (((id, cat.replace(" ", "_"))
                   for cat in self._categories(txt))
                  for id, txt in self.all_articles(limit, namespace))
        return chain.from_iterable(id_cat)

    def _categories(self, txt):
        """
        return the names of the categories.
        """

        # It is slightly faster like this because we are nto creating
        # a lambda obj each time.
        def first_part(s):
            return s.split(']]', 1)[0].split('|')[0]

        return map(first_part, txt.split("[[Category:")[1:]) + \
            ["wikipedia-article"]

    def article_text(self, article):
        """
        You need to jump from page(title)->revision->text
        """

        if isinstance(article, str):
            self.cmd = "select old_text from page " \
                       "inner join revision on rev_page = page_id " \
                       "inner join text on old_id = rev_text_id " \
                       "where page_title = '%s';" % article

        else:                   # Assume it's an id
            self.cmd = "select old_text from revision " \
                       "inner join text on old_id = rev_text_id " \
                       "where rev_page = '%d';" % article

        return self._query_single()


def get_dbfetcher(new=False, **kw):
    if not new:
        try:
            return get_dbfetcher._fetcher
        except AttributeError:
            pass

    get_dbfetcher._fetcher = DBFetcher(**kw)
    return get_dbfetcher(**kw)

OUTPUT_SPARSITY = 100


def _main():
    """
    dbfetcher.py {category_map, category_fix} [in file] [out file]

    Create a category map or fix the names of the catgories replacing
    spaces with _. Input and output files default to stdin and stdout.

    Note that there are about 1M categories and 11M (namespace 0)
    articles.

    Examples:

    dbfetcher.py category_map > category-map.txt
    """
    import string

    try:
        fi = open(sys.argv[2]) if sys.argv[2] != '-' else sys.stdin
    except IndexError:
        fi = sys.stdin

    try:
        fo = open(sys.argv[3], 'w') if sys.argv[2] != '-' else sys.stdout
    except IndexError:
        fo = sys.stdout

    err = sys.stderr

    if sys.argv[1] == "category_map":

        fetcher = get_dbfetcher()
        gen = fetcher.all_article_categories()

        err.write("SQL: %s\n" % fetcher.cmd)
        for counter, (id, cat) in enumerate(gen):

            if counter == 0:
                sys.stderr.write("[ <time interval> ] Start...\n")

            fo.write("%s %s\n" % (id, cat))
            if counter % OUTPUT_SPARSITY == 0:
                sys.stderr.write("[ %s ] %d categories parsed...\n" %
                                 (time_interval(), counter))

    elif sys.argv[1] == "category_fix":
        for i, l in enumerate(fi):
            lstr = l.strip()

            if len(lstr):
                car, cdr = string.split(lstr, " ", 1)
                fo.write("%s %s\n" % (car, string.replace(cdr, " ", "_")))

    elif sys.argv[1] == 'dump_categories':
        fetcher = get_dbfetcher()

        for i, (id, cat) in enumerate(fetcher.categories()):
            fo.write("%s %s\n" % (id, cat))

            if i == 0:
                err.write("SQL: %s\n", fetcher.cmd)

            if i % OUTPUT_SPARSITY == 0:
                err.write("[ %s ] %d categories dumped (current: %s)\n" %
                          (time_interval(), i, cat))

    else:
        sys.stderr.write(_main.__doc__.strip() + "\n")


dbf = lambda: get_dbfetcher(new=True)


def monitor(timeout=10, dbf=None, fd=None, conf=None):
    event = threading.Event()
    fd = fd or sys.stderr
    dbf = dbf or get_dbfetcher(new=False)
    conf = dict(event=event, timeout=timeout, dbf=dbf, fd=fd)
    fd.write("Starting monitor at timeout %d\n" % timeout)

    def callback():
        while not conf['event'].is_set():
            conf['fd'].write("Monitor: %s\n" % conf['dbf'].msg)
            sys.stdout.flush()
            event.wait(conf['timeout'])

    conf['thread'] = threading.Thread(target=callback)
    conf['thread'].start()

    return conf


def exit_thread(conf):
    cnf['event'].set()
    sys.stderr.write("Waiting for thread to yield...")
    cnf['thread'].join()
    sys.stderr.write("OK\n")


if __name__ == "__main__":

    _main()
    # cnf = monitor(timeout=60)
    # try:
    #     _main()
    # except BaseException, e:
    #     exit_thread(cnf)
    #     raise e
