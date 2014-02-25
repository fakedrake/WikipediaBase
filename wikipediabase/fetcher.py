try:
    from urllib2 import urlopen
except:
    from urllib import urlopen

from urllib import urlencode
import re
import json

import bs4

from log import Logging
from util import INFOBOX_ATTRIBUTE_REGEX


WIKISOURCE_TAG_ID = "wpTextbox1"
REDIRECT_REGEX = r"#REDIRECT\s*\[\[(.*)\]\]"

class BaseFetcher(Logging):
    """
    The base fetcher does not really fetch an article, it just assumes
    that an article was given to it. Subclass this to make more
    complex fetchers.
    """

    def fetch(self, article):
        """
        Just return the article itself.
        """

        return article


class WikipediaSiteFetcher(BaseFetcher):
    def __init__(self, url="http://en.wikipedia.org", base="w"):
        self.url = url.strip('/')
        self.base = base.strip('/')

    def get_wikisource(self, soup):
        """
        Get the source from an html soup of the edit page.
        """
        tag = soup.find_all(attrs={"id":WIKISOURCE_TAG_ID})

        return tag

    def download(self, symbol, get=None):
        """
        Download a wikipedia article.

        :param symbol: The wikipedia symbol we are interested in.
        :param get: dictionary of the get request. eg. `{'action':'edit'}`
        :returns: HTML code
        """
        if not get:
            get = dict(title=symbol)
        else:
            get = get.copy()
            get.update(title=symbol)

        url = "%s/%s?%s" % (self.url, self.base,
                            urlencode(get))
        return urlopen(url).read()

    def _infobox_braces(self, txt):
        ret = ""
        ibs = -1
        braces = 0
        rngs = []

        for m in re.finditer("(({{)\s*(\w*)|(}}))", txt):
            if m.group(2) == "{{":
                if braces > 0:
                    braces += 1

                if m.group(3) == "Infobox":
                    braces = 1
                    ibs = m.start(2)

            elif m.group(1) == "}}" and braces > 0:
                braces -= 1

                if braces == 0:
                    eoi = m.end(1)
                    rngs.append((ibs, eoi))

        # There may be more than one infoboxes, concaenate them.
        for s,e in rngs:
            ret += txt[s:e]

        return ret or None

    def infobox_type(self, symbol, follow=True):
        """
        Get the infobox type. 'follow' returns the alias infobox of this
        infobox. E.g. president => officeholder
        """

        raise NotImplementedError

    def _html_infobox_parse(self, html):
        """
        Given the infobox html or as soup.
        """

        if isinstance(html, str):
            html = bs4.BeautifulSoup(html)

        tpairs = [(i.parent.th.text, i.text) for i in
                  html.select('table.infobox > tr > td')
                  if i.parent.find('th')]

        return tpairs

    def _source_infobox_parse(self, src):
        """
        Given the source parse the infobox into pairs of values.
        """

        matchers = re.finditer(INFOBOX_ATTRIBUTE_REGEX % r"(?P<key>.*)", src)
        return [(m.group("key"), m.group("val")) for m in matchers]

    def _infobox_rendered(self, html):
        ret = bs4.BeautifulSoup()

        bs = bs4.BeautifulSoup(html)
        for i in bs.select('table.infobox'):
            ret.append(i)

        return ret

    def infobox(self, symbol, rendered=False, parsed=False):
        """
        Get the infobox in wiki markup. Renedered means return
        html. Parsed is to get attribute/value pairs. To change this
        behaviour in a subclass override any of the following
        _{html,source}_infobox_parse().
        """

        self.log().info("Looking for infobox: %s" % symbol)

        if not rendered:
            article = self.source(symbol)
            ib = self._infobox_braces(article)
            if parsed:
                return self._source_infobox_parse(ib)

        else:
            article = self.download(symbol)
            ib = self._infobox_rendered(article)
            if parsed:
                return self._html_infobox_parse(ib)
            else:
                ib = ib.text

        if ib:
            return ib

        self.log().warning("Could not find infobox in source (source size: %d)." %
                           len(article))

    def source(self, symbol, get_request=dict(action="edit"), redirect=True):
        """
        Get the full wiki markup of the symbol.
        """

        self.log().info("Looking for article source: %s." % symbol)
        # <textarea tabindex="1" accesskey="," id="wpTextbox1" cols="80" rows="25" style="" lang="en" dir="ltr" name="wpTextbox1">
        html = self.download(symbol=symbol, get=get_request)
        soup = bs4.BeautifulSoup(html)

        try:
            src = str(self.get_wikisource(soup)[0])
        except IndexError:
            raise KeyError("Source retrieval for rticle '%s' failed." % symbol)

        # Handle redirecions silently
        redirect_match = re.search(REDIRECT_REGEX, src)

        if redirect and redirect_match:
            self.log().info("Redirecting to '%s'.", redirect_match.group(1))
            src = self.download(symbol=redirect_match.group(1),
                                get=get_request)

        return src


class CachingSiteFetcher(WikipediaSiteFetcher):
    """
    Caches pages in a json file and reads from there.
    """

    _fname = "/tmp/pages.json"

    def download(self, symbol, get=None):
        try:
            if not hasattr(self, 'data'):
                self.data = json.load(open(self._fname))

        except (ValueError, IOError):
            self.data = dict()

        dkey = "%s;%s" % (symbol, get)
        if dkey in self.data:
            return self.data[dkey]

        pg = super(CachingSiteFetcher, self).download(symbol, get=get)
        self.data[dkey] = pg
        json.dump(self.data, open(self._fname, "w"))
        return pg
