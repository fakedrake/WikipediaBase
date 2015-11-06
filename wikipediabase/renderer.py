"""
Turn markdown into html.
"""

from urllib import urlopen
from urllib import urlencode

import wikipediabase.fetcher
import wikipediabase.util as util

from wikipediabase.config import Configurable, configuration


class SandboxRenderer(Configurable):
    """
    Use the wikipedia site sandbox to render mediawiki markup.
    """

    def __init__(self, configuration=configuration):
        """
        Provide a fetcher an I ll figure out how to render stuff from
        there or actually provide a url.
        """

        self.cache = configuration.ref.cache.rendered_pages
        self.xml_string = configuration.ref.strings.xml_string_class
        self.url = (configuration.ref.remote.url & configuration.ref.remote.base) \
            .lens(lambda u,b: u+'/'+b)
        self.sandbox_title = configuration.ref.remote.sandbox_title

    def post_data(self, data, get, form_id):
        """
        Get a dict with the default post data.
        """

        soup = self.xml_string(self.uopen(get).read())
        inputs = soup.xpath(".//input")
        fields = dict([(i.get('name'), i.get('value')) for i in inputs
                       if i.get('type') != 'submit' and i.get('value')])

        fields.update(data)
        return fields

    def uopen(self, get, post=None):
        """
        Open the url and provided a map of the get request.
        """
        if not post:
            return urlopen(self.url+'?'+urlencode(get))

        post.update(get)
        return urlopen(self.url+'?'+urlencode(get), data=urlencode(post))

    def render(self, string, key=None):
        """
        Turn markdown into html.
        """

        if not key:
            key = str(hash((self.url, string)))

        if key in self.cache:
            return util.encode(self.cache[key])

        # XXX: here we assume tha t the mediawiki project name is wikipedia.
        get = dict(title=self.sandbox_title, action="edit")
        post = self.post_data(dict(wpTextbox1=string, wpSave="Save page"),
                              get, 'editForm')
        get['action'] = 'submit'
        get['printable'] = 'yes'


        ufd = self.uopen(get, post)

        ret = ufd.read()
        self.cache[key] = ret

        return util.encode(ret)
