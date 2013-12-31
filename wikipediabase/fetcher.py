import urllib
import re
import json

import bs4

from log import Logging


INFOBOX_REGEX = r"{{Infobox .+?^}}$"
WIKISOURCE_TAG_ID = "wpTextbox1"
REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"

class BaseFetcher(Logging):
    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    def fetch(self, article):
        """
        Just return the article itself.
        """

        return article


class WikipediaSiteFetcher(BaseFetcher):
    def __init__(self, url="http://en.wikipedia.org", base="w"):
        self.url = url.strip('/')
        self.base = base.strip('/')

    def get_wikisource(self, soup):
        """
        Get the source from an html soup of the edit page.
        """
        tag = soup.find_all(attrs={"id":WIKISOURCE_TAG_ID})

        return tag

    # XXX: Turn get into a dict and have urllib do the formatting
    def download(self, symbol, get=None):
        """
        Return the contents of page relative to the current url.
        """
        if not get:
            get = dict(title=symbol)
        else:
            get = get.copy()
            get.update(title=symbol)

        url = "%s/%s?%s" % (self.url, self.base,
                            urllib.urlencode(get))
        return urllib.urlopen(url).read()

    def article(self, symbol):
        """
        Given a symbol get what wikipedia has to say.
        """

        self.log().info("Looking for rendered article: %s" % symbol)
        return self.download(symbol=symbol)

    def infobox(self, symbol, rendered=False):
        """
        Get the infobox in wiki markup.
        """

        mu = self.source(symbol)

        self.log().info("Looking for infobox: %s" % symbol)
        m = re.search(INFOBOX_REGEX, mu, re.M|re.DOTALL)

        if m:
            self.log().info("Found an infobox.")
            return m.group(0)

        self.log().warning("Could not find infobox in source (source size: %d)." %
                      len(mu))

    def source(self, symbol, get_request=dict(action="edit")):
        """
        Get the full wiki markup of the symbol.
        """

        self.log().info("Looking for article source: %s." % symbol)
        # <textarea tabindex="1" accesskey="," id="wpTextbox1" cols="80" rows="25" style="" lang="en" dir="ltr" name="wpTextbox1">
        html = self.download(symbol=symbol, get=get_request)

        # Handle redirections silently
        redirect = re.search(REDIRECT_REGEX, html)
        if redirect:
            self.log().info("Redirecting to '%s'.", redirect.group(1))
            html = self.download(symbol=redirect.group(1), get=get_request)

        soup = bs4.BeautifulSoup(html)

        try:
            return str(self.get_wikisource(soup)[0])
        except IndexError:
            raise KeyError("Article '%s' not found." % symbol)

class CachingSiteFetcher(WikipediaSiteFetcher):
    """
    Caches pages in a json file and reads from there.
    """

    _fname = "/tmp/pages.json"

    def download(self, symbol, get=None):
        try:
            data = json.load(open(self._fname))
        except (ValueError, IOError):
            data = dict()

        dkey = "%s;%s" % (symbol, get)
        if dkey in data:
            return data[dkey]

        pg = super(CachingSiteFetcher, self).download(symbol, get=get)
        data[dkey] = pg
        json.dump(data, open(self._fname, "w"))
        return pg
