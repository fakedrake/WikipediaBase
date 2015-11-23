from itertools import islice, chain
from urlparse import urlparse

import re
import collections
import functools
import inspect

import lxml.etree as ET
import copy
import lxml
from lxml import html

from wikipediabase.config import configuration

# General tools
# XXX: Plug in here for permanent memoization. You may need to do some
# garbage collection here.

# XXX: I deepcopy objects. If you disable that be very
# careful. However use this only on out facing functions.
DEEPCOPY = True

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


def get_meta_infobox(symbol, configuration=configuration):
    return configuration.ref.object_cache \
                            .meta_infoboxes \
                            .with_args(symbol, configuration=configuration) \
                            .deref()

def get_infobox(symbol, configuration=configuration):
    return configuration.ref.object_cache \
                            .infoboxes \
                            .with_args(symbol, configuration=configuration) \
                            .deref()

def get_article(symbol, configuration=configuration):
    return configuration.ref.object_cache \
                        .articles \
                        .with_args(symbol, configuration=configuration) \
                        .deref()


def get_knowledgebase(configuration=configuration):
    return configuration.ref.knowledgebase \
                            .with_args(configuration=configuration) \
                            .deref()

def _get_persistent_dict(filename=None):
    """
    A dict that syncs with persistent data storage.
    """
    return configuration.ref.object_cache.persistent_dict.with_args(filename,
                                                                    configuration=configuration).deref()

def markup_categories(wiki_markup):
    """
    return the names of the categories.
    """

    # It is slightly faster like this because we are nto creating
    # a lambda obj each time.
    def first_part(s):
        return s.split(']]', 1)[0]

    return map(first_part, wiki_markup.split("[[Category:")[1:])

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
def fromstring(txt, literal_newlines=False):
    if isinstance(txt, lxml.etree._Element):
        return txt

    if not hasattr(fromstring, 'memoized'):
        fromstring.memoized = dict()

    if txt in fromstring.memoized:
        return copy.deepcopy(fromstring.memoized[txt])

    if literal_newlines:
        txt = re.sub('<\s*br\s*/?>',"\n", txt)
        if not txt.strip():
            return txt

        ret = html.fromstring(txt)
        # Keep a separate copy in the cache
        fromstring.memoized[txt] = copy.deepcopy(ret)

def url_get_dict(url):
    ret = urlparse(url)

    if ret.query:
        return dict(map(lambda x: x.split('='), ret.query.split('&')))

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


def encode(txt):
    # return txt.decode('utf-8')
    # return unicode(txt.decode("utf-8", errors='ignore'))
    return txt

def markup_unlink(markup):
    return re.sub(r"\[+(.*\||)(?P<content>.*?)\]+", r'\g<content>', markup)
