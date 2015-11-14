from glancespeed import core

import unittest

class TestCore(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_calculate_diff(self):
        diff = core._calculate_diff(5, 2)
        self.assertEqual(diff, 3)
        diff = core._calculate_diff(5.3, 2.1)
        self.assertEqual(diff, 5.3 - 2.1)
        diff = core._calculate_diff('a', 2.1)
        self.assertEqual(diff, 'a')
        diff = core._calculate_diff('a', 'b')
        self.assertEqual(diff, 'a')

    def test_find_item(self):
        new = {
            'first': 5,
            'complex': {
                'first': 'http://',
                'second': 10
            }
        }

        old = {
            'first': 2,
            'complex': {
                'first': 'http://',
                'second': 1
            }
        }

        diff = {
            'first': 3,
            'complex': {
                'first': 'http://',
                'second': 9
            }
        }

        diff_result = core._creatediff(new, old)
        self.assertEqual(diff_result, diff)


