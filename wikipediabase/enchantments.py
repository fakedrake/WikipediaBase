"""
Enchantments convert Python objects into Lisp-like encoded strings that are
readable by START.

To use the enchantment infrastructure use the 'enchant' function.
To create a new way of interpreting data subclass the Enchanted class.

Prefix your class with an underscore (_) if it is an intermediate generation
between Enchanted and the classes that actually parse so that the enchant 
method will ignore it.
"""

import re
from numbers import Number
import warnings
import overlay_parse

from wikipediabase.log import Logging
from wikipediabase.util import subclasses, output


# For fully deterministic enchantments use this priority.
MIN_PRIORITY = 0
MAX_PRIORITY = 15


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
    START understands. Its `val` attribute is a Python object.

    Note that not only answers but also questions are enchanted.

    To use this subclass it and provide any of the following:

    - __str__: string representation
    - should_parse
    - parse_val
    """

    priority = 0
    literal = False

    def __init__(self, val, typecode, infobox_attr=None):
        """
        Enchant a piece of data. Throws EnchantError on failure.
        """

        self.typecode = typecode
        self.infobox_attr = infobox_attr
        self.val = val
        self.valid = False

        if self.should_parse():
            self.val = self.parse_val(val)
            self.valid = True
        else:
            self.val = None

    def should_parse(self):
        """
        If this returns false enchantment is invalid whatever the value.
        """

        return True

    def parse_val(self, val):
        """
        Override this to have special value manipulation.
        """

        return val

    def typed_value(self):
        if self.typecode is None:
            return u"%s" % self.val_str()
        else:
            return u"(:%s %s)" % (self.typecode_str(), self.val_str())

    def __repr__(self):
        r = u"<%s object %s>" % (self.__class__.__name__,
                                 self.__str__())
        return output(r)

    def __str__(self):
        return output(self.typed_value())

    def val_str(self):
        return unicode(self.val)

    def typecode_str(self):
        return self.typecode

    def __nonzero__(self):
        return self.valid

    def __eq__(self, other):
        # compare Enchanted objects based on their string representation
        if isinstance(other, self.__class__) or isinstance(other, basestring):
            return self.__str__() == other.__str__()
        return False

    def __hash__(self):
        return hash(self.__str__())


class EnchantedString(Enchanted):
    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, basestring)

    def typecode_str(self):
        if self.infobox_attr is not None and \
                self.typecode.lower() in ('code', 'rendered'):
            return 'html'
        return super(EnchantedString, self).typecode_str()

    def val_str(self):
        v = re.sub(r"\[\d*\]", "", self.val)  # remove references, e.g. [1]
        v = re.sub(r"[[\]]", "", v)  # remove wikimarkup links, e.g. [[Ruby]]
        v = output(unicode(v)) # remove unicode characters
        v = v.replace('"', '\\"')  # escape double quotes
        v = u'"{0}"'.format(v)
        return v


class EnchantedList(Enchanted):

    """
    This is coordinates and other things like that
    """

    priority = next(MID_PRIORITY)
    literal = True

    def should_parse(self):
        return hasattr(self.val, '__iter__')

    def __str__(self):
        if self.typecode:
            return '%s' % (super(EnchantedList, self).__str__())
        else:
            return '(%s)' % super(EnchantedList, self).__str__()

    def erepr(self, v):
        if isinstance(v, Enchanted):
            return str(v)

        if isinstance(v, basestring):
            return str(EnchantedString(v, None))

        if hasattr(v, '__iter__'):
            return str(EnchantedList(v, None))

        return repr(v)

    def val_str(self):
        return " ".join([self.erepr(v) for v in self.val])

    def __contains__(self, val):
        return val in self.val_str()


class EnchantedDate(Enchanted):

    """
    Date enchantment using the overlay framework.
    """

    priority = next(MID_PRIORITY)

    def val_str(self):
        d, m, y = self.val
        return "%s%04d%02d%02d" % ("-" if y < 0 else "", abs(y), m, d)

    def typecode_str(self):
        return "yyyymmdd"

    def should_parse(self):
        if self.infobox_attr and (self.infobox_attr.lower() == 'date' or
                                  self.infobox_attr.lower().endswith("-date")):
            self.typecode = "yyyymmdd"
            return True

        if self.typecode == "yyyymmdd":
            return True

    def _range_middle(self, date):
        # Very imprecise

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
        Return of the extracted dates the one appearing most often. Count
        the ones that are in ranges etc.

        Note that while this works it is not used. See results for the
        jesus date of birth. The correct way would be to have a
        special enchantment that may be a date or a date range.
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


class EnchantedDict(Enchanted):

    """
    Get a lispy dictionary of non-None items.
    """

    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, dict)

    def __str__(self):
        pairs = sorted(self.val.items())
        return output(u'(%s)' % self._plist(pairs))

    def _plist(self, pairs):
        """
        A lispy plist without the parens.
        """

        return " ".join(list(self._paren_content_iter(pairs)))

    def _kv_pair(self, k, v):
        if k is None:
            return output(u"%s" % v)

        if isinstance(k, basestring):
            return output(u":%s %s" % (k, v))

    def _paren_content_iter(self, pairs):
        for k, v in pairs:
            if v is not None:
                # XXX: NastyHack(TM). Replace the nonbreaking space
                # with a space.
                yield self._kv_pair(k, enchant(v))


class EnchantedError(EnchantedDict):

    """
    An error with a reply and a symbol. The expected value should be a
    dict-like object with the keys 'kw' and 'symbol' and the the typecode
    should be 'error'. Alternatively you can pass as value an
    exception and I will try to deal with it.
    """

    priority = MAX_PRIORITY
    # Here you can translate python exception names to wikibase error
    # symbols
    lookup = dict()

    def should_parse(self):
        return self.typecode == 'error' or isinstance(self.val, BaseException)

    def __str__(self):
        if isinstance(self.val, BaseException):
            self.val = dict(
                symbol=self.lookup.get(type(self.val).__name__) or
                type(self.val).__name__,
                # :reply should only be used for error messages that can be
                # displayed to START users
                # use :message for Python exceptions
                kw={'message': self.val.message}
            )

        return output(u"(:error {symbol} {keys})".format(
            symbol=self.val['symbol'],
            keys=self._plist(sorted(self.val['kw'].items()))))

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


class EnchantedKeyword(_EnchantedLiteral):

    """
    Just a keyword. No content.
    """

    def should_parse(self):
        return isinstance(self.val, basestring) and self.val.startswith(':') \
            and ' ' not in self.val

    def val_str(self):
        return self.val


class EnchantedBool(_EnchantedLiteral):

    """
    Enchant a boolean value
    """

    def should_parse(self):
        return isinstance(self.val, bool)

    def val_str(self):
        return 't' if self.val else 'nil'


class EnchantedNone(_EnchantedLiteral):

    """
    Enchanted none object
    """

    def should_parse(self):
        return self.val is None

    def val_str(self):
        return 'nil'


class EnchantedNumber(_EnchantedLiteral):

    def should_parse(self):
        return isinstance(self.val, Number)

    def val_str(self):
        return str(self.val)


WIKIBASE_ENCHANTMENTS = subclasses(Enchanted, instantiate=False)


def enchant(obj, typecode=None, infobox_attr=None):
    """
    Return an enchanted object.

    infobox_attr is the name of the infobox attribute where obj came from
    """

    if isinstance(obj, Enchanted):
        return obj

    for E in WIKIBASE_ENCHANTMENTS:
        e = E(obj, typecode, infobox_attr=infobox_attr)
        if e.valid:
            return e

    raise NotImplementedError(
        "Implement enchantment for typecode: %s, val: %s or"
        "provide fallback error." % (typecode, obj))

__all__ = ['enchant']
