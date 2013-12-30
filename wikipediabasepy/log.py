import logging
import sys

class Logger(logging.Logger):
    """
    Logn the way we like it.
    """

    def __init__(self, filename=None, name="WikipediaBase logger"):
        """
        Log into stdout.
        """

        super(Logger, self).__init__(name)

        if not filename:
            ch = logging.StreamHandler(sys.stdout)
        else:
            ch = logging.FileHandler(filename)

        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
        %(message)s')
        ch.setFormatter(formatter)
        self.addHandler(ch)
