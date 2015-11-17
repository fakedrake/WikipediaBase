#!/usr/bin/env python

"""
Parse Wikipedia XML dump and create the WikipediaBase backend
Based on github.com/larsmans/wiki-dump-tools
"""

import re
import sys
import time

from lxml import etree
from namedentities import numeric_entities

from wikipediabase.dbutil import insert_article_batch

BATCH_SIZE = 250  # number of articles to bulk insert


def _get_namespace(tag):
    namespace = re.match("^{(.*?)}", tag).group(1)
    if not namespace.startswith("http://www.mediawiki.org/xml/export-"):
        raise ValueError("%s not recognized as MediaWiki database dump"
                         % namespace)
    return namespace


def extract_pages(f):
    """
    Extract pages from the Wikimedia database dump

    :param file-like f: Handle on Wikipedia dump. May be any type supported by
        etree.iterparse.
    :return (page_id, title, markup) triples
    :rtype iterable (int, string, string)
    """
    elems = (elem for _, elem in etree.iterparse(f, events=["end"]))

    elem = next(elems)
    namespace = _get_namespace(elem.tag)
    ns_mapping = {"ns": namespace}
    page_tag = "{%(ns)s}page" % ns_mapping
    markup_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
    id_path = "./{%(ns)s}id" % ns_mapping
    ns_path = "./{%(ns)s}ns" % ns_mapping
    title_path = "./{%(ns)s}title" % ns_mapping

    for elem in elems:
        if elem.tag == page_tag:
            markup = elem.find(markup_path).text
            if markup is None:
                continue

            # only look at articles (namespace 0) and templates (namespace 10)
            # see https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
            page_ns = elem.find(ns_path)
            if page_ns is None or page_ns.text not in ('0', '10'):
                continue

            page_id = int(elem.find(id_path).text)
            title = elem.find(title_path).text.replace('_', ' ')

            if not isinstance(title, unicode):
                title = title.decode('utf-8')

            if not isinstance(markup, unicode):
                markup = markup.decode('utf-8')

            yield (page_id, title, markup)

            elem.clear()
            if hasattr(elem, "getprevious"):
                while elem.getprevious() is not None:
                    del elem.getparent()[0]


def main():
    batch = []
    count = 0

    start = time.time()

    for page_id, title, markup in extract_pages(sys.stdin):
        assert(isinstance(title, unicode))
        assert(isinstance(markup, unicode))

        # As of Oct '15, Allegro Lisp doesn't correctly decode a utf-8 string.
        # As a temporary workaround, we encode into numeric HTML entities
        # e.g. "&#160;" for Unicode non-breaking space
        # TODO: remove when unicode issue in Allegro is fixed
        title = numeric_entities(title)

        batch.append({
            'id': page_id,
            'title': title,
            'markup': markup,
        })

        if len(batch) == BATCH_SIZE:
            insert_article_batch(batch)
            count += len(batch)
            print "progress: inserted %s articles" % (count)
            batch = []

    if len(batch) != 0:
        insert_article_batch(batch)
        count += len(batch)

    print "=== Finished inserting %s articles ===" % (count)
    print "Total time elapsed: %s seconds" % (time.time() - start)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        cmd = sys.argv[0]
        print "Usage: %s; will read from standard input\n" % cmd
        print "To create the WikipediaBase backend, run:"
        print "  $ bzcat /path/to/article/dump.xml.bz2 | %s" % cmd
        sys.exit(1)

    main()
