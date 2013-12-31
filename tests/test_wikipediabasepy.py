from . import BaseTestCase

from wikipediabase import wikipediabase


class TestWikipediabase(BaseTestCase):

    def test_something(self):
        self.assertEquals(
            'Hello World!',
            wikipediabase(),
        )
