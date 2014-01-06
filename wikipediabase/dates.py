from collections import defaultdict
import re

from enchanted import Enchanted, EnchantError

import dateutil


class EnchantedDate(Enchanted):
    """
    This is coordinates and other things like that
    """

    force_tag = 'yyyymmdd'
    allowed_tags = ['yyyymmdd']
    allowed_que = re.compile(r".*date$", re.I)

    def __init__(self, tag, date_txt, **kw):
        """
        Give the date in year, month day format and profit.
        """

        date = self.extract_date(date_txt)

        super(EnchantedDate, self).__init__(tag, date, **kw)
        self.log().info("Created an enchanted date obj: %s, tag: %s" \
                        % (date, self.tag))

    def extract_date(self, txt):
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
