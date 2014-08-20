import string
import re
import lxml.etree as ET
from collections import defaultdict

from .util import totext, tostring, fromstring
from .log import Logging
from .article import Article
from .fetcher import WIKIBASE_FETCHER
from .infobox_tree import ibx_type_superclasses

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=(\n|\\n)\s*\|)"


class Infobox(Logging):

    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    def __init__(self, title, fetcher=WIKIBASE_FETCHER):
        """
        It is a good idea to provide a fetcher as caching will be done
        much better.
        """

        self.title = title
        self.fetcher = fetcher
        self._rendered_keys = dict()

    def __nonzero__(self):
        return bool(self.fetcher.download(self.title))

    @staticmethod
    def __tt(tmpl):
        return "wikipedia-" + \
            tmpl.lower().replace(
                " ", "-").replace("_", "-").replace("template:infobox-", "")

    def types(self, extend=True):
        """
        The infobox type. Extend means search inn other places except here
        (ie find equivalent ones, parent ones etc)
        to_start will make the types into start classes.
        """

        types = []
        ibox_source = self.markup_source()
        if ibox_source:
            # XXX: includ taxoboes
            for m in re.finditer(r'{{\s*(?P<type>[Ii]nfobox\s+[\w ]*)',
                                 ibox_source):
                # The direct ibox
                dominant = "Template:" + m.group('type')
                types.append(dominant)

                if extend:
                    title = Article(dominant,
                                    self.fetcher).title()
                    if self.__tt(dominant) != self.__tt(title):
                        types.append(title)

        return types

    def start_types(self):
        types = self.types(extend=True)
        ret = types[:]

        if not hasattr(self, "_sc"):
            self._sc = ibx_type_superclasses()

        for t in types:
            try:
                # In case of redirections this may fail
                ret.extend(self._sc[t.replace("Template:Infobox ", "")])
            except KeyError:
                pass

        return map(self.__tt, ret)

    def get(self, key, source=None):
        """
        Get a specific infobox field. SOURCE tells us where to look. If it
        is None try 'markup', then 'html'.
        """

        # Look into html first. The results here are much more
        # readable.
        html_key = key.lower().replace(u"-", u" ")
        markup_key = key.lower().replace(u"-", u"_")
        rendered_key = self.rendered_key(markup_key)

        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k.lower().replace(u".", u"") == html_key or \
                   k == rendered_key:
                    return v

        # Then look into the markup
        markup_key = key.lower().replace(u"-", u"_")
        ret = u"\n".join([v for k, v in self.markup_parsed_iter()
                          if re.sub(ur"[0-9]+$", "",
                                    k.replace("-", "_"),) == markup_key])

        return ret or None

    def rendered_key(self, mkey):
        """
        Get the corresponding rendered key to the markup key if you can.
        """

        mkey = mkey.lower().replace("-", "_")
        ret = self._rendered_keys.get(mkey, False)
        if ret is not False:
            return ret

        for t in self.types(extend=False):
            tibox = Infobox(t)
            for k, v in tibox.html_parsed():
                if v == '{{{%s}}}' % mkey or v == mkey + " text":
                    self._rendered_keys[mkey] = k
                    return k

        self._rendered_keys[mkey] = None

    def markup_parsed_iter(self):
        """
        Generate the pairs from markup
        """

        mu = self.markup_source()
        for m in re.finditer(INFOBOX_ATTRIBUTE_REGEX % "(?P<key>[a-z\-_]*)", mu,
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

        txt = self.fetcher.source(self.title)
        return self._braces_markup(txt)

    def html_source(self):
        """
        A div with all the infoboxes in it.
        """

        html = self.fetcher.download(self.title)
        bs = fromstring(html)
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
                return ""

            return re.sub(r"<\s*(/?\s*(br\s*/?|/?ul|/?li))\s*>", "&lt;\\1&gt;", val)

        def unescape_lists(val):
            if not val:
                return ""

            return re.sub(r"&lt;(/?\s*(br\s*/?|ul|li))&gt;", "<\\1>", val)

        soup = self.html_source()
        # Render all tags except <ul> and <li>. Escape them in some way and
        # then reparse

        tpairs = []

        for row in soup.findall('.//tr'):
            e_key = row.find('.//th')
            e_val = row.find('.//td')

            if e_key is not None and e_val is not None:
                key = totext(e_key).strip()
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

        for m in re.finditer("((?P<open>{{)\s*(?P<ibox>\w*)|(?P<close>}}))", txt):

            if m.group('open'):
                # If we are counting just continue
                if braces:
                    braces += 1
                    continue

                # If we are not counting we better start and mark our
                # position
                if m.group('ibox') in ["infobox", "Infobox"]:
                    braces = 1
                    ibs = m.start('open')

            elif m.group('close') and braces > 0:
                braces -= 1

                if braces == 0:
                    ibe = m.end('close')
                    rngs.append((ibs, ibe))

        # There may be more than one infoboxes, concaenate them.
        for s, e in rngs:
            ret += txt[s:e]

        return ret
