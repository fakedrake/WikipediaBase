from itertools import islice, takewhile, dropwhile

import os
import urllib
import re

from bs4 import BeautifulSoup

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=\n\s*\|)"

# General tools
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

# Wikipedia
def soup_factory(soup_or_article):
    """
    Return a soup from html. If already a soup dont bother.
    """

    if not isinstance(soup_or_article, BeautifulSoup):
        return BeautifulSoup(soup_or_article)
    else:
        return soup_or_article

def article_json(rendered_article, nwrap=None, lwrap=None):
    """
    Return a dict,

    Example:

    >>> article(get_html("http://en.wikipedia.org/wiki/Edgar_Allan_Poe"))
    {'head': <heading>, 'paragraphs': [...], 'children': [...]}
    """

    if nwrap is None:
        nwrap = lambda x: x

    if lwrap is None:
        lwrap = lambda x: x

    soup = soup_factory(rendered_article)
    txt = soup.find_all(id="mw-content-text")
    l = []
    stack = []

    for tag in dropwhile(lambda x: x.name != 'p', txt[0].children):
        # There are some tags with no content, some empty of
        # non-spaces and divs have no real content.
        if hasattr(tag, "text") and tag.name != 'div' and tag.text.strip():
            if re.match(r"h[123]", tag.name):
                while stack and stack[-1].name >= tag.name:
                    stack.pop()

                stack.append(tag)
            else:
                l.append(([nwrap(i) for i in reversed(stack)], lwrap(tag)))

    return paths_to_tree(l)

def _get_head(lvl, h):
    for n in lvl:
        if n['head'] is h:
            return n

    lvl.append({'head': h, 'paragraphs': [], 'children': []})
    return lvl[-1]

def create_path(path, leaf, tree=None):
    if tree is None:
        tree = {'head': None, 'paragraphs': [], 'children': []}

    lvl = tree
    for h in path:
        lvl = _get_head(lvl['children'], h)

    lvl['paragraphs'].append(leaf)

    return tree

def paths_to_tree(ls):
    tree = {'head': None, 'paragraphs': [], 'children': []}

    for path, par in ls:
        create_path(path, par, tree)

    return tree

def paragraphs(article):
    """
    Given an article in json mode iterato over the paragraphs.
    """

    nodes = [article]
    while nodes:
        nod = nodes.pop()
        for p in nod['paragraphs']:
            yield p

        nodes += nod['children']

def get_html(url):
    """
    Given a url or a filename see if you can ge the corresponding
    html.
    """

    if os.path.isfile(url):
        return open(url, "r").read()

    return urllib.urlopen(url).read()
