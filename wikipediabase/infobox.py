import re
import bs4

from log import Logging
from article import Article

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=\n\s*\|)"


class Infobox(Logging):
    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    def __init__(self, title, fetcher):
        self.title = title
        self.fetcher = fetcher

    def __nonzero__(self):
        return bool(self.fetcher.download(self.title))

    def _to_start_type(self, ibx):
        """
        Turn an infobox into a strart type.
        """

        ret = ibx.lower().replace("template:", "")
        return ret.replace(" ","-").replace("infobox", "wikipedia")

    def types(self):
        """
        The infobox type.
        """

        ret = set()
        ibox_source = self.markup_source()
        if ibox_source:
            for m in re.finditer(r'{{\s*(?P<type>Infobox\s+[\w ]*)',
                                    ibox_source):
                # The direct ibox
                primary = m.group('type')
                ret.add(self._to_start_type(primary))

                # The ibox redirect
                title = Article("Template:"+primary, self.fetcher).title()
                ret.add(self._to_start_type(title))

        return ret


    def get(self, key, source=None):
        """
        Get a specific infobox field. SOURCE tells us where to look. If it
        is None try 'markup', then 'html'.
        """

        key = key.lower().replace("-", "_")

        # Look into html first. The results here are much more
        # readable.
        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k == key:
                    return v

        # Then look into the markup
        for k, v in self.markup_parsed_iter():
            if k == key:
                return v


    def markup_parsed_iter(self):
        """
        Generate the pairs from markup
        """

        mu = self.markup_source()
        for m in re.finditer(INFOBOX_ATTRIBUTE_REGEX % "(?P<key>[a-z\-_]*)", mu,
                             flags=re.IGNORECASE|re.DOTALL):
            key = m.group("key").replace("-", "_").lower()
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
        Get the infobox source as a soup.
        """

        html = self.fetcher.download(self.title)
        ret = bs4.BeautifulSoup()
        bs = bs4.BeautifulSoup(html)

        for i in bs.select('table.infobox'):
            ret.append(i)

        return ret

    def rendered(self):
        return self.html_source().text


    def html_parsed(self):
        """
        Given the infobox html or as soup, return a list of (key, value)
        pairs.
        """

        soup = self.html_source()
        tpairs = [(i.parent.th.text, i.text) for i in soup.select('tr > td')
                  if i.parent.find('th')]

        return tpairs

    def _braces_markup(self, txt):
        """
        Using the braces make a concatenation of all infoboxes.
        """

        ret = ""
        ibs = -1
        braces = 0
        rngs = []

        for m in re.finditer("(({{)\s*(\w*)|(}}))", txt):
            if m.group(2) == "{{":
                if braces > 0:
                    braces += 1

                if m.group(3) == "Infobox":
                    braces = 1
                    ibs = m.start(2)

            elif m.group(1) == "}}" and braces > 0:
                braces -= 1

                if braces == 0:
                    eoi = m.end(1)
                    rngs.append((ibs, eoi))

        # There may be more than one infoboxes, concaenate them.
        for s,e in rngs:
            ret += txt[s:e]

        return ret or None
