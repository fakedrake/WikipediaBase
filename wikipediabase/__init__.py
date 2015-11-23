"""Wikipedia backend interface for start.mit.edu"""

__author__ = 'Chris Perivolaropoulos'
__email__ = 'cperivol@csail.mit.edu'
__url__ = 'https://github.com/fakedrake/wikipediabase'
__version__ = '1.2'

from wikipediabase.config import configuration
from wikipediabase.frontend import TelnetFrontend, Frontend


def wikipediabase(cmd=None, **kw):
    fe = TelnetFrontend(configuration=configuration)
    fe.run()
    return None
