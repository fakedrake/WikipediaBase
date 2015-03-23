"""
Enchantments are an abstraction to representation of data within
and outside of wikipediabase, ie wikipedia free text, python types and
START s-expressions.

To use the enchantment infrastructure use the 'enchant' function. To
create a new way of interpreting data subclass the Enchanted
class. Prefix your class with an underscore (_) if it is an
intermediate generation between Enchanted and the classes that
actually parse so that the enchant method will ignore it.
"""

import re
from numbers import Number

import overlay_parse

from wikipediabase.log import Logging
from wikipediabase.util import subclasses


# For fully deterministic enchantments use this prioroty.
MIN_PRIORITY = 0
MAX_PRIORITY = 15

def kv_pair(k, v):
    if isinstance(k, basestring):
        return ":%s %s" % (k, v)

    return "%s %s" % (k, v)


def erepr(v):
    if isinstance(v, basestring):
        return '"%s"' % v

    return repr(v)

def mid_priority():
    """
    Just count. Later classes override previous ones.
    """

    for i in xrange(MIN_PRIORITY + 1, MAX_PRIORITY):
        yield i

    while True:
        warnings.warn("Increase MAX_PRIORITY")
        yield i

MID_PRIORITY = mid_priority()

class Enchanted(Logging):

    """
    An enchanted object's string representation is something that
    START understands. Also its `val` attribute is something that
    makes sense to python.

    Note that not only answers but also questions are enchanted.

    To use this subclass it and provide any of the following:

    - _str: string representation
    - should_parse
    - parse_val
    """

    priority = 0
    literal = False

    def __init__(self, tag, val, question=None, **kw):
        """
        Enchant a piece of data. Throws EnchantError on failure.
        """

        self.tag = tag
        self.question = question
        self.val = val
        self.valid = False

        if self.should_parse():
            self.val = self.parse_val(val)
            self.valid = True
        else:
            self.val = None

    def should_parse(self):
        """
        If this returns false echantment is invalid whatever the value.
        """

        return True

    def parse_val(self, val):
        """
        Override this to have special value manipulation.
        """

        return val

    def __repr__(self):
        return u"<%s object (%s)>" % (
            self.__class__.__name__, kv_pair(self.tag_str(), self.val_str()))

    def __str__(self):
        if self.literal:
            return self._str()

        return u"(%s)" % self._str()

    def _str(self):
        if self:
            return u"(%s)" % kv_pair(self.tag_str(), self.val_str())

        return ''

    def val_str(self):
        return unicode(self.val)

    def tag_str(self):
        return self.tag or "html"

    def __nonzero__(self):
        return self.valid


class EnchantedString(Enchanted):
    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, basestring)

    def tag_str(self):
        if self.tag == "code" or self.tag is None:
            return "html"

        return self.tag

    def val_str(self):
        return u"\"%s\"" % re.sub(r"[[\]]", "", self.val)


class EnchantedList(Enchanted):

    """
    This is coordinates and other things like that
    """

    priority = next(MID_PRIORITY)

    def should_parse(self):
        return hasattr(self.val, '__iter__')

    def _str(self):
        if self.tag is None:
            return '(%s)' % self.val_str()
        else:
            return '(:%s %s)' % (self.tag_str(), self.val_str())

    def val_str(self):
        return " ".join([erepr(v) for v in self.val])

    def __contains__(self, val):
        return val in self.val


class EnchantedDate(Enchanted):

    """
    Date enchantment but using the overlay framework.
    """

    priority = next(MID_PRIORITY)

    def val_str(self):
        d, m, y = self.val
        return "%s%04d%02d%02d" % ("-" if y < 0 else "", abs(y), m, d)

    def tag_str(self):
        return "yyyymmdd"

    def should_parse(self):
        if self.question and self.question.lower().endswith("date"):
            return True

        return self.tag == "yyyymmdd"

    def _range_middle(self, date):
        # Very impercise

        (d1, d2) = date
        return tuple(int((i + j) / 2) for i, j in zip(d1, d2))

    def parse_val(self, txt):
        # Might be already parsed
        if not isinstance(txt, basestring):
            return txt

        dor = overlay_parse.dates.just_props(txt, {'date'}, {'range'})

        if dor:
            if len(dor[0]) == 2:
                return self._range_middle(dor[0])

            return dor[0]


