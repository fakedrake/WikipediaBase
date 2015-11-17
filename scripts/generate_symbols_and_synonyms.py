#!/usr/bin/env python

"""
Create wikibase-term symbols and synonyms
"""

import logging
import copy

from unidecode import unidecode

from wikipediabase.dbutil import all_articles, extract_redirect, \
    extract_disambiguation_links, get, is_disambiguation
from wikipediabase.symbols import is_good_title, get_synonyms, should_skip
from wikipediabase.util import LRUCache, decode, encode

logging.basicConfig(filename='symbols.log', level=logging.DEBUG)
logging.getLogger("peewee").setLevel(logging.WARNING)

symbols_f = open('wikibase-term-symbols', 'w')
synonyms_f = open('wikibase-term-generated-synonyms', 'w')

latest_symbols = LRUCache(100)


def write(symbol, synonyms):
    if is_good_title(symbol):
        assert(isinstance(symbol, unicode))
        symbol = encode(symbol)

        if symbol not in latest_symbols:
            symbols_f.write('%s\n' % symbol)
            latest_symbols.set(symbol, symbol)
        for synonym in synonyms:
            if is_good_title(synonym):
                # TODO: remove for production
                assert(isinstance(synonym, unicode))

                # TODO: remove when we upgrade to Guile 2.0
                synonym = unidecode(synonym)
                synonyms_f.write("{}\t{}\n".format(symbol, synonym))


def generate(title, markup, trail):
    if title in trail or should_skip(title):
        # already visited, circular loop
        return

    trail.add(title)

    if len(trail) > 20:
        logging.debug(' .. LONG TRAIL -> %s' % trail)
    logging.debug("  .. added %s to trail" % title)
    redirect = extract_redirect(markup)
    disambig = is_disambiguation(title, markup)

    if not redirect and not disambig:
        logging.debug("  .. base symbol, will write")
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
    for page_id, title, markup in all_articles():
        title = decode(title)
        logging.info("=== evaluating: %s" % title)
        if not should_skip(title):
            generate(title, markup, set())

if __name__ == '__main__':
    main()
