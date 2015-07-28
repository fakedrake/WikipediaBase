"""
Turn markdown into html.
"""

from wikipediabase.log import Logging
from wikipediabase.fetcher import USER_AGENT
import wikipediabase.util as util
import requests


class BaseRenderer(Logging):

    """
    Render mediawiki markup into HTML.
    """

    def render(self, wikitext, key=None):
        pass


class Renderer(BaseRenderer):

    """
    Use Wikipedia's API to render mediawiki markup.
    """

    def __init__(self, url="https://en.wikipedia.org/w/api.php"):
        self.url = url.strip('/')

    def render(self, wikitext, key=None):
        """
        Turn markdown into html.
        """

        # TODO : remove for production
        if not isinstance(wikitext, unicode):
            self.log().warn("Renderer received a non-unicode string: %s",
                            wikitext)

        params = {"action":"parse", "text":wikitext, "prop": "text", "format": "json"}
        headers = {'User-Agent': USER_AGENT}
        r = requests.post(self.url, params=params, headers=headers)
        if r.status_code != requests.codes.ok:
            raise LookupError("Error rendering from the Wikipedia API. "
                              "%s returned status code %s : %s" %
                              (r.url, r.status_code, r.reason))

        rendered = r.json()['parse']['text']['*']
        assert(isinstance(rendered, unicode)) # TODO : remove for production
        return rendered

WIKIBASE_RENDERER = Renderer()
