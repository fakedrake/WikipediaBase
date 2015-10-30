# -*- coding: utf-8 -*-

from wikipediabase.classifiers import classify
from wikipediabase.lispify import lispify
from wikipediabase.provider import Provider, provide
from wikipediabase.resolvers import resolve, resolver_attributes
from wikipediabase.sort_symbols import sort_by_length, sort_named


class KnowledgeBase(Provider):

    def __init__(self, *args, **kw):
        super(KnowledgeBase, self).__init__(*args, **kw)
        self.frontend = kw.get('frontend')

        if self.frontend:
            self.provide_to(self.frontend)

    @provide(name='get')
    def get(self, cls, symbol, attr):
        """
        Gets the value of a symbol's attribute.

        :param cls: Wikipedia class of the symbol
        :param symbol: the Wikipedia article
        :param attr: the attribute to get
        :returns: the attribute's value or an error, lispified
        """
        return lispify([resolve(cls, symbol, attr)])

    @provide(name="get-attributes")
    def get_attributes(self, cls, symbol):
        return lispify(resolver_attributes(cls, symbol))

    @provide(name="get-classes")
    def get_classes(self, symbol):
        return lispify(classify(symbol))

    @provide(name='sort-symbols')
    def sort_symbols(self, *args):
        return lispify(sort_by_length(*args))

    @provide(name='sort-symbols-named')
    def sort_symbols_named(self, synonym, *args):
        return lispify(sort_named(synonym, *args))
