import os
import wikipediabase.fetcher
from wikipediabase.fetcher import CachingSiteFetcher
import urllib2 as urllib

ALL_TEST_PAGES = []

class MockURLOpen(object):
    """
    Always redirect to redirect_url and receive content.
    """

    def __init__(self, redirect_url, content):
        self.redirect_url = redirect_url
        self.content = content

    def __enter__(self):
        self.original = urllib.urlopen

        class MyURLfd(object):
            def __init__(self, _):
                pass

            def geturl(slf):
                return self.redirect_url

            def read(slf):
                return self.content


        urllib.urlopen = MyURLfd

    def __exit__(self, exc_type, exc_value, traceback):
        urllib.urlopen = self.original


def data(fname):
    return os.path.abspath('/'.join([__package__, 'data', fname]))


def read_data(fname):
    return open(data(fname)).read()


def download_all(pages=ALL_TEST_PAGES):
    f = CachingSiteFetcher(offline=False, cache_file=data("pages.db"))

    for p in pages:
        f.download(p)
        f.source(p)

TEST_FETCHER_SETUP = dict(offline=False, cache_file=data("pages.db"))


def get_fetcher():
    return CachingSiteFetcher(**TEST_FETCHER_SETUP)

wikipediabase.fetcher.WIKIBASE_FETCHER.cache_file = data('pages.db')
