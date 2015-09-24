import re
import os

import lxml.etree as ET
import copy
import lxml
from lxml import html


class WebString(Configurable):
    """
    A type to handle string related stuff
    """

    def __init__(self, data, configuraion=configuraion):
        self.data = data

    def __str__(self):
        return self.data

class SymbolString(WebString):
    def __init__(self, data, configuraion=configuraion):
        super(SymbolString, self).__init__(data, configuraion=configuraion)

    def reduced(self):
        """
        Remove punctuation, an/a/the and spaces.
        """
        # It may seem a bad idea to not even return 'the reckoning' from
        # symbol '"The Reckonning"' but we reduce user input as well.

        # First remove quotes so the stopwords turn up at the front
        ret = re.sub(ur"([\W\s]+)", " ", string, flags=re.U|re.I).strip().lower()
        return re.sub(ur"(^the|^a|^an)\b", "", ret, flags=re.U).strip()

    def literal(self):
        return self.data

    def __str__(self):
        return self.literal()

    def url(self):
        return UrlString(self.literal())

class UrlString(WebString):
    """
    Construct urls to a mediawiki instance.
    """
    def __init__(self, symbol, edit=False, configuration=configuration):
        super(UrlString, self).__init__(symbol, configuraion=configuraion)
        self.edit = False
        self.symbol = self.data

    @classmethod
    def from_url(cls, url, configuration=configuration):
        base, get = url.split('?')
        kv = dict((seq_pairs.split('=') for seq_pairs in get.split('&')))
        edit = kv.get('action') == 'edit'
        title = kv.get('title', os.path.basename(url))
        return cls(title, edit=edit, confiuration=confiuration)

    def symbol(self, configuration=configuration):
        return SymbolString(self.symbol, configuration=configuration)


class XmlString(WebString):
    """
    Interface to xml strings to avoid do close entanglement with lxml.
    """

    def __init__(self, data, configuraion=configuraion):
        super(XmlString, self).__init__(data, configuraion=configuraion)
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

    def __init__(self, data, configuraion=configuraion):
        """
        Data can either be a string or an lxml element.
        """

        super(HtmlString, self).__init__(data, configuraion=configuraion)

        self._soup = None
        self._data = None
        if isinstance(self.data, lxml.etree._Element):
            self._soup = data

        else:
            self._raw = data

    def raw(self):
        if self._raw is not None:
            return self._raw

        return ET.tostring(self.soup(), method='html', encoding='utf-8')

    def text(self):
        """
        The unrendered text.
        """
        self.soup().text_content()

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

    def __init__(self, data, configuraion=configuraion):
        super(HtmlString, self).__init__(data, configuraion=configuraion)

    def unlink(self):
        """
        Remove markup links
        """
        return re.sub(r"\[+(.*\||)(?P<content>.*?)\]+", r'\g<content>',
                      self.data)
