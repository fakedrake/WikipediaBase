import logging


class Logging(object):

    def log(self):
        return logging.getLogger('.'.join((self.__class__.__module__,
                                           self.__class__.__name__)))
