from wikipediabase.classifiers import is_wikipedia_class
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.lispify import lispify, LispType
from wikipediabase.resolvers.base import BaseResolver, check_resolver
from wikipediabase.util import get_infoboxes


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

    def _should_resolve(self, cls):
        return is_wikipedia_class(cls)

    def resolve_infobox(self, cls, symbol, attr):
        """
        Return the value of the attribute for the article.
        """

        if "\n" in symbol:
            # There are no newlines in article titles
            return None

        if isinstance(attr, LispType):
            typecode, attr = attr.typecode, attr.val
        else:
            typecode, attr = self._typecode, attr

        infoboxes = get_infoboxes(symbol, cls=cls, fetcher=self.fetcher)

        for ibox in infoboxes:
            result = ibox.get(attr)
            if result:
                self.log().info("Found infobox attribute '%s'" % attr)
                assert(isinstance(result, unicode))  # TODO: remove for production

                return lispify(result, typecode=typecode, infobox_attr=attr)

            self.log().warning("Could not find infobox attribute '%s'" % attr)

        self.log().warning("Could not resolve attribute '%s' for '%s' with "
                           "class '%s'", attr, symbol, cls)

    @check_resolver
    def attributes(self, cls, symbol):
        """
        Get all infobox attributes
        """

        attributes = []
        infoboxes = get_infoboxes(symbol, cls=cls, fetcher=self.fetcher)

        for ibox in infoboxes:
            for k, v in ibox.markup_parsed_iter():
                rendered = ibox.rendered_attributes().get(k.replace('-', '_'))
                tmp = dict(code=k.upper(), rendered=rendered)
                attributes.append(tmp)

        return lispify(attributes)
