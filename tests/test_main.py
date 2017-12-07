import sys
import unittest
from unittest.mock import patch
from microdc import main


class TestMain(unittest.TestCase):

    def test_main_with_no_options(self):
        """
        If no options are given then we expect a valid arguments object
        """
        with self.assertRaises(SystemExit) as result:
            main()

        self.assertEqual(result.exception.code, 2)

    def test_main_with_valid_options(self):
        """
        If valid options are given then main should return True
        """
        sys.argv = ['microdc',
                    '--config', 'tests/good_config.yaml',
                    '--account', 'nonprod',
                    '--env', 'dev',
                    '--stack', 'application',
                    'up']
        result = main()
        self.assertEquals(result, True)
