"""Wikipedia backend interface for start.mit.edu"""

__author__ = 'Chris Perivolaropoulos'
__email__ = 'darksaga2006@gmail.com'
__url__ = 'https://github.com/fakedrake/wikipediabase'
__version__ = '0.0.1'

from knowledgebase import KnowledgeBase
from resolvers import StaticResolver
from frontend import TelnetFrontend, Frontend

def wikipediabase(cmd=None, **kw):
    if cmd is None:
        fe = TelnetFrontend(knowledgebase=KnowledgeBase())
        fe.run()
        return None

    return Frontend(**kw).eval(cmd)
