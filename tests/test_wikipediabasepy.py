from . import BaseTestCase

from wikipediabasepy import wikipediabasepy


class TestWikipediabasepy(BaseTestCase):

    def test_something(self):
        self.assertEquals(
            'Hello World!',
            wikipediabasepy(),
        )
