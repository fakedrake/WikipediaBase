"""
Each resolver is a provider tha may also provide an abstract way
of resolving an attribute through `resolve'.
"""

from provider import Provider, provide
from fetcher import BaseFetcher, WikipediaSiteFetcher
from enchanted import Enchanted
from enchantments import enchant
from dates import EnchantedDate
from util import INFOBOX_ATTRIBUTE_REGEX

import re


class BaseResolver(Provider):

    def __init__(self, fetcher=None, compat=True, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or BaseFetcher()
        self.compat = compat

        self._tag = None

    def resolve(self, article, attribute, **kw):
        """
        Use your resources to resolve.
        """

        key, attr = Enchanted.keyattr(attribute)

        if attr in self._resources:
            return self._resources[attr](article, attribute)

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

        return EnchantedList("coordinates", [0,0])

    @provide(name="gender")
    def gender(self, article, attribute):
        return ":hermaphrodie"

    @provide(name="image-data")
    def image(self, article, attribute):
        return "hello.jpg"


class InfoboxResolver(BaseResolver):
    """
    Use this to resolve based on the resolver.
    """

    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(InfoboxResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or WikipediaSiteFetcher()
        self._tag = "html"

    def resolve(self, article, attribute, **kw):
        self.log().info("Using infobox resolver in %s mode" %
                        "compatibility" if self.compat else "classic")
        if "\n" in article:
            # There are no newlines in article titles
            return None

        key, attr = Enchanted.keyattr(attribute)

        attr = attr.replace("-", "_").lower()
        infobox = self.fetcher.infobox(article, rendered=(key=="html"))

        if infobox:
            val = re.search(INFOBOX_ATTRIBUTE_REGEX % attr,
                            infobox, flags=re.IGNORECASE|re.DOTALL)
            if val:
                self.log().info("Found infobox attribute '%s'" % attr)
                ret = val.group("val")

                return enchant(key, ret, result_from=attr, compat=self.compat, log=self.log())

            self.log().warning("Could nont find infobox attribute '%s'" \
                               % attribute)
