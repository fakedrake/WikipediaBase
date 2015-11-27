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
testcfg = configuration.child()


def data(fname):
    pkgpath = __package__ or os.path.abspath(os.path.curdir)
    return os.path.abspath('/'.join([pkgpath, 'data', fname]))


class MockUrlFd(Configurable):
    """
    Common interface to urllib's open. Use this for debugging requests
    and for abstracting the remote server.
    """

    def __init__(self, url, data=None):
        self.cache = testcfg.ref.test.offline_cache
        self.post_data = data
        self.url = url

    def key(self):
        return json.dumps((self.url, self.post_data))

    def geturl(self):
        return self.operation('geturl')

    def read(self):
        return self.operation('read')

    def operation(self, op):
        key = self.key() + ('' if op == 'read' else op)
        ret = self.cache.get(key)
        if ret:
            return ret

        fd = real_urlopen(self.url, data=self.post_data)
        ret = getattr(fd, op)()
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
testcfg.ref.test.offline_cache = DbmPersistentDict(data('pages.cache'))
testcfg.ref.strings.xml_prune_tags = ['script', 'style', r'div.*navigation', 'head']

# configuration.ref.remote.base = 'mediawiki/index.php'
# configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'

testcfg.ref.remote.url = 'https://en.wikipedia.org'
testcfg.ref.remote.base = 'w/index.php'
testcfg.ref.remote.sandbox_title = "Wikipedia:Sandbox"


testcfg.ref.cache.pages = dict()
testcfg.ref.offline = False
testcfg.freeze()
