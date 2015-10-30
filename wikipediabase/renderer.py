"""
Turn markdown into html.
"""

from wikipediabase.log import Logging
from wikipediabase.util import Expiry, get_user_agent
import logging
import redis
import requests

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

WIKIBASE_RENDERER = None


class BaseRenderer(Logging):

    """
    Render mediawiki markup into HTML.
    """

    def render(self, wikitext, key=None, **kwargs):
        pass


class Renderer(BaseRenderer):

    """
    Use Wikipedia's API to render mediawiki markup.
    """

    def __init__(self, url="https://en.wikipedia.org/w/api.php"):
        self.url = url.strip('/')

    def render(self, wikitext, key=None, **kwargs):
        """
        Turn markdown into html.
        """

        data = {"action": "parse", "text": wikitext, "prop": "text", "format": "json"}
        headers = {'User-Agent': get_user_agent()}
        r = requests.post(self.url, data=data, headers=headers)
        if r.status_code != requests.codes.ok:
            raise LookupError("Error rendering from the Wikipedia API. "
                              "%s returned status code %s : %s" %
                              (r.url, r.status_code, r.reason))

        rendered = r.json()['parse']['text']['*']
        assert(isinstance(rendered, unicode))  # TODO : remove for production
        return rendered


class CachingRenderer(Renderer):

    def __init__(self, url="https://en.wikipedia.org/w/api.php"):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0,
                                       decode_responses=True)
        super(CachingRenderer, self).__init__(url)

    def render(self, wikitext, key=None, expiry=Expiry.LONG):
        if key is None:
            key = hash(wikitext)

        dkey = u'renderer:' + key
        content = self.redis.get(dkey)

        if content is None:
            content = super(CachingRenderer, self).render(wikitext, key=key)
            self.redis.set(dkey, content)
            if expiry is not None:
                self.redis.expire(dkey, expiry)

        return content


def get_renderer():
    global WIKIBASE_RENDERER
    if WIKIBASE_RENDERER is None:
        WIKIBASE_RENDERER = CachingRenderer()
    return WIKIBASE_RENDERER
