# -*- coding: utf-8 -*-

import re

from ..provider import provide
from .base import BaseResolver
from ..enchantments import enchant
from .. util import get_infobox, get_article, totext

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
        from ..classifiers import PersonClassifier
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
        ret = d = int(ls.pop(0))
        if len(ls):
            m = float(ls.pop(0))
            ret += m/60

        if len(ls):
            s = float(ls.pop(0))
            ret += s/3600

        return sig*(ret if isinstance(ret, int) else round(ret, 4))

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

        imgl = get_infobox(article).html_source().find('.//td/a/img/..')
        if imgl is None:
            return None

        fnam = imgl.get('href').split("File:")[1]
        cap = totext(imgl.getparent()).strip()

        return enchant(None, [0, fnam] + ([cap] if cap else []))

    @provide(name='url')
    def url(self, article, _):
        # Will also take care of redirections.
        return enchant("url", get_article(article).url())

    @provide(name='number')
    def number(self, article, _):
        a = re.sub(r"\s*\(.*\)\s*", "", article.replace("_", " "))

        # First paragraph refers more often to the symbol itself
        # rather than things related to it.
        txt = get_article(article).paragraphs()[0]

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
        ret = (txt.count(a.lower()) - txt.count(". " + a.lower()) < \
               txt.count(a))

        return enchant(None, ret)
