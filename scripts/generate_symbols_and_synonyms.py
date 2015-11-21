#!/usr/bin/env python

"""
Create wikibase-term symbols and synonyms
"""

import logging
import copy
import time

from unidecode import unidecode

from wikipediabase.dbutil import all_articles, extract_redirect, \
    extract_disambiguation_links, get, is_disambiguation, total_articles
from wikipediabase.symbols import is_good_title, get_synonyms, should_skip
from wikipediabase.util import LRUCache, decode, encode

logging.basicConfig(filename='symbols.log', level=logging.DEBUG)
logging.getLogger("peewee").setLevel(logging.WARNING)

# TODO: change paths; pass in data_dir in sys.argv
symbols_f = open('../data/wikibase-term-foo-symbols', 'w')
synonyms_f = open('../data/wikibase-term-foo-generated-synonyms', 'w')

latest_symbols = LRUCache(100)


def write(symbol, synonyms):
    if is_good_title(symbol):
        symbol = encode(symbol)

        if symbol not in latest_symbols:
            # easy way to prevent writing (too) many duplicate symbols
            symbols_f.write('%s\n' % symbol)
            latest_symbols.set(symbol, symbol)
        for synonym in synonyms:
            if is_good_title(synonym):
                # TODO: remove when we upgrade to Guile 2.0
                synonym = unidecode(synonym)
                synonyms_f.write("{}\t{}\n".format(symbol, synonym))


def generate(title, markup, trail):
    """
    Generate symbols and synonyms by recursively following redirects and
    disambiguation pages.

    trail is a set that stores the titles of articles visited in the
    recursion path.
    """
    if title in trail or should_skip(title):
        # already visited, circular loop
        return

    trail.add(title)

    logging.debug("  .. added %s to trail" % title)
    if len(trail) > 20:
        logging.debug(' .. long trail (%s) -> %s' % (len(trail), trail))

    redirect = extract_redirect(markup)
    disambig = is_disambiguation(title, markup)

    if not redirect and not disambig:
        logging.debug("  .. found a symbol, will write")
        for t in trail:
            write(title, get_synonyms(t))
    else:
        if redirect:
            logging.debug("  .. is redirect, extracted: %s" % redirect)
            try:
                article = get(encode(redirect))
                generate(decode(article.title), article.markup, copy.copy(trail))
            except LookupError as e:
                logging.exception(e)
        elif disambig:
            logging.debug("  .. is disambig")
            for l in extract_disambiguation_links(markup):
                try:
                    article = get(encode(l))
                    generate(decode(article.title), article.markup, copy.copy(trail))
                except LookupError as e:
                    logging.exception(e)


def main():
    print "Calculating total number of articles in the DB"
    total = total_articles()
    print "Found %d articles in the DB" % total

    count = 0.0
    start = time.time()

    for page_id, title, markup in all_articles():
        count += 1
        title = decode(title)
        logging.info("=== evaluating: %s" % title)

        markup = get(encode(title)).markup

        if count % 50000 == 0:
            pct = count / total * 100.0
            print "processed %s articles -- %s percent" % (count, pct)

        if not should_skip(title):
            generate(title, markup, set())


    print "\nDONE"
    print "time to process %s articles: %s" % (total, time.time() - start)

    # TODO: call sort -u
    symbols_f.close()
    synonyms_f.close()

if __name__ == '__main__':
    main()
