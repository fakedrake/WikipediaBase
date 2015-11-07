import json
import re

from fuzzywuzzy import fuzz, process

from wikipediabase.article import get_article
from wikipediabase.fetcher import get_fetcher
from wikipediabase.log import Logging
from wikipediabase.renderer import get_renderer
from wikipediabase.util import Expiry, LRUCache, fromstring, totext, tostring


class Infobox(Logging):

    def __init__(self, symbol, markup, html):
        self.symbol = symbol
        self.markup = markup
        self.html = html

    @property
    def attributes(self):
        """
        Gets a dictionary of attributes, where keys are markup attributes and
        values are rendered attributes.

        Rendered attributes may be None if no mapping exists. Markup attributes
        are never None.
        """

        attrs = {k: None for k, v in self._markup_items()}

        ibx = get_meta_infobox(self.template)
        meta_attributes = ibx.attributes

        for attr in attrs:
            # ignore numeric suffixes when looking for rendered attributes
            # e.g. '3' in 'SUCCESSOR3'
            clean_attr = InfoboxUtil.clean_attribute(attr)
            if clean_attr in meta_attributes:
                attrs[attr] = meta_attributes[clean_attr]

        return attrs

    def get(self, attr, source=None):
        """
        - First try plain markup attributes
        - Then translating each markup's translations
        """

        # Look into html first. The results here are much more readable
        html_attr = attr.lower().replace(u"-", u" ")
        markup_attr = attr.lower()
        rendered_attr = self.attributes.get(markup_attr)

        if source is None or source == 'html':
            for k, v in self._html_items():
                if k.lower().replace(u".", u"") == html_attr or \
                   k == rendered_attr:
                    return v

        # Then look into the markup
        for k, v in self._markup_items():
            if k == markup_attr:
                return v

    @property
    def template(self):
        for m in re.finditer(InfoboxUtil.TEMPLATE_REGEX, self.markup):
            template = "Template:" + m.group('infobox').strip()
            return template

    @property
    def wikipedia_class(self):
        return InfoboxUtil.to_class(self.template)

    def _html_items(self):
        """
        HTML parsed as a list of (key, val)
        """
        return InfoboxUtil.parse_infobox_html(self.html)

    def _markup_items(self):
        """
        Markup parsed as a list of (key, val)
        """

        items = []
        for m in re.finditer(InfoboxUtil.ATTRIBUTE_VALUE_REGEX, self.markup):
            key = m.group("attr").replace("_", "-").lower()
            val = m.group("val").strip()
            items.append((key, val))
        return items


class MetaInfobox(Logging):

    def __init__(self, symbol, attrs):
        self.symbol = symbol
        self.attrs = attrs

    @property
    def attributes(self):
        """
        Gets a dictionary of attributes, where keys are markup attributes and
        values are rendered attributes.

        The dictionary contains no None values. All markup attributes have a
        corresponding rendered attributes. Markup attributes with no rendered
        mappings are not included.
        """
        return self.attrs


# -------
# Builders
# -------


