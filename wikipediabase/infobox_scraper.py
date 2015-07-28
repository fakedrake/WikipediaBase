"""
Screape the attributes out of infoboxes.
"""

import re

from wikipediabase.renderer import WIKIBASE_RENDERER
from wikipediabase.fetcher import StaticFetcher
from wikipediabase.infobox import Infobox
from wikipediabase.util import string_reduce, get_article


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
        infobox_type = infobox_type.strip()
        if not infobox_type.startswith("Template:"):
            symbol, title = "Template:" + infobox_type, infobox_type

        else:
            symbol, title = infobox_type, infobox_type.replace("Template:", "")

        self.title = string_reduce(title).replace(" ", "_")
        self.symbol = symbol

        # Infobox or ambox
        self.type = title.split("_")[0]
        self.renderer = renderer or WIKIBASE_RENDERER

        mu = self.markup_source()
        fetcher = StaticFetcher(self.renderer.render(mu, key=self.title), mu)
        super(MetaInfobox, self).__init__(symbol, title=title, fetcher=fetcher,
                                          **kw)

    def attributes(self):
        """
        A list of the markup attributes.
        """

        # There will always be an example in the documentation but
        # there may be more than one.

        try:
            ibxes = get_article(self.symbol + '/doc').markup_source()
        except LookupError:
            # fallback if no /doc page exists
            ibxes = get_article(self.symbol).markup_source()

        return [i for i
                in set(re.findall(r"^\s*|\s*([a-zA-Z_\-]+)\s*=", ibxes)) if i]

    def markup_source(self):
        """
        Markup of the meta infobox. Each attribute has a value that
        contains all the equivalent attributes to itself.
        """

        return '{{' + self.title.capitalize().replace("_", " ") + "\n" + \
            '\n'.join(["| %s = !!!!!%s!!!!!" % (attr, attr) for
                       attr in self.attributes()]) + \
            "\n}}\n"

    def html_source(self):
        return self.renderer.render(self.markup_source())

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
