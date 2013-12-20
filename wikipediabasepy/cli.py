"""
wikipediabasepy.

Usage:
  wikipediabasepy [options] command <param> <another_params>
  wikipediabasepy [options] another-command <param>

  wikipediabasepy -h | --help

Options:
  --kw-arg=<kw>         Keyword option description.
  -b --boolean          Boolean option description.
  --debug               Debug.

  -h --help             Show this screen.
"""

from docopt import docopt
import logging

import wikipediabasepy

log = logging.getLogger(__name__)


def main():
    arguments = docopt(__doc__, version=wikipediabasepy.__version__)
    debug = arguments['--debug']
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    log.debug('arguments: %s', arguments)
