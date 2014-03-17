#!/usr/bin/env python
"""
Downloads source and html of a wikipedia page.

    ./page_download.py "ARTICLE" [OUTPUT_BASENAME]

Will download article src and html in OUTPUT_BASENAME.html and
OUTPUT_BASENAME.wiki respectively.
"""

import sys

from wikipediabase.fetcher import WikipediaSiteFetcher as Fetcher

def main(argv):
    f = Fetcher()

    fname = argv[2] if len(argv) > 2 else sys.argv[1].replace(" ", "_")
    print "Downloading html for %s..." % argv[1]
    html = f.download(argv[1])
    print "Downloading source for %s..." % argv[1]
    src = f.source(argv[1])

    print "Writing source in %s.wiki..." % fname
    open(fname+".wiki", "w").write(src)
    print "Writing html in %s.html..." % fname
    open(fname+".html", "w").write(html)

    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main(sys.argv)
