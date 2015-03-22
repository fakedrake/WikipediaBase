import lxml.etree as ET
import os
import re
import itertools
from urlparse import urlparse

from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.log import Logging
from wikipediabase.util import (markup_categories,
                                fromstring,
                                tostring,
                                totext,
                                memoized,
                                url_get_dict)

# XXX: also support images.
class Article(Logging):

    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title, fetcher=WIKIBASE_FETCHER):
        self._title = title
        self.fetcher = fetcher
        self.ibox = None

    @memoized
    def url(self):
        return self.fetcher.urlopen(self._title).geturl()

    def symbol(self):
        url = self.url()
        return url_get_dict(url).get('title') or \
            os.path.basename(url)

    def _soup(self):
        if not hasattr(self, '__soup'):
            self.__soup = fromstring(self.html_source())

        return self.__soup

    def categories(self):
        return markup_categories(self.markup_source())

    def infobox(self):
        if not self.ibox:
            self.ibox = Infobox(self.title, fetcher=self.fetcher)

        return self.ibox

    def types(self):
        return self.infobox().types()

    def title(self):
        """
        The title after redirections and stuff.
        """
        # Warning!! dont feed this to the fetcher. This depends on the
        # fetcher to resolve redirects and a cirular recursion will
        # occur

        return "".join(
            self._soup().find(".//*[@id='firstHeading']/span").itertext())

    def markup_source(self):
        """
        Markup source of the article.
        """

        return self.fetcher.source(self._title)

    def html_source(self):
        """
        Markup source of the article.
        """

        return self.fetcher.download(self._title)

    def paragraphs(self):
        """
        Generate paragraphs.
        """

        return ["".join(p.itertext()) for p in
                self._soup().findall(".//*[@id='mw-content-text']/p")
                if "".join(p.itertext())]

    def headings(self):
        """
        Generate all the headings in a DFS fashion.
        """

        s = self._soup()
        xpath = ".//*[@id='mw-content-text']//span[@class='mw-headline']/.."

        return ["".join(h.itertext())[:-len("[edit]")]
                for h in s.findall(xpath)
                if "".join(h.itertext())]
