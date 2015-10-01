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
        self._typecode = "html"

    def resolve(self, symbol, attr, cls=None):
        """
        Return the value of the attribute for the article.
        """

        if "\n" in symbol:
            # There are no newlines in article titles
            return None

        if isinstance(attr, Enchanted):
            typecode, attr = attr.typecode, attr.val
        else:
            typecode, attr = self._typecode, attr

        ibox = get_infobox(symbol, self.fetcher)

        if ibox:
            result = ibox.get(attr)
            if result:
                self.log().info("Found infobox attribute '%s'" % attr)
                assert(isinstance(result, unicode)) # TODO: remove for production

                return enchant(result, typecode=typecode, infobox_attr=attr)

            self.log().warning("Could not find infobox attribute '%s'" % attr)
        else:
            self.log().warning("Could not find infobox for article '%s'"
                               % symbol)
