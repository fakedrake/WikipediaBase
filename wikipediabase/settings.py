import os
import re

from wikipediabase.config import *


class CurryingFactory(object):
    """
    An immutable factory that remembers arguemntes. One way to think
    of it is that each time you update the arguments you get a new
    factory. Another way to think of this (if you are half-mad) is as
    a comonadic structure.

    For the initiated this is a typical comonadic structure:

    -- Definitions
    data Factory a = Monoid context => Factory {ctx::context, constructor::(ctx->a)}
    withContext ctx (Factory _ f) = Factory ctx f
    withConstructor f (Factory ctx _) = Factory ctx f

    -- Comonad (all the merging logic is encapsulated here)
    expand (Factory ctx constructor) = Factory (ctx, \newCtx -> Factory (newCtx <> ctx) constructor)
    unpack (Factory ctx constructor) = constructor ctx

    -- Factory for factories, provide context, create factory
    kw :: context -> Factory a -> Factory a
    kw factory ctx = unpack $ withContext ctx $ expand factory
    """

    def __init__(self, cls=None, **kw):
        self._cls = cls
        self._kwargs = kw

    def cls(self, cls):
        return CurryingFactory(cls, **self._kwargs)

    def kw(self, **kwargs):
        return CurryingFactory(self._cls, **kwargs)

    def __call__(self, *args, **kwargs):
        kwargs.update(self._kwargs)
        return self._cls(*args, **kwargs)

# Do everything offline
configuration.ref.offline = False

# Wikipedia mirror
# configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'
# configuration.ref.remote.base = 'mediawiki/index.php'
# configuration.ref.remote.sandbox_title = "CSAIL_Wikipedia:Sandbox"

# Wikipedia
configuration.ref.remote.url = 'https://en.wikipedia.org'
configuration.ref.remote.base = 'w/index.php'
configuration.ref.remote.sandbox_title = "Wikipedia:Sandbox"
configuration.ref.remote.api_base = 'w/api.php'

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
from wikipediabase.renderer import ApiRenderer
configuration.ref.renderer = VersionedItem(ApiRenderer)

## Infobox Superclasses
from wikipediabase.infobox_tree import InfoboxSuperclasses
configuration.ref.infobox_types = VersionedItem(InfoboxSuperclasses)

## Resolvers
from wikipediabase.resolvers import BaseResolver
configuration.ref.resolvers = SubclassesItem(
    BaseResolver, configuration=configuration)

## Classifiers
from wikipediabase.classifiers import BaseClassifier
configuration.ref.classifiers = SubclassesItem(
    BaseClassifier, configuration=configuration)

## Knowledgebase
from wikipediabase.knowledgebase import Knowledgebase
configuration.ref.knowledgebase = VersionedItem(
    Knowledgebase, configuration=configuration)

## Frontend
from wikipediabase.frontend import Frontend
configuration.ref.frontend = VersionedItem(Frontend, configuration=configuration)

## String manipulation

# True if we want newlines instead of <br/>
configuration.ref.strings.literal_newlines = False

# Lxml cleaner applied to the lxml string.
import lxml.html.clean
cleaner_args = dict(links=False, safe_attrs_only=False,
                    style=True, forms=False)
configuration.ref.strings.lxml_cleaner = VersionedItem(lxml.html.clean.Cleaner,
                                                       **cleaner_args)

import wikipediabase.web_string as ws
configuration.ref.strings.xml_string_class = VersionedItem(CurryingFactory(ws.LxmlString).kw,
                                                           configuration=configuration)
configuration.ref.strings.symbol_string_class = VersionedItem(CurryingFactory(ws.SymbolString).kw,
                                                              configuration=configuration)
configuration.ref.strings.url_api_string_class = VersionedItem(CurryingFactory(ws.ApiUrlString).kw,
                                                               configuration=configuration)
configuration.ref.strings.url_edit_string_class = VersionedItem(CurryingFactory(ws.EditUrlString).kw,
                                                                configuration=configuration)
configuration.ref.strings.url_page_string_class = VersionedItem(CurryingFactory(ws.PageUrlString).kw,
                                                                configuration=configuration)
configuration.ref.strings.xml_preprocessor = VersionedItem(ws.XmlStringPreprocessor,
                                                           configuration=configuration)
configuration.ref.strings.xml_prune_tags = ['script', 'style']

## Object caches
from wikipediabase.infobox import Infobox
configuration.ref.object_cache.infoboxes = VersionedItem(Infobox,
                                                         configuration=configuration)

from wikipediabase.article import Article
configuration.ref.object_cache.articles = VersionedItem(Article,
                                                        configuration=configuration)

from wikipediabase.infobox_scraper import MetaInfobox
configuration.ref.object_cache.meta_infoboxes = VersionedItem(MetaInfobox,
                                                              configuration=configuration)

configuration.ref.object_cache.persistent_dict = VersionedItem(pkv.DbmPersistentDict,
                                                               filename='default')

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration']
