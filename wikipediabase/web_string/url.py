import os

from wikipediabase.web_string.base import WebString
from wikipediabase.config import SubclassesItem, configuration
from urllib import quote, unquote

class UrlString(WebString):
    """
    Abstract class for urls.
    """

    def __init__(self, data, configuration=configuration):
        super(UrlString, self).__init__(data, configuration=configuration)

        self.get_data = {}
        self.configuration = configuration

    def copy(self):
        ret = self.__class__(self.data, configuration=self.configuration)
        ret.get_data = self.get_data.copy()
        return ret

    def raw(self):
        get = '&'.join("%s=%s" % (k, quote(unquote(v))) for k, v in self.get_data.iteritems())
        ret = "%s?%s" % (self.url, get)
        return ret

    def literal(self):
        return self.raw()

    def with_get(self, get_dict):
        ret = self.copy()
        ret.get_data.update(get_dict)
        return ret

    @classmethod
    def from_url(cls, url, configuration=configuration):
        """
        Depth first return the first subclass that accepts thafirst intfind all the
        """
        try:
            base, _get = url.split('?')
            get = dict(tuple(kv.split('=')) for kv in _get.split('&'))
        except ValueError:
            base, get = url, None

        def search_subclasses(class_list):
            if len(class_list) == 0:
                return None

            first = class_list[0].from_url(base, get,
                                            configuration=configuration)
            return first or \
                search_subclasses(class_list[0].__subclasses__()) or \
                search_subclasses(class_list[1:])

        return search_subclasses(cls.__subclasses__())


class PageUrlString(UrlString):
    def __init__(self, symbol, configuration=configuration):
        super(PageUrlString, self).__init__(symbol, configuration=configuration)
        from wikipediabase.web_string.symbol import SymbolString

        self.symbol = symbol
        if not isinstance(symbol, SymbolString):
            self.symbol = SymbolString(symbol, configuration=configuration)

        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.base) \
            .lens(lambda a,b: a+'/'+b)
        self.get_data['title'] = symbol.url_friendly()

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = get.get('title', None) or os.path.basename(url)
        symbol_cls = configuration.ref.strings.symbol_string_class.deref()
        if get.get('action') != 'edit' and not title.endswith(".php"):
            return cls(symbol_cls(title, configuration=configuration),
                       configuration=configuration)

        return None

class EditUrlString(PageUrlString):
    def __init__(self, symbol, configuration=configuration):
        super(EditUrlString, self).__init__(symbol, configuration=configuration)
        self.get_data['action'] = 'edit'

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = get.get('title', None) or os.path.basename(url)
        symbol_cls = configuration.ref.strings.symbol_string_class.deref()
        if get.get('action') == 'edit' and not title.endswith(".php"):
            return cls(symbol_cl(title, configuration=configuration),
                       configuration=configuration)

        return None

class ApiUrlString(UrlString):
    def __init__(self, get_data=None, configuration=configuration):
        super(ApiUrlString, self).__init__(get_data, configuration=configuration)
        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.api_base).lens(lambda a,b: a+'/'+b)
        self.get_data = get_data or {}

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = get.get('title', None) or os.path.basename(url)
        if title == configuration.ref.remote.api_base:
            return cls(title, configuration=configuration)

        return None
