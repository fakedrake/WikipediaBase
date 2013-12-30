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
    def get(self, article, attr):
        """
        Iterate of the provided attribute resolvers.
        """

        for ar in self.resolvers():
            res = ar.resolve(article, attr)
            if res:
                return res

    @provide()
    def get_class(self):
        pass

    @provide()
    def get_attributes(self):
        pass
