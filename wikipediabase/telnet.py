# -*- coding: utf-8 -*-

"""
A simple socket server for WikipediaBase
"""

import SocketServer

from wikipediabase.log import Logging


class TelnetHandler(SocketServer.StreamRequestHandler, Logging):

    def handle(self):
        msg = self.rfile.readline().strip()
        self.log().info('Received request: %s', msg)
        answer = self.server.eval(msg)
        assert(isinstance(answer, unicode))  # TODO : remove for production
        self.wfile.write(answer.encode('utf-8'))


class TelnetServer(SocketServer.TCPServer):

    """
    The telnet server.
    """

    allow_reuse_address = True  # much faster rebinding

    def __init__(self, server_address, eval):
        SocketServer.TCPServer.__init__(self, server_address, TelnetHandler)
        self.eval = eval
