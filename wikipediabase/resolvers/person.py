# -*- coding: utf-8 -*-

import re

import overlay_parse

from wikipediabase.classifiers import InfoboxClassifier
from wikipediabase.lispify import lispify
from wikipediabase.provider import provide
from wikipediabase.resolvers import InfoboxResolver
from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.util import get_article


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


def find_date(symbol, date_type):
    """
    Resolve birth and death dates from infoboxes, or, if it is not found,
    from the first paragraph
    """
    for cls in InfoboxClassifier().classify(symbol):
        ibox_date = InfoboxResolver().resolve_infobox(cls, symbol, date_type)
        if ibox_date is not None:
            return ibox_date

    # TODO: look at categories for dates

    article = get_article(symbol)
    text = article.paragraphs()[0]  # the first paragraph
    for s, e in iter_paren(text, "."):
        paren = text[s:e]

        for ovl in overlay_parse.dates.just_ranges(paren):
            if date_type == 'birth-date':
                return lispify(ovl[0], typecode='yyyymmdd')
            elif date_type == 'death-date':
                return lispify(ovl[1], typecode='yyyymmdd')

        # If there is just one date and we need a birth date, get that
        if date_type == 'birth-date':
            for ovl in overlay_parse.dates.just_dates(paren):
                return lispify(ovl, typecode='yyyymmdd')


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
        return find_date(symbol, 'death-date')

    @provide(name='gender')
    def gender(self, symbol, _):
        gender = ":" + self._guess_gender(symbol)
        return lispify(gender, typecode='calculated')

    def _guess_gender(self, symbol):
        male_prep = ["he", "him", "his"]
        female_prep = ["she", "her", "hers"]
        neuter_prep = ["it", "its", "they", "their", "theirs"]

        article = get_article(symbol, fetcher=self.fetcher)
        full_text = "\n\n".join(article.paragraphs()).lower()

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
