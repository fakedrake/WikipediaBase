import re

import overlay_parse

class Enchanted(object):
    """
    An enchanted object's string representation is something that
    START understands. Also its `val` attribute is something that
    makes sense to python.

    Note that not only answers but also questions are enchanted.
    """

    force_tag = None

    def __init__(self, tag, val, question=None):
        """
        Enchant a piece of data. Throws EnchantError on failure.
        """

        self.tag = tag
        self.question = question

        if self.should_parse():
            self.val = self.parse_val(val)
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
        return "<%s object (:%s %s)>" % (self.__class__, self.tag, self.val)

    def __str__(self):
        if self:
            return "((:%s %s))" % (self.tag_str(), self.val_str())

    def val_str(self):
        return str(self.val)

    def tag_str(self):
        return self.tag or "html"

    def __nonzero__(self):
        return self.val is not None


class EnchantedString(Enchanted):
    def tag_str(self):
        if self.tag == "code":
            return "html"

        return self.tag

    def val_str(self):
        return "\"%s\"" % re.sub(r"[[\]]" , "", self.val)


class EnchantedList(Enchanted):
    """
    This is coordinates and other things like that
    """

    def val_str(self):
        return " ".join(self.val)


class EnchantedDate(Enchanted):
    """
    Date enchantment but using the overlay framework.
    """
    force_tag = "yyyymmdd"

    def val_str(self):
        d, m, y = self.val
        return "%04d%02d%02d" % (y, m, d)

    def tag_str(self):
        return "yyyymmdd"

    def should_parse(self):
        if self.question and self.question.lower().endswith("date"):
            return True

        return self.tag == "yyyymmdd"

    def _range_middle(self, (d1, d2)):
        # Very impercise

        return tuple(int((i+j)/2) for i,j in zip(d1, d2))

    def _in_range(self, date, rng):
        sd, ed = rng

        for c, rs, re in reversed(zip(date, sd, ed)):
            # If all are defined and c is between [grs, re)
            if c*rs*re != 0 and c >= rs and c < re:
                return True

        return False


    def parse_val(self, txt):
        """
        Return of the extracted date the one appearing most often.
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

        # if "BC" in txt:
        #     import ipdb; ipdb.set_trace()

        try:
            return max(dates, key=lambda d: scores[d])
        except ValueError:
            if ranges:
                return self._range_middle(ranges[0])

        return None

def enchant(tag, obj, result_from=None, compat=True, log=None):
    """
    Return an appropriate enchanted object. reslut is true when we are
    enchanting a result. Sometimes tags mean different thigs in
    results. Also for now you always want to be enchanting.
    """

    for E in [EnchantedDate, EnchantedString, EnchantedList]:
        ret = E(tag, obj, question=result_from)
        if ret:
            return ret
