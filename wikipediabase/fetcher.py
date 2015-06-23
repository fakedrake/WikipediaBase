# -*- coding: utf-8 -*-

try:
    import urllib2 as ul
except:
    import urllib as ul

from urllib import urlencode
import re
import os

import lxml.etree as ET

from wikipediabase.log import Logging
import wikipediabase.util as util


REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"
OFFLINE_PAGES = "./pages.sqlite"


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

    def caching_fetch(self, dkey, callback, *args, **kwargs):
        """
        If you support caching use this.
        """

        return callback(*args, **kwargs)


class WikipediaSiteFetcher(BaseFetcher):

    priority = 1

    def __init__(self, url="http://ashmore.csail.mit.edu:8080", base="mediawiki/index.php", **kw):
        self.url = url.strip('/')
        self.base = base.strip('/')

    def get_wikisource(self, soup):
        """
        Get the source from an html soup of the edit page.
        """
        return util.totext(soup.find(".//*[@id='wpTextbox1']"))


    def download(self, *args, **kwargs):
        return self.urlopen(*args, **kwargs).read()

    def urlopen(self, symbol, get=None, base=None):
        """
        Download a wikipedia article.

        :param symbol: The wikipedia symbol we are interested in. Set
        this to None to do different calls.
        :param get: dictionary of the get request. eg. `{'action':'edit'}`
        :returns: HTML code
        """

        if not get:
            get = dict(title=symbol)
        else:
            get = get.copy()
            if symbol is not None:
                get.update(title=symbol)

        url = "%s/%s?%s" % (self.url, base or self.base,
                            urlencode(get))

        try:
            return ul.urlopen(url)
        except ul.HTTPError:
            raise LookupError("404 - Uropen args: %s" % repr(url))


    def redirect_url(self, symbol):
        return self.urlopen(symbol).geturl()

    def source(self, symbol, get_request=None, redirect=True):
        """
        Get the full wiki markup of the symbol.
        """

        # Edit tag:
        # <textarea tabindex="1" accesskey="," id="wpTextbox1"
        # cols="80" rows="25" style="" lang="en" dir="ltr"
        # name="wpTextbox1">
        get_request = get_request or dict(action="edit")
        html = self.download(symbol=symbol, get=get_request)
        soup = util.fromstring(html)

        try:
            src = self.get_wikisource(soup)
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
    cache_file = OFFLINE_PAGES

    def __init__(self, *args, **kw):
        """
        The `offline` keyword arg will stop ot from looking pages up
        online. The default is True.
        """

        self.offline = kw.get("offline", False)
        self.cache_file = kw.get("cache_file", self.cache_file)

        super(CachingSiteFetcher, self).__init__(*args, **kw)

    def redirect_url(self, symbol):
        return self.caching_fetch("REDIRECT:" + symbol,
                                  lambda sym: super(CachingSiteFetcher,
                                                    self).redirect_url(symbol), symbol)

    def download(self, symbol, get=None, base=None):
        dkey = "%s;%s" % (symbol, get) if not base else \
               "%s:%s;%s" % (base, symbol, get)
        callback = super(CachingSiteFetcher, self).download
        return self.caching_fetch(dkey, callback, symbol, get=get, base=base)


    @property
    def data(self):
        return util._get_persistent_dict(self.cache_file)

    def caching_fetch(self, dkey, callback, *args, **kwargs):
        ret = None
        dkey = util.encode(dkey)

        if dkey in self.data:
            ret = self.data[dkey]

        if not self.offline and not ret:
            ret = callback(*args, **kwargs)
            if ret:
                self.data[dkey] = ret

        if ret is not None:
            return util.encode(ret)

        raise LookupError("Failed to find page '%s' (%s online)." %
                          (symbol, "didnt look" if self.offline else "looked"))


class StaticFetcher(BaseFetcher):
    """
    Will just get the html and markup provided in init.
    """

    def __init__(self, html=None, markup=None):
        self.html = html
        self.markup = markup

    def download(self, *args, **kw):
        return self.html

    def source(self, *args, **kw):
        return self.markup

WIKIBASE_FETCHER = CachingSiteFetcher()
