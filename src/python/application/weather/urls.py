from django.urls import path
from .views import AsyncWeatherView

urlpatterns = [
    path('weather/', AsyncWeatherView.as_view(), name='weather'),
]
