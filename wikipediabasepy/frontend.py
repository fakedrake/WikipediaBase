#!/usr/bin/env python
# -*- coding: utf-8 -*-

from edn_format import loads
from provider import Aquirer
from telnet import TelnetServer
from log import Logger

class Frontend(Aquirer):
    def __init__(self, knowledgebase=None, *args, **kwargs):
        super(Frontend, self).__init__(*args, **kwargs)

        if knowledgebase:
            self.aquire_from(knowledgebase)

    def eval(self, string):
        ls = loads(string)

        return self.resources()[ls[0]._name](*ls[1:])


class TelnetFrontend(Frontend):

    def __init__(self, *args, **kwargs):
        self.srv = TelnetServer(answer = lambda msg:
                                str(self.eval(msg))+"\n", log=Logger(),
                                safeword="quit")

        super(TelnetFrontend, self).__init__(*args, **kwargs)

    def run(self):
        self.srv.start(thread=False)

if __name__ == '__main__':
    from knowledgebase import KnowledgeBase
    from resolvers import StaticResolver

    fe = TelnetFrontend(knowledgebase=KnowledgeBase(resolvers=[StaticResolver()]))
    fe.run()