class _EnchantedDateVoting(EnchantedDate):
    priority = next(MID_PRIORITY)

    def parse_val(self, txt):
        """
        Return of the extracted date the one appearing most often. Count
        the ones that are in ranges etc.

        Note that while this works it is not used. See results for the
        jesus date of birth. The correct way would be to have a
        sepcial enchantment that may be a date or a date range.
        """

        # Do not parse separately, it's expensive and you will get
        # date duplicates from range edges.
        dnr = overlay_parse.dates.just_props(txt, {'date'}, {'range'})
        dates = [d for d in dnr if len(d) == 3]
        ranges = [r for r in dnr if len(r) == 2]

        # Most common date
        scores = dict()
        for d in dates:
            score = scores.get(d, 0)

            for r in ranges:
                if self._in_range(d, r):
                    score += 1

            scores[d] = score + 1

        try:
            return max(dates, key=lambda d: scores[d])
        except ValueError:
            if ranges:
                return self._range_middle(ranges[0])

        return None

    def _in_range(self, date, rng):
        sd, ed = rng

        for c, rs, re in reversed(zip(date, sd, ed)):
            # If all are defined and c is between [grs, re)
            if c * rs * re != 0 and c >= rs and c < re:
                return True

        return False

EnchantedDateVoting = _EnchantedDateVoting

class EnchantedStringDict(Enchanted):

    """
    Get a lispy dictionary of non-None items.
    """

    # Just so the test regexes match.
    reverse = True
    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, dict)

    def _str(self):
        if self.reverse:
            pairs = reversed(self.val.items())

        return '(%s)' % self._plist(pairs)

    def _plist(self, pairs):
        """
        A lispy plist without the parens.
        """

        return " ".join(list(self._paren_content_iter(pairs)))


    @staticmethod
    def _paren_content_iter(pairs):
        for k, v in pairs:
            if v is not None:
                # XXX: NastyHack(TM). Replace the nonbreaking space
                # with a space.
                yield kv_pair(k, u'"%s"' % v)


class EnchantedError(EnchantedStringDict):
    """
    An error with a reply and a symbol. The expected value should be a
    dict-like object with the keys 'kw' and 'symbol' and the the tag
    should be 'error'. Alternatively you can pass as value an
    exception and I will try to deal with it.
    """

    priority = MAX_PRIORITY
    # Here you can translate python exception names to wikibase error
    # symbols
    lookup = dict()

    def should_parse(self):
        return self.tag == 'error' or \
            isinstance(self.val, BaseException)

    def _str(self):
        if isinstance(self.val, BaseException):
            self.val = dict(
                symbol=self.lookup.get(type(self.val).__name__) or \
                type(self.val).__name__,
                kw={'reply': self.val.message}
            )

        # Useless 3ple parens needed.
        return "((error {symbol} {keys}))".format(
            symbol=self.val['symbol'],
            keys=self._plist(self.val['kw'].iteritems()))

    def __nonzero__(self):
        """
        Errors should count as zeros so that you can check for an answer with

        if potential_error_or_none:
            # do stuff
        """

        return False


class _EnchantedLiteral(Enchanted):

    """
    Enchanted literals. These are not.
    """
    priority = MAX_PRIORITY
    literal = True


class EnchantKeyword(_EnchantedLiteral):

    """
    Just a keyword. No content.
    """

    def should_parse(self):
        return isinstance(self.tag, basestring) and \
            self.val is None

    def _str(self):
        return self.tag


class EnchantBool(_EnchantedLiteral):

    """
    Enchant a boolean value
    """

    def should_parse(self):
        return isinstance(self.val, bool)

    def _str(self):
        return "#t" if self.val else "#f"


class EnchantNone(_EnchantedLiteral):

    """
    Enchanted none object
    """

    def should_parse(self):
        return self.val is None and \
            self.tag is None

    def _str(self):
        return 'nil'


class EnchantNumber(_EnchantedLiteral):

    def should_parse(self):
        return isinstance(self.val, Number) and \
            self.tag is None

    def _str(self):
        return str(self.val)


WIKIBASE_ENCHANTMENTS = subclasses(Enchanted, instantiate=False)


def enchant(tag, obj, result_from=None, fallback=None, **kw):
    """
    Return an appropriate enchanted object. reslut is true when we are
    enchanting a result. Sometimes tags mean different thigs in
    results. Also for now you always want to be enchanting.
    """

    if isinstance(obj, Enchanted):
        return obj

    for E in WIKIBASE_ENCHANTMENTS:
        ret = E(tag, obj, question=result_from, **kw)
        if ret.valid:
            return ret

    if fallback:
        return EnchantedError('error', fallback)

    raise NotImplementedError(
        "Implement enchatment tag: %s, val: %s or"
        "provide fallback error." % (tag, obj))

__all__ = ['enchant']
