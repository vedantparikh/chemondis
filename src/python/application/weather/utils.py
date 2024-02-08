from enum import Enum, unique


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
