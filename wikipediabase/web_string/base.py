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
