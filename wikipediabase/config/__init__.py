from wikipediabase.config.item import *
from wikipediabase.config.ref import *
from wikipediabase.config.lensref import *
from wikipediabase.config.configurable import *
from wikipediabase.config.configuration import Configuration

configuration = Configuration()
__all__ = ['LazyItem',
           'VersionedItem',
           'SubclassesItem',
           'ConfigRef',
           'Configuration',
           'Configurable',
           'configuration']