class InfoboxBuilder(Logging):

    """
    InfoboxBuilder scrapes markup and HTML of an article to build a list
    of infoboxes
    """

    def __init__(self, symbol):
        self.symbol = symbol

    def build(self, expiry=Expiry.DEFAULT):
        """
        Returns a list of Infobox objects constructed from the article
        """

        fetcher = get_fetcher()
        markup = fetcher.markup_source(self.symbol, expiry=expiry)
        html = fetcher.html_source(self.symbol, expiry=expiry)

        infoboxes, external = self._infoboxes_from_article(markup, html)

        for template in external:
            title = 'Template:%s' % template.strip()
            try:
                # templates are not stored in the backend, so we need to fetch
                # from live wikipedia.org
                # TODO: revisit. now that templates are in the backend, what
                # is more convenient?
                m = fetcher.markup_source(title, expiry=expiry, force_live=True)
                h = fetcher.html_source(title, expiry=expiry)

                # we only follow external infobox templates once, instead of
                # looping until we can't find additional external templates.
                # it seems dangerous to keep following template links. It's
                # possible to get stuck in a long redirect loop
                external_infoboxes, _ = self._infoboxes_from_article(m, h)
                infoboxes.extend(external_infoboxes)
            except LookupError:
                self.log().warn("Could not find external infobox template '%s'",
                                title)

        return infoboxes

    def _infoboxes_from_article(self, markup, html):
        markup_infoboxes, external_templates = self._markup_infoboxes(markup)
        html_infoboxes = self._html_infoboxes(html)

        # TODO: not a valid assumption, assertion frequently fails
        # e.g. "IS (manga)"
        # TODO: remove for production
        assert(len(markup_infoboxes) <= len(html_infoboxes))

        if len(markup_infoboxes) != len(html_infoboxes):
            # hack/optimization: remove sidebar table about article series
            # for an example, see Barack Obama or JFK's article
            series_txt = 'This article is part of a series about'
            html_infoboxes = filter(lambda t: series_txt not in totext(t),
                                    html_infoboxes)

        if len(markup_infoboxes) != len(html_infoboxes):
            # filter out infobox-like tables that don't match the infobox markup
            # this operation is expensive. Try to find optimizations like above
            html_infoboxes = self._best_html_infoboxes(markup_infoboxes,
                                                       html_infoboxes)

        infoboxes = []
        for i, source in enumerate(markup_infoboxes):
            ibox = Infobox(self.symbol, source, html_infoboxes[i])
            infoboxes.append(ibox)

        return infoboxes, external_templates

    def _markup_infoboxes(self, source):
        infoboxes = []
        ibs = -1
        braces = 0
        rngs = []

        for m in re.finditer(InfoboxUtil.INFOBOX_REGEX, source):
            if m.group('open'):
                # If we are counting just continue, dont count outside
                # of iboxes
                if braces:
                    braces += 1
                    continue

                # If we are not counting we better start and mark our
                # position
                if m.group('ibox') and braces == 0:
                    braces = 1
                    ibs = m.start('open')

            elif m.group('close') and braces > 0:
                braces -= 1

                if braces == 0:
                    ibe = m.end('close')
                    rngs.append((ibs, ibe))

        # There may be more than one infobox
        for s, e in rngs:
            infoboxes.append(source[s:e])

        external_templates = []
        for m in re.finditer(InfoboxUtil.SPECIAL_INFOBOX_REGEX, source):
            template = m.group('template')
            if template:
                external_templates.append(template)

        return infoboxes, external_templates

    def _html_infoboxes(self, html):
        """
        A list of rendered infobox-like tables.

        We find rendered infoboxes by looking for a <table> element with
        class "infobox"

        Unfortunately, non-infobox tables such as sidebars might also match this
        criteria. Until Wikipedia uses a CSS class specifically for infoboxes
        we don't have a better way of selecting them.
        """

        bs = fromstring(html)
        return [t for t in bs.findall(".//table")
                if 'infobox' in t.get('class', '')]

    def _best_html_infoboxes(self, markup, html):
        """
        Given n markup infoboxes and n+m infobox-like html tables
        returns a list of n best candidates for html infoboxes
        """
        n = len(markup)
        m = len(html) - n
        pos = 0
        infoboxes = []

        for ibox in markup:
            choices = html[pos:pos + m]
            best_match, score = process.extractOne(totext(ibox),
                                                   choices,
                                                   processor=totext,
                                                   scorer=fuzz.token_set_ratio)

            infoboxes.append(best_match)
            pos = html.index(best_match) + 1

        return infoboxes


