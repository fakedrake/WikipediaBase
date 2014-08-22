# -*- coding: utf-8 -*-

from itertools import chain

from .provider import Provider, provide
from .fetcher import WIKIBASE_FETCHER
from .infobox import Infobox
from .enchantments import enchant, EnchantedList
from .resolvers import WIKIBASE_RESOLVERS
from .classifiers import WIKIBASE_CLASSIFIERS

import re


class KnowledgeBase(Provider):

    def __init__(self, *args, **kw):
        """
        Accepted parapameters are:

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

    @provide(name='sort-symbols')
    def sort_symbols(self, *args):
        key = lambda a: len(' '.join(get_article(a).paragraphs()))
        return enchant(sorted(args, reverse=True, key=key))

    @provide()
    def get(self, v1, v2, v3=None):
        """
        Iterate of the provided attribute resolvers. The wikipedia class
        in the question which would be v2 if all 3 args are present is
        obsolete.
        """

        if v3 is not None:
            article, attr = v2, v3
        else:
            article, attr = v1, v2

        ret = self._get(article, attr, compat=bool(v3))

        # It probably is enchated but give it a chance.
        return enchant(None, ret)

    def _get(self, article, attr, compat):
        """
        In compatibility mode _get returns a tuple of the resolver gives
        to the answer (for now 'code' or 'html') and the actual
        answer.
        """

        # Attribute is wrapped into a dict just until we retrieve the
        # keys.

        for ar in self.resolvers:
            res = ar.resolve(article, attr)
            # Errors enchantments should get returned.
            if res is not None:
                return res


    @provide(name="get-classes")
    def get_classes(self, symbol):
        """
        Get a symbol classes.
        """

        it = chain.from_iterable((c.classify(symbol)
                                  for c in self.classifiers))

        return enchant(None, it)

    @provide(name="get-attributes")
    def get_attributes(self, wb_class,  symbol=None):
        if symbol is not None:
            return self._get_attrs(symbol)

        # We dont really need wb_class, symbol is eough so it might
        # not be provided
        return self._get_attrs(wb_class)

    def _get_attrs(self, symbol):
        """
        Get all attributes of a symbol you cna find.
        """

        ibox = Infobox(symbol, self.fetcher)

        ret = []
        for k, v in ibox.markup_parsed_iter():
            tmp = enchant(None, dict(code=k.upper(),
                                     rendered=ibox.rendered_key(k)))

            ret.append(tmp._str())

        return " ".join(ret)

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
