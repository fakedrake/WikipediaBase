import re
import bs4

from log import Logging
from article import Article
from fetcher import WIKIBASE_FETCHER

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
        markup_key = key.lower().replace("-", "_")
        rendered_key = self.rendered_key(markup_key)

        if source is None or source == 'html':
            for k, v in self.html_parsed():
                if k.lower().replace(".", "") == html_key or \
                   k == rendered_key:
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
        ret = self._rendered_keys.get(mkey, False)
        if ret is not False:
            return ret

        for t in self.types(extend=False, to_start=False):

            tibox = Infobox("Template:"+t)
            for k,v in tibox.html_parsed():
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
        # Render all tags except <ul> and <li>. Escape them in some way and then reparse


        tpairs = []

        for val in soup.select('tr > td'):
            if val.find_previous_sibling('th'):
                key = val.parent.th.text
                # self._unwrapper(val)
                # val = str(val).replace("<td>", "").replace("</td>", "")

                val = bs4.BeautifulSoup(self._escape_list(str(val)),
                                        "html.parser").text
                tpairs.append((key, val))

        return tpairs

    def _escape_list(self, val):
        """
        We dont want to render lists because then we have no way of
        knowing they were lists.
        """

        if not val:
            val = ""

        return re.sub(r"<(br\s*/?|/?ul|/?li)>", "&lt;\\1&gt;", val)


    def _unwrapper(self, val):
        for tag in val:
            if isinstance(tag, bs4.Tag):
                self._unwrapper(tag)
                if tag.name not in {'ul','li'}:
                    tag.unwrap()

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

        if ret:
            return ret