class MetaInfoboxBuilder(Logging):

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

    def __init__(self, infobox_type):
        prefix = "Template:"
        infobox_type = infobox_type.strip()
        if not infobox_type.startswith(prefix):
            raise ValueError("'%s' is not a valid Infobox template name. "
                             "This function expects infobox_type to have "
                             "format 'Template:Infobox <class>'."
                             % infobox_type)

        self.symbol, self.title = infobox_type, infobox_type.replace(prefix, "")

    def build(self):
        return MetaInfobox(self.symbol, self.rendered_attributes())

    def attributes(self):
        """
        A list of the markup attributes. Attributes are extracted by looking
        at template documentation subpages and pages.
        """
        # deduplicate and remove empty string
        attributes = self._best_attributes()
        attributes = [InfoboxUtil.clean_attribute(a) for a in attributes if a]
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

    def html_parsed(self):
        return InfoboxUtil.parse_infobox_html(self.html_source())

    def html_source(self):
        return get_renderer().render(self.markup_source(), key=self.title)

    def rendered_attributes(self):
        """
        A dictionary mapping unrendered markup attributes to rendered HTML
        attributes
        """
        attrs = dict()
        for k, v in self.html_parsed():
            for m in re.finditer("!!!!!([^!]+)!!!!!", v):
                attr = m.group(1).replace("_", "-").lower()
                attrs[attr] = k

        return attrs

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

        We fetch markup for infoboxes from live wikipedia.org. We do this to
        follow redirects and have up-to-date rendered attributes. Although this
        is slower than fetching from the backend, we mitigate the performance
        hit by caching all meta infoboxes. The work to build a meta infobox
        should only be done once per infobox template.
        """
        template = self.symbol

        try:
            page = get_article(self.symbol)
            template = page.title
        except LookupError:
            self.log().warn("Could not find doc any template pages for "
                            "template: \"%s\".",
                            self.symbol)
            return []

        attributes = []
        doc_page = get_article(template)
        try:
            doc_subpage = get_article(template + '/doc')

            # fetch markup from live wikipedia.org
            markup = doc_subpage.markup_source(force_live=True,
                                               expiry=Expiry.LONG)
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
        match = re.search(InfoboxUtil.TEMPLATE_DATA_REGEX, markup)
        if match:
            template_data = json.loads(match.group(1))
            for a in template_data["params"]:
                attributes.append(a)
                if "aliases" in a:
                    attributes.extend(a["aliases"])

        return attributes

    def _attributes_from_html(self, html):
        match = re.finditer(InfoboxUtil.ATTRIBUTE_REGEX, html)
        return [m.group('attr') for m in match]

# -------
# Utilities to parse and extract values from wikimarkup and article HTML
# -------


class InfoboxUtil:
    ATTRIBUTE_REGEX = re.compile(r"\|\s*(?P<attr>[a-z\-_0-9]+)\s*=",
                                 flags=re.IGNORECASE | re.DOTALL)

    ATTRIBUTE_VALUE_REGEX = re.compile(r"\|\s*(?P<attr>[a-z\-_0-9]+)\s*="
                                       "[\t ]*(?P<val>.*?)\s*(?=(\n|\\n)\s*\|)",
                                       flags=re.IGNORECASE | re.DOTALL)

    TEMPLATE_DATA_REGEX = re.compile(r"<templatedata>(.*?)</templatedata>",
                                     flags=re.M | re.S)

    # Various names under which you may find an infobox
    # TODO: include geobox
    BOX_REGEX = r"\b(infobox|Infobox|taxobox|Taxobox)\b"
    TEMPLATE_REGEX = re.compile(r'{{\s*(?P<infobox>%s\s+[\w ]*)' % BOX_REGEX)

    # Infoboxes may be defined in a separate article and included
    # using a special template
    # for an example, see WWI's "{{World War I infobox}}"
    SPECIAL_INFOBOX_REGEX = re.compile(
        r"{{\s*(?P<template>([\w ]+)[Ii]nfobox)}}")

    INFOBOX_REGEX = "((?P<open>{{)\s*(?P<ibox>%s)?|(?P<close>}}))" % BOX_REGEX

    @staticmethod
    def parse_infobox_html(html_source):
        """
        Given the infobox html, return a list of (key, value) pairs.
        """

        def escape_lists(val):
            if val is None:
                return u""

            return re.sub(
                r"<\s*(/?\s*(br\s*/?|/?ul|/?li))\s*>", "&lt;\\1&gt;", val)

        def unescape_lists(val):
            if val is None:
                return u""

            val = re.sub(r"&lt;(/?\s*(br\s*/?|ul|li))&gt;", "<\\1>", val)
            return val

        soup = fromstring(html_source)
        # Render all tags except <ul> and <li> and <br>. Escape them
        # in some way and then reparse

        tpairs = []

        for row in soup.findall('.//tr'):
            try:
                e_key, e_val = row.findall('./*')[:2]
            except ValueError:
                continue

            if e_key is not None and e_val is not None:
                # Turn the key into xml string, parse the other tags
                # making brs into newlines, parse the rest of the
                # tags, get the text back
                key = totext(fromstring(tostring(e_key), True))
                key = re.sub(r"\s+", " ", key).strip()
                val = escape_lists(tostring(e_val))
                # Extract text
                val = fromstring(val)
                val = totext(val)
                val = unescape_lists(val.strip())
                tpairs.append((key, val))

        return tpairs

    @staticmethod
    def clean_attribute(attr):
        """
        Remove numeric suffixes from attributes
        """
        attr = attr.strip()
        while attr[-1].isdigit():
            attr = attr[:-1]
        return attr

    @staticmethod
    def to_class(template):
        # TODO: add more boxes

        if "infobox" in template.lower():
            return "wikipedia-" + template.strip().lower().replace(" ", "-")\
                .replace("_", "-").replace("template:infobox-", "")

        elif "taxobox" in template.lower():
            return "wikipedia-taxobox"


# -------
# Caching
# -------

# Infobox objects are cached in memory
# The cache size was determined from a typical WikipediaBase workload where
# START calls get-classes and get-attributes for many symbols, and get only
# for the few symbols that contain the matching classes and attributes
_INFOBOX_CACHE = LRUCache(20)

# MetaInfobox objects are cached in memory forever
# There are about 3200 infoboxes, so these should easily fit in memory
# Switch to util.LRUCache if memory usage becomes a problem
_META_INFOBOX_CACHE = {}


def get_infoboxes(symbol, cls=None):
    try:
        infoboxes = _INFOBOX_CACHE.get(symbol)
    except KeyError:
        infoboxes = InfoboxBuilder(symbol).build()
        _INFOBOX_CACHE.set(symbol, infoboxes)

    if cls:
        return filter(lambda i: i.wikipedia_class == cls.lower(), infoboxes)
    return infoboxes


def get_meta_infobox(symbol):
    """
    Get an infobox that only has keys and not values. A quick and
    dirty way avoid parsing the values of an infobox.
    """
    try:
        ibx = _META_INFOBOX_CACHE[symbol]
        return ibx
    except KeyError:
        ibx = MetaInfoboxBuilder(symbol).build()
        _META_INFOBOX_CACHE[symbol] = ibx
        return ibx
