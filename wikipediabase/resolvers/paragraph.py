import overlay_parse

from .base import BaseResolver
from ..util import get_article
from ..enchantments import enchant, Enchanted

def iter_paren(text, delim=None):
    """
    Iterate over the top level parnetheses of the text.
    """

    depth = 0
    first_paren = None

    for i, c in enumerate(text):
        if c == "(":
            depth += 1
            if depth == 1:
                first_paren = i+1

        elif c == ")" and depth > 0:
            if depth == 1:
                yield (first_paren, i)

            depth -= 1

        if depth == 0 and text[i:].startswith(delim):
            break

def first_paren(text):
    for s,e in iter_paren(text, "."):
        return text[s:e]


class LifespanParagraphResolver(BaseResolver):
    """
    Resolve paragraph related stuff.
    """

    priority = 9

    def __init__(self, *args, **kwargs):

        super(LifespanParagraphResolver, self).__init__(*args, **kwargs)

    def resolve(self, article, attribute, **kw):
        """
        Resolve birth and death dates based on the first paragraph.
        """

        if isinstance(attribute, Enchanted):
            attr = attribute.val.lower()
        else:
            attr = attribute.lower()

        if attr == 'short-article':
            return get_article(article).paragraphs()[0]

        if attr not in ("birth-date", "death-date"):
            return None

        art = get_article(article)

        # The frst paragraph
        text = art.paragraphs()[0]
        for s,e in iter_paren(text, "."):
            paren = text[s:e]

            for ovl in overlay_parse.dates.just_ranges(paren):
                if attr == 'birth-date':
                    return enchant('yyyymmdd' , ovl[0])
                elif attr == 'death-date':
                    return enchant('yyyymmdd' , ovl[1])

            # If there is just one date and we need a birth date, get
            # that.
            if attr == 'birth-date':
                for ovl in overlay_parse.dates.just_dates(paren):
                    return enchant('yyyymmdd', ovl)
