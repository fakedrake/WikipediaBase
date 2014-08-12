# -*- coding: utf-8 -*-

try:
    from urllib2 import urlopen
except:
    from urllib import urlopen

from urllib import urlencode
import re
import json

import lxml.etree as ET

from .log import Logging
from .util import subclasses, fromstring


REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"
OFFLINE_PAGES = "/tmp/pages.json"


class BaseFetcher(Logging):
    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    priority = 0

    def download(self, symbol, get=None):
        return symbol

    def source(self, symbol, redirect=True):
        return symbol


class WikipediaSiteFetcher(BaseFetcher):

    priority = 1

    def __init__(self, url="http://en.wikipedia.org", base="w", **kw):
        self.url = url.strip('/')
        self.base = base.strip('/')

    def get_wikisource(self, soup):
        """
        Get the source from an html soup of the edit page.
        """
        tag = "".join(soup.find(".//*[@id='wpTextbox1']").itertext())

        return tag

    def download(self, symbol, get=None):
        """
        Download a wikipedia article.

        :param symbol: The wikipedia symbol we are interested in.
        :param get: dictionary of the get request. eg. `{'action':'edit'}`
        :returns: HTML code
        """

        if not get:
            get = dict(title=symbol)
        else:
            get = get.copy()
            get.update(title=symbol)

        url = "%s/%s?%s" % (self.url, self.base,
                            urlencode(get))
        self.log().info("Fetching url: " + url)
        return urlopen(url).read()

    def source(self, symbol, get_request=dict(action="edit"), redirect=True):
        """
        Get the full wiki markup of the symbol.
        """

        # <textarea tabindex="1" accesskey="," id="wpTextbox1" cols="80" rows="25" style="" lang="en" dir="ltr" name="wpTextbox1">
        html = self.download(symbol=symbol, get=get_request)
        soup = fromstring(html)


        try:
            src = self.get_wikisource(soup).encode("utf-8", "ignore")
        except IndexError:
            raise ValueError("Got invalid source page for article '%s'." %
                              symbol)

        # Handle redirecions silently
        redirect_match = re.search(REDIRECT_REGEX, src)

        if redirect and redirect_match:
            self.log().info("Redirecting to '%s'.", redirect_match.group(1))
            src = self.download(symbol=redirect_match.group(1),
                                get=get_request)

        return src


class CachingSiteFetcher(WikipediaSiteFetcher):
    """
    Caches pages in a json file and reads from there.
    """

    priority = 10
    _fname = OFFLINE_PAGES

    def __init__(self, *args, **kw):
        """
        The `offline` keyword arg will stop ot from looking pages up
        online. The default is True.
        """

        self.offline = kw.get("offline", False)
        self._fname = kw.get("fname", self._fname)

        super(CachingSiteFetcher, self).__init__(*args, **kw)


    def download(self, symbol, get=None):
        try:
            if not hasattr(self, 'data'):
                self.data = json.load(open(self._fname))

        except (ValueError, IOError):
            self.data = dict()

        dkey = "%s;%s" % (symbol, get)
        if dkey in self.data:
            return self.data[dkey]

        if not self.offline:
            pg = super(CachingSiteFetcher, self).download(symbol, get=get)
            if pg:
                self.data[dkey] = pg
                json.dump(self.data, open(self._fname, "w"))
                return pg

        raise LookupError("Failed to find page '%s' (%s online)." %
                          (symbol, "didnt look" if self.offline else "looked"))

WIKIBASE_FETCHER = CachingSiteFetcher()
