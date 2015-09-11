import os
import wikipediabase.fetcher
from wikipediabase.persistentkv import JsonPersistentDict
from wikipediabase.fetcher import CachingSiteFetcher
from wikipediabase.settings import *
from wikipediabase.config import Configurable
import urllib2 as urllib
import json

real_urlopen = urllib.urlopen


def data(fname):
    pkgpath = __package__ or os.path.abspath(os.path.curdir)
    return os.path.abspath('/'.join([pkgpath, 'data', fname]))



class MockUrlFd(Configurable):
    def __init__(self, url, data=None):
        self.key = json.dumps((url, data))
        self.data = configuration.ref.test.urldata
        self.urlopen = real_urlopen(url, data)
        self.url = url

    def geturl(self):
        return self.url

    def read(self):
        ret = self.data.get(self.key)
        if ret:
            return ret

        ret = self.urlopen.read()
        self.data[self.key] = ret

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
configuration.ref.test.urldata = JsonPersistentDict(data('pages.json'))
