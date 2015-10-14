from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.resolvers.error import ErrorResolver
from wikipediabase.resolvers.infobox import InfoboxResolver
from wikipediabase.resolvers.person import PersonResolver
from wikipediabase.resolvers.section import SectionResolver
from wikipediabase.resolvers.term import TermResolver
from wikipediabase.util import subclasses

WIKIBASE_RESOLVERS = subclasses(BaseResolver)

__all__ = [
    "BaseResolver",
    "ErrorResolver",
    "InfoboxResolver",
    "PersonResolver",
    "SectionResolver",
    "TermResolver",
    "WIKIBASE_RESOLVERS",
]
