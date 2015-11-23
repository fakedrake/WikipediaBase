import re
import lxml.etree as ET

from wikipediabase.util import (totext,
                                tostring,
                                fromstring,
                                get_meta_infobox,
                                get_article)

from wikipediabase.caching import cached, Caching
from wikipediabase.config import Configurable, configuration


INFOBOX_ATTRIBUTE_REGEX = r"\|\s*(?P<key>[a-z\-_0-9]+)\s*=" \
                                                            "[\t ]*(?P<val>.*?)\s*(?=(\n|\\n)\s*\|)"


class Infobox(Caching):

    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    # Various names under which you may find an infobox
    box_rx = ur"\b(infobox|Infobox|taxobox|Taxobox)\b"


    def __init__(self, symbol, configuration=configuration):
        """
        It is a good idea to provide a fetcher as caching will be done
        much better.
        """
        super(Infobox, self).__init__(configuration=configuration)

        self.configuration = configuration
        self.symbol_string = configuration.ref.strings.symbol_string_class
        self.xml_string = configuration.ref.strings.xml_string_class

        self.fetcher = configuration.ref.fetcher.with_args(
            configuration=configuration)
        self.infobox_types = configuration.ref.infobox_types.with_args(
            configuration=configuration)

        self.symbol = self.symbol_string(symbol)
        self._html = None


    def title(self):
        return self.symbol.literal()

    def __nonzero__(self):
        return bool(self.fetcher.download(self.symbol.url_friendly()))

    @staticmethod
    def __tt(tmpl):
        return "wikipedia-" + \
            tmpl.lower().replace(
                " ", "-").replace("_", "-").replace("template:infobox-", "")

    def types(self, extend=True):
        """
        The infobox type. Extend means search in other places except here
        (ie find equivalent ones, parent ones etc).
        """

        types = []
        ibox_source = self.markup_source()
        if ibox_source:
            # XXX: includ taxoboes
            for m in re.finditer(r'{{\s*(?P<type>%s\s+[\w ]*)' % self.box_rx,
                                 ibox_source):
                # The direct ibox
                dominant = "Template:" + m.group('type')
                types.append(dominant)

                if extend:
                    title = get_article(dominant,
                                        configuration=self.configuration).title()

                    if self.__tt(dominant) != self.__tt(title):
                        types.append(title)

        return types

    def get(self, key, source=None):
        """
        - First try plain markup keys
        - Then translating each markup's tanslations
        """

        # Look into html first. The results here are much more
        # readable.
        html_key = key.lower().replace(u"-", u" ")
        markup_key = key.lower().replace(u"-", u"_")
        rendered_key = self.rendered_keys().get(markup_key)

        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k.text().lower().replace(u".", u"") == html_key or \
                   k == rendered_key:
                    return v.text()

        # Then look into the markup
        for k, v in self.markup_parsed_iter():
            if k.replace("-", "_") == markup_key:
                return v

    def rendered_keys(self):
        # Populate the rendered keys dict
        if hasattr(self, '_rendered_keys'):
            return self._rendered_keys

        self._rendered_keys = dict()
        for infobox_type in reversed(self.types()):
            ibx = get_meta_infobox(infobox_type, configuration=self.configuration)
            self._rendered_keys.update(ibx.rendered_keys())

        return self._rendered_keys

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

    def markup_source(self):
        """
        Get the markup source of this infobox.
        """

        txt = self.fetcher.source(self.symbol).raw()
        return self._braces_markup(txt)

    @cached('_html')
    def html_source(self):
        """
        A div with all the infoboxes in it.
        """

        html = self.fetcher.download(self.symbol.url_friendly())
        bs = self.xml_string(html)
        return self.xml_string(
            '\n'.join([t.raw() for t in bs.xpath(".//table")
                       if 'infobox' in t.get('class', '')]))


    def rendered(self):
        return self.html_source().text()

    def html_parsed(self):
        """
        Given the infobox html or as soup, return a list of (key, value)
        pairs.
        """

        ignore_tags = ['br', 'ul', 'li']
        soup = self.html_source()

        # Render all tags except <ul> and <li> and <br>. Escape them
        # in some way and then reparse
        for row in soup.xpath('.//tr'):
            try:
                key, val = list(row.ignoring(ignore_tags).xpath('./*'))[:2]

            except ValueError:
                continue

            yield key, val


    def _braces_markup(self, txt):
        """
        Using the braces make a concatenation of all infoboxes.
        """

        ret = ""
        ibs = -1
        braces = 0
        rngs = []
        token_regex = "((?P<open>{{)\s*(?P<ibox>%s)?|(?P<close>}}))" % self.box_rx

        for m in re.finditer(token_regex, txt):
            if m.group('open'):
                # If we are counting just continue, dont count outside
                # of iboxes
                if braces:
                    braces += 1
                    continue

            if m.group('ibox') and braces == 0:
                # If we are not counting we better start and mark our
                # position
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
