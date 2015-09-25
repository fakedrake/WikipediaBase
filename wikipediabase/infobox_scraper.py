"""
Scrape the attributes out of infoboxes.
"""

import json
import re

from wikipediabase.renderer import WIKIBASE_RENDERER
from wikipediabase.fetcher import StaticFetcher
from wikipediabase.infobox import Infobox
from wikipediabase.util import get_article, Expiry

ATTRIBUTE_REGEX = re.compile(r"^\s*\\|\s*([a-zA-Z_\-]+)\s+=")
TEMPLATE_DATA_REGEX = re.compile(r"<templatedata>(.*?)</templatedata>",
                                 flags=re.M | re.S)


def _clean_attribute(a):
    a = a.strip()
    while a[-1].isdigit():
        a = a[:-1]
    return a


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

    A MetaInfobox is generated by looking at both:

    documentation subpages, e.g.
    https://en.wikipedia.org/wiki/Template:Infobox_officeholder/doc

    and documentation pages, e.g.
    https://en.wikipedia.org/wiki/Template:Infobox_officeholder
    """

    def __init__(self, infobox_type, fetcher=None, renderer=None, **kw):
        prefix = "Template:"
        infobox_type = infobox_type.strip()
        if not infobox_type.startswith(prefix):
            raise ValueError("'%s' is not a valid Infobox template docpage "
                             "name. This function expects infobox_type to have "
                             "format 'Template:Infobox <class>'."
                             % infobox_type)

        self.symbol, self.title = infobox_type, infobox_type.replace(prefix, "")
        self.renderer = renderer or WIKIBASE_RENDERER

        mu = self.markup_source()
        fetcher = StaticFetcher(self.renderer.render(mu, key=self.title), mu)
        super(MetaInfobox, self).__init__(self.symbol, title=self.title,
                                          fetcher=fetcher, **kw)

    def _best_attributes(self):
        """
        Returns the best possible list of attributes from various infobox 
        template pages

        Consider the "president" infobox. We first try to follow any 
        redirects, and find that "president" redirects to "officeholder".

        Then we fetch the wikimarkup source of the template documentation 
        subpage at: "/index.php?title=Template:Infobox_officeholder/doc"

        If it exists, we use the <templatedata> block that contains a JSON
        object with attributes. For more info on <templatedata>, see:
        https://www.mediawiki.org/wiki/Extension:TemplateData. Some templates 
        do not have documentation subpages, just documentation pages (no 
        trailing "/doc").

        We look at the rendered HTML of subpages and pages and use a regex 
        that looks for attributes like "| name    =  BBC News".  
        """
        template = self.symbol

        try:
            page = get_article(self.symbol)
            template = page.title()
        except LookupError:
            self.log().warn("Could not find doc any template pages for "
                            "template: \"%s\".",
                            self.symbol)
            return []

        attributes = []
        doc_page = get_article(template)
        try:
            doc_subpage = get_article(template + '/doc')

            markup = doc_subpage.markup_source(expiry=Expiry.LONG)
            attributes.extend(self._attributes_from_template_data(markup))

            html = doc_subpage.html_source(expiry=Expiry.LONG)
            attributes.extend(self._attributes_from_html(html))
        except ValueError:
            self.log().error("Error parsing <templatedata> json for %s. "
                             "Check the page for trailing commas. ",
                             template, exc_info=True)
        except LookupError:
            self.log().warn("Could not find doc subpage for template: \"%s\".",
                            template)

        html = doc_page.html_source(expiry=Expiry.LONG)
        attributes.extend(self._attributes_from_html(html))

        return attributes

    def _attributes_from_template_data(self, markup):
        attributes = []
        match = re.search(TEMPLATE_DATA_REGEX, markup)
        if match:
            template_data = json.loads(match.group(1))
            for a in template_data["params"]:
                attributes.append(a)
                if "aliases" in a:
                    attributes.extend(a["aliases"])

        return attributes

    def _attributes_from_html(self, html):
        return re.findall(ATTRIBUTE_REGEX, html)

    def attributes(self):
        """
        A list of the markup attributes. Attributes are extracted by looking
        at template documentation subpages and pages.
        """
        # deduplicate and remove empty string
        attributes = self._best_attributes()
        attributes = [_clean_attribute(a) for a in attributes if a]
        attributes = list(set(attributes))
        return attributes

    def markup_source(self):
        """
        Markup of the meta infobox. Each attribute has a value that
        contains all possible attributes for this type of infobox.
        """

        return '{{' + self.symbol.replace("Template:", "") + "\n" + \
            '\n'.join(["| %s = !!!!!%s!!!!!" % (attr, attr) for
                       attr in self.attributes()]) + \
            "\n}}\n"

    def html_source(self):
        return self.renderer.render(self.markup_source(), key=self.title)

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
