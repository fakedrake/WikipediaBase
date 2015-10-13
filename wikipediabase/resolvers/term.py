# -*- coding: utf-8 -*-

import re

from wikipediabase.provider import provide
from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.lispify import lispify
from wikipediabase.util import get_infoboxes, get_article, totext, markup_unlink


class TermResolver(BaseResolver):

    """
    A resolver that can resolve a fixed set of simple attributes.
    """

    priority = 11

    # TODO: add provided methods for SHORT-ARTICLE
    # as described in the WikipediaBase InfoLab wiki page

    def _should_resolve(self, cls):
        return cls == 'wikibase-term'

    @provide(name="coordinates")
    def coordinates(self, article, _):
        for ibox in get_infoboxes(article):
            src = ibox.html_source()
            if src is None:
                return None

            xpath = ".//span[@id='coordinates']"
            lat = src.find(xpath + "//span[@class='latitude']")
            lon = src.find(xpath + "//span[@class='longitude']")

            if lat is None or lon is None:
                return None

            nlat = self._dton(totext(lat))
            nlon = self._dton(totext(lon))

            return lispify([nlat, nlon], typecode='coordinates')

    @provide(name="image-data")
    def image(self, article, attribute):
        # Make sure we are not getting back a LispType.

        infoboxes = get_infoboxes(article)
        imgs = [ibx.get('image') for ibx in infoboxes]
        if not imgs:
            return None

        img = imgs[0]
        fnam = img.replace(" ", "_")
        if "File:" in img:
            fnam = fnam.split("File:")[1]

        # TODO : is this a temporary fix? investigate what this annotation means
        # see 'Bill Clinton' for an example
        if "{{!}}border" in img:
            fnam = fnam.split("{{!}}border")[0]

        caps = [ibx.get('caption') for ibx in infoboxes]
        caps = filter(lambda x: x, caps)  # remove None values
        return lispify([0, fnam] + ([markup_unlink(caps[0])] if caps else []))

    @provide(name='number')
    def number(self, article, _):
        """
        True if it is plural.
        """
        # First paragraph refers more often to the symbol itself
        # rather than things related to it.
        txt = get_article(article).first_paragraph()

        nay = sum(map(txt.count, [' is ', ' was ', ' has ']))
        yay = sum(map(txt.count, [' are ', ' were ', ' have ']))

        # inequality because there are many more nays
        return lispify(yay > nay, typecode='calculated')

    @provide(name='proper')
    def proper(self, article, _):
        """
        Get a quick boolean answer based on the symbol text and the
        article text.
        """

        # Blindly copied by the ruby version
        a = re.sub(r"\s*\(.*\)\s*", "", article.replace("_", " "))
        txt = totext(get_article(article).html_source())
        ret = (txt.count(a.lower()) - txt.count(". " + a.lower()) <
               txt.count(a))

        return lispify(ret, typecode='calculated')

    @provide(name='short-article')
    def short_article(self, symbol, _):
        """
        The first paragraph of the article, or if the first paragraph is
        shorter than 350 characters, then returns the first paragraphs such
        that the sum of the rendered characters is at least 350.
        """

        # TODO: check if the first paragraph is shorter than 350 characters
        first_paragraph = get_article(symbol).first_paragraph()
        return lispify(first_paragraph, typecode='html')

    @provide(name='url')
    def url(self, article, _):
        """
        Note that this url is the wikipedia.org url. NOT the place where
        we got the page.
        """
        # Will also teake care of redirections.
        article = get_article(article)
        url = article.url()
        return lispify(url, typecode='url')

    @provide(name="word-count")
    def word_count(self, article, attribute):
        self.log().info("Trying 'word-count' tag from static resolver.")
        self._tag = "html"
        return len(self._words(self.fetcher.html_source(article)))

    @staticmethod
    def _dton(s):
        """
        degrees minutes, seconds to float or int.
        """

        ls = re.split(ur'(?:°|′|″)', s.strip())
        sig = -1 if ls.pop() in ['S', 'W'] else 1
        ret = int(ls.pop(0))
        if len(ls):
            m = float(ls.pop(0))
            ret += m / 60

        if len(ls):
            s = float(ls.pop(0))
            ret += s / 3600

        return sig * (ret if isinstance(ret, int) else round(ret, 4))

    def _words(self, article):
        return re.findall('\w+', article.lower())
