from django.test import (
    override_settings,
    AsyncClient,
)
from unittest import mock
from rest_framework.test import APITestCase
from django.urls import reverse

from weather.views import AsyncWeatherView


data = {'coord': {'lon': -94.04, 'lat': 33.44},
        'weather': [{'id': 804, 'main': 'Clouds', 'description': 'overcast clouds', 'icon': '04d'}], 'base': 'stations',
        'main': {'temp': 17.87, 'feels_like': 17.64, 'temp_min': 17.05, 'temp_max': 18.47, 'pressure': 1015,
                 'humidity': 74}, 'visibility': 10000, 'wind': {'speed': 5.14, 'deg': 190}, 'clouds': {'all': 100},
        'dt': 1707415689, 'sys': {'type': 2, 'id': 62880, 'country': 'US', 'sunrise': 1707397632, 'sunset': 1707436412},
        'timezone': -21600, 'id': 4133367, 'name': 'Texarkana', 'cod': 200}


@override_settings(ROOT_URLCONF='api.urls')
class MyAsyncTestCase(APITestCase):

    @mock.patch.object(AsyncWeatherView, '_fetch_data')
    async def test_async_view(self, mock_fetch_data):
        mock_fetch_data.json().side_effect = data
        mock_fetch_data.status_code.side_effect = 200
        url = reverse('weather') + f'?lat=40&lon=50'
        client = AsyncClient()
        response = await client.get(url, format='json')

        self.assertEqual(response.status_code, 200)