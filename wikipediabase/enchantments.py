import re

from enchanted import Enchanted, multiplex
from dates import EnchantedDate

class EnchantedString(Enchanted):
    base_rate = 0.1
    def _str(self):
        return "((:%s \"%s\"))" % ("html" if self.tag == "code" else self.tag,
                                   re.sub("[\[\]]", "", self.val))


class EnchantedList(Enchanted):
    """
    This is coordinates and other things like that
    """

    def _str(self):
        return "((:%s %s))" % (self.tag, " ".join(self.val))


def enchant(tag, obj, result_from=None, compat=True, log=None):
    """
    Return an appropriate enchanted object. reslut is true when we are
    enchanting a result. Sometimes tags mean different thigs in
    results. Also for now you always want to be enchanting.
    """

    return multiplex(obj, tag, result_from,
                     [EnchantedDate, EnchantedString, EnchantedList],
                     log=log)
