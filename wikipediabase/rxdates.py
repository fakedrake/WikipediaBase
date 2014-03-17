"""
Examples:

>>> MONTH_NAMES.search("22 jun", name="month", flags=re.I)
'jun'
"""


from rxbuilder import ConcatRx, Regex, OrRx

MONTH_NUM = OrRx(r"0?\d", r"1[012]", name="month")
DAY_NUM = OrRx(r"[0-2]?[1-9]", "[1-2]0", "3[01]", name="day")
YEAR_NUM4 = Regex(r"\d{4}", name="year")
DAY_NUM_ALL = DAY_NUM           # XXX: also numerics

SEPARATORS = ['-', '/', '.', '\\|', '']

DMY = OrRx(*[ConcatRx(DAY_NUM, MONTH_NUM, YEAR_NUM4, sep=s) for s in SEPARATORS])
MDY = ConcatRx(MONTH_NUM, DAY_NUM, YEAR_NUM4, sep=SEPARATORS)
YMD = ConcatRx(YEAR_NUM4, MONTH_NUM, DAY_NUM, sep=SEPARATORS)

# Note that these should not be case sensitive. But besides these
# dates are generally not letters so we can make everything case
# insensitive.
MONTH_NAMES_LONG = OrRx("January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December", name="month")
MONTH_NAMES_SHORT = OrRx("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", name="month")

MONTH_NAMES = OrRx(MONTH_NAMES_LONG, MONTH_NAMES_SHORT, name="month")

ADDC = OrRx("A\.?D\.?", "D\.?C\.?")
YEAR_NUM_ANY = Regex("\d+", name='year')
YEAR_ADDC_FULL = ConcatRx(YEAR_NUM_ANY, ADDC, name='year')
YEAR_FULL = OrRx(YEAR_ADDC_FULL, YEAR_NUM_ANY)

DAY_FIRST_FULL = DAY_NUM_ALL + r"\s+" + MONTH_NAMES + r"\s+" + YEAR_FULL
MONTH_FIRST_FULL = MONTH_NAMES + r"\s+" + DAY_NUM_ALL + r"\s+" + YEAR_FULL
MONTH_DAY_NO_YEAR = MONTH_NAMES + r"\s+" + DAY_NUM_ALL
DAY_MONTH_NO_YEAR = DAY_NUM_ALL + r"\s+" + MONTH_NAMES

DATE_RATINGS = [(.91,  MDY),
                (.92,  YMD),
                # (.853, DMY),
                # (.94,  DAY_FIRST_FULL),
                # (.95,  MONTH_FIRST_FULL),
                # (.86,  DAY_MONTH_NO_YEAR),
                # (.87,  MONTH_DAY_NO_YEAR),
            ]
