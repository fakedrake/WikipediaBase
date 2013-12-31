"""
wikipediabasepy.

Usage:
  wikipediabasepy [options]

  wikipediabasepy -h | --help

Options:
  --debug               Debug.

  -h --help             Show this screen.
"""

from docopt import docopt
import logging

import wikipediabasepy
from knowledgebase import KnowledgeBase
from resolvers import StaticResolver, InfoboxResolver
from frontend import TelnetFrontend

log = logging.getLogger(__name__)


def main():
    arguments = docopt(__doc__, version=wikipediabasepy.__version__)
    debug = arguments['--debug']
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    log.debug('arguments: %s', arguments)

    fe = TelnetFrontend(knowledgebase=KnowledgeBase(resolvers=[StaticResolver(), InfoboxResolver()]))
    fe.run()
