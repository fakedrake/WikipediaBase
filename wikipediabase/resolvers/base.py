from wikipediabase.enchanted import Enchanted
from wikipediabase.fetcher import CachingSiteFetcher
from wikipediabase.provider import Provider

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
        Use your resources to resolve. Use provided methods if available
        or return None.
        """

        if isinstance(attribute, Enchanted):
            attr = attribute.val
        else:
            attr = attribute

        if attr in self._resources:
            return self._resources[attr](article, attribute)
