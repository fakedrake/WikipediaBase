import os

from wikipediabase.config import Configurable, configuration
from wikipediabase.util import (markup_categories,
                                fromstring,
                                totext,
                                url_get_dict,
                                get_infobox)
from wikipediabase.web_string import SymbolString

# XXX: also support images.
class Article(Configurable):

    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title, configuration=configuration):
        self.symbol = SymbolString(title, configuration=configuration)
        self.config = configuration
        self.fetcher = configuration.ref.fetcher.with_args(
            configuration=configuration)
        self.xml_string = configuration.ref.strings.xml_string_class

        self.ibox = None
        self._xml = None
        self._url = None

    def url(self):
        return self.symbol.url()

    def xml(self):
        if self._xml is None:
            self._xml = self.html_source()

        return self._xml

    def categories(self):
        return markup_categories(self.markup_source())

    def infobox(self):
        if not self.ibox:
            self.ibox = get_infobox(self.title(), configuration=self.config)

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

        heading = next(self.xml().xpath(".//*[@id='firstHeading']"), None)
        if heading is not None:
            return heading.text().strip()

        open("/tmp/err.html", "w").write(self.xml().raw())
        raise Exception("No title found for '%s' url: %s" % (self.symbol.url_friendly(), self.url()))

    def markup_source(self):
        """
        Markup source of the article.
        """

        return self.fetcher.source(self.symbol.url_friendly())

    def html_source(self):
        """
        Markup source of the article.
        """

        return self.xml_string(self.fetcher.download(self.symbol))

    def paragraphs(self):
        """
        Generate paragraphs.
        """

        return [p.text() for p in
                self.xml().xpath(".//*[@id='mw-content-text']/p")
                if p.text()]

    def headings(self):
        """
        Generate all the headings in a DFS fashion.
        """

        xml = self.xml()
        xpath = ".//*[@id='mw-content-text']//span[@class='mw-headline']/.."

        return [h.text()[:-len("[edit]")]
                for h in xml.xpath(xpath)
                if h.text()]

    def first_paragraph(self):
        for p in self.paragraphs():
            if p.strip():
                return p

        return None
