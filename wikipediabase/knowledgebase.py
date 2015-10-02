# -*- coding: utf-8 -*-

from itertools import chain

from wikipediabase.provider import Provider, provide
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.enchantments import enchant
from wikipediabase.resolvers import WIKIBASE_RESOLVERS
from wikipediabase.classifiers import WIKIBASE_CLASSIFIERS
from wikipediabase.synonym_inducers import WIKIBASE_INDUCERS
from wikipediabase.util import get_article, get_infobox


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
        return enchant(sorted(args, reverse=True, key=key))

    @provide(name='get')
    def get(self, cls, symbol, attr):
        """
        Gets the value of a symbol's attribute.

        :param cls: Wikipedia class of the symbol
        :param symbol: the Wikipedia article
        :param attr: the attribute to get
        :returns: the attribute's value or an error, enchanted
        """
        for ar in self.resolvers:
            res = ar.resolve(symbol, attr, cls=cls)
            if res is not None:
                break

        return enchant([res])

    @provide(name="get-classes")
    def get_classes(self, symbol):
        it = chain.from_iterable((c.classify(symbol)
                                  for c in self.classifiers))
        return enchant(list(it))

    @provide(name="get-types")
    def get_types(self, symbol):
        types = get_article(symbol).types()
        return enchant(types)

    @provide(name="get-categories")
    def get_categories(self, symbol):
        categories = get_article(symbol).categories()
        return enchant(categories)

    @provide(name="get-attributes")
    def get_attributes(self, cls, symbol):
        if symbol is not None:
            return enchant(self._get_attrs(symbol))

        # We don't really need wb_class, symbol is enough so it might
        # not be provided
        return enchant(self._get_attrs(cls))

    def synonyms(self, symbol):
        synonyms = set()

        for si in self.synonym_inducers:
            synonyms.update(si.induce(symbol))

        return enchant(synonyms)

    def _get_attrs(self, symbol):
        """
        Get all attributes of a symbol you can find.
        """

        ibox = get_infobox(symbol, self.fetcher)

        ret = []
        for k, v in ibox.markup_parsed_iter():
            rendered = ibox.rendered_attributes().get(k.replace('-', '_'))
            tmp = enchant(dict(code=k.upper(),
                               rendered=rendered))

            ret.append(tmp)

        return ret

    def attribute_wrap(self, val, **keys):
        """
        Make a dict with val and keys. This wraps attributes which are
        strings only for internal use in knowledgebase.
        """

        try:
            val["keys"].update(keys)
            return val
        except (KeyError, TypeError):
            return dict(val=val, keys=keys)
