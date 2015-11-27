from wikipediabase.lispify import lispify_error, LispType
from wikipediabase.resolvers.base import MIN_PRIORITY, BaseResolver


class ErrorResolver(BaseResolver):

    """
    Yield an error message given that all else failed
    """

    priority = MIN_PRIORITY

    def resolve_error(self, cls, symbol, attr):
        if isinstance(attr, LispType):
            attr = attr.val
        else:
            attr = attr

        attr = attr.lower()

        # TODO: come up with a more descriptive error message
        return lispify_error('attribute-value-not-found', message='Unknown')
