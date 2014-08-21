from ..util import subclasses
from .base import BaseResolver
from .paragraph import LifespanParagraphResolver
from .infobox import InfoboxResolver
from .static import StaticResolver
from .error import ErrorResolver

WIKIBASE_RESOLVERS = subclasses(BaseResolver)

__all__ = [
    "WIKIBASE_RESOLVERS",
    "BaseResolver",
    "LifespanParagraphResolver",
    "InfoboxResolver",
    "StaticResolver",
    "ErrorResolver",
]
