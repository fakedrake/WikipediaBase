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
configuration.ref.cache.sync_period = 5 # In transactions
configuration.ref.cache.path = os.getenv('HOME') + '/.wikipediabase/'
configuration.ref.cache.persistent_dict = VersionedItem(pkv.DbmPersistentDict, filename='pages')

# Logging. Use lenses for this:
#    self.log = config.ref.log.lens(lambda log, this: log(this), self)
from wikipediabase.log import log_gen
configuration.ref.log = log_gen

## Fetcher
from wikipediabase.fetcher import CachingSiteFetcher
configuration.ref.fetcher = VersionedItem(CachingSiteFetcher)

## Renderer
from wikipediabase.renderer import SandboxRenderer
configuration.ref.renderer = VersionedItem(SandboxRenderer)

## Infobox Superclasses
from wikipediabase.infobox_tree import InfoboxSuperclasses
configuration.ref.infobox_types = VersionedItem(InfoboxSuperclasses)

## String manipulation

# True if we want newlines instead of <br/>
configuration.ref.strings.literal_newlines = False

## Object caches
from wikipediabase.infobox import Infobox
configuration.ref.object_cache.infoboxes = VersionedItem(Infobox,
                                                         configuration=cnfiguration)

from wikipediabase.article import Article
configuration.ref.object_cache.articles = VersionedItem(Article,
                                                        configuration=configuration)

from wikipediabase.knowledgebase import KnowledgeBase
configuration.ref.object_cache.knowledgebases = VersionedItem(KnowledgeBase,
                                                              configuration=configuration)

from wikipediabase.infobox_scraper import MetaInfobox
configuration.ref.object_cache.meta_infoboxes = VersionedItem(MetaInfobox,
                                                              configuration=cnfiguration)

configuration.ref.object_cache.persistent_dict = VersionedItem(pkv.DbmPersistentDict,
                                                               filename='default')

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration']
