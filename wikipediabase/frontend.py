#!/usr/bin/env python
# -*- coding: utf-8 -*-

from edn_format import loads, Keyword
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

    def _eval(self, ls):

        # Are we facing a standalone literal
        if not isinstance(ls, tuple):
            return ls

        fn = (":" if isinstance(ls[0], Keyword) else "") + \
             self._eval(ls[0])._name.lower()
        args = [self._eval(a) for a in ls[1:]]

        return self.resources()[fn](*args)

    def eval(self, string):
        ls = loads(string)

        return self._eval(ls)


class TelnetFrontend(Frontend):

    def __init__(self, *args, **kwargs):
        self.srv = TelnetServer(answer = lambda msg:
                                str(self.eval(msg))+"\n",
                                safeword="quit")

        super(TelnetFrontend, self).__init__(*args, **kwargs)

    def run(self):
        self.log().info("Running telnet server...")
        self.srv.start(thread=False)

if __name__ == '__main__':
    from knowledgebase import KnowledgeBase
    from resolvers import StaticResolver

    fe = TelnetFrontend(knowledgebase=KnowledgeBase(resolvers=[StaticResolver()]))
    fe.start()
