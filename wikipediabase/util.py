from itertools import islice, takewhile, dropwhile

import os
import urllib
import re
import collections

from bs4 import BeautifulSoup

_CONTEXT = dict()

# General tools
def iwindow(seq, n):
    """
    Returns a sliding window (of width n) over data from the iterable
    s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    """
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

# Wikipedia
def soup_factory(soup_or_article):
    """
    Return a soup from html. If already a soup dont bother.
    """

    if not isinstance(soup_or_article, BeautifulSoup):
        return BeautifulSoup(soup_or_article)
    else:
        return soup_or_article

def tag_depth(tag):
    return len(list(tag.parents))


def get_infobox(symbol, fetcher=None):
    from infobox import Infobox

    return _get_context(symbol, "infobox", Infobox, fetcher=fetcher)

def get_article(symbol, fetcher=None):
    from article import Article

    return _get_context(symbol, "article", Article)

def markup_categories(wiki_markup):
    """
    return the names of the categories.
    """

    # It is slightly faster like this because we are nto creating
    # a lambda obj each time.
    def first_part(s):
        return s.split(']]', 1)[0]

    return map(first_part, txt.split("[[Category:")[1:])


def _get_context(symbol, domain, cls, fetcher=None):
    global _CONTEXT

    if isinstance(symbol, cls):
        return symbol

    if not domain in _CONTEXT:
        _CONTEXT[domain] = dict()

    ret = _CONTEXT[domain].get(symbol, None)
    if ret:
        return ret

    kw = fetcher and dict(fetcher=fetcher) or dict()
    ret = cls(symbol, **kw)
    _CONTEXT[domain][symbol] = ret

    return ret


def first_paren(text):
    """
    If the first sentence in the text has parentheses return those. If
    not return None.
    """

    depth = 0
    first_paren = None

    for i, c in enumerate(text):
        if c == "(":
            depth += 1
            if depth == 1:
                first_paren = i+1

        elif c == ")" and depth > 0:
            if depth == 1:
                return text[first_paren:i]

            depth -= 1

        elif c == "." and depth == 0:
            return None

# This is for printing out stuff only. It is too slow to use for too
# much data.
import datetime

def time_interval(key="default"):
    """
    Give me the interval from the last time I called you.
    """

    if not hasattr(time_interval, 'time_dict'):
        time_interval.time_dict = collections.defaultdict(datetime.datetime.now)

    now = datetime.datetime.now()
    ret = now - time_interval.time_dict[key]
    time_interval.time_dict[key] = now

    return ret

def sublcasses(cls):
    retirn [c for c in cls.subclasses if not c.__name__.startswith("_")]
