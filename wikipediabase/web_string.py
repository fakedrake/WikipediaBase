import re
import os
import types
try:
    import urllib2 as urllib
except:
    import urllib

from urllib import urlencode

import lxml.etree as ET
import copy
import lxml
import lxml.html.clean
from lxml import html

from wikipediabase.config import Configurable, configuration

class WebString(Configurable):
    """
    A type to handle string related stuff
    """

    def __init__(self, data, configuration=configuration):
        self.data = data
        self.configuration = configuration

    def raw(self):
        return self.data

    def __len__(self):
        return len(self.raw())

    def __str__(self):
        return self.raw()

    def __contains__(self, item):
        return item in self.data

class SymbolString(WebString):
    def __init__(self, data, configuration=configuration):
        super(SymbolString, self).__init__(data, configuration=configuration)

        self.fetcher = configuration.ref.fetcher.with_args(
            configuration=configuration)
        self.prefix = None
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
        return re.sub(r"\s+", "_", self.prefixed())

    def synonym(self):
        """
        Get the true name of the article.
        """
        real_url = self.fetcher.redirect_url(self)
        urlstr = UrlString.from_url(real_url, configuration=configuration)
        return urlstr.symbol()

    def literal(self):
        return re.sub(r"(\s+|_)", " ", self.symbol)

    def url(self, *args, **kw):
        if 'configuration' not in kw:
            kw['configuration'] = self.configuration

        return UrlString(self, *args, **kw)

class UrlString(WebString):
    """
    Construct urls to a mediawiki instance.
    """
    def __init__(self, symbol, edit=False, extra_get=None,
                 configuration=configuration):
        super(UrlString, self).__init__(symbol, configuration=configuration)

        self.extra_get = extra_get or {}
        self.configuration = configuration
        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.base).lens(lambda a,b: a+'/'+b)
        self.edit = edit

    def get_data(self):
        ret = {'title': self.symbol().url_friendly()}
        if self.edit:
            ret['action'] = 'edit'

        ret.update(self.extra_get)
        return ret

    def raw(self):
        get = '&'.join("%s=%s" % (k,v) for k, v in self.get_data().iteritems())
        ret = "%s?%s" % (self.url, get)
        return ret

    def literal(self):
        return self.raw()

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
        if isinstance(self.data, SymbolString):
            return self.data

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

class NullHtmlElement(html.HtmlElement):
    """
    Keeping type consistency with a null empty element.
    """
    def __nonzero__(self):
        return False

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
        self.cleaner = configuration.ref.strings.lxml_cleaner
        self.prune_tags = configuration.ref.strings.xml_prune_tags

        if isinstance(self.data, LxmlStringState):
            self.state = data
            return

        self.state = LxmlStringState()
        if isinstance(self.data, lxml.etree._Element):
            self.state._soup = self.data
            return

        if isinstance(self.data, types.StringType):
            self.state._raw = reduce(self.raw_pruned, self.prune_tags, data)
            return

        raise ValueError("Bad type of data '%s'" % type(data))

    def raw_pruned(self, raw, tagname):
        """
        Prune the xml tree with just sting operations. It is used to
        remove style and script tags. This function accounts for
        unclosed tags by removing them completely.
        """
        end_tag = r"</\s*%s\s*>" % tagname
        start_tag = r"<\s*%s.*?>" % tagname
        ended_blocks = [re.split(start_tag, eb) for eb in
                            re.split(end_tag, raw)]

        def merge_blocks(ret_block, next_block):
            if len(next_block) == 0:
                # invalid next block
                return ret_block

            if len(ret_block) == 0:
                # Actually illegal
                return next_block

            if len(ret_block) == 1:
                # Unstarted closing block.
                return [ret_block[0] + next_block[0]] + next_block[1:]

            # Normal case where the closed ret_block has a start. Pop
            # ret_block and merge with next_block
            mid_text = ret_block[-2] + next_block[0]
            return ret_block[:-2] + [mid_text] + next_block[1:]

        return "".join(reduce(merge_blocks, ended_blocks))

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


        if not len(self.raw()):
            return NullHtmlElement()

        self.state._soup = html.fromstring(self.raw())

        # XXX: I am assuming we will never need the scripts.
        self.cleaner(self.state._soup)
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
        return (self.__class__(o.state,
                               trusted_state=True,
                               tags=self.tags,
                               configuration=self.configuration)
                for o in objs)


class MarkupString(WebString):
    """
    Some basic mediawiki parsing stuff.
    """

    def __init__(self, data, symbol=None, configuration=configuration):
        super(MarkupString, self).__init__(data, configuration=configuration)
        self.symbol = symbol and SymbolString(symbol, configuration)

    def redirect_target(self):
        """
        A SymbolString of the redirect target or None.
        """
        redirect_match = re.search(r"^\s*#\s*redirect\s*\[\[(.*)\]\]\s*$",
                                   self.raw(), re.I | re.MULTILINE)
        if redirect_match:
            return SymbolString(redirect_match.group(1).strip())

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
