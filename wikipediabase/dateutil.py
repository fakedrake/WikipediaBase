from itertools import chain, izip
from util import iwindow

import re

def merge_rx(rx_list, name=None):
    if name:
        fmt = "(?P<%s>%%s)" % name
    else:
        fmt = "(%s)"

    return fmt % r"|".join(["(%s)" % t for t in rx_list])

# Note the nongreedy space matching so that dates are just dates.
def join_rx(rx_lists, sep=r"\s*?", name=None):
    rxs = [merge_rx(rxl) if hasattr(rxl, '__iter__') else rxl for rxl in rx_lists]
    if not name:
        return sep.join(rxs)
    else:
        return "(?P<%s>%s)" % (name, sep.join(rxs))

# Dates
def _join_with(sep):
    return [r"\b%s\b" % sep.join(f) for f in [YMD_RXF, MDY_RXF, DMY_RXF]]

MONTH_NUM = r"(0?\d|1[0-2])"
DAY_NUM = r"([0-2]?\d|3[01])"
YEAR_NUM = r"(\d{4})"
MDY_RXF = (r"(?P<month>%s)" % MONTH_NUM, r"(?P<day>%s)" % DAY_NUM,
           r"(?P<year>%s)" % YEAR_NUM)
DMY_RXF = (r"(?P<day>%s)" % DAY_NUM, r"(?P<month>%s)" % MONTH_NUM,
           r"(?P<year>%s)" % YEAR_NUM)
YMD_RXF = (r"(?P<year>%s)" % YEAR_NUM, r"(?P<month>%s)" % MONTH_NUM,
           r"(?P<day>%s)" % DAY_NUM)
DATE_SPLITTERS = ["-", "/", "", r"\.", r"\|" ]
SHORT_FORMATS = list(chain(*[_join_with(c) for c in DATE_SPLITTERS]))

AD = r"A\.?D\.?"
BC = r"B\.?C\.?"

ST_NUMERICS = r"(11th|12th|13th|\d*[4-9]th|1st|2nd|3rd)"
DAY_NUMERICS = r"(11th|12th|13th|[012]?[4-9]th|[123]0th|[0-3]1st|[02]2nd|023rd)"
DAY_GENERAL = merge_rx([DAY_NUMERICS, DAY_NUM], name='day')

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
MONTH_NAMED = merge_rx(MONTH_NAMES, name='month')

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
]

YEAR_DENOTED = join_rx([r"((?<=\s)|\A)\d+", merge_rx([AD,BC])], name='year')
YEAR_GENERAL = join_rx([r"\d+", merge_rx([AD,BC,""])], name='year')

DAY_FIRST_FULL = join_rx([DAY_GENERAL, "(of|)", MONTH_NAMED, YEAR_GENERAL])
MISSING_DAY_FULL = join_rx([MONTH_NAMED, YEAR_GENERAL], sep=r"\s*(?:,|of|)\s*")
MONTH_FIRST_FULL = join_rx([MONTH_NAMED, "(the|)", DAY_GENERAL, YEAR_GENERAL], sep=r"\b\s*")

def grp(match, key):
    try:
        return match.group(key)
    except IndexError:
        return '0'

def date_parse(m):
    """
    The matcher m should have the keyword groups (day, month, year)
    """

    return (day(grp(m, 'day')), month(grp(m, 'month')), year(grp(m, 'year')))

def day(txt):
    if not txt:
        return 0

    return int(re.search("\d+", txt).group(0))

def year(txt):
    if not txt:
        return 0

    y = re.search("\d+", txt).group(0)

    sign = -1 if re.search(BC, txt) else 1
    return sign*int(y)

def month(txt):
    if not txt:
        return 0

    try:
        return int(txt)
    except ValueError:
        for i,m in enumerate(MONTH_NAMES):
            if re.match(m, txt, re.I):
                return (i % 12) + 1

    return 0

# Date and an float [0-1] showing how sure we are this is a date.
FULL_DATES = [
    (DAY_FIRST_FULL, 1),
    (MONTH_FIRST_FULL, 1),
    (MISSING_DAY_FULL, .9)] + \
    [(sf, .8) for sf in SHORT_FORMATS] + \
    [(YEAR_DENOTED, .6), (YEAR_GENERAL, .1)]

def tokenize(txt, tokenizers=FULL_DATES):
    """
    Just get string representations of the dates you found.
    """

    global_rx = merge_rx([i for i,j in tokenizers])
    return [t[0] for t in re.findall(global_rx, txt)]


