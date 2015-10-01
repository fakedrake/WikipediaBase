import re
from itertools import chain

from wikipediabase.fetcher import WIKIBASE_FETCHER

MW_HEADING_RX = map(re.compile, [
    ur"\s*==([\w\s]+)==",
    ur"\s*===([\w\s]+)===",
    ur"\s*====([\w\s]+)====",
    ur"\* \[\[Template:Infobox ([\w\s]*)\]\]",
    ur"\*\* \[\[Template:Infobox ([\w\s]*)\]\]",
    # Not there but just in case
    ur"\*\*\* \[\[Template:Infobox ([\w\s]*)\]\]",
])


def ibx_tree(src, prefix=None, form=None):
    """
    [(item-name, [parents, ...]), ...]

    There are times when item-name will be in parents

    You can also provide a prefix path in case you need a different
    root.

    You also have the chance to change the form of the category
    """

    # TODO : case is inconsistent, e.g. "Person" instead of "person"

    stack = (prefix or []) + ([None] * len(MW_HEADING_RX))
    queue = []
    offset = len(prefix or [])

    for l in src.split(u"\n"):

        for d, r in enumerate(MW_HEADING_RX, offset):
            m = r.match(l)
            if m:
                if form:
                    it = form(m.group(1), l)
                else:
                    it = m.group(1)
                for i, _ in enumerate(stack[d:], d):
                    stack[i] = None

                stack[d] = it
                if d > offset + 2:
                    queue.append((it,
                                  [i for i in stack[:d] if i is not None]))

                break

    return queue


def ibx_type_tree(fetcher=None, form=None):
    if hasattr(ibx_type_tree, "ret"):
        return ibx_type_tree.ret

    if not fetcher:
        fetcher = WIKIBASE_FETCHER

    src = fetcher.markup_source("Wikipedia:List_of_infoboxes")
    titles = map(lambda x: x.split("}}", 1)[0],
                 src.split(u"{{Wikipedia:List of infoboxes/")[1:])
    symbols = (u"Wikipedia:List_of_infoboxes/" + i
               for i in titles)
    tuples = chain.from_iterable((ibx_tree(fetcher.markup_source(sym),
                                           form=form)
                                  for sym, tit in zip(symbols, titles)))
    ibx_type_tree.ret = dict(tuples)
    return ibx_type_tree.ret

ibx_type_superclasses = ibx_type_tree

__all__ = ["ibx_type_superclasses", "ibx_type_tree", "ibx_tree"]
