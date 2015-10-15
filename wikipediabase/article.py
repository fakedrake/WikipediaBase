from itertools import chain

from wikipediabase.classifiers import WIKIBASE_CLASSIFIERS
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.log import Logging
from wikipediabase.synonym_inducers import ForwardRedirectInducer
from wikipediabase.util import (Expiry,
                                fromstring,
                                get_infoboxes,
                                markup_categories,
                                memoized,
                                tostring,
                                totext)

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
        self._infoboxes = []
        self.title_inducer = ForwardRedirectInducer()

    @memoized
    def url(self):
        symbol = self.symbol().replace(" ", "_")
        return u"https://en.wikipedia.org/wiki/%s" % symbol

    @memoized
    def symbol(self):
        return self.title_inducer.title(self._title, fetcher=self.fetcher)

    def _soup(self):
        if not hasattr(self, '__soup'):
            self.__soup = fromstring(self.html_source())

        return self.__soup

    def categories(self):
        return markup_categories(self.markup_source())

    def classes(self):
        it = chain.from_iterable((c.classify(self.symbol())
                                  for c in WIKIBASE_CLASSIFIERS))
        return list(it)

    def infoboxes(self):
        if not self._infoboxes:
            self._infoboxes = get_infoboxes(self.title(), fetcher=self.fetcher)

        return self._infoboxes

    def types(self):
        types = [ibox.types() for ibox in self.infoboxes()]
        types = list(chain.from_iterable(types))  # flatten list
        return types

    def title(self):
        """
        The title after redirections and stuff.
        """
        # Warning!! dont feed this to the fetcher. This depends on the
        # fetcher to resolve redirects and a cirular recursion will
        # occur

        heading = self._soup().get_element_by_id('firstHeading')
        if heading is not None:
            return totext(heading).strip()

        raise Exception("No title found for '%s'" % self.symbol())

    def markup_source(self, expiry=Expiry.DEFAULT):
        """
        Markup source of the article.
        """

        return self.fetcher.markup_source(self._title, expiry=expiry)

    def html_source(self, expiry=Expiry.DEFAULT):
        """
        Markup source of the article.
        """

        return self.fetcher.html_source(self._title, expiry=expiry)

    def paragraphs(self, keep_html=False):
        """
        Generate paragraphs.
        """

        xpath = ".//*[@id='mw-content-text']/p"
        if keep_html:
            return ["".join(tostring(p)) for p in self._soup().findall(xpath)
                    if "".join(p.itertext())]
        else:
            return ["".join(p.itertext()) for p in self._soup().findall(xpath)
                    if "".join(p.itertext())]

    def headings(self):
        """
        Generate all the headings in a DFS fashion.
        """

        s = self._soup()
        xpath = ".//*[@id='mw-content-text']//span[@class='mw-headline']/."

        return [u"".join(h.itertext())
                for h in s.findall(xpath)
                if "".join(h.itertext())]

    def first_paragraph(self, keep_html=False):
        for p in self.paragraphs(keep_html=keep_html):
            if p.strip():
                return p

        return None
