import bs4
import re
import itertools

from log import Logging
from util import tag_depth

from fetcher import CachingSiteFetcher

class Heading(object):
    """
    The main container of paragraphs.
    """

    def __init__(self, tag):
        """
        tag is a bs4 tag of the header
        """

        self.tag = tag
        self.level = int(self.tag.name[1])
        self.document = list(tag.parents).pop()
        self._name = None
        self._paragrpahs = None
        self._subheadings = None

    def _next_tags(self):
        if self.level == 1:
            return self.document.select("#mw-content-text")[0].children

        return self.tag.next_siblings

    def paragraphs(self, subheadings=False):
        """
        List of paragraphs of this heading, if subheadings is True then
        look into the subheadings too.
        """

        if self._paragrpahs is not None:
            return self._paragrpahs

        # Get paragraphs until the first subheading.

        hfilter = lambda c: re.match(r"(p|h[%d-%d])" % (1, self.level+1),
                                     str(c.name))
        tags = filter(hfilter, self._next_tags())
        pars = itertools.takewhile(lambda x: x.name == 'p',
                                     tags)

        return filter(lambda x: len(x.text) != 0, pars)

    def name(self):
        """
        Get the name from the soup.
        """

        if self._name is not None:
            return self._name

        self._name = self.tag.text.replace("[edit]","")
        return self._name

    def subheadings(self):
        """
        Generate subheadings.
        """

        if self._subheadings is not None:
            return self._subheadings

        # use select
        hfilter = lambda c: re.match(r"h[%d-%d]" % (1, self.level+1),
                                     str(c.name))
        htags = filter(hfilter, self._next_tags())
        htags1 = itertools.takewhile(lambda x: int(x.name[1]) == self.level+1,
                                     htags)

        self._subheadings = map(Heading, htags1)

        return self._subheadings

    def __repr__(self):
        return "<Wikipedia Heading object '%s' of depth %d>" % \
            (self.name(), self.level)

# XXX: also support images.
class Article(Logging):
    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title, fetcher=CachingSiteFetcher()):
        self.title = title
        self.fetcher = fetcher
        self.ibox = None

    def _soup(self):
        """
        A BeautifulSoup object of the entire article.
        """

        return bs4.BeautifulSoup(self.html_source())

    def _primary_heading(self):
        """
        The primary heading. This is the starting point for the rest
        headings.
        """

        h1 = self._soup().find("h1")
        return Heading(h1)

    def markup_source(self):
        """
        Markup source of the article.
        """

        return self.fetcher.source(self.title)

    def html_source(self):
        """
        Markup source of the article.
        """

        return self.fetcher.download(self.title)

    def infobox(self):
        """
        This article's infobox.
        """

        if self.ibox is None:
            self.ibox = Infobox(self.title, self.fetcher)

        return self.ibox

    def paragraphs(self):
        """
        Generate paragraphs.
        """

        for p in self._recursive_paragraphs(self._primary_heading()):
            yield p

    def _recursive_paragraphs(self, heading):
        """
        ITEMS is a callable that accepts a heading and returns a generator
        function for the heading level. The children are found with
        headin.subheadings
        """

        for p in heading.paragraphs():
            yield p

        for h in heading.subheadings():
            for p in self._recursive_paragraphs(h):
                yield p

    def headings(self):
        """
        Generate all the headings in a DFS fashion.
        """

        for h in self._recursive_headings(self._primary_heading()):
            yield h

    def _recursive_headings(self, heading):
        """
        Find headings recursively in a dfs fashion.
        """

        for h in heading.subheadings():
            yield h

            for h in self._recursive_headings(h):
                yield h
