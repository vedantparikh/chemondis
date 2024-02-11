from enum import Enum

from rest_framework import serializers

from weather.utils import (
    UnitType,
    LanguageType,
)


class BaseSerializer(serializers.Serializer):
    """Base Serializer for all Serializer implementations."""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class QuerySerializer(BaseSerializer):
    """Base Serializer for all QuerySerializer implementations."""


class EnumField(serializers.ChoiceField):
    """A choice field that uses an enum as the possible values"""

    def __init__(self, **kwds):
        self.enum = kwds.pop('enum', None)
        if not self.enum:
            raise ValueError('You must pass a value for `enum`.')
        if not issubclass(self.enum, Enum):
            raise ValueError('The value passed for `enum` is not an Enum')
        choices = [(entry, entry.name) for entry in self.enum]

        super().__init__(choices, **kwds)

    def to_internal_value(self, data):
        try:
            return self.enum(data)
        except ValueError:
            raise serializers.ValidationError(
                f'Invalid choice: {data}. Must be one of {", ".join(entry.value for entry in self.enum)}.')

    def to_representation(self, value):
        return value.value


class WeatherQuerySerializer(QuerySerializer):
    """Query serializer for the weather view."""

    q = serializers.CharField(help_text='City name, state code and country code divided by comma.', required=True)
    units = EnumField(help_text='Unit type for the weather data.', required=False, enum=UnitType,
                      default=UnitType.METRIC)
    lang = EnumField(help_text='Language type for the weather data.', required=False, enum=LanguageType,
                     default=LanguageType.ENGLISH)


class WeatherSerializer(BaseSerializer):
    """Weather Serializer."""

    city_name = serializers.CharField(help_text='Name of the city.', required=False)
    temperature = serializers.FloatField(help_text='Current temperature in the city.', required=False)
    min_temperature = serializers.FloatField(help_text='Current day minimum temperature in the city.', required=False)
    max_temperature = serializers.FloatField(help_text='Current day maximum temperature in the city.', required=False)
    humidity = serializers.IntegerField(help_text='Current day humidity in the city.', required=False)
    pressure = serializers.IntegerField(help_text='Current day atmospheric pressure in the city.', required=False)
    wind_speed = serializers.FloatField(help_text='Current day wind speed in the city.', required=False)
    direction = serializers.CharField(help_text='Current day wind direction in the city.', required=False)
    description = serializers.CharField(help_text='Current day weather description in the city.', required=False)
