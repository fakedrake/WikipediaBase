"""
Turn markdown into html.
"""

try:
    import urllib2 as urllib
except:
    import urllib as urllib

from urllib import urlencode
import wikipediabase.fetcher
import wikipediabase.util as util

from wikipediabase.config import Configurable, configuration
from wikipediabase.caching import Caching, cached
from wikipediabase.web_string import UrlString

class SandboxRenderer(Caching):
    """
    Use the wikipedia site sandbox to render mediawiki markup.
    """

    def __init__(self, configuration=configuration):
        """
        Provide a fetcher an I ll figure out how to render stuff from>
        there or actually provide a url.
        """
        super(SandboxRenderer, self).__init__(configuration=configuration)
        self.xml_string = configuration.ref.strings.\
                          xml_string_class.with_args(configuration=configuration)
        self.url_edit_string = configuration.ref.strings.\
                               url_edit_string_class.with_args(configuration=configuration)
        self.symbol_string = configuration.ref.strings.\
                             symbol_string_class.with_args(configuration=configuration)
        self.sandbox_title = configuration.ref.remote.sandbox_title

    def post_data(self, data, url, form_id):
        """
        Get a dict with the default post data.
        """

        soup = self.xml_string(urllib.urlopen(str(url)).read())
        inputs = soup.xpath(".//form[@id='editform']//input")
        fields = dict([(i.get('name'), i.get('value')) for i in inputs
                       if i.get('type') != 'submit' and i.get('value')])

        fields.update(data)
        return fields

    @cached()
    def render(self, string):
        """
        Turn markdown into html.
        """

        # XXX: here we assume tha t the mediawiki project name is wikipedia.
        get = {'action':'submit', 'printable': 'yes'}
        url = self.url_edit_string(self.symbol_string(self.sandbox_title))\
                  .with_get(get)
        post = self.post_data(dict(wpTextbox1=string, wpPreview="Show preview"),
                              url, 'editForm')
        ufd = urllib.urlopen(str(url), data=urlencode(post))

        ret = self.xml_string(ufd.read())

        return ret

class ApiRenderer(Caching):
    def __init__(self, configuration=configuration):
        super(ApiRenderer, self).__init__(configuration=configuration)
        self.xml_string = configuration.ref.strings.\
                          xml_string_class.with_args(configuration=configuration)
        self.url_string = configuration.ref.strings.\
                          url_string_class.with_args(configuration=configuration)
        self.sandbox_title = configuration.ref.remote.sandbox_title


    @cached()
    def render(self, string):
        req = dict(action='parse', text=string, contentmodel='wikitext')
        url = self.url_string(self.sandbox_title, api=True).with_get(req)
        ufd = urllib.urlopen(str(url))
        ret = self.xml_string(ufd.read())
        return ret
