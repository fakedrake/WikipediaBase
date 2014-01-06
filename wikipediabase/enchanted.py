from log import Logging

RESULT_TAG_MAP = dict(code="html")
DATE_REGEX = r"(\d{4})\|(\d{1,2})\|(\d{1,2})\b"

class Enchanted(Logging):
    """
    Enchanted objects are objets that come from or translate to
    objects of the sort ((:tag obj)). Subclass this and update
    enchant() to create your own.

    When subclassing use default_tag and force_tag to enforce or
    default to a tag.
    """

    default_tag = "html"
    force_tag = None
    allowed_tags = None
    allowed_que = None

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
    def with_tag(cls, tag):
        """
        Check if it is possible to enchant an object with this tag using
        this enchantment (aka this Enchanted class). In subclasses you
        may override this altogether or use the 'allowed_tags' class
        attribute which is a list of allowed tags. If it is None then
        just return true.
        """

        if cls.allowed_tags is not None:
            return tag.lower() in cls.allowed_tags

        return True

    @classmethod
    def with_que(cls, que):
        """
        Like with_tag() but checks if the que given is ok with this
        enchantment. 'allowed_que' is a regex.
        """

        if cls.allowed_que is not None:
            return re.match(cls.allowed_que, que)

        return True

def multiplex(ans, tag, que, enchantments):
    """
    Given 'ans', the text that contains the information we are looking
    for or the actual object we are enchanting, it's tag, the question
    that it came from (the attribute of the query) and a list of
    Enchanted classes that implement 'with_tag' and 'with_que' return
    an instance of the correct one that does not raise EnchantError.
    """

    for E in enchantments:
        if E.with_tag(tag):
            try:
                return E(tag, ans)
            except EnchantError:
                log.info("Failed to enchant (:%s '%s') with %s" \
                         % (tag, ans, E.__name__))

    for E in enchantments:
        if E.with_que(que):
            try:
                return E(tag, ans)
            except EnchantError:
                log.info("Failed to enchant (:%s '%s') with %s coming \
                from que %s" % (tag, ans, E.__name__, que))
