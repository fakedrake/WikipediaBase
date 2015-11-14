import lxml.etree as ET
import copy
import lxml
import lxml.html.clean
from lxml import html
import types
import re

from wikipediabase.config import configuration, Configurable
from wikipediabase.web_string.base import WebString

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

class XmlStringPreprocessor(Configurable):
    def __init__(self, configuration=configuration):
        self.prune_tags = configuration.ref.strings.xml_prune_tags

    def preprocess(self, raw_data):
        return reduce(self.raw_pruned, self.prune_tags, raw_data)

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
        self.preprocessor = configuration.ref.strings.xml_preprocessor. \
                            with_args(configuration=configuration)

        if isinstance(self.data, LxmlStringState):
            self.state = data
            return

        self.state = LxmlStringState()
        if isinstance(self.data, lxml.etree._Element):
            self.state._soup = self.data
            return

        if isinstance(self.data, types.StringType):
            self.state._raw = self.preprocessor.preprocess(data)
            return

        raise ValueError("Can't convert type '%s' to xml" % type(data))

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
