from unittest import mock

from django.test import (
    override_settings,
    AsyncClient,
)
from rest_framework.test import APITestCase
from django.urls import reverse

from api.redis_client import get_redis

data = {'coord': {'lon': -94.04, 'lat': 33.44},
        'weather': [{'id': 804, 'main': 'Clouds', 'description': 'overcast clouds', 'icon': '04d'}], 'base': 'stations',
        'main': {'temp': 17.87, 'feels_like': 17.64, 'temp_min': 17.05, 'temp_max': 18.47, 'pressure': 1015,
                 'humidity': 74}, 'visibility': 10000, 'wind': {'speed': 5.14, 'deg': 190}, 'clouds': {'all': 100},
        'dt': 1707415689, 'sys': {'type': 2, 'id': 62880, 'country': 'US', 'sunrise': 1707397632, 'sunset': 1707436412},
        'timezone': -21600, 'id': 4133367, 'name': 'Texarkana', 'cod': 200}


@override_settings(ROOT_URLCONF='api.urls')
class TestAsyncWeather(APITestCase):

    def setUp(self) -> None:
        self.fake_redis = get_redis()
        super().setUp()

    def tearDown(self) -> None:
        self.fake_redis.flush_all()

    @mock.patch('weather.views.httpx.AsyncClient')
    async def test_async_weather_view_with_200_ok(self, mock_async_client):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = data

        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        url = reverse('weather') + f'?q=Texarkana'
        client = AsyncClient()
        response = await client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'city_name': 'Texarkana', 'temperature': 17.87, 'min_temperature': 17.05,
                                               'max_temperature': 18.47, 'humidity': 74, 'pressure': 1015,
                                               'wind_speed': 5.14, 'direction': 'South',
                                               'description': 'overcast clouds'}
                             )
        # test cache generated
        self.assertListEqual(self.fake_redis.get_all_keys(),
                             ['lang_en_q_Texarkana_units_metric'])

    @mock.patch('weather.views.httpx.AsyncClient')
    async def test_async_weather_view_with_exception(self, mock_async_client):
        self.fake_redis.flush_all()
        mock_response = mock.MagicMock()
        mock_response.status_code = 400

        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        url = reverse('weather') + f'?q=Texarkana????'
        client = AsyncClient()
        response = await client.get(url, format='json')

        self.assertEqual(response.status_code, 400)
