from wikipediabase.config import *

# Do everything offline
configuration.ref.offline = True

# Wikipedia mirror
configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'
configuration.ref.remote.base = 'mediawiki/index.php'

# Caching
def get_persistent_dict(filename):
    return

import wikipediabase.persistentkv as pkv
configuration.ref.cache.path = '~/.wikipediabase/'
configuration.ref.cache.pages = LazyItem(lambda: pkv.DbmPersistentDict(configuration.ref.cache.path.deref() + 'pages'))

# Logging. Use lenses for this:
#    self.log = config.ref.log.lens(lambda log, this: log(this), self)
from wikipediabase.log import log_gen
configuration.ref.log = log_gen

# Fetcher
from wikipediabase.fetcher import CachingSiteFetcher
configuration.ref.fetcher = LazyItem(lambda : CachingSiteFetcher())

# Renderer
configuration.ref.renderer = LazyItem(lambda : SandboxRenderer())

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration']
