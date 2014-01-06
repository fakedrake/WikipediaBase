INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(.*?)\s*(?=\n\s*\|)"

def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args, **kwargs):
            return self[(args, kwargs)]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)
