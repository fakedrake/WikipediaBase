#!/usr/bin/env python
# -*- coding: utf-8 -*-

from edn_format import loads, Keyword, Symbol
from enchantments import enchant
from provider import Acquirer, Provider
from telnet import TelnetServer
from log import Logging

import logging


class Frontend(Acquirer):

    def __init__(self, knowledgebase=None, *args, **kwargs):
        super(Frontend, self).__init__(*args, **kwargs)

        if knowledgebase:
            self.acquire_from(knowledgebase)

        logging.getLogger("edn_format").setLevel(logging.WARNING)


    def get_callable(self, symbol):
        """
        Given a function name return the callable. Keywods should enchant
        the arguments.
        """

        if isinstance(symbol, Symbol):
            return self.resources()[symbol._name]

        if isinstance(symbol, Keyword):
            return lambda *args: enchant(symbol._name, *args)

        raise TypeError("Could not resolve function %s (type %s)." \
                        % (symbol, str(type(symbol))))


    def _eval(self, ls):
        # Are we facing a standalone literal
        if not isinstance(ls, tuple):
            return ls

        fn = self.get_callable(self._eval(ls[0]))

        args = [self._eval(a) for a in ls[1:]]

        return fn(*args) or "nil"

    def eval(self, string):
        ls = loads(string)

        return str(self._eval(ls))


class TelnetFrontend(Frontend):

    def __init__(self, *args, **kwargs):
        self.srv = TelnetServer(answer = lambda msg:
                                str(self.eval(msg))+"\n",
                                safeword="quit")

        super(TelnetFrontend, self).__init__(*args, **kwargs)

    def run(self):
        self.log().info("Running telnet server...")
        self.srv.start(thread=False)
