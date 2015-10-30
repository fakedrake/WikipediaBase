"""
Synonyms are are based upon:

- redirects
- inclusion/exlusion of parentheses
"""


import re
from wikipediabase.util import subclasses, string_reduce
from wikipediabase.fetcher import get_fetcher

WIKIBASE_INDUCERS = []
TITLE_REGEX = re.compile(r"\"wgTitle\":\"(.*?)\",")
# looks for the wgTitle element in a <script> block that contains metadata for
# wikipedia


def lexical_synonyms(symbol):
    """
    List of string_reduced lexical synonyms. Just try removing parens.
    """

    if '(' in symbol:
        ret = [symbol, re.sub(r"\(.*\)", "", symbol)]
    else:
        ret = [symbol]

    return map(string_reduce, ret)


class BaseInducer(object):

    """
    All inducers should take care of also lexically inducing.
    """

    priority = 0


class ForwardRedirectInducer(BaseInducer):

    """
    Finds the title of the article. Useful for redirects.
    """

    def title(self, symbol):
        html = get_fetcher().html_source(symbol)
        match = re.search(TITLE_REGEX, html)
        if match:
            return match.group(1)

    def induce(self, symbol):
        synonyms = []
        title = self.title(symbol)
        if title:
            sym = string_reduce(symbol)
            if title != sym:
                synonyms.extend(lexical_synonyms(title))

        return synonyms


class LexicalInducer(BaseInducer):

    """
    Induce just the lexicals of the symbol
    """

    def induce(self, symbol):
        return lexical_synonyms(symbol)


def get_inducers():
    global WIKIBASE_INDUCERS
    if not WIKIBASE_INDUCERS:
        WIKIBASE_INDUCERS = subclasses(BaseInducer)
    return WIKIBASE_INDUCERS


def induce(symbol):
    synonyms = set()
    for si in get_inducers():
        synonyms.update(si.induce(symbol))
    return synonyms
