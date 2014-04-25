from provider import Acquirer, Provider, provide
from fetcher import CachingSiteFetcher
from infobox import Infobox

import re

class KnowledgeBase(Provider):

    def __init__(self, frontend=None, resolvers=None, fetcher=None, *args, **kwargs):
        super(KnowledgeBase, self).__init__(*args, **kwargs)
        self.frontend = frontend

        if frontend:
            self.provide_to(frontend)

        self.fetcher = fetcher or CachingSiteFetcher()
        self.resolvers_acquirer = Acquirer(providers=resolvers or [])

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

        return self._get(article, attr, compat=bool(v3))

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
        pass

    @provide(name="get-attributes")
    def get_attributes(self, wb_class,  symbol, compat=None):
        ibox = Infobox(symbol, self.fetcher)

        return [k for k,v in ibox.markup_parsed_iter()]

    def attribute_wrap(self, val, **keys):
        """
        Make a dict with val and keys. This wraps
        attributes which are strings only for internal use in
        knowledgebase.
        """

        try:
            val["keys"].update(keys)
            return val
        except (KeyError, TypeError):
            return dict(val=val, keys=keys)
