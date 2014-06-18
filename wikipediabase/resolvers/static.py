import re

from wikipediabase.provider import provide
from base import BaseResolver

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
