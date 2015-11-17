from __future__ import unicode_literals

import re

SKIP_PATTERNS = (
    re.compile(r"^:?image:", flags=re.I),
    re.compile(r"^:?file:", flags=re.I),
    re.compile(r"^:?TimedText:", flags=re.I),
    re.compile(r"^:?wikipedia:", flags=re.I),
    re.compile(r"^:?wiktionary:", flags=re.I),
    re.compile(r"^:?meta:", flags=re.I),
    re.compile(r"^:?category:", flags=re.I),
    re.compile(r"^:?portal:", flags=re.I),
    re.compile(r"^:?help:", flags=re.I),
    re.compile(r"^:?user:", flags=re.I),
    re.compile(r"^:?talk:", flags=re.I),
    re.compile(r"^:?media:", flags=re.I),
    re.compile(r"^:?mediawiki:", flags=re.I),
    re.compile(r"^:?template:", flags=re.I),
    re.compile(r"^:?book:", flags=re.I),
    re.compile(r"^:?List of", flags=re.I),
    re.compile(r"^:?Lists of", flags=re.I),
)

IGNORE_PATTERNS = SKIP_PATTERNS + (
    re.compile(r"^:?Arbitration in ", flags=re.I),
    re.compile(r"^:?Communications in ", flags=re.I),
    re.compile(r"^:?Constitutional history of ", flags=re.I),
    re.compile(r"^:?Economy of ", flags=re.I),
    re.compile(r"^:?Demographics of ", flags=re.I),
    re.compile(r"^:?Foreign relations of ", flags=re.I),
    re.compile(r"^:?Geography of ", flags=re.I),
    re.compile(r"^:?History of ", flags=re.I),
    re.compile(r"^:?Military of ", flags=re.I),
    re.compile(r"^:?Politics of ", flags=re.I),
    re.compile(r"^:?Transport in ", flags=re.I),
    re.compile(r"^:?Transportation in ", flags=re.I),
    re.compile(r"^:?Outline of ", flags=re.I),
    re.compile(r" in \d\d\d\d$", flags=re.I),
    re.compile(r"^\d\d\d\d in ", flags=re.I),
    re.compile(r"\(disamb", flags=re.I),
    re.compile(r"\{+", flags=re.I),
    re.compile(r"\}+", flags=re.I),
)


def should_skip(title):
    for p in SKIP_PATTERNS:
        if re.search(p, title):
            return True
    return False


def is_good_title(title):
    for p in IGNORE_PATTERNS:
        if re.search(p, title):
            return False
    return True


def chop_leading_determiners(title):
    """
    Remove leading determiners from title (the, a, an)
    """

    # Note: no regexp is perfect. The one used here considers 'the'
    # followed by any non-word character to be bad. This rules out
    # 'The-underdogs' and 'The.scene', which turn into 'the underdogs' and
    # 'the scene' after put-symbols, respectively. However, 'a'
    # at the beginning is only considered bad if the next character is a
    # space. This is meant to keep things like 'A. H. Robbins', which is
    # converted into 'a h robbins' by put-symbols.
    pattern = re.compile(r"^\W*(the\W|an\W|a )", flags=re.I)

    m = re.match(pattern, title)
    while m is not None:
        title = title[len(m.group(0)):]
        m = re.match(pattern, title)

    return title


def reverse_comma(synonym):
    """
    Reverse synonyms with a comma
    """

    # For now, we are only able to reverse synonyms that end in
    # [Tt]he|[Aa]n?, not all synonyms with a comma because of the case
    # when a comma is properly used, e.g.
    #     "11th/28th Battalion, the Royal Western Australia Regiment"
    #     "Tenzin Gyatso, the 14th Dalai Lama"
    # By only flipping synonyms that have an article at the end, we are
    # still able to correct:
    #     "Congo, Democratic Republic Of The"
    #     "Martyrs, Acts of the"
    #     "Golden ratio, the"
    # The following are incorrectly reversed:
    # "a" could be the letter "a" as in "Class A"
    #     e.g. "Scavenger receptors, class a"
    # "a" could be a preposition in French or Italian
    #     e.g. "Bernadine a Piconio": "Piconio, Bernadine a"
    # In addition, "an" and "the" could be used in another language, such
    # as the French word for tea, "the" (with a lost accent on the e).

    m = re.search(r', (.* )?([Tt]he|[Aa]n?)$', synonym)
    if m:
        split = synonym.split(',')
        if len(split) == 2:
            split = map(lambda s: s.strip(), split)
            synonym = split[1] + " " + split[0]
    return synonym


def clean_synonym(title):
    title = title.strip()

    try:
        last_s = title.rindex("'s")
        if last_s == len(title) - 2:
            title = title[:-2]
    except ValueError:
        pass

    title = title.replace("\\\\", "\\ ")
    title = title.replace("''", "'")

    title = reverse_comma(title)
    title = chop_leading_determiners(title)

    # replace multiple spaces (including nbsp) with a single space
    title = re.sub(r'\s+', ' ', title, flags=re.U)

    return title


def get_synonyms(symbol):
    synonyms = [symbol]

    without_parens = re.sub(r'\(.*?\)', '', symbol)
    if without_parens != symbol:
        synonyms.append(without_parens)

    synonyms = map(clean_synonym, synonyms)

    # delete synonyms with no word characters
    synonyms = filter(lambda s: re.match(r'^\W*$', s) is None, synonyms)

    return synonyms
