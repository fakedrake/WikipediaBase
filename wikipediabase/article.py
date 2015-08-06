from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.log import Logging
from wikipediabase.synonym_inducers import ForwardRedirectInducer
from wikipediabase.util import (Expiry,
                                markup_categories,
                                fromstring,
                                totext,
                                memoized,
                                get_infobox)

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

    def infobox(self):
        if not self.ibox:
            self.ibox = get_infobox(self.title(), fetcher=self.fetcher)

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

        heading = self._soup().get_element_by_id('firstHeading')
        if heading is not None:
            return totext(heading).strip()

        raise Exception("No title found for '%s'" % self.symbol())

    def markup_source(self, expiry=Expiry.DEFAULT):
        """
        Markup source of the article.
        """

        return self.fetcher.source(self._title, expiry=expiry)

    def html_source(self, expiry=Expiry.DEFAULT):
        """
        Markup source of the article.
        """

        return self.fetcher.download(self._title, expiry=expiry)

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
        xpath = ".//*[@id='mw-content-text']//span[@class='mw-headline']/."

        return [u"".join(h.itertext())
                for h in s.findall(xpath)
                if "".join(h.itertext())]

    def first_paragraph(self):
        for p in self.paragraphs():
            if p.strip():
                return p

        return None
