"""
Examples:

>>> MONTH_NAMES.search("22 jun", name="month", flags=re.I)
'jun'
"""


from rxbuilder import ConcatRx, Regex, OrRx

MONTH_NUM = OrRx(r"0?\d", r"1[012]", name="month")
DAY_NUM = OrRx(r"[0-2]?[1-9]", "[1-2]0", "3[01]", name="day")
YEAR_NUM4 = Regex(r"\d{4}", name="year")

SEPARATORS = r"[-/.|]?"

DMY = ConcatRx(DAY_NUM, MONTH_NUM, YEAR_NUM4, sep=SEPARATORS)
MDY = ConcatRx(MONTH_NUM, DAY_NUM, YEAR_NUM4, sep=SEPARATORS)
YMD = ConcatRx(YEAR_NUM4, MONTH_NUM, DAY_NUM, sep=SEPARATORS)

MONTH_NAMES_LONG = OrRx("January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December", name="month")

MONTH_NAMES_SHORT = OrRx("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", name="month")

MONTH_NAMES = OrRx(MONTH_NAMES_LONG, MONTH_NAMES_SHORT, name="month")
