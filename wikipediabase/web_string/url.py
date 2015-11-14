import os

from wikipediabase.web_string.base import WebString
from wikipediabase.config import SubclassesItem, configuration

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
        get = '&'.join("%s=%s" % (k,v) for k, v in self.get_data.iteritems())
        ret = "%s?%s" % (self.url, get)
        return ret

    def literal(self):
        return self.raw()

    def with_get(self, get_dict):
        ret = self.copy()
        ret.get_data.update(get_dict)
        return ret

    @staticmethod
    def from_url(url, configuration=configuration):
        try:
            base, get = url.split('?')

        except ValueError:
            base, get = url, None

        kv = dict()
        if get is not None:
            kv = dict((seq_pairs.split('=') for seq_pairs in get.split('&')))

        return ApiUrlString(kw, configuration=configuration)
        if not title.endswith(".php"):
            cls = PageUrlString
            if kv.get('action') == 'edit':
                cls = EditUrlString

            return retcls(symbol=symbol, configuration=configuration).with_get(kw)


class PageUrlString(UrlString):
    def __init__(self, symbol, configuration=configuration):
        super(PageUrlString, self).__init__(symbol, configuration=configuration)
        from wikipediabase.web_string.symbol import SymbolString

        self.symbol = symbol
        if not isinstance(symbol, SymbolString):
            self.symbol = SymbolString(symbol, configuration=configuration)

        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.api_base) \
            .lens(lambda a,b: a+'/'+b)
        if not self.url:
            import pdb; pdb.set_trace()

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = kv.get('title', None) or os.path.basename(url)
        if get.get('action') != 'edit' and not title.endswith(".php"):
            return cls(title, configuration=configuration)

        return Nonex

class EditUrlString(PageUrlString):
    def __init__(self, symbol, configuration=configuration):
        super(EditUrlString, self).__init__(symbol, configuration=configuration)
        self.get_data['action'] = 'edit'

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = kv.get('title', None) or os.path.basename(url)
        if get.get('action') == 'edit' and not title.endswith(".php"):
            return cls(title, configuration=configuration)

        return None

class ApiUrlString(UrlString):
    def __init__(self, get_data, configuration=configuration):
        super(ApiUrlString, self).__init__(get_data, configuration=configuration)
        self.url = (configuration.ref.remote.url & \
                    configuration.ref.remote.api_base).lens(lambda a,b: a+'/'+b)
        self.get_data = get_data

    @classmethod
    def from_url(cls, base, get, configuration=configuration):
        title = kv.get('title', None) or os.path.basename(url)
        if title == configuration.ref.remote.api_base:
            return cls(title, configuration=configuration)

        return None