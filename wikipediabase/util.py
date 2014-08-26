from itertools import islice, takewhile, dropwhile, chain
from urlparse import urlparse

import os
import urllib
import re
import collections
import functools

import lxml.etree as ET
import copy
from lxml import html

_CONTEXT = dict()

# General tools
# XXX: Plug in here for permanent memoization. You may need to do some
# garbage collection here.

# XXX: I deepcopy objects. If you disable that be very
# careful. However use this only on out facing functions.
DEEPCOPY = True
def memoized(fn):
    @functools.wraps(fn)
    def wrap(*args, **kw):
        try:
            kwkey = hash(tuple(kw.items()))
            argkey = hash(args)
            key = hash((kwkey, argkey))
        except TypeError:
            return wrap(*args, **kw)


        if key in wrap.memoized:
            if DEEPCOPY:
                return copy.deepcopy(wrap.memoized[key])
            else:
                return wrap.memoized[key]

        ret = fn(*args, **kw)
        wrap.memoized[key] = copy.deepcopy(ret)
        return ret

    wrap.memoized = dict()
    # I dont worry too much about the rest of the signature but I
    # really need the name.
    if hasattr(fn, '_provided'):
        wrap.__name__ = fn.__name__
        wrap._provided = fn._provided

    return wrap

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


def get_dummy_infobox(symbol, fetcher=None):
    from .infobox_scraper import DummyInfobox

    return _get_context(symbol, "rendered_infobox", DummyInfobox, fetcher)


def get_infobox(symbol, fetcher=None):
    from .infobox import Infobox

    return _get_context(symbol, "infobox", Infobox, fetcher)


def get_article(symbol, fetcher=None):
    from .article import Article

    return _get_context(symbol, "article", Article, fetcher)


def get_knowledgebase(**kw):
    from .knowledgebase import KnowledgeBase

    ret = _get_context(None, "knowledgebase", KnowledgeBase, **kw)

    # It is important to have the correnct frontend or the fronted
    # will fail to find methods.
    if kw.get('frontend') is not None and \
       kw.get('frontend') is not ret.frontend:
        return _get_context(None, "knowledgebase", KnowledgeBase, new=True, **kw)

    return ret

def markup_categories(wiki_markup):
    """
    return the names of the categories.
    """

    # It is slightly faster like this because we are nto creating
    # a lambda obj each time.
    def first_part(s):
        return s.split(']]', 1)[0]

    return map(first_part, wiki_markup.split("[[Category:")[1:])


def _get_context(symbol, domain, cls, new=False, **kwargs):
    global _CONTEXT

    if isinstance(symbol, cls):
        return symbol

    if domain not in _CONTEXT:
        _CONTEXT[domain] = dict()

    if not new:
        ret = _CONTEXT[domain].get(symbol, None)
        if ret is not None:
            return ret

    if symbol:
        ret = cls(symbol, **kwargs)
    else:
        ret = cls(**kwargs)

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
    for c in rcls:
        assert isinstance(c.priority, int), \
            "type(%s . priority) = %s != int" % (repr(c), type(c.priority.name))

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

# A memoization
def fromstring(txt):
    if not hasattr(fromstring, 'memoized'):
        fromstring.memoized = dict()

    if txt in fromstring.memoized:
        ret = copy.deepcopy(fromstring.memoized[txt])
    else:
        ret = html.fromstring(txt)
        # Keep a separate copy in the cache
        fromstring.memoized[txt] = copy.deepcopy(ret)

    return ret

def expand(fn, ite):
    return reduce(lambda a,b: a+b, [fn(i) for i in ite])

def concat(*args):

    return reduce(lambda a,b: a+b,
                  [list(i) if isinstance(i, list) else [i]
                   for i in args])


def url_get_dict(url):
    ret = urlparse(url)

    if ret.query:
        return dict(map(lambda x: x.split('='), ret.query.split('&')))
    else:
        return dict()


def string_reduce(string):
    """
    Remove punctuation, an/a/the and spaces.
    """
    # It may seem a bad idea to not even return 'the reckoning' from
    # symbol '"The Reckonging"' but we rduce user input as well.

    # First remove quotes so the stopwords turn up at the front
    ret = re.sub(ur"([\W\s]+)", " ", string, flags=re.U|re.I).strip().lower()
    return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()
