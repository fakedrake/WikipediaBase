from wikipediabase.lispify import lispify
from wikipediabase.provider import provide
from wikipediabase.resolvers.base import BaseResolver, check_resolver


class SectionResolver(BaseResolver):

    """
    A resolver that gets sections from articles
    """
    priority = 8

    def _should_resolve(self, cls):
        return cls == 'wikibase-sections'

    @provide(name="sections")
    def resolve_section(self, cls, symbol, attr):
        # TODO : implement sections resolver
        return lispify([])

    @check_resolver
    def attributes(self, cls, symbol):
        # TODO : return section headings as attributes
        return lispify([])
