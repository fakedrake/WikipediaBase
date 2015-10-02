"""
Subclass BaseClassifier and implement the classify()
method to return an iterable of strings.

Classes can be one of two kinds:
 * infobox templates, prefixed by "wikipedia-"
 * calculated classes, prefixed by "wikibase-"
"""

from wikipediabase.util import get_infobox, subclasses
from wikipediabase.log import Logging

# Return a LIST of classes


class BaseClassifier(Logging):

    """
    Given a symbol provide some classes for it.
    """
    priority = 0
    fetcher = None

    def classify(self, symbol, fetcher=None):
        raise NotImplemented("Abstract function.")

    def __call__(self, symbol, *av, **kw):
        return self.classify(symbol, *av, **kw)


class StaticClassifier(BaseClassifier):

    def classify(self, symbol, fetcher=None):
        return ['wikibase-term', 'wikibase-paragraphs']


class InfoboxClassifier(BaseClassifier):

    def classify(self, symbol, fetcher=None):
        ibox = get_infobox(symbol, fetcher)
        classes = ibox.classes()

        return classes


class PersonClassifier(BaseClassifier):

    def is_person(self, symbol):
        # TODO : test the precision of this method of determining is_person
        ibx = get_infobox(symbol, fetcher=self.fetcher)

        if 'wikipedia-person' in ibx.classes():
            # TODO : check for children of the infobox class
            return True

        if ibx.get('birth-date'):
            return True

        from wikipediabase.resolvers import LifespanParagraphResolver as LPR
        if LPR().resolve(symbol, 'birth-date'):
            return True

        return False

    def classify(self, symbol, fetcher=None):
        if fetcher:
            self.fetcher = fetcher

        classes = []
        if self.is_person(symbol):
            classes += ['wikibase-person']
        return classes


WIKIBASE_CLASSIFIERS = subclasses(BaseClassifier)
