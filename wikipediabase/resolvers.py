"""
Each resolver is a provider tha may also provide an abstract way
of resolving an attribute through `resolve'.
"""

import re
import bs4

from provider import Provider, provide
from fetcher import BaseFetcher, WikipediaSiteFetcher, CachingSiteFetcher
from enchantments import enchant, Enchanted
from infobox import Infobox

class BaseResolver(Provider):

    def __init__(self, fetcher=None, compat=True, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or CachingSiteFetcher()
        self.compat = compat

        self._tag = None

    def resolve(self, article, attribute, **kw):
        """
        Use your resources to resolve.
        """

        if isinstance(attribute, Enchanted):
            attr = attribute.val
        else:
            attr = attribute

        if attr in self._resources:
            return self._resources[attr](article, attribute)


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
        return len(self._words(self.fetcher.download(article)))

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
        """
        Return the value of the attribute for the article.
        """

        self.log().info("Using infobox resolver in %s mode" %
                        "compatibility" if self.compat else "classic")
        if "\n" in article:
            # There are no newlines in article titles
            return None

        if isinstance(attribute, Enchanted):
            key, attr = attribute.tag, attribute.val
        else:
            key, attr = None, attribute

        ibox = Infobox(article, self.fetcher)

        if ibox:
            ret = ibox.get(attr)
            if ret:
                self.log().info("Found infobox attribute '%s'" % attr)
                return enchant(key, ret, result_from=attr,
                               gcompat=self.compat, log=self.log())

            self.log().warning("Could nont find infobox attribute '%s'" \
                               % attr)
        else:
            self.log().warning("Could nont find infobox for article '%s'" \
                               % article)
