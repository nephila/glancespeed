from glancespeed import core
from mock import patch

import unittest


class TestCore(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_calculate_diff(self):
        diff = core._calculate_diff('Score', 5, 2)
        self.assertEqual(diff['diff'], 3)
        diff = core._calculate_diff('Score', 5.3, 2.1)
        self.assertEqual(diff['diff'], 5.3 - 2.1)
        diff = core._calculate_diff('Score', 2.1, 5.3)
        self.assertEqual(diff['diff'], 5.3 - 2.1)
        diff = core._calculate_diff('Score', 'a', 2.1)
        self.assertEqual(diff, 'a')
        diff = core._calculate_diff('Score', 'a', 'b')
        self.assertEqual(diff, 'a')

        diff = core._calculate_diff('Score', '24.5 kB', '34.6 kB')
        self.assertEqual(diff['new'], '24.5 kB')
        self.assertEqual(diff['diff'], '10.1 kB')

        diff = core._calculate_diff('Score', 5, 2)
        self.assertEqual(diff['status'], 'OK')
        diff = core._calculate_diff('numberCssResources', 5, 2)
        self.assertEqual(diff['status'], 'BAD')

        diff = core._calculate_diff('Score', 5, 2)
        self.assertEqual(diff['sign'], '+')
        diff = core._calculate_diff('Score', 1, 2)
        self.assertEqual(diff['sign'], '-')

    def test_create_diff(self):
        _OLD_POSITIVES = core.POSITIVES
        _OLD_NEGATIVES = core.NEGATIVES

        core.POSITIVES = ['result']
        core.NEGATIVES = ['second', 'third']

        new = {
            'result': 5,
            'complex': {
                'first': 'http://',
                'second': 10,
                'third': 1
            }
        }

        old = {
            'result': 2,
            'complex': {
                'first': 'http://',
                'second': 1,
                'third': 10
            }
        }

        diff = {
            'result': {
                'diff': 3,
                'new': 5,
                'status': 'OK',
                'sign': '+'
            },
            'complex': {
                'first': 'http://',
                'second': {
                    'diff': 9,
                    'new': 10,
                    'status': 'BAD',
                    'sign': '+'
                },
                'third': {
                    'diff': 9,
                    'new': 1,
                    'status': 'OK',
                    'sign': '-'
                }
            }
        }

        diff_result = core._create_diff(new, old)
        self.assertEqual(diff_result, diff)

        core.POSITIVES = _OLD_POSITIVES
        core.NEGATIVES = _OLD_NEGATIVES

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
