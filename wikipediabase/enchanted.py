from log import Logging

import re

RESULT_TAG_MAP = dict(code="html")
DATE_REGEX = r"(\d{4})\|(\d{1,2})\|(\d{1,2})\b"


class EnchantError(Exception):
    pass

class Enchanted(Logging):
    """
    Enchanted objects are objets that come from or translate to
    objects of the sort ((:tag obj)). Subclass this and update
    enchant() to create your own.

    When subclassing use default_tag and force_tag to enforce or
    default to a tag.
    """

    default_tag = "html"
    base_rate = 0
    force_tag = None
    allowed_tags = None
    tag_rate = 0.6
    allowed_que = None
    que_rate = 0.3

    def __init__(self, tag, val=None, compat=True):
        if self.force_tag:
            self.tag = self.force_tag
        else:
            self.tag = tag or self.default_tag

        self.compat = compat
        self.val = val

    def _str(self):
        return str(self.val)

    def __str__(self):
        if self.val is not None:
            if self.compat:
                return self._str()
            else:
                return str(self.val)

        return "(error 'no-value-found)"

    def __repr__(self):
        return "<%s object (:%s %s)>" % (self.__class__, self.tag, self.val)

    @staticmethod
    def keyattr(enchanted):
        """
        Given an Enchanted object return it's enchant key and value.
        """

        if isinstance(enchanted, Enchanted):
            return (enchanted.tag, enchanted.val)
        else:
            return (None, enchanted)


    @classmethod
    def rate(cls, que, tag, ans):
        """
        0-1 how good would this enchantment be for this particular value.
        """

        r = cls.base_rate

        if cls.allowed_tags and tag and tag in cls.allowed_tags:
            r += cls.tag_rate

        if cls.allowed_que and que and re.match(cls.allowed_que, que):
            r += cls.que_rate

        return r


def multiplex(ans, tag, que, enchantments, log=None):
    """
    Enchant an answer based on the `enchantments` ratings.

    :param ans: The answer yielded from wikipedia.
    :param tag: The tag {html,code,...}. This is the tag Enchanted uses
    :param que: This is also passed to Enchanted to rate.
    :param enchantments: A list of Enchanted classes to choose from
    :param log: A logger.
    :returns: The best enchanted object you could find or None.
    """

    ratings = [(E.rate(que, tag, ans), E) for E in enchantments]

    for r, E in sorted(ratings, key=lambda (x,y): x, reverse=True):
        try:
            return E(tag, ans)
        except EnchantError:
            if log:
                log.info("Failed to enchant (:%s '%s') with %s" \
                         % (tag, ans, E.__name__))
