from itertools import chain

import re

def merge_rx(rx_list, name=None):
    if name:
        fmt = "(?P<%s>%%s)" % name
    else:
        fmt = "(%s)"

    return fmt % r"|".join(["(%s)" % t for t in rx_list])

def join_rx(rx_lists, sep=r"\s*"):
    rxs = [merge_rx(rxl) if hasattr(rxl, '__iter__') else rxl for rxl in rx_lists]
    return sep.join(rxs)

MONTH_NUM = r"(0?\d|1[0-2])"
DAY_NUM = r"([0-2]?\d|3[01])"
YEAR_NUM = r"(\d{4})"

MDY_RXF = (r"(?P<month>%s)" % MONTH_NUM, r"(?P<day>%s)" % DAY_NUM,
           r"(?P<year>%s)" % YEAR_NUM)
DMY_RXF = (r"(?P<day>%s)" % DAY_NUM, r"(?P<month>%s)" % MONTH_NUM,
           r"(?P<year>%s)" % YEAR_NUM)
YMD_RXF = (r"(?P<day>%s)" % DAY_NUM, r"(?P<month>%s)" % MONTH_NUM,
           r"(?P<year>%s)" % YEAR_NUM)

DATE_SPLITTERS = ["-", "/", "", r"\.", r"\|" ]

def _join_with(sep):
    return [r"\b%s\b" % sep.join(f) for f in [MDY_RXF, DMY_RXF, YMD_RXF]]

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
MONTH_GENERAL = merge_rx(MONTH_NAMES, name='month')

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
]

YEAR_GENERAL = merge_rx([join_rx([r"\d+", merge_rx([AD,BC,""])])], name='year')
DAY_FIRST_FULL = join_rx([DAY_GENERAL, "(of|)", MONTH_GENERAL, YEAR_GENERAL])
MONTH_FIRST_FULL = join_rx([MONTH_GENERAL, "(the|)", DAY_GENERAL, YEAR_GENERAL])

def date_parse(m):
    return (day(m.group('day')), month(m.group('month')), year(m.group('year')))

def year_parse(m):
    return (0, 0, year(m.group("year")))

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

FULL_DATES = [
    (DAY_FIRST_FULL, date_parse),
    (MONTH_FIRST_FULL, date_parse)] + \
    [(sf, date_parse) for sf in SHORT_FORMATS] + \
    [(YEAR_GENERAL, year_parse)]

def tokenize(txt, tokenizers=FULL_DATES):
    """
    Just get string representations of the dates you found.
    """

    global_rx = merge_rx([i for i,j in tokenizers])
    return [t[0] for t in re.findall(global_rx, txt)]

def parse(txt, tokenizers=FULL_DATES, yield_position=False):
    """
    Iterate over the dates found in text. More certain dates will
    appear first.
    """

    _txt = txt
    new_txt = ""
    cursor = 0

    for rx,f in tokenizers:
        if cursor:
            _txt = new_txt
            new_txt = ""
            cursor = 0

        for m in re.finditer(rx, _txt, re.I):
            new_txt += _txt[cursor:m.start()]
            cursor = m.end()

            if yield_position:
                yield (m.start(), m.end()), f(m)
            else:
                yield f(m)
