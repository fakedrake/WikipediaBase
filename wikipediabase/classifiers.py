"""
Subclass BaseClassifier and implement the classify()
method to return an iterable of strings.

Classes can be one of two kinds:
 * infobox templates, prefixed by "wikipedia-"
 * calculated classes, prefixed by "wikibase-"
"""

import re

from wikipediabase.util import get_infobox, get_article, subclasses
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

    male_prep = ["he", "him", "his"]
    female_prep = ["she", "her"]

    def is_person(self, symbol):
        ibx = get_infobox(symbol, fetcher=self.fetcher)
        if ibx.get('birth-date'):
            return True

        from wikipediabase.resolvers import LifespanParagraphResolver as LPR
        if LPR().resolve(symbol, 'birth-date'):
            return True

        return False

    def is_male(self, symbol):
        art = get_article(symbol, fetcher=self.fetcher)
        full_text = "\n\n".join(art.paragraphs())

        def word_search(w):
            return len(re.findall(r"\b%s\b" % w, full_text, re.I))

        male_words = sum(map(word_search, self.male_prep))
        female_words = sum(map(word_search, self.female_prep))

        return male_words > female_words

    def classify(self, symbol, fetcher=None):
        if fetcher:
            self.fetcher = fetcher

        ret = []
        if self.is_person(symbol):
            ret += ['wikibase-person']

            if self.is_male(symbol):
                ret += ['wikibase-male']
            else:
                ret += ['wikibase-female']

        return ret


WIKIBASE_CLASSIFIERS = subclasses(BaseClassifier)
