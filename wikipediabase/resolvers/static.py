# -*- coding: utf-8 -*-

import re

from wikipediabase.provider import provide
from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.enchantments import enchant
from wikipediabase.util import get_infobox, get_article, totext, markup_unlink


class StaticResolver(BaseResolver):

    """
    A resolver that can resolve a fixed set of simple attributes.
    """

    priority = 11

    def _words(self, article):
        return re.findall('\w+', article.lower())

    @provide(name="word-count")
    def word_cout(self, article, attribute):
        self.log().info("Trying 'word-count' tag from static resolver.")
        self._tag = "html"
        return len(self._words(self.fetcher.download(article)))

    @provide(name="gender")
    def gender(self, article, attribute):
        from wikipediabase.classifiers import PersonClassifier
        cls = PersonClassifier().classify(article)

        if 'wikipedia-male' in cls:
            return enchant(':masculine', None)

        if 'wikipedia-female' in cls:
            return enchant(':feminine', None)

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

    @provide(name="coordinates")
    def coordinates(self, article, _):
        src = get_infobox(article).html_source()
        if src is None:
            return None

        lat = src.find(".//span[@id='coordinates']//span[@class='latitude']")
        lon = src.find(".//span[@id='coordinates']//span[@class='longitude']")

        if lat is None or lon is None:
            return None

        nlat = self._dton(totext(lat))
        nlon = self._dton(totext(lon))

        return enchant("coordinates", [nlat, nlon])

    @provide(name="image-data")
    def image(self, article, attribute):
        # Make sure we are not getting back the enchanted.

        ibx = get_infobox(article)
        img = ibx.get('image')
        if not img:
            return None

        fnam = img.replace(" ", "_")
        if "File:" in img:
            fnam = fnam.split("File:")[1]

        # TODO : is this a temporary fix? investigate what this annotation means
        # see 'Bill Clinton' for an example
        if "{{!}}border" in img:
            fnam = fnam.split("{{!}}border")[0]

        cap = ibx.get('caption')
        return enchant(None, [0, fnam] + ([markup_unlink(cap)] if cap else []))

    @provide(name='url')
    def url(self, article, _):
        """
        Note that this url is the wikipedia.org url. NOT the place where
        we got the page.
        """
        # Will also teake care of redirections.
        article = get_article(article)
        url = article.url()
        return enchant("url", url)

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
        return enchant(None, yay > nay)

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

        return enchant(None, ret)
