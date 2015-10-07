import re

from fuzzywuzzy import fuzz, process

from wikipediabase.util import (Expiry,
                                fromstring,
                                get_meta_infobox,
                                get_article,
                                totext,
                                tostring)
from wikipediabase.log import Logging
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.infobox_tree import ibx_type_superclasses

ATTRIBUTE_REGEX = r"\|\s*(?P<key>[a-z\-_0-9]+)\s*=" \
    "[\t ]*(?P<val>.*?)\s*(?=(\n|\\n)\s*\|)"

# Various names under which you may find an infobox
# TODO: include geobox
BOX_REGEX = r"\b(infobox|Infobox|taxobox|Taxobox)\b"

# Infoboxes may be defined in a separate article and included
# using a special template
# for an example, see WWI's "{{World War I infobox}}"
SPECIAL_INFOBOX_REGEX = r"{{\s*(?P<template>([\w ]+)[Ii]nfobox)}}"


class Infobox(Logging):

    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    def __init__(self, symbol, markup_source, html_source, fetcher=None,
                 title=None):
        self.symbol = self.title = symbol
        if title is not None:
            self.title = title
        self._markup = markup_source
        self._html = html_source
        self.fetcher = fetcher or WIKIBASE_FETCHER

    def __nonzero__(self):
        return bool(self._html)

    def template(self):
        ibox_source = self.markup_source()
        if ibox_source:
            template_regex = r'{{\s*(?P<infobox>%s\s+[\w ]*)' % BOX_REGEX
            for m in re.finditer(template_regex, ibox_source):
                template = "Template:" + m.group('infobox').strip()
                return template
        return None

    def wikipedia_class(self):
        return self._to_class(self.template())

    def types(self):
        """
        The infobox type. Extend means search in other places except here
        (ie find equivalent ones, parent ones etc).
        """
        if not hasattr(self, "_sc"):
            self._sc = ibx_type_superclasses()

        template = self.template()
        types = filter(lambda t: t is not None, [self._to_type(template)])

        t = self._to_type(template)
        title = get_article(template, self.fetcher).title()
        if t != self._to_type(title):
            types.append(self._to_type(title))

        if t in self._sc:
            types.extend(self._sc[t])

        return types

    def get(self, attr, source=None):
        """
        - First try plain markup attributes
        - Then translating each markup's translations
        """

        # Look into html first. The results here are much more readable
        html_attr = attr.lower().replace(u"-", u" ")
        markup_attr = attr.lower().replace(u"-", u"_")
        rendered_attr = self.rendered_attributes().get(markup_attr)

        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k.lower().replace(u".", u"") == html_attr or \
                   k == rendered_attr:
                    return v

        # Then look into the markup
        for k, v in self.markup_parsed_iter():
            if k.replace("-", "_") == markup_attr:
                return v

    def rendered_attributes(self):
        # Populate the rendered attributes dict
        if hasattr(self, '_rendered_attributes'):
            return self._rendered_attributes

        self._rendered_attributes = dict()
        ibx = get_meta_infobox(self.template())
        self._rendered_attributes.update(ibx.rendered_attributes())

        return self._rendered_attributes

    @staticmethod
    def _to_class(template):
        # TODO: add more boxes

        if "infobox" in template.lower():
            return "wikipedia-" + \
                template.strip().lower().replace(
                    " ", "-").replace("_", "-").replace("template:infobox-", "")

        elif "taxobox" in template.lower():
            return "wikipedia-taxobox"

    @staticmethod
    def _to_type(template):
        if "infobox" in template.lower():
            return template.replace("_", " ")[len("template:infobox "):]

    def markup_parsed_iter(self):
        """
        Generate the pairs from markup
        """

        mu = self.markup_source()
        for m in re.finditer(ATTRIBUTE_REGEX, mu,
                             flags=re.IGNORECASE | re.DOTALL):
            key = m.group("key").replace("_", "-").lower()
            val = m.group("val")

            yield key, val

    def markup_parsed(self):
        """
        Markup parsed as a list of (key, val)
        """

        return list(self.markup_parsed_iter())

    def markup_source(self):
        """
        Get the markup source of this infobox.
        """

        return self._markup

    def html_source(self, expiry=Expiry.DEFAULT):
        """
        A rendered infobox as a <table>
        """
        return self._html

    def rendered(self):
        return totext(self.html_source())

    def html_parsed(self):
        """
        Given the infobox html or as soup, return a list of (key, value)
        pairs.
        """

        def escape_lists(val):
            if not val:
                return u""

            return re.sub(
                r"<\s*(/?\s*(br\s*/?|/?ul|/?li))\s*>", "&lt;\\1&gt;", val)

        def unescape_lists(val):
            if not val:
                return u""

            val = re.sub(r"&lt;(/?\s*(br\s*/?|ul|li))&gt;", "<\\1>", val)
            return val

        soup = fromstring(self.html_source())
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


class InfoboxScraper(Logging):

    """
    InfoboxScraper scrapes markup and HTML of an article to produce a list
    of infoboxes
    """

    def __init__(self, symbol, title=None, fetcher=None):
        self.symbol = self.title = symbol
        if title is not None:
            self.title = title

        self.fetcher = fetcher or WIKIBASE_FETCHER

    def infoboxes(self, expiry=Expiry.DEFAULT):
        """
        Returns a list of Infobox objects constructed from the article
        """

        markup_source = self.fetcher.markup_source(self.symbol, expiry=expiry)
        html_source = self.fetcher.html_source(self.symbol, expiry=expiry)

        infoboxes, external_templates = self._infoboxes_from_article(markup_source, html_source)
        for t in external_templates:
            title = 'Template:%s' % t.strip()
            try:
                m = self.fetcher.markup_source(title, expiry=expiry)
                h = self.fetcher.html_source(title, expiry=expiry)

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

    def _infoboxes_from_article(self, markup_source, html_source):
        markup_infoboxes, external_templates = self._markup_infoboxes(markup_source)
        html_infoboxes = self._html_infoboxes(html_source)

        assert(len(markup_infoboxes) <= len(html_infoboxes))  # TODO: remove for production

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
            ibox = Infobox(self.symbol, source, html_infoboxes[i],
                           title=self.title)
            infoboxes.append(ibox)

        return infoboxes, external_templates

    def _markup_infoboxes(self, source):
        infoboxes = []
        ibs = -1
        braces = 0
        rngs = []

        for m in re.finditer(
                "((?P<open>{{)\s*(?P<ibox>%s)?|(?P<close>}}))" % BOX_REGEX,
                source):

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
        for m in re.finditer(SPECIAL_INFOBOX_REGEX, source):
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
