from itertools import islice, chain
from urlparse import urlparse
import collections
import copy
import datetime
import functools
import inspect
import re

from bs4 import UnicodeDammit
from lxml import etree as ET, html

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


_CONTEXT = dict()

DBM_FILE = "/tmp/wikipediabase.mdb"


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


def get_user_agent():
    return _USER_AGENT


def get_knowledgebase(**kw):
    from wikipediabase.knowledgebase import KnowledgeBase

    ret = _context_get(None, "knowledgebase", KnowledgeBase, **kw)

    # It is important to have the correnct frontend or the fronted
    # will fail to find methods.
    if kw.get('frontend') is not None and \
       kw.get('frontend') is not ret.frontend:
        return _context_get(None, "knowledgebase", KnowledgeBase, new=True, **kw)

    return ret


def _get_persistent_dict(filename=DBM_FILE):
    """
    A dict that syncs with persistent data storage.
    """
    from wikipediabase.persistentkv import PersistentDict

    return _context_get(filename, 'peristent_store', PersistentDict)


def markup_categories(wiki_markup):
    """
    return the names of the categories.
    """

    # It is slightly faster like this because we are nto creating
    # a lambda obj each time.
    def first_part(s):
        return s.split(']]', 1)[0]

    return map(first_part, wiki_markup.split("[[Category:")[1:])


def _context_get(symbol, domain, cls, new=False, **kwargs):
    """
    The context is actually a global cache used to keep track of the
    objects created and reuse them when possible.

    For example if I need an infobox for bill clinton I can get it by
    calling. _get_context('bill clinton', 'infoboxes' Infobox). which
    will create an Infobox instance for 'bill clinton' and cache
    it. If I later try to create an object in the same way, I will be
    reusing the old one.

    In place of symbol an object can be passed. In that case we return
    the object itself. This way we can have some flexibility with
    types and when calling get_<class>(<class instance>) have the
    right thing done.

    :param symbol: The symbol for which an object is created.
    :param domain: The domain for which the object is created.
    :param cls: The class of the object.
    :param new: Force the creation of a new object.
    :param kwargs: Extra keywords to be passed for the instance creation
    :returns: An instance of class cls.
    """
    global _CONTEXT

    if inspect.isclass(cls) and isinstance(symbol, cls):
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

# A memoization


def fromstring(txt, literal_newlines=False):
    if isinstance(txt, ET._Element):
        return txt

    if not hasattr(fromstring, 'memoized'):
        fromstring.memoized = dict()

    if txt in fromstring.memoized:
        ret = copy.deepcopy(fromstring.memoized[txt])
    else:
        if literal_newlines:
            txt = re.sub('<\s*br\s*/?>', u"\n", txt)
            if not txt.strip():
                return txt

        # force lxml to do unicode encoding
        ud = UnicodeDammit(txt, is_html=True)
        ret = html.fromstring(ud.unicode_markup)

        # Keep a separate copy in the cache
        fromstring.memoized[txt] = copy.deepcopy(ret)

    return ret


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


def output(s):
    # TODO : remove this function for production
    if not isinstance(s, unicode):
        raise StringException("Not a unicode string: %s" % s)
    return s
