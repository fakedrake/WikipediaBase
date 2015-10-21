#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_telnet
----------------------------------

Tests for `telnet` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest


import telnetlib

from wikipediabase import telnet


# TODO: fix this test, it's hanging because the server is single-threaded

def answer(msg):
    return "You said '%s'" % msg


class TestTelnet(unittest.TestCase):

    def setUp(self):
        self.srv = telnet.TelnetServer(('0.0.0.0', 1984), answer)
        self.cli = telnetlib.Telnet("0.0.0.0", 1984)

    # def test_answer(self):
    #    self.srv.serve_forever()
    #    self.cli.write("Awesome!!\n")
    #    self.assertIn("You said 'Awesome!!", self.cli.read_some())

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

if __name__ == '__main__':
    unittest.main()
