from .base import BaseResolver
from ..util import get_article


def first_paren(text):
    """
    If the first sentence in the text has parentheses return those. If
    not return None.
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
                return text[first_paren:i]

            depth -= 1

        elif c == "." and depth == 0:
            return None

class LifespanPragraphResolver(BaseResolver):
    """
    Resolve paragraph related stuff.
    """

    priority = 9

    def __init__(self, *args, **kwargs):

        super(LifespanPragraphResolver, self).__init__(*args, **kwargs)

    def resolve(self, article, attrirbute, **kw):
        """
        Resolve birth and death dates based on the first paragraph.
        """

        art = get_article(article)

        # The frst paragraph
        text = next(art.paragraphs())
        paren = first_paren(text)
