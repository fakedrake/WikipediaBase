"""
Screape the attributes out of infoboxes.
"""

import re

from .renderer import WIKIBASE_RENDERER
from .fetcher import StaticFetcher
from .infobox import Infobox
from .util import fromstring, totext, string_reduce, get_article

class DummyInfobox(Infobox):
    """
    This is an infobox of an infobox. Actually it's an infobox whose
    attribute values are the attributes themselves
    """

    def __init__(self, infobox, fetcher=None, renderer=None, **kw):
        if not infobox.startswith("Template:"):
            self.symbol = "Template:"+infobox
            self.title = infobox

        else:
            self.symbol = infobox
            self.title = infobox.replace("Template:", "")

        self.title = string_reduce(self.title).replace(" ", "_")

        # Infobox or ambox
        self.type = self.title.split("_")[0]
        self.renderer = renderer or WIKIBASE_RENDERER

        mu = self.dummy_markup()
        ftchr = StaticFetcher(self.renderer.render(mu, self.title), mu)
        super(DummyInfobox, self).__init__(self.symbol, fetcher=ftchr, **kw)



    # These use the scratch.
    def dummy_attributes(self):
        """
        This iterates over lists of equivalent attributes.
        """

        soup = fromstring(get_article(self.symbol).html_source())

        for table in soup.findall(".//table"):
            if 'mw-templatedata-doc-params' in table.get("class", ""):
                for codes in table.findall(
                        ".//td[@class='mw-templatedata-doc-param-name']"):
                    yield [totext(c).strip() for c in codes.findall('.//code')]

    def dummy_markup(self):
        ret = '{{'+self.title.capitalize().replace("_", " ")+ "\n"
        for aset in self.dummy_attributes():
            ret += "| %s = " % aset[0]

            # Put all equivalent attributes next to each other.
            for a in aset:
                ret += "!!!!!%s!!!!! " % a

            ret += '\n'

        ret += "}}\n"

        return ret

    def rendered_keys(self):
        """
        A dictionary mapping markup keys to the html they were rendered
        to.
        """

        ret = dict()

        for k, v in self.html_parsed():

            for m in re.finditer("!!!!!([^!]+)!!!!!", v):
                ret[m.group(1)] = k

        return ret
