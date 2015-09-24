import os
import wikipediabase.fetcher
from wikipediabase.persistentkv import DbmPersistentDict
from wikipediabase.fetcher import CachingSiteFetcher
from wikipediabase.settings import *
from wikipediabase.config import Configurable, configuration
try:
    import urllib2 as urllib
except:
    import urllib as urllib

import json

real_urlopen = urllib.urlopen


def data(fname):
    pkgpath = __package__ or os.path.abspath(os.path.curdir)
    return os.path.abspath('/'.join([pkgpath, 'data', fname]))



class MockUrlFd(Configurable):
    def __init__(self, url, data=None):
        self.cache = configuration.ref.test.offline_cache
        self.post_data = data
        self.url = url

    def key(self):
        return json.dumps((self.url, self.post_data))

    def geturl(self):
        return self.url

    def read(self):
        key = self.key()
        ret = self.cache.get(key)
        if ret:
            return ret

        ret = real_urlopen(self.url, data=self.post_data).read()
        self.cache[key] = ret
        return ret

urllib.urlopen = MockUrlFd

def read_data(fname):
    return open(data(fname)).read()


def download_all():
    f = CachingSiteFetcher(offline=False, cache_file=data("pages.json"))

    for p in configuration.ref.test_pages:
        f.download(p)
        f.source(p)

# wikipediabase.fetcher.WIKIBASE_FETCHER.cache_file = data('pages.db')
configuration.ref.test.offline_cache = DbmPersistentDict(data('pages.dumbdbm'))
configuration.ref.cache.pages = dict()
configuration.ref.offline = False
