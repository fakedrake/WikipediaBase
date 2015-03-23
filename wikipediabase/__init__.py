"""Wikipedia backend interface for start.mit.edu"""

__author__ = 'Chris Perivolaropoulos'
__email__ = 'cperivol@csail.mit.edu'
__url__ = 'https://github.com/fakedrake/wikipediabase'
__version__ = '1.0'

from wikipediabase.knowledgebase import KnowledgeBase
from wikipediabase.resolvers import StaticResolver
from wikipediabase.frontend import TelnetFrontend, Frontend


def wikipediabase(cmd=None, **kw):
    if cmd is None:
        fe = TelnetFrontend(knowledgebase=KnowledgeBase())
        fe.run()
        return None

    return Frontend(**kw).eval(cmd)
