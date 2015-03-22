"""
Screape the attributes out of infoboxes.
"""

import re

from wikipediabase.renderer import WIKIBASE_RENDERER
from wikipediabase.fetcher import StaticFetcher
from wikipediabase.infobox import Infobox
from wikipediabase.util import fromstring, totext, string_reduce, get_article

class MetaInfobox(Infobox):
    """
    This is an infobox of an infobox. It is an infobox with all the
    valid attributes and each value is all the names of all attributes
    that are equivalent to them. Eg An infobox of type Foo that has
    valid attributes A, B, C and D and A, B and C are equivalent has a
    meta infobox that looks something like:

    | Attribute | Value                   |
    |-----------+-------------------------|
    | A         | !!!A!!! !!!B!!! !!!C!!! |
    | B         | !!!A!!! !!!B!!! !!!C!!! |
    | C         | !!!A!!! !!!B!!! !!!C!!! |
    | D         | !!!D!!!                 |

    """

    def __init__(self, infobox_type, fetcher=None, renderer=None, **kw):
        if not infobox.startswith("Template:"):
            self.symbol = "Template:" + infobox_type
            self.title = infobox_type

        else:
            self.symbol = infobox_type
            self.title = infobox_type.replace("Template:", "")

        self.title = string_reduce(self.title).replace(" ", "_")

        # Infobox or ambox
        self.type = self.title.split("_")[0]
        self.renderer = renderer or WIKIBASE_RENDERER

        mu = self.meta_markup()
        ftchr = StaticFetcher(self.renderer.render(mu, self.title), mu)
        super(MetaInfobox, self).__init__(self.symbol, fetcher=ftchr, **kw)



    # These use the scratch.
    def attributes(self):
        """
        Generator of lists whose elements are names of infobox attributes
        that are equivalent. These are essentially the attributes of
        the meta infobox.
        """

        soup = fromstring(get_article(self.symbol).html_source())

        for table in soup.findall(".//table"):
            if 'mw-templatedata-doc-params' in table.get("class", ""):
                for codes in table.findall(
                        ".//td[@class='mw-templatedata-doc-param-name']"):
                    yield [totext(c).strip() for c in codes.findall('.//code')]

    def markup(self):
        """
        Markup of the meta infobox. Each attribute has a value that
        contains all the equivalent attributes to itself.
        """

        ret = '{{'+self.title.capitalize().replace("_", " ")+ "\n"
        for aset in self.attributes():
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
