# -*- coding: utf-8 -*-

import re

import overlay_parse

from wikipediabase.article import get_article
from wikipediabase.classifiers import InfoboxClassifier
from wikipediabase.lispify import lispify, lispify_error
from wikipediabase.provider import provide
from wikipediabase.resolvers import InfoboxResolver
from wikipediabase.resolvers.base import BaseResolver


def iter_paren(text, delim=None):
    """
    Iterate over the top-level parentheses of text
    """

    depth = 0
    first_paren = None

    for i, c in enumerate(text):
        if c == "(":
            depth += 1
            if depth == 1:
                first_paren = i + 1

        elif c == ")" and depth > 0:
            if depth == 1:
                yield (first_paren, i)

            depth -= 1

        if depth == 0 and text[i:].startswith(delim):
            break


def first_paren(text):
    for s, e in iter_paren(text, "."):
        return text[s:e]

def remove_annotations(text):
    return re.sub(r'\[[0-9]+\]', '', text)

def find_date(symbol, date_type):
    """
    Resolve birth and death dates from infoboxes, or, if it is not found,
    from the first paragraph
    """

    def missing(ls):
        return sum([x==0 for x in ls])

    for cls in InfoboxClassifier().classify(symbol):
        ibox_date = InfoboxResolver().resolve_infobox(cls, symbol, date_type)
        if ibox_date is not None:
            return ibox_date

    # TODO: look at categories for dates

    article = get_article(symbol)
    text = remove_annotations(article.paragraphs()[0])  # the first paragraph
    for s, e in iter_paren(text, "."):
        paren = text[s:e]

        # The date range with the least missing values
        nil = ((0,0,0),(0,0,0))
        best_rng = reduce(lambda (x1,x2), (y1,y2): (x1,x2) if \
                          missing(x1)+missing(x2) <= missing(y1)+missing(y2)
                          else (y1,y2),
                          overlay_parse.dates.just_ranges(paren),
                          nil)

        if best_rng is not nil:
            if date_type == 'birth-date':
                return lispify(best_rng[0], typecode='yyyymmdd')
            elif date_type == 'death-date':
                return lispify(best_rng[1], typecode='yyyymmdd')

        if date_type == 'birth-date':
            nil = (0,0,0)
            best_date = reduce(lambda x, y: x if missing(x) <= missing(y) else y,
                               overlay_parse.dates.just_dates(paren), nil)
            if best_date is not nil:
                return lispify(best_date, typecode='yyyymmdd')


class PersonResolver(BaseResolver):

    """
    A resolver that can resolve a fixed set of simple attributes.
    """

    priority = 9

    def _should_resolve(self, cls):
        return cls == 'wikibase-person'

    @provide(name='birth-date')
    def birth_date(self, symbol, _):
        return find_date(symbol, 'birth-date')

    @provide(name='death-date')
    def death_date(self, symbol, _):
        death_date = find_date(symbol, 'death-date')
        if death_date:
            return death_date
        else:
            if self.birth_date(symbol, _):
                return lispify_error('attribute-value-not-found',
                                     reply='Currently alive')

    @provide(name='gender')
    def gender(self, symbol, _):
        gender = ":" + self._guess_gender(symbol)
        return lispify(gender, typecode='calculated')

    def _guess_gender(self, symbol):
        male_prep = ["he", "him", "his"]
        female_prep = ["she", "her", "hers"]
        neuter_prep = ["it", "its", "they", "their", "theirs"]

        article = get_article(symbol)
        full_text = article.markup_source().lower()

        def word_search(w):
            return len(re.findall(r"\b%s\b" % w, full_text, re.I))

        male_words = sum(map(word_search, male_prep))
        female_words = sum(map(word_search, female_prep))
        neuter_words = sum(map(word_search, neuter_prep))

        if neuter_words > male_words and neuter_words > female_words:
            return 'neuter'
        elif male_words >= female_words:
            return 'masculine'
        else:
            return 'feminine'
