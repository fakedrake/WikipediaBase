from wikipediabase.enchantments import Enchanted
from wikipediabase.fetcher import Fetcher
from wikipediabase.provider import Provider

MIN_PRIORITY = 0

class BaseResolver(Provider):

    priority = 1

    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or Fetcher()

        self._tag = None

    def resolve(self, symbol, attr, **kw):
        """

        Use your resources to resolve. Use provided methods if available
        or return None.
        """
        if isinstance(attr, Enchanted):
            attr = attr.val
        else:
            attr = attr

        attr = attr.lower()
        if attr in self._resources:
            return self._resources[attr](symbol, attr)
