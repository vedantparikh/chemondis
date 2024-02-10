from django.test import TestCase

from api.singletonmeta import SingletonMeta


class SingletonClass(metaclass=SingletonMeta):
    """Sample class using the SingletonMeta metaclass"""

    def __init__(self, value):
        self.value = value


class SingletonTestCase(TestCase):
    def test_singleton_instance(self):
        # Create two instances of SingletonClass
        instance1 = SingletonClass(value=1)
        instance2 = SingletonClass(value=2)

        # Both instances should be the same, as the SingletonMeta ensures singleton behavior
        self.assertIs(instance1, instance2)

        # Check the values to ensure they were properly initialized
        self.assertEqual(instance1.value, 1)
        self.assertEqual(instance2.value, 1)
