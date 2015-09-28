"""
Synonyms are are based upon:

- redirects
- inclusion/exlusion of parentheses
"""


import re
from wikipediabase.util import subclasses, string_reduce
from wikipediabase.fetcher import WIKIBASE_FETCHER

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

    def title(self, symbol, fetcher=None):
        fetcher = fetcher or WIKIBASE_FETCHER
        html = fetcher.html_source(symbol)
        match = re.search(TITLE_REGEX, html)
        if match:
            return match.group(1)

    def induce(self, symbol, fetcher=None):
        synonyms = []
        fetcher = fetcher or WIKIBASE_FETCHER
        title = self.title(symbol, fetcher=fetcher)
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


WIKIBASE_INDUCERS = subclasses(BaseInducer)
