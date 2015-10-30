from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.resolvers.error import ErrorResolver
from wikipediabase.resolvers.infobox import InfoboxResolver
from wikipediabase.resolvers.person import PersonResolver
from wikipediabase.resolvers.section import SectionResolver
from wikipediabase.resolvers.term import TermResolver
from wikipediabase.util import subclasses

WIKIBASE_RESOLVERS = []

__all__ = [
    "BaseResolver",
    "ErrorResolver",
    "InfoboxResolver",
    "PersonResolver",
    "SectionResolver",
    "TermResolver",
    "WIKIBASE_RESOLVERS",
]


def get_resolvers():
    global WIKIBASE_RESOLVERS
    if not WIKIBASE_RESOLVERS:
        WIKIBASE_RESOLVERS = subclasses(BaseResolver)
    return WIKIBASE_RESOLVERS


def resolve(cls, symbol, attr):
    for ar in get_resolvers():
        res = ar.resolve(cls, symbol, attr)
        if res is not None:
            break
    return res


def resolver_attributes(cls, symbol):
    for r in get_resolvers():
        attributes = r.attributes(cls, symbol)
        if attributes is not None:
            return attributes
    return []
