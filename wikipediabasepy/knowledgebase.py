from provider import Aquirer, Provider, provide


class KnowledgeBase(Provider):

    def __init__(self, frontend=None, resolvers=None, *args, **kwargs):
        super(KnowledgeBase, self).__init__(*args, **kwargs)
        self.frontend = frontend

        if frontend:
            self.provide_to(frontend)

        self.resolvers_aquirer = Aquirer(providers=resolvers or [])

    def resolvers(self):
        """
        The resolvers the the knowledgebase uses. This is a thin wapper
        around the stock `Aquirer' functionality.
        """

        return self.resolvers_aquirer._providers

    @provide()
    def get(self, v1, v2, v3=None):
        """
        Iterate of the provided attribute resolvers.
        """

        if v3:
            return self.old_get(v1, v2, v3)

        return self.new_get(v1, v2)


    def old_get(self, cls, article, attr):
        raw_ret = self.new_get(article, attr, compat=True)
        if raw_ret:
            tag, ret = raw_ret
            if isinstance(ret, str):
                ret = '"'+ret+'"'

            return "((:%s %s))" % (tag, ret)

    def new_get(self, article, attr, compat=False):
        """
        In compatibility mode new_get returns a tuple of the resolver
        gives to the answer (for now 'code' or 'html') and the actual
        answer.
        """

        self.log().info("Get article: '%s', attribute: '%s'" % (article, attr))

        # Attribute is wrapped into a dict just until we retrieve the
        # keys.
        wattr = self.attribute_wrap(attr)
        for ar in self.resolvers():
            res = ar.resolve(article, wattr['val'], **wattr['keys'])
            if res:
                if not compat:
                    return res
                else:
                    return ar.tag(), res

    @provide()
    def get_class(self):
        pass

    @provide()
    def get_attributes(self):
        pass

    # pass: keywords MUST be in lower case
    @provide(name=":code")
    def kw_code(self, x):
        return self.attribute_wrap(x, rendered=False)

    @provide(name=":rendered")
    def kw_rendered(self, x):
        return self.attribute_wrap(x, rendered=True)

    @provide(name=":id")
    def kw_id(self, x):
        return x


    def attribute_wrap(self, val, **keys):
        """
        Make a dict with val and keys. This wraps
        attributes which are strings only for internal use in
        knowledgebase.
        """

        try:
            val["keys"].update(keys)
            return val
        except (KeyError, TypeError):
            return dict(val=val, keys=keys)
