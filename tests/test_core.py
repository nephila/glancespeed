from glancespeed import core
from mock import patch

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

    def test_create_diff(self):
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

        diff_result = core._create_diff(new, old)
        self.assertEqual(diff_result, diff)

    @patch('glancespeed.core._create_diff')
    def test_diff_results(self, mock_create_diff):
        old_value = {'a' : 1}
        new_value = {'b' : 2}
        core._diff_results(new_value, old_value)
        mock_create_diff.assert_called_with(new_value, old_value)

        old_value = None
        new_value = {'b' : 2}
        core._diff_results(new_value, old_value)
        mock_create_diff.assert_called_with(new_value, new_value)

    @patch('glancespeed.core._get_result_json')
    def test_get_results(self, mock_get_result_json):
        mock_get_result_json.return_value = {'a': 1, 'b': 2}
        expected_result = {
            'mobile': {'a': 1, 'b': 2},
            'desktop': {'a': 1, 'b': 2}
        }
        results = core._get_results('http://fakehost')
        self.assertEqual(results, expected_result)
