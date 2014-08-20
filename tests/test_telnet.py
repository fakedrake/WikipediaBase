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

from wikipediabase import telnet

import telnetlib


def answer(msg):
    return "You said '%s'" % msg


class TestTelnet(unittest.TestCase):

    def setUp(self):
        self.srv = telnet.TelnetServer(answer=answer)
        self.cli = telnetlib.Telnet("0.0.0.0", 1984)

    def test_threaded(self):
        self.srv.start(thread=True)
        self.cli.write("Awesome!!\n")
        self.assertEqual(self.cli.read_some(), "You said 'Awesome!!'")

    def tearDown(self):
        self.srv.stop()

if __name__ == '__main__':
    unittest.main()
