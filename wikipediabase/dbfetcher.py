from itertools import chain

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
        return self._query_one_raw(cmd)[0]

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

    def all_articles(self, limit=None):
        """
        Get a list of tuples (page_id, page_text)
        """

        cmd = "select rev_page, old_text from revision " \
              "inner join text on old_id = rev_text_id " \
              "%s;" % ("limit %d" % limit if limit is not None else "")
        return self._query_raw(cmd)

    # XXX: there is no obvious way to just get the category ids
    # traight from the data base so you might want to do you training
    # with the strings.
    def article_categories(self, article):
        """
        Find in the article text [[Category:.*]]
        """

        return self._categories(self.article_text(article))

    def _categories(self, txt):
        """
        return the names of the categories.
        """

        # It is slightly faster like this because we are nto creating
        # a lambda obj each time.
        def first_part(s):
            return s.split(']]', 1)[0]

        return map(first_part, txt.split("[[Category:")[1:])

    def all_article_categories(self, limit=None):
        return chain.from_iterable((((id, cat) for cat in self._categories(txt) )
                                    for id, txt in self.all_articles(limit)))

    def article_text(self, article):
        """
        You need to jump from page(title)->revision->text
        """

        if isinstance(article, str):
            cmd = "select old_text from page " \
                  "inner join revision on rev_page = page_id " \
                  "inner join text on old_id = rev_text_id " \
                  "where page_title = '%s';" % article

        else:                   # Assume it's an id
            cmd = "select old_text from revision " \
                  "inner join text on old_id = rev_text_id " \
                  "where rev_page = '%d';" % article

        return self._query_single(cmd)


def get_dbfetcher(new=False, **kw):
    if not new:
        try:
            return get_dbfetcher._fetcher
        except AttributeError:
            pass

    get_dbfetcher._fetcher = DBFetcher(**kw)
    return get_dbfetcher(**kw)


def _main():
    import json
    fetcher = get_dbfetcher()
    json.dump(list(fetcher.all_article_categories()), "./article_categories.json")

if __name__ == "__main__":
    _main()
