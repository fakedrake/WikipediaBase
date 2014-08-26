from urllib import urlopen as uopen
from urllib import urlencode

import dbm
from .fetcher import WIKIBASE_FETCHER
from .util import fromstring, totext, memoized


class SandboxRenderer(object):

    default_file = './renderer.mdb'

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

        self.cache = dbm.open(self.default_file, 'c')

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

    def render(self, string, key=None):
        if not key:
            key = str(hash(string))

        if key in self.cache:
            return self.cache[key].decode('utf-8')

        # XXX: here we assume tha t the mediawiki project name is wikipedia.
        get = dict(title="Wikipedia:Sandbox", action="edit")
        post = self.post_data(dict(wpTextbox1=string, wpSave="Save page"),
                              get, 'editForm')
        get['action'] = 'submit'
        get['printable'] = 'yes'


        ufd = self.uopen(get, post)

        ret = ufd.read()
        if key:
            self.cache[key] = ret

        return ret.decode('utf-8')


WIKIBASE_RENDERER = SandboxRenderer()
