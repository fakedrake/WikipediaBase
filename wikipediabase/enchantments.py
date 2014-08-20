"""
Enchantments are meant to represent anything that comes in the
form (:<key> <vale>). The interface to the outer world is
enchant(). To add your own enchantments teach enchant() how to deal
with them.
"""

import re
from numbers import Number

import overlay_parse

from .log import Logging
from .util import subclasses

def kv_pair(k, v):
    if isinstance(k, basestring):
        return ":%s %s" % (k, v)

    return "%s %s" % (k, v)

def erepr(v):
    if isinstance(v, basestring):
        return '"%s"' % v

    return repr(v)

MAX_PRIORITY = 15

class Enchanted(Logging):
    """
    An enchanted object's string representation is something that
    START understands. Also its `val` attribute is something that
    makes sense to python.

    Note that not only answers but also questions are enchanted.
    """

    force_tag = None
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
        return u"<%s object (%s)>" % (self.__class__, kv_pair(self.tag_str(), self.val_str()))

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
    priority = 1
    def tag_str(self):
        if self.tag == "code" or self.tag is None:
            return "html"

        return self.tag

    def val_str(self):
        return u"\"%s\"" % re.sub(r"[[\]]" , "", self.val)

class EnchantedList(Enchanted):
    """
    This is coordinates and other things like that
    """

    priority = 4

    def should_parse(self):
        return hasattr(self.val, '__iter__')

    def _str(self):
        if self.tag is None:
            return '(%s)' % self.val_str()
        else:
            return '(:%s %s)' % (self.tag_str(), self.val_str())

    def val_str(self):
        return " ".join([erepr(v) for v in self.val])

    def __iter__(self):
        return iter(self.val)


class EnchantedDate(Enchanted):
    """
    Date enchantment but using the overlay framework.
    """
    force_tag = "yyyymmdd"
    priority = 5

    def val_str(self):
        d, m, y = self.val
        return "%s%04d%02d%02d" % ("-" if y<0 else "" ,abs(y), m, d)

    def tag_str(self):
        return "yyyymmdd"

    def should_parse(self):
        if self.question and self.question.lower().endswith("date"):
            return True

        return self.tag == "yyyymmdd"

    def _range_middle(self, (d1, d2)):
        # Very impercise

        return tuple(int((i+j)/2) for i,j in zip(d1, d2))

    def parse_val(self, txt):
        if not isinstance(txt, basestring):
            return txt

        try:
            u'7 B.C.' in txt
        except:
            import pdb; pdb.set_trace()

        dor = overlay_parse.dates.just_props(txt, {'date'}, {'range'})

        if dor:
            if len(dor[0]) == 2:
                return self._range_middle(dor[0])

            return dor[0]


class _EnchantedDateVoting(EnchantedDate):
    priority = 5

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

            scores[d] = score+1

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
            if c*rs*re != 0 and c >= rs and c < re:
                return True

        return False

EnchantedDateVoting = _EnchantedDateVoting

class EnchantedStringDict(Enchanted):
    """
    Get a lispy dictionary of non-None items.
    """

    # Just so the test regexes match.
    reverse = True
    priority = 10

    def should_parse(self):
        return type(self.val) is dict

    def _str(self):
        if self.reverse:
            pairs =reversed(self.val.items())

        # XXX: NastyHack(TM). Replace the nonbreaking space with a space.
        return '(%s)' % " ".join([kv_pair(k, "\""+v.replace(unichr(160), " ") + "\"")
                                  for k,v in pairs
                                  if v is not None])

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

def enchant(tag, obj, result_from=None, **kw):
    """
    Return an appropriate enchanted object. reslut is true when we are
    enchanting a result. Sometimes tags mean different thigs in
    results. Also for now you always want to be enchanting.
    """

    if isinstance(obj, Enchanted):
        return obj

    for E in WIKIBASE_ENCHANTMENTS:
        ret = E(tag, obj, question=result_from, **kw)
        if ret:
            return ret

    raise NotImplementedError("Implement enchatment tag: %s, val: %s" % (tag, obj))

__all__ = ['enchant']
