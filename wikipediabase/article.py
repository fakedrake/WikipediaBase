from wikipediabase.fetcher import get_fetcher
from wikipediabase.log import Logging
from wikipediabase.util import (Expiry,
                                LRUCache,
                                fromstring,
                                markup_categories,
                                tostring,)

_ARTICLE_CACHE = LRUCache(100)

# XXX: also support images.


class Article(Logging):

    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title):
        self.title = title

    def url(self):
        # TODO: decode HTML entities
        symbol = self.title.replace(" ", "_")
        return u"https://en.wikipedia.org/wiki/%s" % symbol

    def _soup(self):
        if not hasattr(self, '__soup'):
            self.__soup = fromstring(self.html_source())

        return self.__soup

    def categories(self):
        return markup_categories(self.markup_source())

    def markup_source(self, force_live=False, expiry=Expiry.DEFAULT):
        """
        Markup source of the article.
        """
        if not hasattr(self, '_markup_source'):
            page = get_fetcher().markup_source(self.title,
                                               force_live=force_live,
                                               expiry=expiry)
            self._markup_source = page
        return self._markup_source

    def html_source(self, expiry=Expiry.DEFAULT):
        """
        HTML source of the article.
        """
        if not hasattr(self, '_html_source'):
            page = get_fetcher().html_source(self.title, expiry=expiry)
            self._html_source = page
        return self._html_source

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


def get_article(symbol):
    try:
        article = _ARTICLE_CACHE.get(symbol)
        return article
    except KeyError:
        article = Article(symbol)
        _ARTICLE_CACHE.set(symbol, article)
        return article
