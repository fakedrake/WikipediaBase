import os

def data(fname):
    return os.path.abspath('/'.join([__package__, 'data', fname]))
