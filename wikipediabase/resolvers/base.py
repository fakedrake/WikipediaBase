from wikipediabase.enchantments import Enchanted
from wikipediabase.fetcher import CachingSiteFetcher
from wikipediabase.provider import Provider
from wikipediabase.config import configuration

MIN_PRIORITY = 0

class BaseResolver(Provider):

    priority = 1

    def __init__(self, compat=True, configuration=configuration):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(configuration=configuration)
        self.fetcher = configuration.ref.fetcher
        self.compat = compat

        self._tag = None

    def resolve(self, article, attribute, **kw):
        """
        Use your resources to resolve. Use provided methods if available
        or return None.
        """
        if isinstance(attribute, Enchanted):
            attr = attribute.val
        else:
            attr = attribute

        attr = attr.lower()
        if attr in self._resources:
            return self._resources[attr](article, attribute)
