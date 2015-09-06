from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.util import get_infobox
from wikipediabase.enchantments import enchant, Enchanted
from wikipediabase.fetcher import WIKIBASE_FETCHER


class InfoboxResolver(BaseResolver):

    """
    Use this to resolve based on the resolver.
    """

    priority = 10

    def __init__(self, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(InfoboxResolver, self).__init__(*args, **kwargs)
        self.fetcher = kwargs.get('fetcher', WIKIBASE_FETCHER)
        self._tag = "html"

    def resolve(self, symbol, attr, cls=None):
        """
        Return the value of the attribute for the article.
        """

        if "\n" in symbol:
            # There are no newlines in article titles
            return None

        if isinstance(attr, Enchanted):
            key, attr = attr.tag, attr.val
        else:
            key, attr = None, attr

        ibox = get_infobox(symbol, self.fetcher)

        if ibox:
            ret = ibox.get(attr)
            if ret:
                self.log().info("Found infobox attribute '%s'" % attr)
                assert(isinstance(ret, unicode))  # TODO: remove for production
                return enchant(key, ret, result_from=attr, log=self.log())

            self.log().warning("Could not find infobox attribute '%s'" % attr)
        else:
            self.log().warning("Could not find infobox for article '%s'"
                               % symbol)
