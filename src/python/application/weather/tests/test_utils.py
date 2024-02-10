from django.test import TestCase

from weather.utils import (
    get_cardinal_direction,
    LanguageType,
    UnitType,
)


class TestUtils(TestCase):

    def test_get_cardinal_direction(self):
        # happy path
        direction = get_cardinal_direction(degree=75)
        self.assertEqual(direction, 'East')
        # unhappy path
        direction = get_cardinal_direction(degree=None)
        self.assertIsNone(direction)

    def test_language_type_enum(self):
        self.assertEqual(LanguageType.GERMAN.value, 'de')

    def test_unit_type_enum(self):
        self.assertEqual(UnitType.METRIC.value, 'metric')
