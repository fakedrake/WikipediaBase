from urllib import urlopen as uopen
from urllib import urlencode

from fetcher import WIKIBASE_FETCHER
from .util import fromstring, totext

#  Generate this with
#
#  >>> inputs = rnd.findall(".//form[@id='editform']//input")
#  >>> [(i.get('name'), i.get('value')) for i in inputs
#           if i.get('type') != 'submit']
#
# But they are pretty static so


class Renderer(object):
    def __init__(self, fetcher=None, url=None):
        """
        Provide a fetcher an I ll figure out how to render stuff from
        there or actually provide a url.
        """

        if url is not None:
            self.url = url
        else:
            if fetcher is None:
                fetcher = WIKIBASE_FETCHER

            self.url = fetcher.url + '/' + fetcher.base

    def post_data(self, data, get, form_id):
        soup = fromstring(self.uopen(get).read())
        form = soup.find(".//form[@id='%s']" % form_id)
        inputs = soup.findall(".//input")
        fields = dict([(i.get('name'), i.get('value')) for i in inputs
                       if i.get('type') != 'submit' and i.get('value')])

        fields.update(data)
        return fields

    def uopen(self, get, post=None):
        if not post:
            return uopen(self.url+'?'+urlencode(get))

        post.update(get)
        return uopen(self.url+'?'+urlencode(get), data=urlencode(post))


    def render(self, string):
        # XXX: here we assume tha t the mediawiki project name is wikipedia.
        get = dict(title="Wikipedia:Sandbox", action="edit")
        post = self.post_data(dict(wpTextbox1=string, wpSave="Save page"),
                              get, 'editForm')
        get['action'] = 'submit'
        get['printable'] = 'yes'


        ufd = self.uopen(get, post)

        return ufd.read().decode('utf-8')
