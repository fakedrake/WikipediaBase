"""
Each resolver is a provider tha may also provide an abstract way
of resolving an attribute through `resolve'.
"""

from provider import Provider, provide
from fetcher import BaseFetcher, WikipediaSiteFetcher

import re

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(.*)\s*\n\s*\|"
DATE_REGEX = r"(\d{4})\|(\d{1,2})\|(\d{1,2})\b"

class BaseResolver(Provider):

    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or BaseFetcher()

        self._tag = None

    def resolve(self, article, attribute, **kw):
        """
        Use your resources to resolve.
        """

        if attribute in self._resources:
            return self._resources[attribute](article, attribute)

    def tag(self):
        """
        For compatibility reasons we will want to know where we found each
        thing.
        """

        return self._tag

class StaticResolver(BaseResolver):
    """
    A resolver that can resolve a fixed set of simple attributes.
    """


    def _words(self, article):
        return re.findall('\w+', article.lower())

    @provide(name="word-count")
    def word_cout(self, article, attribute):
        self.log().info("Trying 'word-count' tag from static resolver.")
        self._tag = "html"
        return len(self._words(self.fetcher.fetch(article)))

    @provide(name="COORDINATES")
    def coordinates(self, article, attribute):
        self.log().info("Trying 'coordnates' tag from static resolver.")
        self._tag = 'coordinates'

        return 0,0

class InfoboxResolver(BaseResolver):
    """
    Use this to resolve based on the resolver.
    """

    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or WikipediaSiteFetcher()
        self._tag = "html"

    def resolve(self, article, attribute, rendered=False, **kw):
        self.log().info("Using infobox resolver")
        if "\n" in article:
            # There are no newlines in article titles
            return None

        attribute = attribute.replace("-", "_")
        infobox = self.fetcher.infobox(article, rendered=rendered)

        if infobox:
            val = re.search(INFOBOX_ATTRIBUTE_REGEX % attribute, infobox, flags=re.IGNORECASE)
            if val:
                self.log().info("Found infobox attribute '%s'" % attribute)
                return re.sub(r"[^\w.,()|/]+", " ", val.group(1)).strip()

            self.log().warning("Could nont find infobox attribute '%s'" % attribute)

class InfoboxDateResolver(InfoboxResolver):
    def __init__(self, *args, **kwargs):
        super(InfoboxDateResolver, self).__init__(*args, **kwargs)
        self._tag = "yyyymmdd"

    def resolve(self, *args, **kw):
        """
        Try to resolve a date or fail.
        """

        self.log().info("Trying to pull a date from the infobox.")

        date = super(InfoboxDateResolver, self).resolve(*args, **kw)

        if date:
            only_date = re.search(DATE_REGEX, date)
            if only_date:
                ret = "%04d%02d%02d" % tuple([int(i) for i in only_date.groups()])
                return int(ret)

        self.log().info("No luck with the dates.")
