from django.test import TestCase

from api.redis_client import get_redis


class TestRedisClient(TestCase):

    def setUp(self) -> None:
        self.redis = get_redis()
        self.redis.set('test1', 'data1')
        self.redis.set('test5', 'data5')
        self.redis.set('test55', 'data5')
        self.redis.set('some_test51_text', 'data5')
        self.redis.set('test25', 'data5')

    def test_set_method(self):
        self.assertTrue(self.redis.set('test_set1', 'data1'))
        self.assertTrue(self.redis.set('test_set2', 5))

        with self.assertRaises(TypeError):
            self.redis.set('missing_value', )

    def test_get_method(self):
        self.assertEqual(self.redis.get('test1'), 'data1')
        self.assertEqual(self.redis.get('test4'), None)

    def test_exists_method(self):
        self.assertEqual(self.redis.exists('test1'), 1)
        self.assertEqual(self.redis.exists('notAvailable'), 0)

    def test_delete_method(self):
        self.assertEqual(self.redis.delete('test5'), 1)
        self.assertEqual(self.redis.delete('notAvailable'), 0)
