from collections import OrderedDict
from os.path import commonprefix
import copy
import json
import re

from fuzzywuzzy import fuzz, process
import mwparserfromhell

from wikipediabase.article import get_article
from wikipediabase.fetcher import get_fetcher
from wikipediabase.log import Logging
from wikipediabase.renderer import get_renderer
from wikipediabase.util import Expiry, LRUCache, fromstring, \
    n_copies_without_children, tostring, totext


class Infobox(Logging):

    def __init__(self, symbol, template, cls, markup):
        self.symbol = symbol
        self.template = template
        self.cls = cls
        self.markup = mwparserfromhell.parse(markup)

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
        raise NotImplemented('get should only be called on a RenderedInfobox')

    def get_from_markup(self, attr):
        attr = attr.lower()
        for k, v in self._markup_items():
            if k == attr:
                return v

    def _markup_items(self):
        """
        Markup parsed as a list of (key, val)
        """

        items = []
        templates = self.markup.filter_templates(recursive=True)

        if not templates:
            return items

        infobox = templates[0]
        for item in infobox.params:
            # only include items with a named attribute
            if item.showkey:
                attr = item.name.strip().replace("_", "-")\
                    .replace(" ", "-").lower()

                if attr == 'module':
                    # infoboxes can include a module. More info:
                    # wikipedia.org/wiki/Wikipedia:WikiProject_Infoboxes/embed
                    module_templates = item.value.filter_templates()
                    if not module_templates:
                        continue

                    module = module_templates[0]
                    for module_item in module.params:
                        if module_item.showkey:
                            attr = module_item.name.strip().replace("_", "-")\
                                .replace(" ", "-").lower()

                            if attr == 'embed':
                                # skip the 'embed' attribute of modules
                                continue

                            val = module_item.value.strip()
                            items.append((attr, val))
                else:
                    val = item.value.strip()
                    items.append((attr, val))
        return items


class RenderedInfobox(Infobox):

    def __init__(self, symbol, template, cls, markup, html):
        super(RenderedInfobox, self).__init__(symbol, template, cls, markup)
        self.html = html

    def get(self, attr, source=None):
        """
        - First try plain markup attributes
        - Then translating each markup's translations
        """

        # Look into html first. The results here are much more readable
        markup_attr = attr.lower()
        html_attr = attr.lower().replace(u"-", u" ")
        rendered_attr = self.attributes.get(markup_attr)

        if source is None or source == 'html':
            for k, v in self._html_items():
                if k.lower().replace(u".", u"") == html_attr or \
                   k == rendered_attr:
                    return v

        return self.get_from_markup(markup_attr)

    def _html_items(self):
        """
        HTML parsed as a list of (key, val)
        """
        return InfoboxUtil.parse_infobox_html(self.html)


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
        infoboxes, external = self._markup_infoboxes_from_article(markup)

        for template in external:
            title = 'Template:%s' % template.strip()
            try:
                m = fetcher.markup_source(title, expiry=expiry)

                # we only follow external infobox templates once, instead of
                # looping until we can't find additional external templates.
                # it seems dangerous to keep following template links. It's
                # possible to get stuck in a long redirect loop
                external_infoboxes, _ = self._markup_infoboxes_from_article(m)
                infoboxes.extend(external_infoboxes)
            except LookupError:
                self.log().warn("Could not find external infobox template '%s'",
                                title)

        return infoboxes

    def _markup_infoboxes_from_article(self, markup, title=None):
        """
        Gets a list of Infobox objects and external templates
        """
        markup_infoboxes, external_templates = self._markup_infoboxes(markup)
        infoboxes = []
        for i, t in enumerate(markup_infoboxes):
            ibox = Infobox(self.symbol, t['template'], t['cls'], t['markup'])
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
            markup = source[s:e]
            template = self._find_template(markup)
            cls = InfoboxUtil.to_class(template)
            infoboxes.append({'markup': markup, 'template': template,
                              'cls': cls})

        # note that by extracting markup infoboxes separately from external
        # infoboxes, we're not preserving the ordering of the infoboxes
        # in the article

        # this may mess up the RenderedInfoboxBuilder:
        # let m_i = markup infobox in position i in the article
        # let e_i = external infobox in position i in the article
        # if an article has [m_1, e_2, m_3] ==> [m_1, m_3], [e_2]

        # but we haven't found an example of an article that contains both
        # markup and external infoboxes
        external_templates = []
        for m in re.finditer(InfoboxUtil.EXTERNAL_INFOBOX_REGEX, source):
            template = m.group('template')
            if template:
                external_templates.append(template)

        return infoboxes, external_templates

    def _find_template(self, markup):
        for m in re.finditer(InfoboxUtil.TEMPLATE_REGEX, markup):
            template = "Template:" + m.group('infobox').strip()
            return template


