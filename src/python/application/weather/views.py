import httpx
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from api.redis_client import get_redis
from weather.serializers import (
    WeatherQuerySerializer,
    WeatherSerializer,
)
from weather.utils import get_cardinal_direction


class AsyncWeatherView(View):
    redis = get_redis()

    @swagger_auto_schema(
        query_serializer=WeatherQuerySerializer(),
        responses={
            status.HTTP_200_OK: WeatherQuerySerializer(),
        },
    )
    async def get(self, request, *args, **kwargs) -> JsonResponse:
        # Extract query parameters from the request
        query_serializer = WeatherQuerySerializer(data=request.GET.dict())
        if not query_serializer.is_valid():
            return JsonResponse(data=query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        query_params = query_serializer.data
        sorted_query_params = dict(sorted(query_params.items()))
        redis_key = '_'.join([f'{key}_{value}' for key, value in sorted_query_params.items()])
        from_redis = self.redis.get(redis_key)

        if from_redis:
            return JsonResponse(status=status.HTTP_200_OK, data=from_redis)

        # adds api key into query parameter
        query_params['appid'] = settings.API_KEY

        # Make an asynchronous HTTPS request with query parameters
        try:
            response = await self._fetch_data(query_params)
        except Exception as e:
            error_message = f'Error making request to API: {str(e)}'
            return JsonResponse({'status': 'error', 'error_message': error_message})

        data = response.json()
        processed_data = await self._process_data(data=data)
        serializer = WeatherSerializer(data=processed_data)
        if serializer.is_valid():
            data = serializer.data
            # store in redis cache
            self.redis.set(redis_key, data)
            return JsonResponse(data=data, status=response.status_code)

        return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    async def _fetch_data(query_params: dict):
        async with httpx.AsyncClient() as client:
            # Make the asynchronous GET request with query parameters
            response = await client.get(settings.DATA_ACCESS_URL, params=query_params)

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
