from provider import Acquirer, Provider, provide
from fetcher import CachingSiteFetcher
from infobox import Infobox
from enchantments import enchant
from resolvers import StaticResolver, InfoboxResolver

import re


DEFAULT_RESOLVERS = [StaticResolver, InfoboxResolver]


class KnowledgeBase(Provider):

    def __init__(self, frontend=None, resolvers=None, fetcher=None, *args, **kwargs):
        super(KnowledgeBase, self).__init__(*args, **kwargs)
        self.frontend = frontend

        if frontend:
            self.provide_to(frontend)

        self.fetcher = fetcher or CachingSiteFetcher()
        self.resolvers_acquirer = Acquirer(providers=resolvers or
                                           [R(self.fetcher) for R in
                                            DEFAULT_RESOLVERS])

    def resolvers(self):
        """
        The resolvers the the knowledgebase uses. This is a thin wapper
        around the stock `Acquirer' functionality.
        """

        return self.resolvers_acquirer._providers

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

        txt = self._get(article, attr, compat=bool(v3))

        return u"(%s)" % txt

    def _get(self, article, attr, compat):
        """
        In compatibility mode _get returns a tuple of the resolver gives
        to the answer (for now 'code' or 'html') and the actual
        answer.
        """

        self.log().info("Get article: '%s', attribute: '%s'" % (article, attr))

        # Attribute is wrapped into a dict just until we retrieve the
        # keys.

        for ar in self.resolvers():
            res = ar.resolve(article, attr)
            if res:
                return res


    @provide(name="get-classes")
    def get_classes(self, symbol):
        ibox = Infobox(symbol, self.fetcher)
        types = ibox.types().union({'wikipedia-term'})
        return enchant(None, types)

    @provide(name="get-attributes")
    def get_attributes(self, wb_class,  symbol=None):
        if symbol is not None:
            return self._get_attrs(symbol)

        # We dont really need wb_class, symbol is eough so it might
        # not be provided
        return self._get_attrs(wb_class)

    def _get_attrs(self, symbol):
        ibox = Infobox(symbol, self.fetcher)

        ret = []
        for k,v in ibox.markup_parsed_iter():
            tmp = enchant(None, dict(code= k.upper(),
                                     rendered=ibox.rendered_key(k)))

            ret.append(str(tmp))

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
