import re
import os
from urllib import urlencode

import lxml.etree as ET
import copy
import lxml
from lxml import html

from wikipediabase.config import Configurable, configuration

class WebString(Configurable):
    """
    A type to handle string related stuff
    """

    def __init__(self, data, configuration=configuration):
        self.data = data

    def __str__(self):
        return self.data

class SymbolString(WebString):
    def __init__(self, data, configuration=configuration):
        super(SymbolString, self).__init__(data, configuration=configuration)

    def reduced(self):
        """
        Remove punctuation, an/a/the and spaces.
        """
        # It may seem a bad idea to not even return 'the reckoning' from
        # symbol '"The Reckonning"' but we reduce user input as well.

        # First remove quotes so the stopwords turn up at the front
        ret = re.sub(ur"([\W\s]+)", " ", self.literal(),
                     flags=re.U|re.I).strip().lower()
        return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()

    def literal(self):
        return re.sub(r"(\s+|_)", " ", self.data)

    def url_friendly(self):
        return re.sub(r"\s+", "_", self.data.lower())

    def __str__(self):
        return self.literal()

    def url(self, *args, **kw):
        return UrlString(self.literal(), *args, **kw)

class UrlString(WebString):
    """
    Construct urls to a mediawiki instance.
    """
    def __init__(self, symbol, edit=False, configuration=configuration):
        super(UrlString, self).__init__(symbol, configuration=configuration)

        self.configuration = configuration
        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.base).lens(lambda a,b: a+'/'+b)
        self.edit = edit

    def get_data(self):
        ret = {'title': self.symbol().url_friendly()}
        if self.edit:
            ret['action'] = 'edit'

        return ret

    def raw(self):
        return "%s?%s" % (self.url, urlencode(self.get_data()))

    @classmethod
    def from_url(cls, url, configuration=configuration):
        try:
            base, get = url.split('?')
        except ValueError:
            base, get = url, None

        kv = dict()
        if get is not None:
            kv = dict((seq_pairs.split('=') for seq_pairs in get.split('&')))

        edit = (kv.get('action') == 'edit')
        title = kv.get('title', os.path.basename(url))

        return cls(title, edit=edit, configuration=configuration)

    def symbol(self, configuration=None):
        cfg = configuration or self.configuration
        return SymbolString(self.data, configuration=cfg)


class XmlString(WebString):
    """
    Interface to xml strings to avoid do close entanglement with lxml.
    """

    def __init__(self, data, configuration=configuration):
        super(XmlString, self).__init__(data, configuration=configuration)
        self.literal_newlines = configuration.ref.strings.literal_newlines

    def raw(self):
        """
        Get a raw markup string.
        """
        raise NotImplemented

    def text(self):
        """
        The unrendered text.
        """
        raise NotImplemented

    def xpath(self, xpath):
        """
        Get iterator over XmlString types that corresponds to xpath.
        """
        raise NotImplemented

class LxmlString(XmlString):
    """
    An lxml xmlstring implementation. It is a very thin wrapper but it
    is lazy with actually creating the lxml element.
    """

    def __init__(self, data, configuration=configuration):
        """
        Data can either be a string or an lxml element.
        """

        super(LxmlString, self).__init__(data, configuration=configuration)

        self._soup = None
        self._data = None
        if isinstance(self.data, lxml.etree._Element):
            self._soup = self.data

        else:
            self._raw = self.data

    def raw(self):
        if self._raw is not None:
            return self._raw

        return ET.tostring(self.soup(), method='html', encoding='utf-8')

    def text(self):
        """
        The unrendered text.
        """
        return self.soup().text_content()

    def xpath(self, xpath):
        return (LxmlString(i) for i in self.soup().findall(xpath))

    def soup(self):
        """
        Get an lxml soup.
        """
        if self._soup is not None:
            return self._soup

        if self._raw is None:
            raise ValueError("No useful info to create soup.")

        if self.literal_newlines:
            self._raw = re.sub('<\s*br\s*/?>',"\n", self._raw)

        self._soup = html.fromstring(self._raw)
        return self._soup

class MarkupString(WebString):
    """
    Some basic mediawiki parsing stuff.
    """

    def __init__(self, data, configuration=configuration):
        super(HtmlString, self).__init__(data, configuration=configuration)

    def raw(self):
        return self.data

    def unlink(self):
        """
        Remove markup links
        """
        return re.sub(r"\[+(.*\||)(?P<content>.*?)\]+", r'\g<content>',
                      self.data)


class MarkupOverlay(MarkupString):
    def __init__(self, rng, parent, configuration=configuration):
        super(HtmlString, self).__init__("", configuration=configuration)
        self.start, self.end = rng
        self.parent = parent

    def raw(self, rng=None):
        return self.parent.raw(rng)

    def modify_range(self, rng):
        return rng
