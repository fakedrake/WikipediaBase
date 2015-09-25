import re
import os
import types
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
        self.configuration = configuration

    def __str__(self):
        return self.data

    def __contains__(self, item):
        return item in str(self)

class SymbolString(WebString):
    def __init__(self, data, configuration=configuration):
        super(SymbolString, self).__init__(data, configuration=configuration)


        self.prefix =  None
        self.symbol = re.sub(r"\s*:\s*", ":", self.data)
        self.symbol = re.sub(r"\s+", " ", self.symbol).strip()

        if ':' in self.symbol:
            self.prefix, self.symbol = self.data.split(':', 1)

    def prefixed(self):
        if self.prefix:
            return self.prefix + ':' + self.symbol

        return self.symbol


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

    def url_friendly(self):
        return re.sub(r"\s+", "_", self.prefixed().lower())

    def literal(self):
        return re.sub(r"(\s+|_)", " ", self.symbol)

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

    def ignoring(self, tags):
        """
        A new one that ignores these tags
        """
        raise NotImplemented

    def get(self, attr):
        """
        Get xml attribute.
        """
        raise NotImplemented

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

class LxmlStringState(object):
    _soup = None
    _text = None
    _raw = None


class LxmlString(XmlString):
    """
    An lxml xmlstring implementation. It is a very thin wrapper but it
    is lazy with actually creating the lxml element.
    """

    def __init__(self, data=None, configuration=configuration):
        """
        Data can either be a string (raw) or an lxml element (soup) or
        state object (state)
        """
        super(LxmlString, self).__init__(data, configuration=configuration)

        if isinstance(self.data, LxmlStringState):
            self.state = data
            return

        self.state = LxmlStringState()
        if isinstance(self.data, lxml.etree._Element):
            self.state._soup = self.data
            return

        if isinstance(self.data, types.StringType):
            self.state._raw = self.data
            return

        raise ValueError("Bad type of data '%s'" % type(data))


    def raw(self):
        if self.state._raw is None:
            self.state._raw = ET.tostring(self.soup(),
                                          method='html', encoding='utf-8')

        return self.state._raw

    def text(self):
        """
        The unrendered text.
        """
        if self.state._text is None:
            self.state._text = self.soup().text_content().strip()

        return self.state._text

    def xpath(self, xpath):
        return (LxmlString(soup, configuration=self.configuration)
                for soup in self.soup().findall(xpath))

    def get(self, key, default=None):
        return self.soup().get(key, default)

    def ignoring(self, tags):
        return LxmlIgnoringString(self.raw(), tags=tags,
                                  configuration=self.configuration)

    def soup(self):
        """
        Get an lxml soup.
        """
        if self.state._raw is None and self.state._soup is None:
            raise ValueError("No useful info to create soup.")

        if self.state._soup is not None:
            return self.state._soup


        self.state._soup = html.fromstring(self.raw())
        return self.state._soup

class LxmlIgnoringString(LxmlString):
    def __init__(self, data, configuration=configuration, tags=None,
                 trusted_state=False):
        super(LxmlIgnoringString, self).__init__(data, configuration=configuration)
        self.tags = tags or []

        if trusted_state:
            return

        raw = self.raw()
        self.state = LxmlStringState()

        rx = r'<(%s)>' % self.tag_rx_internal()
        self.state._raw = re.sub(rx, r'&lt;\1&gt;', raw)

    def tag_rx_internal(self):
        return "/?\s*{tag}(:?{attr})*\s*/?".format(tag=r'|'.join(self.tags),
                                                   attr=r'\s+\w+=".*?"')

    def text(self):
        ret = super(LxmlIgnoringString, self).text()
        rx = r'&lt;(%s)&gt;' % self.tag_rx_internal()
        self.state._text = re.sub(rx, r'<\1>', ret)
        return self.state._text

    def xpath(self, xpath):
        objs = super(LxmlIgnoringString, self).xpath(xpath)
        return (LxmlIgnoringString(o.state,
                                   trusted_state=True,
                                   tags=self.tags,
                                   configuration=self.configuration)
                for o in objs)


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
