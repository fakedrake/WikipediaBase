from .base import BaseResolver
from ..util import get_infobox
from ..enchantments import enchant, Enchanted
from ..fetcher import WIKIBASE_FETCHER


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

        ibox = get_infobox(article, self.fetcher)

        if ibox:
            ret = ibox.get(attr)
            if ret:
                self.log().info("Found infobox attribute '%s'" % attr)
                return enchant(key, ret, result_from=attr,
                               log=self.log())

            self.log().warning("Could nont find infobox attribute '%s'"
                               % attr)
        else:
            self.log().warning("Could nont find infobox for article '%s'"
                               % article)
