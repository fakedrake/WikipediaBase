from bs4 import BeutifulSoup

class Heading(object):
    """
    The main container of paragraphs.
    """

    def __init__(self, soup):
        """
        Lazily get your paragraphs when you have to. The given soup's
        first heading item is the one we are interested in.
        """

        self.soup = soup
        self._name = None
        self._paragrpahs = None
        self._subheadings = None

    def paragraphs(self):
        """
        Generate paragraphs from soup.
        """

        raise NotImplemented

    def name(self):
        """
        Get the name from the soup.
        """

        raise NotImplemented

    def subheadings(self):
        """
        Generate subheadings.
        """

        raise NotImplemented



# XXX: also support images.
class BaseArticle(object):
    """
    This is meant to be a wrapper around a fetcher. I do not use
    articles as a very persistent resource so this is only an
    abstraction.
    """

    def __init__(self, title, fetcher):
        self.title = title
        self.fetchers = fetcher
        self.ibox = None

    def _primary_heading(self):
        """
        The primary nameless heading. This is the starting point for the
        rest headings.
        """

        raise NotImplemented

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
