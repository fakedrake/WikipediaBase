try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import test_util

class BaseTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
