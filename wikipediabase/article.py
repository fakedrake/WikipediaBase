import lxml.etree as ET
import re
import itertools

from .log import Logging
from .util import markup_categories, fromstring, tostring, totext

from .fetcher import WIKIBASE_FETCHER


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

    def url(self):
        return self.fetcher.urlopen(self._title).geturl()

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

        return ["".join(h.itertext())[:-len("[edit]")]
                for h in
                s.findall(
                    ".//*[@id='mw-content-text']//span[@class='mw-headline']/..")
                if "".join(h.itertext())]
