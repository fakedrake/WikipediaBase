from .ref import ConfigRef

class Configurable(object):
    """
    Superclass of an object that can have attributes that are
    references to a configuration object. They are evaluated lazily so
    changing the configuration in runtime will immediately change the
    entire system's behavior.
    """

    def __setattr__(self, attr, val):
        """
        If the attribute is a ConfigRef set it in the
        local_config_scope. Otherwise set it anywhere.
        """
        # Create a special dict with ConfigRefs
        if self.__dict__.get('local_config_scope', None) is None:
            self.__dict__['local_config_scope'] = {}

        # If we are setting a reference put it in the dict
        lcs = self.__dict__['local_config_scope']
        if isinstance(val, ConfigRef):
            lcs[attr] = val
            return

        # If we are overriding an existing ref delete it
        if attr in lcs:
            del lcs[attr]

        # fallback to normal set
        self.__dict__[attr] = val

    def __getattr__(self, attr):
        """
        If the attribute is available in the local_config_scope, take it
        from there and deref it.
        """

        lcs = self.__dict__.get('local_config_scope', {})
        if attr in lcs:
            return lcs[attr].deref()

        try:
            return self.__dict__[attr]
        except:
            raise AttributeError("'%s' has no attribute '%s'" %
                                 (str(self.__class__), attr))
