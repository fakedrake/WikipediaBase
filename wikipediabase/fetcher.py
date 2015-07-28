# -*- coding: utf-8 -*-

import re
import requests

from wikipediabase.log import Logging

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

    def download(self, symbol):
        return symbol

    def source(self, symbol):
        return symbol

class Fetcher(BaseFetcher):

    priority = 1

    def __init__(self, url='https://en.wikipedia.org/w/index.php'):
        self.url = url.strip('/')

    def urlopen(self, url, params):
        # TODO : remove for production
        if not isinstance(params['title'], unicode):
            self.log().warn('Fetcher received a non-unicode string: %s', 
                            params['title'])

        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, params=params, headers=headers)

        if r.status_code != requests.codes.ok:
            raise LookupError("Error fetching: %s. Status code %s : %s" %
                              (r.url, r.status_code, r.reason))

        page = r.text
        assert(isinstance(page, unicode))  # TODO : remove for production
        return page

    def download(self, symbol):
        """
        Get the rendered HTML article of the symbol.
        """

        params = {'action': 'view', 'title': symbol, 'redirect': 'yes'}
        return self.urlopen(self.url, params)

    def source(self, symbol):
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

class StaticFetcher(BaseFetcher):
    """
    Will just get the html and markup provided in init.
    """

    def __init__(self, html=None, markup=None):
        self.html = html
        self.markup = markup

    def download(self, symbol):
        return self.html

    def source(self, symbol):
        return self.markup

WIKIBASE_FETCHER = Fetcher()
