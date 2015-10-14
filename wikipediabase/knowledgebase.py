# -*- coding: utf-8 -*-

from wikipediabase.classifiers import WIKIBASE_CLASSIFIERS
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.lispify import lispify
from wikipediabase.provider import Provider, provide
from wikipediabase.resolvers import WIKIBASE_RESOLVERS
from wikipediabase.synonym_inducers import WIKIBASE_INDUCERS
from wikipediabase.util import get_article


class KnowledgeBase(Provider):

    def __init__(self, *args, **kw):
        """
        Accepted parameters are:

        - frontend (default: None)
        - fetcher (default: WIKIBASE_FETCHER)
        - resolvers (default: WIKIBASE_RESOLVERS)
        - classifiers (default: WIKIBASE_CLASSIFIERS)
        """

        super(KnowledgeBase, self).__init__(*args, **kw)
        self.frontend = kw.get('frontend')

        if self.frontend:
            self.provide_to(self.frontend)

        self.fetcher = kw.get('fetcher', WIKIBASE_FETCHER)
        self.resolvers = kw.get('resolvers', WIKIBASE_RESOLVERS)
        self.classifiers = kw.get('classifiers', WIKIBASE_CLASSIFIERS)
        self.synonym_inducers = kw.get('synonym_inducers', WIKIBASE_INDUCERS)

    @provide(name='sort-symbols')
    def sort_symbols(self, *args):
        key = lambda a: len(' '.join(get_article(a).paragraphs()))
        return lispify(sorted(args, reverse=True, key=key))

    @provide(name='get')
    def get(self, cls, symbol, attr):
        """
        Gets the value of a symbol's attribute.

        :param cls: Wikipedia class of the symbol
        :param symbol: the Wikipedia article
        :param attr: the attribute to get
        :returns: the attribute's value or an error, lispified
        """
        for ar in self.resolvers:
            res = ar.resolve(cls, symbol, attr)
            if res is not None:
                break

        return lispify([res])

    @provide(name="get-attributes")
    def get_attributes(self, cls, symbol):
        for r in self.resolvers:
            attributes = r.attributes(cls, symbol)
            if attributes is not None:
                return attributes
        return lispify([])

    @provide(name="get-categories")
    def get_categories(self, symbol):
        categories = get_article(symbol).categories()
        return lispify(categories)

    @provide(name="get-classes")
    def get_classes(self, symbol):
        return get_article(symbol).classes()

    @provide(name="get-types")
    def get_types(self, symbol):
        types = get_article(symbol).types()
        return lispify(types)

    def synonyms(self, symbol):
        synonyms = set()

        for si in self.synonym_inducers:
            synonyms.update(si.induce(symbol))

        return lispify(synonyms)
