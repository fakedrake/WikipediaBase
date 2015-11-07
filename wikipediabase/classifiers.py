"""
Subclass BaseClassifier and implement the classify()
method to return an iterable of strings.

Classes can be one of two kinds:
 * infobox templates, prefixed by "wikipedia-"
 * calculated classes, prefixed by "wikibase-"
"""

from itertools import chain

from wikipediabase.log import Logging
from wikipediabase.infobox import get_infoboxes
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
            classes.append(ibox.wikipedia_class)
        return classes


class PersonClassifier(BaseClassifier):

    def is_person(self, symbol):
        # TODO : test the precision of this method of determining is_person
        infoboxes = get_infoboxes(symbol)
        for ibx in infoboxes:
            if ibx.wikipedia_class == 'wikipedia-person' or \
                    ibx.get('birth-date'):
                return True

        from wikipediabase.resolvers import PersonResolver
        if PersonResolver().birth_date(symbol, 'birth-date'):
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
