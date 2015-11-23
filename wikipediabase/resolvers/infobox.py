from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.util import get_infobox
from wikipediabase.enchantments import enchant, Enchanted
from wikipediabase.config import configuration


class InfoboxResolver(BaseResolver):

    """
    Use this to resolve based on the resolver.
    """

    priority = 10

    def __init__(self, configuration=configuration, **kw):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(InfoboxResolver, self).__init__(configuration=configuration, **kw)
        self.configuration = configuration
        self.fetcher = configuration.ref.fetcher
        self._tag = "html"

    def resolve(self, article, attribute, **kw):
        """
        Return the value of the attribute for the article.
        """

        if "\n" in article:
            # There are no newlines in article titles
            return None

        if isinstance(attribute, Enchanted):
            key, attr = attribute.tag, attribute.val
        else:
            key, attr = None, attribute

        ibox = get_infobox(article, configuration=self.configuration)

        if ibox:
            ret = ibox.get(attr)
            if ret:
                return enchant(key, ret, result_from=attr)
