# -*- coding: utf-8 -*-

"""
A simple socket server for WikipediaBase
"""

import SocketServer

from wikipediabase.log import Logging
from wikipediabase.util import encode


class TelnetHandler(SocketServer.StreamRequestHandler, Logging):

    def handle(self):
        msg = self.rfile.readline().strip()
        self.log().info('Received request: %s', msg)
        answer = self.server.eval(msg)
        assert(isinstance(answer, unicode))  # TODO : remove for production

        # answer is a unicode string that needs to be encoded
        # As of Oct '15, Allegro Lisp doesn't correctly decode a utf-8 string.
        # As a temporary workaround, we encode into numeric HTML entities
        # e.g. "&#160;" for Unicode non-breaking space
        # encoding to HTML entities is about 10x slower than encoding to utf-8
        # TODO: use answer.encode('utf-8') instead of HTML entities
        self.wfile.write(encode(answer))


class TelnetServer(SocketServer.TCPServer):

    """
    The telnet server.
    """

    allow_reuse_address = True  # much faster rebinding

    def __init__(self, server_address, eval):
        SocketServer.TCPServer.__init__(self, server_address, TelnetHandler)
        self.eval = eval
