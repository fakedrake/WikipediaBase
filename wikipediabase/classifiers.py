"""
Symbol annotation. Subclass BaseClassifier provideing the classify
method and return an iterable of strings that are the classes that
your classifier provides.
"""

import re

from wikipediabase.util import get_infobox, get_article, subclasses
from wikipediabase.config import Configurable, configuration


# Return a LIST of classes
class BaseClassifier(Configurable):

    """
    Given a symbol provide some classes for it.
    """
    priority = 0
    fetcher = None

    def classify(self, symbol, configuration=configuration):
        raise NotImplemented("Abstract function.")

    def __call__(self, *args, **kw):
        return self.classify(*args, **kw)


class StaticClassifier(BaseClassifier):

    def classify(self, symbol, configuration=configuration):
        return ['wikipedia-term']


class InfoboxClassifier(BaseClassifier):

    def classify(self, symbol, configuration=configuration):
        ibox = get_infobox(symbol, configuration)
        types = ibox.start_types()

        return types


class _CategoryClassifier(BaseClassifier):

    def classify(self, symbol, configuration=configuration):
        article = get_article(symbol, configuration)
        return article.categories()


class PersonClassifier(BaseClassifier):

    male_prep = ["he", "him", "his"]
    female_prep = ["she", "her"]

    def is_person(self, symbol):
        ibx = get_infobox(symbol, self.configuration)
        if ibx.get('birth-date'):
            return True

        from wikipediabase.resolvers import LifespanParagraphResolver as LPR
        if LPR().resolve(symbol, 'birth-date'):
            return True

        return False

    def is_male(self, symbol):
        art = get_article(symbol, self.configuration)
        full_text = "\n\n".join(art.paragraphs())

        def word_search(w):
            return len(re.findall(r"\b%s\b" % w, full_text, re.I))

        male_words = sum(map(word_search, self.male_prep))
        female_words = sum(map(word_search, self.female_prep))

        return male_words > female_words

    def classify(self, symbol, configuration=configuration):
        ret = []
        if self.is_person(symbol):
            ret += ['wikipedia-person']

            if self.is_male(symbol):
                ret += ['wikipedia-male']
            else:
                ret += ['wikipedia-female']

        return ret


WIKIBASE_CLASSIFIERS = subclasses(BaseClassifier)
