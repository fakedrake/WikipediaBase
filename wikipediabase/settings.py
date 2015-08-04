from wikipediabase.config import Configuration, MethodConfiguration

# A global configuration that everyone can use
configuration = Configuration()

# Wikipedia mirror
configuration.ref.remote.url = 'http://ashmore.csail.mit.edu:8080'
configuration.ref.remote.base = 'mediawiki/index.php'

# Caching
configuration.ref.cache.path = '~/.wikipediabase/'
configuration.ref.cache.rendered_pages = 'rendered'
configuration.ref.cache.downloaded_pages = 'downloaded'

# Register all interfaces. See the test for how to do it.
interfaces = MethodConfiguration()
configuration.add_child(interfaces)

# Note: For testing add child configurations insted of editing these

__all__ = ['configuration', 'interfaces']
