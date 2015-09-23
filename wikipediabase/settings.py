import os
import re

from wikipediabase.config import *

# Do everything offline
configuration.ref.offline = False

# Wikipedia mirror
configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'
configuration.ref.remote.base = 'mediawiki/index.php'

# Caching
def get_persistent_dict(filename):
    return

import wikipediabase.persistentkv as pkv
configuration.ref.cache.path = os.getenv('HOME') + '/.wikipediabase/'
configuration.ref.cache.pages = VersionedItem(pkv.DbmPersistentDict, filename='pages')

# Logging. Use lenses for this:
#    self.log = config.ref.log.lens(lambda log, this: log(this), self)
from wikipediabase.log import log_gen
configuration.ref.log = log_gen

# Fetcher
from wikipediabase.fetcher import CachingSiteFetcher
configuration.ref.fetcher = VersionedItem(CachingSiteFetcher)

# Renderer
from wikipediabase.renderer import SandboxRenderer
configuration.ref.renderer = VersionedItem(SandboxRenderer)

#Infobox Superclasses
from wikipediabase.infobox_tree import InfoboxSuperclasses
configuration.ref.infobox_types = VersionedItem(InfoboxSuperclasses)

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration']
