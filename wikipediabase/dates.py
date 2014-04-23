from collections import defaultdict
import re
import overlay_parse

from enchanted import Enchanted, EnchantError

import dateutil


class EnchantedDate(Enchanted):
    """
    This is coordinates and other things like that
    """

    base_rate = 0.1
    force_tag = 'yyyymmdd'
    allowed_tags = ['yyyymmdd']
    allowed_que = re.compile(r".*date$", re.I)

    def __init__(self, tag, date_txt, **kw):
        """
        Give the date in year, month day format and profit.
        """

        if tag == self.force_tag:
            self._is_valid = True
            date = self._extract_date(date_txt)
        else:
            self._is_valid = False
            return

        super(EnchantedDate, self).__init__(tag, date, **kw)
        self.log().info("Created an enchanted date obj: %s, tag: %s from %s" \
                        % (date, self.tag, date_txt))

    def __nonzero__(self):
        return self._is_valid

    def _extract_date(self, txt):
        """
        Return of the extracted date the one appearing most often.
        """

        d = defaultdict(lambda :0)

        for w, i in dateutil.parse(txt, favor='start'):
            d[i] += w

        if len(d) == 0:
            raise EnchantError("No dates found in string '%s" % txt)

        self.log().info("Found dates: %s" % d.items())

        return max(d.items(), key=lambda (x,y): y)[0]

    def date_string(self):
        d,m,y = self.val
        return "%s%04d%02d%02d" % ("-" if y<0 else "",abs(y),m,d)

    def _str(self):
        return "((:%s %s))" % (self.tag, self.date_string())


class EnchantedOverlayDate(EnchantedDate):
    """
    Date enchantment but using the overlay framework.
    """

    def _range_middle(self, (d1, d2)):
        # Very impercise

        return tuple(int((i+j)/2) for i,j in zip(d1, d2))

    def _extract_date(self, txt):
        """
        Return of the extracted date the one appearing most often.
        """

        dr = overlay_parse.dates.just_props(txt, {'date'}, {'range'})
        if dr:
            ret = dr[0]
        else:
            raise EnchantError("Failed to find date in '%s'" % txt)

        if len(ret) == 2:
            return self._range_middle(ret)

        return ret
