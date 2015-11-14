import re

from wikipediabase.web_string.base import WebString
from wikipediabase.web_string.symbol import SymbolString
from wikipediabase.config import configuration

class MarkupString(WebString):
    """
    Some basic mediawiki parsing stuff.
    """

    def __init__(self, data, configuration=configuration):
        super(MarkupString, self).__init__(data, configuration=configuration)

    def redirect_target(self):
        """
        A SymbolString of the redirect target or None.
        """
        redirect_match = re.search(r"^\s*#\s*redirect\s*\[\[(.*)\]\]\s*$",
                                   self.raw(), re.I | re.MULTILINE)
        if redirect_match:
            return SymbolString(redirect_match.group(1).strip())

    def raw(self):
        return self.data

    def unlink(self):
        """
        Remove markup links
        """
        return re.sub(r"\[+(.*\||)(?P<content>.*?)\]+", r'\g<content>',
                      self.data)
