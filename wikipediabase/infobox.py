import re
import bs4

from log import Logging

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=\n\s*\|)"


class Infobox(Logging):
    def __init__(self, title, fetcher):
        self.title = title
        self.fetcher = fetcher

    def __nonzero__(self):
        return bool(self.fetcher.download(self.title))

    def type(self):
        """
        The infobox type.
        """

        raise NotImplemented

    def get(self, key, source=None):
        """
        Get a specific infobox field. SOURCE tells us where to look. If it
        is None try 'markup', then 'html'.
        """

        # Try the markup first
        if source is None or source == 'markup':
            # regexes are faster than the parsed.
            mu = self.markup_source()
            m = re.search(INFOBOX_ATTRIBUTE_REGEX % attr, mu,
                          flags=re.IGNORECASE|re.DOTALL)

            if m:
                return val.group("val")

        # Html parsing however is done by bs anyway.
        for k, v in self.html_parsed():
            if k == attr:
                return v

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
