import re
import bs4

from log import Logging
from article import Article
from fetcher import CachingSiteFetcher

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(?P<val>.*?)\s*(?=\n\s*\|)"


class Infobox(Logging):
    """
    The interface with attributes accepts and provides attributes with
    - instead of _.
    """

    def __init__(self, title, fetcher=CachingSiteFetcher()):
        """
        It is a good idea to provide a fetcher as caching will be done
        much better.
        """

        self.title = title
        self.fetcher = fetcher

    def __nonzero__(self):
        return bool(self.fetcher.download(self.title))

    def _to_start_type(self, ibx, do_it=True):
        """
        Turn an infobox into a strart type. If do_it is False then just
        return ibx. This is for convenience.
        """

        if not do_it:
            return ibx

        ret = ibx.lower().replace("template:", "")
        return ret.replace(" ","-").replace("infobox", "wikipedia")

    def types(self, extend=True, to_start=True):
        """
        The infobox type. Extend means search inn other places except here
        (ie find equivalent ones, parent ones etc)
        to_start will make the types into start classes.
        """

        ret = set()
        ibox_source = self.markup_source()
        if ibox_source:
            for m in re.finditer(r'{{\s*(?P<type>[Ii]nfobox\s+[\w ]*)',
                                    ibox_source):
                # The direct ibox
                primary = m.group('type')
                ret.add(self._to_start_type(primary, to_start))

                if extend:
                    # The ibox redirect
                    title = Article("Template:"+primary, self.fetcher).title()
                    ret.add(self._to_start_type(title, to_start))

        return ret


    def get(self, key, source=None):
        """
        Get a specific infobox field. SOURCE tells us where to look. If it
        is None try 'markup', then 'html'.
        """

        # Look into html first. The results here are much more
        # readable.
        html_key = key.lower().replace("-", " ")
        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k.lower() == html_key:
                    return v

        # Then look into the markup
        markup_key = key.lower().replace("-", "_")
        for k, v in self.markup_parsed_iter():
            if k.replace("-", "_") == markup_key:
                return v

    def rendered_key(self, mkey):
        """
        Get the corresponding rendered key to the markup key if you can.
        """

        mkey = mkey.lower().replace("-","_")
        for t in self.types(extend=False, to_start=False):

            tibox = Infobox("Template:"+t)
            for k,v in tibox.html_parsed():
                if v == '{{{%s}}}' % mkey:
                    return k

    def markup_parsed_iter(self):
        """
        Generate the pairs from markup
        """

        mu = self.markup_source()
        for m in re.finditer(INFOBOX_ATTRIBUTE_REGEX % "(?P<key>[a-z\-_]*)", mu,
                             flags=re.IGNORECASE|re.DOTALL):
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
        for s,e in rngs:
            ret += txt[s:e]

        return ret or None
