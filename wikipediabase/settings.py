import os
import re

from wikipediabase.config import *

# Do everything offline
configuration.ref.offline = False

# Wikipedia mirror
configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'
configuration.ref.remote.base = 'mediawiki/index.php'
configuration.ref.remote.sandbox_title = "CSAIL_Wikipedia:Sandbox"

# Caching
def get_persistent_dict(filename):
    return

import wikipediabase.persistentkv as pkv
configuration.ref.cache.sync_period = 5 # In transactions
configuration.ref.cache.path = os.getenv('HOME') + '/.wikipediabase/'
configuration.ref.cache.pages = VersionedItem(pkv.DbmPersistentDict, filename='pages')
configuration.ref.cache.rendered_pages = VersionedItem(pkv.DbmPersistentDict, filename='rendered_pages')
configuration.ref.cache.persistent_dict = VersionedItem(pkv.DbmPersistentDict, filename='pages')
from wikipediabase.caching import DictCacheManager
configuration.ref.cache.manager = VersionedItem(DictCacheManager, dict())

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

## Classifiers
from wikipediabase.classifiers import BaseClassifier
configuration.ref.classifiers = SubclassesItem(BaseClassifier, configuration=configuration)

## Classifiers

## String manipulation

# True if we want newlines instead of <br/>
configuration.ref.strings.literal_newlines = False

# Lxml cleaner applied to the lxml string.
import lxml.html.clean
cleaner_args = dict(links=False, safe_attrs_only=False,
                    style=True, forms=False)
configuration.ref.strings.lxml_cleaner = VersionedItem(lxml.html.clean.Cleaner,
                                                       **cleaner_args)

from wikipediabase.web_string import LxmlString, SymbolString
configuration.ref.strings.xml_string_class = LxmlString
configuration.ref.strings.symbol_string_class = SymbolString
configuration.ref.strings.xml_prune_tags = ['script', 'style']

## Object caches
from wikipediabase.infobox import Infobox
configuration.ref.object_cache.infoboxes = VersionedItem(Infobox,
                                                         configuration=configuration)

from wikipediabase.article import Article
configuration.ref.object_cache.articles = VersionedItem(Article,
                                                        configuration=configuration)

from wikipediabase.knowledgebase import KnowledgeBase
configuration.ref.object_cache.knowledgebases = VersionedItem(KnowledgeBase,
                                                              configuration=configuration)

from wikipediabase.infobox_scraper import MetaInfobox
configuration.ref.object_cache.meta_infoboxes = VersionedItem(MetaInfobox,
                                                              configuration=configuration)

configuration.ref.object_cache.persistent_dict = VersionedItem(pkv.DbmPersistentDict,
                                                               filename='default')

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration']
