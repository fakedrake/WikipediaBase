# -*- coding: utf-8 -*-

import re
import redis
import requests

import logging
from wikipediabase.log import Logging
from wikipediabase.util import Expiry

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"
USER_AGENT = "WikipediaBase/1.0 " \
             "(http://start.csail.mit.edu; start-admins@csail.mit.edu)"


class BaseFetcher(Logging):

    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    priority = 0

    def html_source(self, symbol, **kwargs):
        return symbol

    def markup_source(self, symbol, **kwargs):
        return symbol


class Fetcher(BaseFetcher):

    priority = 1

    def __init__(self, url='https://en.wikipedia.org/w/index.php'):
        self.url = url.strip('/')

    def urlopen(self, url, params):
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, params=params, headers=headers)

        if r.status_code != requests.codes.ok:
            raise LookupError("Error fetching: %s. Status code %s : %s" %
                              (r.url, r.status_code, r.reason))

        page = r.text
        assert(isinstance(page, unicode))  # TODO : remove for production
        return page

    def html_source(self, symbol, **kwargs):
        """
        Get the rendered HTML article of the symbol.
        """

        params = {'action': 'view', 'title': symbol, 'redirect': 'yes'}
        return self.urlopen(self.url, params)

    def markup_source(self, symbol, **kwargs):
        """
        Get the wikitext markup of the symbol.
        """

        params = {'action': 'raw', 'title': symbol}
        page = self.urlopen(self.url, params)

        # handle redirecions silently
        redirect_match = re.search(REDIRECT_REGEX, page)
        if redirect_match:
            redirect = redirect_match.group(1)
            self.redirect = redirect
            self.log().debug("Redirecting '%s' to '%s'", symbol, redirect)
            params['title'] = redirect
            page = self.urlopen(self.url, params)

        return page


class CachingFetcher(Fetcher):

    def __init__(self, url='https://en.wikipedia.org/w/index.php'):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0,
                                       decode_responses=True)
        super(CachingFetcher, self).__init__(url)

    def _caching_fetch(self, symbol, content_type, prefix, fetch,
                       expiry=Expiry.DEFAULT):
        dkey = prefix + symbol
        content = self.redis.hget(dkey, content_type)

        if content is None:
            content = fetch(symbol)
            self.redis.hset(dkey, content_type, content)
            if expiry is not None:
                self.redis.expire(dkey, expiry)

        return content

    def html_source(self, symbol, expiry=Expiry.DEFAULT):
        html = self._caching_fetch(symbol, 'html', 'article:',
                                   super(CachingFetcher, self).html_source,
                                   expiry=expiry)

        assert(isinstance(html, unicode))  # TODO : remove for production
        return html

    def markup_source(self, symbol, expiry=Expiry.DEFAULT):
        source = self._caching_fetch(symbol, 'source', 'article:',
                                     super(CachingFetcher, self).markup_source,
                                     expiry=expiry)

        assert(isinstance(source, unicode))  # TODO : remove for production
        return source


class StaticFetcher(BaseFetcher):

    """
    Will just get the html and markup provided in init.
    """

    def __init__(self, html=None, markup=None):
        self.html = html
        self.markup = markup

    def html_source(self, symbol, **kwargs):
        return self.html

    def markup_source(self, symbol, **kwargs):
        return self.markup

WIKIBASE_FETCHER = CachingFetcher()
