import urllib
import re

import bs4

from  repoze.lru import lru_cache


INFOBOX_REGEX = r"{{Infobox .+?^}}$"
WIKISOURCE_TAG_ID = "wpTextbox1"

class BaseFetcher(object):
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


    def download(self, symbol=None, get=None):
        """
        Return the contents of page relative to the current url.
        """

        if not get:
            get = "?"

        if symbol:
            get += "?title=%s" % symbol

        url = "%s/%s?%s" % (self.url, self.base, get.lstrip("?"))
        return urllib.urlopen(url).read()

    def article(self, symbol):
        """
        Given a symbol get what wikipedia has to say.
        """

        return self.download(symbol=symbol)

    def infobox(self, symbol):
        """
        Get the infobox in wiki markup.
        """

        mu = self.source(symbol)
        m = re.search(INFOBOX_REGEX, mu, re.M|re.DOTALL)
        if m:
            return m.group(0)

    def source(self, symbol, get_request="?title=%s&action=edit"):
        """
        Get the full wiki markup of the symbol.
        """

        # <textarea tabindex="1" accesskey="," id="wpTextbox1" cols="80" rows="25" style="" lang="en" dir="ltr" name="wpTextbox1">
        get_req = get_request % symbol
        html = self.download(get=get_req)
        soup = bs4.BeautifulSoup(html)

        return str(self.get_wikisource(soup)[0])
