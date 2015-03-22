#!/usr/bin/env python
# -*- coding: utf-8 -*-

from edn_format import loads, Keyword, Symbol

from wikipediabase.telnet import TelnetServer
from wikipediabase.enchantments import enchant
from wikipediabase.provider import Acquirer, Provider, provide
from wikipediabase.knowledgebase import KnowledgeBase
from wikipediabase.log import Logging
from wikipediabase.util import get_knowledgebase

import logging


class Frontend(Acquirer):

    def __init__(self, knowledgebase=None, *args, **kwargs):
        super(Frontend, self).__init__(*args, **kwargs)

        if 'providers' not in kwargs:
            self.knowledgebase = knowledgebase or get_knowledgebase(
                frontend=self,
                fetcher=kwargs.get('fetcher')
            )

        logging.getLogger("edn_format").setLevel(logging.WARNING)

    @provide(name='commands')
    def commands(self):
        return enchant(None, [i for i,_ in self.resources().iteritems()])

    def get_callable(self, symbol):
        """
        Given a function name return the callable. Keywods should enchant
        the arguments.
        """

        if isinstance(symbol, Symbol):
            return self.resources()[symbol._name]

        if isinstance(symbol, Keyword):
            return lambda *args: enchant(symbol._name, *args)

        raise TypeError("Could not resolve function %s (type %s)."
                        % (symbol, str(type(symbol))))

    def _eval(self, ls):
        # Are we facing a standalone literal
        if not isinstance(ls, tuple):
            return ls

        fn = self.get_callable(self._eval(ls[0]))
        args = [self._eval(a) for a in ls[1:]]
        ret = fn(*args)

        return ret

    def eval(self, string):
        ls = loads(string)
        ret = unicode(self._eval(ls))

        return ret


class TelnetFrontend(Frontend):

    def eval(self, *args, **kw):
        try:
            return super(TelnetFrontend, self).eval(*args, **kw) + "\n"
        except BaseException, e:
            if isinstance(e, SystemExit):
                raise e

            return unicode(enchant('error', e)) + u'\n'

    def __init__(self, *args, **kwargs):
        super(TelnetFrontend, self).__init__(*args, **kwargs)
        self.srv = TelnetServer(answer=self.eval,
                                safeword="quit")

    def run(self):
        self.log().info("Running telnet server...")
        self.srv.start(thread=False)

    @provide()
    def quit(self, status=0):
        self.log().info("Exiting with status %d" % status)
        exit(status)
