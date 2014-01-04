from datetime import datetime as date
from dateutil.parser import parse as dparse
import re

from log import Logging

RESULT_TAG_MAP = dict(code="html")
DATE_REGEX = r"(\d{4})\|(\d{1,2})\|(\d{1,2})\b"

class Enchanted(Logging):
    """
    Enchanted objects are objets that come from or translate to
    objects of the sort ((:tag obj)). Subclass this and update
    enchant() to create your own.

    When subclassing use default_tag and force_tag to enforce or
    default to a tag.
    """

    default_tag = "html"
    force_tag = None

    def __init__(self, tag, val=None, compat=True):
        if self.force_tag:
            self.tag = self.force_tag
        else:
            self.tag = tag or self.default_tag

        self.compat = compat
        self.val = val

    def _str(self):
        return str(self.val)

    def __str__(self):
        if self.val is not None:
            if self.compat:
                return self._str()
            else:
                return str(self.val)

        return "(error 'no-value-found)"

    def __repr__(self):
        return "<%s object (:%s %s)>" % (self.__class__, self.tag, self.val)

    @staticmethod
    def keyattr(enchanted):
        if isinstance(enchanted, Enchanted):
            return (enchanted.tag, enchanted.val)
        else:
            return (None, enchanted)


class EnchantedString(Enchanted):
    def _str(self):
        return "((:%s \"%s\"))" % (self.tag, re.sub("[\[\]]", "", self.val))


class EnchantedList(Enchanted):
    """
    This is coordinates and other things like that
    """

    def _str(self):
        return "((:%s %s))" % (self.tag, " ".join(self.val))


class EnchantedDate(Enchanted):
    """
    This is coordinates and other things like that
    """

    def __init__(self, tag, date, **kw):
        """
        Give the date in year, month day format and profit.
        """

        super(EnchantedDate, self).__init__(tag, date, **kw)
        self.log().info("Created an enchanted date obj: %s, tag: %s" \
                        % (date, self.tag))


    def date_string(self):
        if hasattr(self.val, 'strftime'):
            m = re.match(r"(\d{4})-(\d{2})-(\d{2}).*", self.val.isoformat())
            return "".join(m.groups())

        return self.val

    def _str(self):
        return "((:%s %s))" % (self.tag, self.date_string())

    @staticmethod
    def extract_date(tag, string, result_from=None, log=None):
        """
        Try to extract a date out of the given string.
        """

        dt = re.search(DATE_REGEX, string)
        if dt:
            return ("yyyymmdd", date(year=int(dt.group(1)),
                                     month=int(dt.group(2)), day=int(dt.group(3))))


        # The tag doesnt force and the result doesnt force date parsing
        if not (tag and tag.lower == "yyyymmdd")  and \
           not (result_from and "date" in result_from):
            if log:
                log.info("No reason to keep looking for a date: %s \
                (tag: %s, result_from: %s)" % (string, tag, result_from))

            return (None, None)

        # Make some attempts to extract a date

        # We want 0 at the and so no dateutil can help
        if re.match(r"^\d{4}$", string):
            if log:
                log.info("Found just a year: "+string)

            return ('yyyymmdd', string+"0000")

        dstring = re.sub("[{{}}]", " ", string)
        if log:
            log.info("Attempting fuzziness on '%s'" % dstring)

        # There will rarely be two dates in the block
        for ds in dstring.split('|'):
            val = fuzzy_dates(ds, log=log)
            if val:
                return ("yyyymmdd", val)

        # It doesnt HAVE to be a date
        return (None, None)


def fuzzy_dates(string, log=None):
    # Probably the nastiest hack you will encounter.
    class Trojan(object):
        def replace(self, **kw):
            if 'month' in kw or 'day' in kw or 'year' in kw:
                self.found = True
                self.kw = kw

        def tget(self, kw, digs):
            # Hacking is my business and business is good
            return ("%%0%dd"%digs) % self.kw.get(kw,0)

    trojan = Trojan()
    try:
        dparse(string, fuzzy=True, default=trojan)
        if hasattr(trojan,'found'):
            ret  = trojan.tget("year",4)+trojan.tget("month",2)+trojan.tget("day",2)
            if log:
                log.info("Found date %s on '%s'" % (ret, string))
            return ret
        else:
            if log:
                log.info("Failed fuzzy date mathcing on '%s'" % string)
    except (TypeError, UnicodeDecodeError) as e:
        # Exceptions are hard to foresee
        if log:
            log.info("Could not find date in '%s'" % string)
            log.info("Exception: " + str(e))



def enchant(tag, obj, result_from=None, compat=True, log=None):
    """
    Return an appropriate enchanted object. reslut is true when we are
    enchanting a result. Sometimes tags mean different thigs in
    results. Also for now you always want to be enchanting.
    """

    if isinstance(obj, Enchanted):
        return obj

    if result_from and tag in RESULT_TAG_MAP:
        tag = RESULT_TAG_MAP[tag]

    if hasattr(obj, "__iter__"):
        return EnchantedIterable(tag, obj, compat=compat)

    dtag, date = EnchantedDate.extract_date(tag, obj, result_from=result_from, log=log)
    if date:
        if log:
            log.info("Extract date '%s' from '%s'" % (date, obj))
            return EnchantedDate(dtag, date, compat=compat)

    if isinstance(obj, str):
        return EnchantedString(dtag, obj, compat=compat)


    return Enchanted(tag, obj, compat=compat)
