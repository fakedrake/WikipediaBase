import logging

def loggen(obj):
    return logging.getLogger('.'.join((obj.__class__.__module__,
                                       obj.__class__.__name__)))
