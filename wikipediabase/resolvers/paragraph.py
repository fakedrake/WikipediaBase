from wikipediabase.resolvers.base import BaseResolver
from wikipediabase.util import get_article

class LifespanPragraphResolver(BaseResolver):
    """
    Resolve paragraph related stuff.
    """

    def __init__(self, *args, **kwargs):

        super(ParagraphResolver, self).__init__(*args, **kwargs)

    def resolve(self, article, attrirbute, **kw):
        """
        Resolve birth and death dates based on the first paragraph.
        """

        art = get_article(article)

        # The frst paragraph
        text = next(article.paragraphs())
        paren = first_paren(text)
