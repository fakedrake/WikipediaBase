"""
Subclass BaseClassifier and implement the classify()
method to return an iterable of strings.

Classes can be one of two kinds:
 * infobox templates, prefixed by "wikipedia-"
 * calculated classes, prefixed by "wikibase-"
"""

from itertools import chain
import re

from wikipediabase.article import get_article
from wikipediabase.infobox import get_infoboxes
from wikipediabase.log import Logging
from wikipediabase.util import subclasses

WIKIBASE_CLASSIFIERS = []


def is_wikipedia_class(cls):
    return cls.startswith('wikipedia-')


def is_wikibase_class(cls):
    return cls.startswith('wikibase-')


class BaseClassifier(Logging):

    """
    Given a symbol provide some classes for it.
    """
    priority = 0

    def classify(self, symbol):
        raise NotImplemented("Abstract function.")

    def __call__(self, symbol, *av, **kw):
        return self.classify(symbol, *av, **kw)


class TermClassifier(BaseClassifier):

    def classify(self, symbol):
        return ['wikibase-term']


class SectionsClassifier(BaseClassifier):

    def classify(self, symbol):
        return ['wikibase-sections']


class InfoboxClassifier(BaseClassifier):

    def classify(self, symbol):
        classes = []
        for ibox in get_infoboxes(symbol):
            classes.append(ibox.cls)
        return classes


class PersonClassifier(BaseClassifier):

    CATEGORY_REGEXES = [re.compile(p) for p in [
        ".* people",
        ".* person",
        "^\d+ deaths.*",
        "^\d+ births.*",
        ".* actors",
        ".* musicians",
        ".* players",
        ".* singers",
    ]]

    CATEGORY_MATCHES = [
        "american actors",
        "american television actor stubs",
        "american television actors",
        "architects",
        "british mps",
        "character actors"
        "computer scientist",
        "dead people rumoured to be living",
        "disappeared people",
        "fictional characters",
        "film actors",
        "living people",
        "musician stubs",
        "singer stubs",
        "star stubs",
        "united kingdom writer stubs",
        "united states singer stubs",
        "writer stubs",
        "year of birth missing",
        "year of death missing",
    ]

    def is_person(self, symbol):
        article = get_article(symbol)
        for category in article.categories():
            category = category.lower()
            for pattern in self.CATEGORY_REGEXES:
                if pattern.match(category):
                    return True

            for substring in self.CATEGORY_MATCHES:
                if substring in category:
                    return True

        return False

    def classify(self, symbol):
        classes = []
        if self.is_person(symbol):
            classes += ['wikibase-person']
        return classes


def get_classifiers():
    global WIKIBASE_CLASSIFIERS
    if not WIKIBASE_CLASSIFIERS:
        WIKIBASE_CLASSIFIERS = subclasses(BaseClassifier)
    return WIKIBASE_CLASSIFIERS


def classify(symbol):
    it = chain.from_iterable((c.classify(symbol)) for c in get_classifiers())
    return list(it)
