from unittest import TestCase
from get_steps_schema import get_steps_schema

class TestGet_steps_schema(TestCase):

    def test_get(self):

        get = get_steps_schema()

        returnData = get.get("4418")

        assert (len(returnData['steps']) == 20)
