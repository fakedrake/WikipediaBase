from wikipediabase.resolvers.base import BaseResolver


class SectionsResolver(BaseResolver):

    """
    A resolver that gets sections from articles
    """
    priority = 8

    def _should_resolve(self, symbol, attr, cls=None, **kwargs):
        return cls == 'wikibase-sections'

    def resolve_sections():
        # TODO : implement resolver
        return None
