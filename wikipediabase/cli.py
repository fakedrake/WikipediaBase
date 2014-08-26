"""
wikipediabase.
Open telnet server for start to communicate at.

Usage:
  wikipediabase [options]

  wikipediabase -h | --help

Options:
  -p --port             Port (default: 1984)

  -h --help             Show this screen.
"""

from docopt import docopt
import logging

import wikipediabase
from .knowledgebase import KnowledgeBase
from .resolvers import StaticResolver, InfoboxResolver
from .frontend import TelnetFrontend

log = logging.getLogger(__name__)


def cache_mysql


def main():
    arguments = docopt(__doc__, version=wikipediabase.__version__)
    debug = arguments['--debug']
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    log.debug('arguments: %s', arguments)

    fe = TelnetFrontend()

    fe.run()
