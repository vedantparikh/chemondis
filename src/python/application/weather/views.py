import httpx
from django.views import View
from django.http import JsonResponse
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from api.settings import DATA_ACCESS_URL, API_KEY
from weather.serializers import WeatherQuerySerializer, WeatherSerializer
from weather.utils import get_cardinal_direction


class AsyncHttpsView(View):
    @swagger_auto_schema(
        query_serializer=WeatherQuerySerializer(),
        responses={
        },
    )
    async def get(self, request, *args, **kwargs):
        # Extract query parameters from the request
        query_serializer = WeatherQuerySerializer(data=request.GET.dict())
        query_serializer.is_valid(raise_exception=True)
        query_params = query_serializer.data
        query_params['appid'] = API_KEY

        # Make an asynchronous HTTPS request with query parameters
        response = await self._fetch_data(query_params)

        if response.status_code == status.HTTP_200_OK:
            # Process the response as needed
            data = response.json()
            processed_data = await self._process_data(data=data)
            serializer = WeatherSerializer(data=processed_data)
            serializer.is_valid(raise_exception=True)
            return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

        return JsonResponse(status=response.status_code, data=response.text)



    @staticmethod
    async def _fetch_data(query_params):
        async with httpx.AsyncClient() as client:
            # Make the asynchronous GET request with query parameters
            response = await client.get(DATA_ACCESS_URL, params=query_params)

            # Check if the request was successful (status code 2xx)
            response.raise_for_status()

            return response

    @staticmethod
    async def _process_data(data: dict) -> dict:
        weather = data.get('weather', [])
        processed_data = {
            'city_name': data.get('name'),
            'temperature': data.get('main', {}).get('temp'),
            'min_temperature': data.get('main', {}).get('temp_min'),
            'max_temperature': data.get('main', {}).get('temp_max'),
            'humidity': data.get('main', {}).get('humidity'),
            'pressure': data.get('main', {}).get('pressure'),
            'wind_speed': data.get('wind', {}).get('speed'),
            'direction': get_cardinal_direction(degree=data.get('wind', {}).get('deg')),
            'description': weather[0].get('description') if weather else None,
        }

        return processed_data
