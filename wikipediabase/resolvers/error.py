from .base import MIN_PRIORITY, BaseResolver
from ..util import get_knowledgebase
from ..enchantments import enchant

class ErrorResolver(BaseResolver):
    """
    Yield an error message given that all else failed
    """

    priority = MIN_PRIORITY

    @staticmethod
    def _err(repl=None, sym=None):
        return enchant('error', {'symbol': sym or 'attribute-value-not-found',
                                 'kw': {'reply': repl or 'No such attribute'}})

    def resolve(self, article, attribute):
        kb = get_knowledgebase()

        if 'wikipedia-person' in kb.get_classes(article) and \
           attribute.lower() == 'death-date' and kb.get(article, 'birth-date'):
            return self._err("Currently alive")

        return self._err("Unknown")
