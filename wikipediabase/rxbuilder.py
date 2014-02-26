# Requirements:
# - Operations on regex: sequential/separated, or
# - Exclusivity in naming.
#
# Take a look at the tests to see how this is to be used.

import re

def rxf(rx):
    if not isinstance(rx, Regex):
        return Regex(rx)

    return rx

# XXX: all methods that receve banned_names are destructive to it.
class Regex(object):

    # Note that rx can be None in subclasses.
    def __init__(self, rx=None, name=None, grouped=False, flags=""):
        self.rx = rx or ""
        self.grouped = grouped
        self.name = name
        self.flags = flags

    def _format(self, banned_names, flags=None, grouped=None):
        # XXX: this has the side effect of adding to banned
        # names. This means that a named is sure to be there only
        # once.
        fmt = "%s"

        flg = flags or self.flags
        if flg:
            fmt = "(?%s)%s" % (flg, fmt)

        if self.name and self.name not in banned_names:
            banned_names.append(self.name)
            fmt = "(?P<"+self.name+">%s)" % fmt
        elif (grouped is None and self.grouped) or grouped:
            fmt = "(%s)" % fmt

        flg = flags or self.flags


        return fmt

    def render(self, banned_names=None, raw=False, flags=None, grouped=None):
        """
        Render the regex.

        :param banned_names: A list of names that are banned. if the name
        is among those do not name the rx.
        :param flags: One or more letters from the set 'i', 'L', 'm',
        's', 'u', 'x'. This wraps the rx with `(?<flags>rx)`

        :returns: String of what this regex means.
        """

        if banned_names is None:
            banned_names = []

        if raw:
            fmt = "%s"
        else:
            fmt = self._format(banned_names, grouped, flags)

        s = self.string(banned_names)

        return fmt % s

    def string(self, banned_names=None):
        if isinstance(self.rx, Regex):
            return self.rx.render(banned_names)

        return self.rx

    def compiled(self, **kw):
        """
        Note that only the root node flags are used.
        """

        return re.compile(self.render(**kw))

    def __str__(self):
        return self.render()

    def __nonzero__(self):
        return True if self.render(raw=True) != "" else False

    def __add__(self, rx):
        """
        A concatenated version of rx.
        """

        return ConcatRx(self, rx)

    def __or__(self, rx):
        return OrRx(self, rx)

    def match(self, text, name=None, flags=None):
        """
        Return a `re` matcher or just the matched text if name is given.
        """

        m = self.compiled(flags=flags).match(text)
        if m is None:
            return

        if name:
            return m.group(name)

        return m

    def search(self, text, name=None, flags=None):
        m = self.compiled(flags=flags).search(text)
        if m is None:
            return

        if name:
            return m.group(name)

        return m


class RxExpr(Regex):
    """
    In case of name conflict the name is taken by the shallowest and
    rightmost.
    """

    def __init__(self, left, right, sep="", **kw):
        self.sep = rxf(sep)
        self.left = rxf(left)
        self.right = rxf(right)

        super(RxExpr, self).__init__(**kw)

    def string(self, banned_names=None, **kw):
        if banned_names is None:
            banned_names = []

        r,s,l = [i.render(banned_names, **kw) if bool(i) else None \
                 for i in [self.right, self.sep, self.left]]

        if r is not None and l is not None:
            return l + (s or "") + r

        return l or r


class OrRx(RxExpr):

    def __init__(self, *args, **kwargs):
        lrx = args[0]
        kwargs['sep'] = '|'
        grp = kwargs["grouped"] if 'grouped' in kwargs else True
        kwargs['grouped'] = False

        if len(args) > 2:
            rrx = OrRx(*args[1:], **kwargs)
        elif len(args) == 2:
            rrx = args[1]
        else:
            rrx = None

        kwargs['grouped'] = grp
        super(OrRx, self).__init__(lrx, rrx, **kwargs)

class ConcatRx(RxExpr):

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            return super(ConcatRx, self).__init__("", "", "", **kwargs)

        lrx = args[0]
        if len(args) > 2:
            rrx = ConcatRx(*args[1:], **kwargs)
        elif len(args) == 2:
            rrx = args[1]
        else:
            rrx = ""

        super(ConcatRx, self).__init__(lrx, rrx, **kwargs)

class Matcher(object):
    """
    Retrieve a structured version of the text using regular
    expressions.
    """

    def __init__(self, rx_map):
        """
        :param rx_map: a list of tuples (certainty, Regex).
        """

        self.rx_map = rx_map


    def parse(self, text):
        """
        Make a parsable tree using the parser.

        :param text: The text to be parsed.
        :returns: A tree of elements that are matched.
        """

        for c, rx in self.rx_map:
            pass
