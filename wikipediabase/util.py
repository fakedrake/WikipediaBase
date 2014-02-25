from itertools import islice
import urllib

from bs4 import BeautifulSoup

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=\n\s*\|)"

def iwindow(seq, n):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args, **kwargs):
            return self[(args, kwargs)]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)

def soup_factory(soup_or_article):
    """
    Return a soup from html. If already a soup dont bother.
    """

    if not isinstance(rendered_article, BeautifulSoup):
        return BeautifulSoup(rendered_article)
    else:
        return rendered_articles


def paragraph(rendered_article, paragraph_id, heading=None):
    """
    Given a beautiful soup object or some html code try to find the
    paragraph.

    Example:

    >>> paragraph(get_html("http://en.wikipedia.org/wiki/Edgar_Allan_Poe"), 1)

    """

    soup = soup_factory(rendered_article)
    p = [p for p in  soup.select("div#mw-content-text p") if p.text]
    text = p[paragraph_id].text

    return text


def heading(rendered_article, heading):
    """
    Return the contents of a heading.

    :param rendered_article: Rendered article or soup
    :param heading: The title of the heading.
    :returns: The contents of the heading of the article
    """

    soup = soup_factory(rendered_article)




def get_html(url):
    return urllib.urlopen(url).read()
