# -*- coding: utf-8 -*-

try:
    import urllib2 as urllib
except:
    import urllib

from urllib import urlencode
import re

from wikipediabase.config import Configurable, configuration
import wikipediabase.util as util
from wikipediabase.web_string import MarkupString, SymbolString


REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"
OFFLINE_PAGES = "./pages.sqlite"


class BaseFetcher(Configurable):

    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    priority = 0

    def __init__(self, configuration=configuration):
        self.log = configuration.ref.log.lens(lambda log, this: log(this),
                                              self)

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

    def __init__(self, configuration=configuration):
        self.xml_string = configuration.ref.strings.xml_string_class. \
                          with_args(configuration=configuration)
        self.configuration = configuration

    def get_wikisource(self, xml_string, symbol):
        """
        Get the source from an html soup of the edit page.
        """
        # Edit tag:
        # <textarea tabindex="1" accesskey="," id="wpTextbox1"
        # cols="80" rows="25" style="" lang="en" dir="ltr"
        # name="wpTextbox1">

        for box in xml_string.xpath(".//textarea[@id='wpTextbox1']"):
            return MarkupString(box.text())

        open("/tmp/err.html", "w").write(str(xml_string))
        raise Exception("Couldn't get wikisource for '%s'" % str(symbol))

    def download(self, symbol, get=None):
        return self.urlopen(symbol, get=get).read()

    def urlopen(self, symbol, get=None):
        """
        Download a wikipedia article.

        :param symbol: The wikipedia symbol we are interested in. Set
        this to None to do different calls.
        :param get: dictionary of the get request. eg. `{'action':'edit'}`
        :returns: HTML code
        """

        if not isinstance(symbol, SymbolString):
            symbol = SymbolString(symbol)

        url = symbol.url(get=get, configuration=self.configuration)
        try:
            return urllib.urlopen(url.raw())
        except urllib.URLError:
            raise LookupError("Urllib failed to open:" + url.raw())

        # try:
        #     return urllib.urlopen(url)
        # except urllib.HTTPError:
        #     raise LookupError("404 - Uropen args: %s" % repr(url))


    def redirect_url(self, symbol):
        sym = symbol
        if not isinstance(symbol, SymbolString):
            sym = SymbolString(symbol)

        src = self.source(sym, redirect=False)
        redirect_sym = sym
        if src is not None:
            redirect_sym = src.redirect_target() or sym

        return redirect_sym.url().raw()


    def source(self, symbol, get_request=None, redirect=True):
        """
        Get the full wiki markup of the symbol.
        """

        get_request = get_request or dict(action="edit")
        html = self.download(symbol, get=get_request)
        xml = self.xml_string(html)

        src = self.get_wikisource(xml, symbol)
        if src is None:
            return None

        redirect_target = src.redirect_target()
        if redirect and redirect_target:
            return self.source(symbol=redirect_target, get_request=get_request,
                               redirect=False)

        return src


class CachingSiteFetcher(WikipediaSiteFetcher):

    """
    Caches pages in a json file and reads from there.
    """

    priority = 10
    cache_file = OFFLINE_PAGES

    def __init__(self, configuration=configuration):
        """
        The `offline` keyword arg will stop ot from looking pages up
        online. The default is True.
        """

        import lxml.html.clean
        if not isinstance(configuration.ref.strings.lxml_cleaner.deref(),
                          lxml.html.clean.Cleaner):
            raise ValueError("Expected lxml.html.clean.Cleaner. Got %s" %
                             self.cleaner.__class__)

        self.offline = configuration.ref.offline
        self.data = configuration.ref.cache.pages

        super(CachingSiteFetcher, self).__init__(configuration)

    def redirect_url(self, symbol):
        key = "REDIRECT:" + str(symbol)
        if key in self.data:
             return self.data[key]

        ret = super(CachingSiteFetcher, self).redirect_url(symbol)
        self.data[key] = ret
        return ret

    def download(self, symbol, get=None):
        dkey = "%s;%s" % (symbol, get)
        callback = super(CachingSiteFetcher, self).download
        return self.caching_fetch(dkey, callback, symbol, get=get)

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
                          (dkey, "didnt look" if self.offline else "looked"))


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
