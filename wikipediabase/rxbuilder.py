# Requirements:
# - Operations on regex: sequential/separated, or
# - Exclusivity in naming.

def rxf(rx):
    if not isinstance(rx, Regex):
        return Regex(rx)

    return rx

# XXX: all methods that receve banned_names are destructive to it.
class Regex(object):

    # Note that rx can be None in subclasses.
    def __init__(self, rx=None, name=None, grouped=False, flags=None):
        self.rx = rx or ""
        self.grouped = grouped
        self.name = name
        self.flags = None

    def _format(self, banned_names):
        # XXX: this has the side effect of adding to banned
        # names. This means that a named is sure to be there only
        # once.
        fmt = "%s"
        if self.grouped:
            fmt = "(%s)"

        if self.name and self.name not in banned_names:
            banned_names.append(self.name)
            fmt = "(?P<"+self.name+">%s)"

        return fmt

    def render(self, banned_names=None, raw=False):
        """
        Render the regex.

        :param banned_names: A list of names that are banned. if the name
        is among those do not name the rx.

        :returns: String of what this regex means.
        """

        if banned_names is None:
            banned_names = []

        if raw:
            fmt = "%s"
        else:
            fmt = self._format(banned_names)

        s = self.string(banned_names)

        return fmt % s

    def string(self, banned_names=None):
        if isinstance(self.rx, Regex):
            return self.rx.render(banned_names)

        return self.rx

    def compiled(self, flags=None):
        return re.compile(str(self), flags or self.flags)

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

    def match(self, text):
        pass


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
