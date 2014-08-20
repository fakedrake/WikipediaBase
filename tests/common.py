import os
from wikipediabase.fetcher import CachingSiteFetcher

ALL_TEST_PAGES = [
]


def data(fname):
    return os.path.abspath('/'.join([__package__, 'data', fname]))


def read_data(fname):
    return open(data(fname)).read()


def download_all(pages=ALL_TEST_PAGES):
    f = CachingSiteFetcher(offline=False, fname=data("pages.json"))

    for p in pages:
        f.download(p)
        f.source(p)

TEST_FETCHER_SETUP = dict(offline=False, fname=data("pages.json"))


def get_fetcher():
    return CachingSiteFetcher(**TEST_FETCHER_SETUP)
