import re

from wikipediabase.web_string.base import WebString
from wikipediabase.web_string.url import PageUrlString, UrlString
from wikipediabase.config import configuration, Configurable

class SymbolString(WebString):
    def __init__(self, data, configuration=configuration):
        super(SymbolString, self).__init__(data, configuration=configuration)

        self.fetcher = configuration.ref.fetcher.with_args(
            configuration=configuration)
        self.prefix = None
        self.symbol = re.sub(ur"\s*:\s*", u":", str(data))

        self.symbol = re.sub(ur"\s+", u" ", self.symbol).strip()

        if ':' in self.symbol:
            self.prefix, self.symbol = self.data.split(':', 1)

    def prefixed(self):
        if self.prefix:
            return self.prefix + ':' + self.symbol

        return self.symbol


    def reduced(self):
        """
        Remove punctuation, an/a/the and spaces.
        """
        # It may seem a bad idea to not even return 'the reckoning' from
        # symbol '"The Reckonning"' but we reduce user input as well.

        # First remove quotes so the stopwords turn up at the front
        ret = re.sub(ur"([\W\s]+)", " ", self.literal(),
                     flags=re.U|re.I).strip().lower()
        return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()

    def url_friendly(self):
        return re.sub(r"\s+", "_", self.prefixed())

    def synonym(self):
        """
        Get the true name of the article.
        """

        real_url = self.fetcher.redirect_url(self)
        urlstr = UrlString.from_url(real_url, configuration=configuration)
        if isinstance(urlstr, PageUrlString):
            return urlstr.symbol

        return self

    def literal(self):
        return re.sub(r"(\s+|_)", " ", self.symbol)

    def url(self, get=None, configuration=None):
        if configuration is None:
            configuration = self.configuration

        return PageUrlString(self, configuration=configuration) \
            .with_get(get or {})
