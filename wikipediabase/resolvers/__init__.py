from wikipediabase.util import subclasses
from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.resolvers.paragraph import LifespanParagraphResolver
from wikipediabase.resolvers.infobox import InfoboxResolver
from wikipediabase.resolvers.static import StaticResolver
from wikipediabase.resolvers.error import ErrorResolver

WIKIBASE_RESOLVERS = subclasses(BaseResolver)

__all__ = [
    "WIKIBASE_RESOLVERS",
    "BaseResolver",
    "LifespanParagraphResolver",
    "InfoboxResolver",
    "StaticResolver",
    "ErrorResolver",
]