# (rate, separating-rx-list, dates this translates to)
TIMESPAN_GROUPERS = [
    (.9, [r".*", r"\s*-\s*"], (0, 1)),
    (.9, [r".*", r"\s+to\s+"], (0, 1)),
    (.5, [r".*\b-\s*"], (-1, 0)),
    (.5, [r".*", r".*\b-\s*"], (0, -1))
]

class DateParsed(object):
    def __init__(self, data, txt):
        """
        You may pipe here the output of parse with positions like

        >>> d = DateParsed(parse(txt, yield_position=True), txt)
        """

        self.data = data
        self.txt = txt

    def format(self, date, ratings=True, full=False):
        """
        Return the date in the form (d,m,y) or a list of tuples (rating,
        date). Full means get a list of ((s,e), (r, (d,m,y))).
        """

        if full:
            return date

        pos, (r, d) = date
        if ratings:
            return (r, d)

        return d

    def dates(self, **kw):
        """
        A list of dates in the format specified by kw, see format()
        """

        return [self.format(d, **kw) for d in self.data]


    # XXX: opt into avoiding overlaps
    def dategroups(self, groupers=TIMESPAN_GROUPERS, dfilter=None,
                   grp_yield_position=False, **kw):
        """
        Get groups (rate, group) as defined in groupers. Dates in groups
        are formated as per format() using kw. dfilter filters the
        dates that are taken into account. It is a function single
        argument is a date of the full form: ((s,e),(r, (d,m,y))).

        grp_yield_position True means the return value should be ((s,
        e), (r, grp)) else it is just (r, grp).
        """

        cursor = 0
        intervals = []

        for (s,e), rd in sorted(filter(dfilter, self.data),
                                key=lambda d: d[1][0]):
            intervals.append((self.txt[cursor:s], ((s,e), rd)))
            cursor = e

        intervals.append((self.txt[cursor:], None))
        ret = []

        # Slide a window across intervals returning the dates that match
        for r, sep_ls, tr in groupers:
            for intervals_win in iwindow(intervals, len(sep_ls)):
                if self.win_match(sep_ls, intervals_win):
                    date_rate, grp = self._matching_dates(intervals_win,
                                                          tr, **kw)
                    if grp_yield_position:
                        # first interval, date, pos, start
                        s = intervals_win[0][1][0][0]
                        e = intervals_win[-1][1][0][1]

                        ret.append(((s, e), (r*date_rate, grp)))
                    else:
                        ret.append((r*date_rate, grp))

        return ret

    def _matching_dates(self, intervals, tr, default=(0,0,0),
                        default_rate=.5, rate_dates=True, **kw):
        ret = []
        rate = 1

        for i in tr:
            # Note that we may be mistakenly trying to match the last
            # interval which has inter[1]==None
            if i >= 0 and intervals[i][1]:
                pos, (r, d) = intervals[i][1]
                rate *= r

                ret.append(self.format(intervals[i][1], **kw))
            else:
                rate *= default_rate
                ret.append(default)

        if rate_dates:
            return (rate, ret)
        else:
            return ret

    def win_match(self, separators, intervals):
        for rx, (txt, d) in izip(separators, intervals):

            if not re.match(rx, txt):
                return False

        return True


def parse(txt, tokenizers=FULL_DATES, yield_position=False, favor=None, max_favor=0.01):
    """
    Return a tuple (weight, (d,m,y)) or ((s, e), (d,y,m)). More
    certain dates will appear first. Favor = {'start'|'end'|None} will
    slightly favor results that are found first last or will not. It
    will lineary favor things depending on position with max_favor.
    """

    _txt = txt
    ret = []

    # Greedy algorithm to maximize the correct dates.
    for rx, weight in sorted(tokenizers, key=lambda (x,y): y, reverse=True):

        for m in re.finditer(rx, _txt, re.I):
            if favor == 'start':
                w = weight + float(len(txt)-m.start())/len(txt) * max_favor
            elif favor == 'end':
                w = weight + float(m.end())/len(txt) * max_favor
            else:
                w = weight

            if yield_position:
                ret.append(((m.start(), m.end()), (w, date_parse(m))))
            else:
                ret.append((w, date_parse(m)))

            # Clear what we just found so we dont amtch it again
            _txt = _txt[:m.start()]+'\000'*(m.end()-m.start())+_txt[m.end():]

    return ret
