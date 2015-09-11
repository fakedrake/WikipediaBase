import logging

def log_gen(obj):
    return logging.getLogger('.'.join((obj.__class__.__module__,
                                       obj.__class__.__name__)))
