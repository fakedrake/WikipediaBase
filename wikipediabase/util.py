from itertools import islice

INFOBOX_ATTRIBUTE_REGEX = r"\|\s*%s\s*=[\t ]*(.*?)\s*(?=\n\s*\|)"

def iwindow(seq, n):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

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
