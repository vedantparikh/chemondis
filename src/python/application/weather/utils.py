from enum import Enum, unique
from typing import Optional


class BaseEnum(str, Enum):
    """Base Enum for all enums used in models.

    Inherited from `str` as this gives JSON serialization.
    """

    def __str__(self):
        return "%s" % self._value_


@unique
class UnitType(BaseEnum):
    """Contains different types of units."""

    STANDARD = 'standard'

    METRIC = 'metric'

    IMPERIAL = 'imperial'


@unique
class LanguageType(BaseEnum):
    """Contains different types of languages."""

    ENGLISH = 'en'

    GERMAN = 'de'

    ITALIAN = 'it'


def get_cardinal_direction(degree: Optional[int]) -> Optional[str]:
    """Returns the cardinal direction name based on the degree."""

    if not degree:
        return None
    directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest', 'North']
    index = round(degree / 45) % 8
    return directions[index]
