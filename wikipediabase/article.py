import os

from wikipediabase.config import Configurable, configuration
from wikipediabase.util import (markup_categories,
                                fromstring,
                                totext,
                                memoized,
                                url_get_dict,
                                get_infobox)

# XXX: also support images.
class Article(Configurable):

    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title, configuration=configuration):
        self._title = title
        self.fetcher = configuration.ref.fetcher.with_args(configuration=configuration)
        self.ibox = None
        self.__soup = None

    @memoized
    def url(self):
        return self.fetcher.urlopen(self._title).geturl()

    def symbol(self):
        url = self.url()
        return url_get_dict(url).get('title') or \
            os.path.basename(url)

    def _soup(self):
        if self.__soup is None:
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

    def first_paragraph(self):
        for p in self.paragraphs():
            if p.strip():
                return p

        return None
