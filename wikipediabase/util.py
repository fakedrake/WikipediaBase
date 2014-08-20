from itertools import islice, takewhile, dropwhile, chain

import os
import urllib
import re
import collections

import lxml.etree as ET
from lxml import html

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

    return map(first_part, wiki_markup.split("[[Category:")[1:])


def _get_context(symbol, domain, cls, fetcher=None):
    global _CONTEXT

    if isinstance(symbol, cls):
        return symbol

    if not domain in _CONTEXT:
        _CONTEXT[domain] = dict()

    ret = _CONTEXT[domain].get(symbol, None)
    if ret:
        return ret

    kw = dict(fetcher=fetcher) if fetcher else dict()
    ret = cls(symbol, **kw)
    _CONTEXT[domain][symbol] = ret

    return ret


# This is for printing out stuff only. It is too slow to use for too
# much data.
import datetime


def time_interval(key="default", update=True):
    """
    Give me the interval from the last time I called you.
    """

    if not hasattr(time_interval, 'time_dict'):
        time_interval.time_dict = collections.defaultdict(
            datetime.datetime.now)

    now = datetime.datetime.now()
    ret = now - time_interval.time_dict[key]

    if update:
        time_interval.time_dict[key] = now

    return ret


def subclasses(cls, instantiate=True, **kw):
    """
    A list of instances of subclasses of cls. Instantiate wit kw and
    return just the classes with instantiate=False.
    """

    lcls = cls.__subclasses__()
    rcls = lcls + list(chain.from_iterable([c.__subclasses__() for c in lcls]))
    clss = sorted(rcls, key=lambda c: c.priority, reverse=True)

    if not instantiate:
        return [C for C in clss
                if not C.__name__.startswith("_")]

    return [C(**kw) for C in clss
            if not C.__name__.startswith("_")]


def totext(et):
    return html.HtmlElement(et).text_content()


def tostring(et):
    return ET.tostring(et, method='html', encoding='utf-8')


def fromstring(txt):
    return html.fromstring(txt)
