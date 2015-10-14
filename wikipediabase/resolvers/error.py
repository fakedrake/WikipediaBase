from wikipediabase.resolvers.base import MIN_PRIORITY, BaseResolver
from wikipediabase.util import get_knowledgebase
from wikipediabase.lispify import lispify, LispType


class ErrorResolver(BaseResolver):

    """
    Yield an error message given that all else failed
    """

    priority = MIN_PRIORITY

    @staticmethod
    def _err(repl=None, sym=None):
        return lispify({'symbol': sym or 'attribute-value-not-found',
                        'kw': {'reply': repl or 'No such attribute'}},
                       typecode='error')

    def resolve_error(self, cls, symbol, attr):
        kb = get_knowledgebase()

        if isinstance(attr, LispType):
            attr = attr.val
        else:
            attr = attr

        attr = attr.lower()

        # TODO: seems hacky, move to its own method and allow for multiple
        # error conditions
        if 'wikibase-person' in kb.get_classes(symbol) and \
           attr.lower().startswith('death-') and \
           kb.get(cls, symbol, 'birth-date'):
            return self._err("Currently alive")

        return self._err("Unknown")
