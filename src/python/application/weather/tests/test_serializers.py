from django.test import TestCase

from weather.serializers import (
    WeatherQuerySerializer,
    WeatherSerializer,
)


class TestSerializers(TestCase):

    def test_weather_query_serializer(self):
        # test only required query parameters
        query_params = {
            'q': 'Texarkana',
        }
        serializer = WeatherQuerySerializer(data=query_params)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        # check default query parameters
        self.assertDictEqual(serializer.data, {'q': 'Texarkana', 'units': 'metric', 'lang': 'en'})

        # test all query parameters
        query_params = {
            'q': 'Texarkana',
            'units': 'standard',
            'lang': 'it',
        }
        serializer = WeatherQuerySerializer(data=query_params)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(serializer.data, {'q': 'Texarkana', 'units': 'standard', 'lang': 'it'})

        # test unhappy path
        # test with wrong units and lang
        query_params = {
            'lat': 30,
            'lon': 40,
            'units': 'random units',
            'lang': 'UK',
        }
        serializer = WeatherQuerySerializer(data=query_params)
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

    def test_weather_serializer(self):
        data = {
            'city_name': 'Texarkana',
            'temperature': 16.77,
            'min_temperature': 15.14,
            'max_temperature': 18.04,
            'humidity': 84,
            'pressure': 1014,
            'wind_speed': 4.12,
            'direction': 'South',
            'description': 'broken clouds',
        }
        serializer = WeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        # test with invalid data
        invalid_data = {
            'city_name': 'Texarkana',
            'temperature': 16.77,
            'min_temperature': 15.14,
            'max_temperature': 18.04,
            'humidity': 84.44,
            'pressure': 1014,
            'wind_speed': 4.12,
            'direction': 28,
            'description': 'broken clouds',
        }
        serializer = WeatherSerializer(data=invalid_data)
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)
