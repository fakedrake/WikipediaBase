from ..util import subclasses
from .base import BaseResolver
from .paragraph import LifespanPragraphResolver
from .infobox import InfoboxResolver
from .static import StaticResolver

WIKIBASE_RESOLVERS = subclasses(BaseResolver)

__all__ = ["WIKIBASE_RESOLVERS",
           "BaseResolver",
           "LifespanPragraphResolver",
           "InfoboxResolver",
           "StaticResolver"]
