"""
Synonyms are are based upon:

- redirects
- inclusion/exlusion of parentheses
"""


import re
from .util import get_article, expand, concat, subclasses, fromstring
from .fetcher import WIKIBASE_FETCHER


def string_reduce(string):
    """
    Remove punctuation, an/a/the and spaces.
    """
    # It may seem a bad idea to not even return 'the reckoning' from
    # symbol '"The Reckonging"' but we rduce user input as well.

    # First remove quotes so the stopwords turn up at the front
    ret = re.sub(ur"([\W\s]+)", " ", string, flags=re.U|re.I).strip().lower()
    return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()

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
    def induce(self, symbol, fetcher=None):
        fetcher = fetcher or WIKIBASE_FETCHER
        sym = string_reduce(symbol)
        api_get = dict(action='query', titles=symbol, redirects="",
                       format='xml')
        xml_data = fetcher.download(symbol, get=api_get, base="w/api.php")
        ret = []

        for p in fromstring(xml_data).findall(".//page"):
            title = string_reduce(p.get('title'))
            if title != sym:
                ret.extend(lexical_synonyms(title))

        return ret

class LexicalInducer(BaseInducer):
    """
    Induce just the lexicals of the symbol
    """

    def induce(self, symbol):
        return lexical_synonyms(symbol)


WIKIBASE_INDUCERS = subclasses(BaseInducer)
