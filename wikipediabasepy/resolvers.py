"""
Each resolver is a provider tha may also provide an abstract way
of resolving an attribute through `resolve'.
"""

from provider import Provider, provide

import re

class BaseFetcher(object):
    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    def fetch(self, article):
        """
        Just return the article itself.
        """

        return article


class BaseResolver(Provider):
    def __init__(self, fetcher=None, *args, **kwargs):
        """
        Provide a way to fetch articles. If no fetcher is provider
        fallback to BaseFetcher.
        """

        super(BaseResolver, self).__init__(*args, **kwargs)
        self.fetcher = fetcher or BaseFetcher()

    def resolve(self, article, attribute):
        """
        Use your resources to resolve.
        """

        if attribute in self._resources:
            return self._resources[attribute](article, attribute)


class StaticResolver(BaseResolver):
    """
    A resolver that can resolve a fixed set of simple attributes.
    """


    def _words(self, article):
        return re.findall('\w+', article.lower())

    @provide(name="word-count")
    def word_cout(self, article, attribute):
        return len(self._words(self.fetcher.fetch(article)))
