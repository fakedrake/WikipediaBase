import re
import lxml.etree as ET

from wikipediabase.util import (Expiry,
                                totext,
                                tostring,
                                fromstring,
                                get_meta_infobox,
                                get_article)
from wikipediabase.log import Logging
from wikipediabase.fetcher import WIKIBASE_FETCHER
from wikipediabase.infobox_tree import ibx_type_superclasses

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*(?P<key>[a-z\-_0-9]+)\s*=" \
                          "[\t ]*(?P<val>.*?)\s*(?=(\n|\\n)\s*\|)"


class Infobox(Logging):

    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    # Various names under which you may find an infobox
    box_rx = ur"\b(infobox|Infobox|taxobox|Taxobox)\b"

    def __init__(self, symbol, title=None, fetcher=None):
        """
        It is a good idea to provide a fetcher as caching will be done
        much better.
        """

        self.symbol = self.title = symbol
        if title is not None:
            self.title = title

        self.fetcher = fetcher or WIKIBASE_FETCHER

    def __nonzero__(self):
        return bool(self.fetcher.html_source(self.symbol))

    @staticmethod
    def _to_class(template):
        return "wikipedia-" + \
            template.lower().replace(
                " ", "-").replace("_", "-").replace("template:infobox-", "")

    @staticmethod
    def _to_type(template):
        return template.replace("_", " ")[len("template:infobox "):]

    def templates(self):
        templates = []
        ibox_source = self.markup_source()
        if ibox_source:
            # XXX: includ taxoboes
            for m in re.finditer(r'{{\s*(?P<infobox>%s\s+[\w ]*)' % self.box_rx,
                                 ibox_source):
                # The direct ibox
                template = "Template:" + m.group('infobox')
                templates.append(template)
        return templates

    def classes(self):
        return map(self._to_class, self.templates())

    def types(self, extend=True):
        """
        The infobox type. Extend means search in other places except here
        (ie find equivalent ones, parent ones etc).
        """

        templates = self.templates()
        types = map(self._to_type, templates)
        if extend:
            if not hasattr(self, "_sc"):
                self._sc = ibx_type_superclasses()

            for template in templates:
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
        for template in reversed(self.templates()):
            ibx = get_meta_infobox(template)
            self._rendered_attributes.update(ibx.rendered_attributes())

        return self._rendered_attributes

    def markup_parsed_iter(self):
        """
        Generate the pairs from markup
        """

        mu = self.markup_source()
        for m in re.finditer(INFOBOX_ATTRIBUTE_REGEX, mu,
                             flags=re.IGNORECASE | re.DOTALL):
            key = m.group("key").replace("_", "-").lower()
            val = m.group("val")

            yield key, val

    def markup_parsed(self):
        """
        Markup parsed as a list of (key, val)
        """

        return list(self.markup_parsed_iter())

    def markup_source(self, expiry=Expiry.DEFAULT):
        """
        Get the markup source of this infobox.
        """

        txt = self.fetcher.markup_source(self.symbol, expiry=expiry)
        return self._braces_markup(txt)

    def html_source(self, expiry=Expiry.DEFAULT):
        """
        A div with all the infoboxes in it.
        """

        if not hasattr(self, '_html'):
            self._html = self.fetcher.html_source(self.symbol, expiry=expiry)

        bs = fromstring(self._html)
        ret = ET.Element('div')
        ret.extend([t for t in bs.findall(".//table")
                    if 'infobox' in t.get('class', '')])

        return ret

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

    def _braces_markup(self, txt):
        """
        Using the braces make a concatenation of all infoboxes.
        """

        ret = ""
        ibs = -1
        braces = 0
        rngs = []

        for m in re.finditer(
                "((?P<open>{{)\s*(?P<ibox>%s)?|(?P<close>}}))" % self.box_rx,
                txt):

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
                    self.type = m.group('ibox')

            elif m.group('close') and braces > 0:
                braces -= 1

                if braces == 0:
                    ibe = m.end('close')
                    rngs.append((ibs, ibe))

        # There may be more than one infoboxes, concaenate them.
        for s, e in rngs:
            ret += txt[s:e]

        return ret