class RenderedInfoboxBuilder(InfoboxBuilder):

    """
    RenderedInfoboxBuilder scrapes the HTML of an article to build a list
    of rendered infoboxes
    """

    def __init__(self, symbol, infoboxes):
        self.symbol = symbol
        self.infoboxes = copy.deepcopy(infoboxes)

    def build(self, expiry=Expiry.DEFAULT):
        """
        Returns a list of RenderedInfobox objects constructed from the article
        """

        fetcher = get_fetcher()
        html = fetcher.html_source(self.symbol, expiry=expiry)
        rendered_infoboxes = self._html_infoboxes_from_article(html)
        return rendered_infoboxes

    def _html_infoboxes_from_article(self, html):
        """
        Gets a list of RenderedInfobox objects
        """
        html_infoboxes = self._html_infoboxes(html)

        if len(self.infoboxes) != len(html_infoboxes):
            # article contains non-infobox tables such as sidebars
            html_infoboxes = self._filter_html_infoboxes(html_infoboxes)

        if len(self.infoboxes) > len(html_infoboxes):
            # article contains infobox sub-templates
            # e.g. 'Infobox animanga/Video' and 'Infobox animanga/Header'
            html_infoboxes = self._handle_infobox_sub_templates(self.infoboxes,
                                                                html_infoboxes)

        if len(self.infoboxes) != len(html_infoboxes):
            # filter out infobox-like tables that don't match the infobox markup
            # this operation is expensive. It's better if non-infobox tables
            # are filtered out in _filter_html_infoboxes()
            html_infoboxes = self._best_html_infoboxes(self.infoboxes,
                                                       html_infoboxes)

        rendered_infoboxes = []
        for i, ibox in enumerate(self.infoboxes):
            rendered_ibox = RenderedInfobox(ibox.symbol, ibox.template,
                                            ibox.cls, ibox.markup,
                                            html_infoboxes[i])
            rendered_infoboxes.append(rendered_ibox)

        return rendered_infoboxes

    def _handle_infobox_sub_templates(self, markup_infoboxes, html_infoboxes):
        groups = self._group_infobox_sub_templates(markup_infoboxes)
        assert(len(groups) <= len(html_infoboxes))  # TODO: remove for production

        i = 0
        split_html_infoboxes = []

        for group, infoboxes in groups.items():
            html = html_infoboxes[i]
            size = len(infoboxes)
            if size == 1:
                split_html_infoboxes.append(html)
            else:
                try:
                    split_html = self._split_html_infobox(html, size)
                    split_html_infoboxes.extend(split_html)
                except ValueError as e:
                    self.log().exception(e)
                    # if we're unable to split the HTML, we just copy the whole
                    # HTML infobox for each sub-template
                    copies = [copy.deepcopy(html) for k in xrange(size)]
                    split_html_infoboxes.extend(copies)
            i += 1

        # there may be additional infoboxes
        # this happens when non-infobox tables were not successfully filtered
        split_html_infoboxes.extend(html_infoboxes[i:])
        return split_html_infoboxes

    def _group_infobox_sub_templates(self, markup_infoboxes):
        """
        Group together markup sub-templates with a common prefix

        These templates may render into one single HTML infobox
          e.g. 'Infobox animanga/Header' and 'Infobox animanga/Print'
          e.g. 'Infobox ship career' and 'Infobox ship characteristics'

        Order matters: we can use the fact that sub-templates are included
        sequentially so they render into one HTML template

        Given:
            'Infobox officeholder'
            'Infobox martial artist'
            'Infobox ship begin'
            'Infobox ship career'
            'Infobox ship characteristics'

        The output should be:
        {
            'Infobox officeholder': ['Infobox officeholder'],
            'Infobox martial artist': ['Infobox martial artist'],
            'Infobox ship': [
                'Infobox ship begin',
                'Infobox ship career',
                'Infobox ship characteristics',
            ]
        }
        """
        groups = OrderedDict()
        last_group = None
        last_ibox = None

        for ibox in markup_infoboxes:
            template = ibox.template
            if last_ibox is None:
                last_ibox = ibox
                continue

            if last_group:
                if template.startswith(last_group):
                    groups[last_group].append(ibox)
                else:
                    last_group = None
                    groups[template] = [ibox]
            else:
                last_two = [last_ibox.template, template]
                prefix = commonprefix(last_two)
                if len(prefix) > len("Template:Infobox "):
                    # remove the trailing character to find the group name
                    # e.g. 'Infobox animanga/Header', 'Infobox animanga/Print'
                    # e.g. 'Infobox ship career', 'Infobox ship characteristics'
                    if prefix.endswith('/'):
                        prefix = prefix[:-1]

                    last_group = prefix.strip()
                    groups[last_group] = [last_ibox, ibox]
                else:
                    groups[last_ibox.template] = [last_ibox]

            last_ibox = ibox

        if last_group is None:
            groups[last_ibox.template] = [last_ibox]

        return groups

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
        return bs.cssselect('table.infobox')

    def _filter_html_infoboxes(self, html_infoboxes):
        """
        Filter out non-infobox tables such as sidebars
        """

        # hack/optimization: remove sidebar table about article series
        # for an example, see Barack Obama or JFK's article
        series_txt = 'This article is part of a series about'
        return filter(lambda t: series_txt not in totext(t), html_infoboxes)

    def _split_html_infobox(self, html, n):
        """
        Split an HTML infobox into n partitions, where partitions are
        <th> or <td> tags with a background

        Multiple markup infobox sub-templates may render into one HTML infobox.
        Two infobox sub-templates may have the same attribute with different
        values. To prevent clases, we need to split the HTML infobox into n
        logical partitions.

        Each partition usually starts with a light purple header
        See https://en.wikipedia.org/wiki/IS_(manga) for an example

        :param html is an lxml HtmLElement representing an infobox (<table>)
        """

        # select all <tr> elements that have a <td> or <th> child with
        # 'background' in @style
        xpath = "tr[(td|th)[contains(@style, 'background')]]"
        headers = html.xpath(xpath)

        # we should find at least n logical headers
        if len(headers) < n:
            raise ValueError('Failed to find %d logical partitions; '
                             'only found %d' % (n, len(headers)))

        partitions = n_copies_without_children(html, n)

        pointer = 0

        for i, e in enumerate(html.iterchildren()):
            if pointer + 1 < n and e == headers[pointer + 1]:
                pointer += 1
            partitions[pointer].append(e)

        return partitions

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
            best_match, score = process.extractOne(ibox.markup,
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

    def group_attributes(self, attributes, prefix_length=3):
        """
        Group attributes into lists with non-overlapping prefixes. Returns
        a list of lists

        Wikipedia deduplicates synonymous attributes before rendering an
        infobox. If both SUCCESSOR and SUCCEEDING are in infobox president,
        only one gets rendered.

        The algorithm tries to balance the length of groups by inserting
        an attribute into the smallest group with non-overlapping prefixes.
        This hopes to reduce the chance of two synonymous attributes with
        different prefixes ending up in the same group.
        """
        def make_group():
            return {'prefixes': set(), 'attributes': []}

        groups = [make_group()]
        attributes = sorted(attributes)

        for attr in attributes:
            prefix = attr[:prefix_length]
            candidates = filter(lambda group: prefix not in group['prefixes'],
                                groups)
            if candidates:
                smallest_group = reduce(lambda x, y: x if len(x) < len(y) else y,
                                        candidates)
                smallest_group['prefixes'].add(prefix)
                smallest_group['attributes'].append(attr)
            else:
                groups.append(make_group())
                groups[-1]['prefixes'].add(prefix)
                groups[-1]['attributes'].append(attr)

        return [group['attributes'] for group in groups]

    def markup_source(self):
        """
        Markup of the meta infobox. Each attribute has a value that
        contains all possible attributes for this type of infobox.
        """

        markup = ''

        attributes = self.attributes()
        for group in self.group_attributes(attributes):
            markup += '{{' + self.symbol.replace("Template:", "") + "\n" + \
                '\n'.join(["| %s = !!!!!%s!!!!!" % (attr, attr) for
                           attr in group]) + \
                "\n}}\n"

        return markup

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
                attr = m.group(1).replace("_", "-").replace(' ', '-').lower()
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

        try:
            html = doc_page.html_source(expiry=Expiry.LONG)
            attributes.extend(self._attributes_from_html(html))
        except LookupError:
            self.log().warn("Could not find doc page for template: \"%s\".",
                            template)

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

    TEMPLATE_DATA_REGEX = re.compile(r"<templatedata>(.*?)</templatedata>",
                                     flags=re.M | re.S)

    # Various names under which you may find an infobox
    # TODO: include geobox
    BOX_REGEX = r"\b([iI]nfobox|[tT]axobox)\b"

    # matches infobox templates like 'Infobox animanga' and sub-templates like
    # 'Infobox animanga/Video'
    TEMPLATE_REGEX = re.compile(r'{{\s*(?P<infobox>%s[\w\/\s]*)' % BOX_REGEX)

    # Infoboxes may be defined in a separate article and included
    # using an external template
    # for an example, see WWI's "{{World War I infobox}}"
    EXTERNAL_INFOBOX_REGEX = re.compile(
        r"{{\s*(?P<template>([\w ]+)[Ii]nfobox)}}")

    INFOBOX_REGEX = "((?P<open>{{)\s*(?P<ibox>%s)?|(?P<close>}}))" % BOX_REGEX

    @staticmethod
    def parse_infobox_html(html_source):
        """
        Given the infobox html, return a list of (key, value) pairs.

        Values may contain html that makes sense only in the context
        of the infobox: inner <td> tags, <span> without the
        corresponding css, and unqualified links. This list may or may
        not be comprehensive, so it is safer to only allow text
        formatting tags, lists, and line breaks and throw away
        everything else.
        """

        ignoring_tags = ['ul', 'li', 'b', 'em', 'i', 'small', 'strong',
                         'sub', 'sup', 'ins', 'del', 'mark',]
        def escape_lists(val):
            if val is None:
                return u""

            regex = r"<\s*(/?\s*(br\s*/?|/?%s))\s*>" % \
                    r"|/?".join(ignoring_tags)

            return re.sub(regex , "&lt;\\1&gt;", val)

        def unescape_lists(val):
            if val is None:
                return u""

            val = re.sub(r"&lt;(/?\s*(br\s*/?|%s))&gt;" % \
                         r"|".join(ignoring_tags), "<\\1>", val)
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
                key = totext(fromstring(tostring(e_key), literal_newlines=True))

                # replace multiple spaces (including nbsp) with a single space
                key = re.sub(r"\s+", u" ", key, flags=re.U).strip()

                val = escape_lists(tostring(e_val))
                # Extract text
                val = fromstring(val)
                val = totext(val)

                # replace nbsp (unicode code 160) with space
                val = val.replace(unichr(160), u' ')

                val = unescape_lists(val.strip())
                tpairs.append((key, val))

        return tpairs

    @staticmethod
    def clean_attribute(attr):
        """
        Remove numeric suffixes from attributes
        """
        attr = attr.strip()
        while attr and attr[-1].isdigit():
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

# Infobox and RenderedInfobox objects are cached in memory
# The cache size was determined from a typical WikipediaBase workload where
# START calls get-classes and get-attributes for many symbols, and get only
# for the few symbols that contain the matching classes and attributes
_INFOBOX_CACHE = LRUCache(100)
_RENDERED_INFOBOX_CACHE = LRUCache(100)

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
        return filter(lambda i: i.cls == cls.lower(), infoboxes)
    return infoboxes


def get_rendered_infoboxes(symbol, cls=None):
    try:
        rendered_infoboxes = _RENDERED_INFOBOX_CACHE.get(symbol)
    except KeyError:
        infoboxes = get_infoboxes(symbol)
        rendered_infoboxes = RenderedInfoboxBuilder(symbol, infoboxes).build()
        _RENDERED_INFOBOX_CACHE.set(symbol, rendered_infoboxes)

    if cls:
        return filter(lambda i: i.cls == cls.lower(), rendered_infoboxes)
    return rendered_infoboxes


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
