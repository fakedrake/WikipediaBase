from itertools import chain
from urlparse import urlparse
import collections
import copy
import datetime
import re

from bs4 import UnicodeDammit
from lxml import etree as ET, html
from namedentities import numeric_entities, unicode_entities

_USER_AGENT = "WikipediaBase/1.0 " \
    "(http://start.csail.mit.edu; wikibase-admins@csail.mit.edu)"


class Expiry:
    DEFAULT = 14 * 24 * 60 * 60   # two weeks in seconds
    LONG = 6 * 30 * 24 * 60 * 60   # six months in seconds
    NEVER = None


class LRUCache:

    """
    A least recently used (LRU) cache with a max capacity
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def __contains__(self, item):
        return self.cache.__contains__(item)

    def get(self, key):
        """
        Get the value of key if the key exists in the cache
        Raises a KeyError if key is not in the cache
        """
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def set(self, key, value):
        """
        Insert the value if the key is not already present. When the cache
        reaches its capacity, it should invalidate the least recently used item
        before inserting a new item.
        """
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value


class StringException(Exception):
    pass


def get_user_agent():
    return _USER_AGENT


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
    txt = html.HtmlElement(et).text_content()
    txt = unicode(txt)
    return txt


def tostring(et):
    s = ET.tostring(et, method='html', encoding=unicode)
    assert(isinstance(s, unicode))  # TODO : remove for production
    return s


def fromstring(txt, literal_newlines=False):
    if isinstance(txt, ET._Element):
        return txt

    if literal_newlines:
        txt = re.sub('<\s*br\s*/?>', u"\n", txt)
        if not txt.strip():
            return txt

    # force lxml to do unicode encoding
    ud = UnicodeDammit(txt, is_html=True)
    ret = html.fromstring(ud.unicode_markup)
    return ret


def n_copies_without_children(elem_with_children, n):
    element = copy.copy(elem_with_children)  # shallow copy
    for e in element.iterchildren():
        element.remove(e)
    return [copy.copy(element) for i in xrange(n)]


def expand(fn, ite):
    return reduce(lambda a, b: a + b, [fn(i) for i in ite])


def concat(*args):

    return reduce(lambda a, b: a + b,
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
    ret = re.sub(ur"([\W\s]+)", " ", string, flags=re.U | re.I).strip().lower()
    return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()


def markup_unlink(markup):
    return re.sub(r"\[+(.*\||)(?P<content>.*?)\]+", r'\g<content>', markup)


def encode(s):
    return numeric_entities(s)


def decode(s):
    if isinstance(s, tuple):
        return tuple(map(decode, s))
    elif isinstance(s, basestring):
        return unicode(unicode_entities(s))
    else:
        return s


def output(s):
    # TODO : remove this function for production
    if not isinstance(s, unicode):
        raise StringException("Not a unicode string: %s" % s)
    return s
