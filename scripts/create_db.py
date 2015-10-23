from lxml import etree

import re
import sys
import time

from wikipediabase.dbutil import Article, db, is_good_title, is_redirect


BATCH_SIZE = 250  # number of articles to bulk insert


def _get_namespace(tag):
    namespace = re.match("^{(.*?)}", tag).group(1)
    if not namespace.startswith("http://www.mediawiki.org/xml/export-"):
        raise ValueError("%s not recognized as MediaWiki database dump"
                         % namespace)
    return namespace


def extract_pages(f):
    """Extract pages from Wikimedia database dump.

    Parameters
    ----------
    f : file-like or str
        Handle on Wikimedia article dump. May be any type supported by
        etree.iterparse.

    Returns
    -------
    pages : iterable over (int, string, string)
        Generates (page_id, title, markup) triples.
        In Python 2.x, may produce either str or unicode strings.
    """
    elems = (elem for _, elem in etree.iterparse(f, events=["end"]))

    # We can't rely on the namespace for database dumps, since it's changed
    # it every time a small modification to the format is made. So, determine
    # those from the first element we find, which will be part of the metadata,
    # and construct element paths.
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

            # only look at pages in the main namespace
            # see https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
            page_ns = elem.find(ns_path)
            if page_ns is None or page_ns.text != '0':
                continue

            page_id = int(elem.find(id_path).text)
            title = elem.find(title_path).text.replace('_', ' ')

            if not isinstance(title, unicode):
                title = unicode(title, 'utf-8')

            if not isinstance(markup, unicode):
                markup = unicode(markup, 'utf-8')

            yield (page_id, title, markup)

            # Prune the element tree, as per
            # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
            # We do this only for <page>s, since we need to inspect the
            # ./revision/text element. That shouldn't matter since the pages
            # comprise the bulk of the file.
            elem.clear()
            if hasattr(elem, "getprevious"):
                # LXML only: unlink elem from its parent
                while elem.getprevious() is not None:
                    del elem.getparent()[0]


def insert_batch(batch):
    db.connect()
    with db.atomic():
        Article.insert_many(batch).execute()
    db.close()

def main():
    batch = []
    count = 0

    start = time.time()

    for page_id, title, markup in extract_pages(sys.stdin):
        assert(isinstance(title, unicode))
        assert(isinstance(markup, unicode))

        if not is_good_title(title) or is_redirect(markup):
            continue

        batch.append({
            'id': page_id,
            'title': title,
            'markup': markup,
        })

        if len(batch) == BATCH_SIZE:
            insert_batch(batch)
            count += len(batch)
            print "progress: inserted %s articles" % (count)
            batch = []

    if len(batch) != 0:
        insert_batch(batch)
        count += len(batch)

    print "=== Finished inserting %s articles ===" % (count)
    print "Total time elapsed: %s seconds" % (time.time() - start)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print "usage: %s; will read from standard input" % sys.argv[0]
        sys.exit(1)

    main()
