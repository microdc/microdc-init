import sys
import unittest
from unittest.mock import patch
from microdc import main


class TestMain(unittest.TestCase):

    def test_main_with_valid_options(self):
        """
        If valid options are given then main should return True
        """
        return_value = ['microdc',
                        '--config', 'tests/good_config.yaml',
                        '--account', 'nonprod',
                        '--env', 'dev',
                        '--stack', 'service',
                        '--workdir', 'tests',
                        '--tool', 'terraform',
                        'up']
        with patch('sys.argv', return_value):
            print(sys.argv)
            result = main()
        self.assertEquals(result, True)

    def test_main_with_kops_tool(self):
        """
        If valid options and kops tool is given main should return True
        """
        return_value = ['microdc',
                        '--config', 'tests/good_config.yaml',
                        '--account', 'nonprod',
                        '--env', 'dev',
                        '--workdir', 'tests',
                        '--tool', 'kops',
                        'up']
        with patch('sys.argv', return_value):
            print(sys.argv)
            result = main()
        self.assertEquals(result, True)

    def test_main_with_kubectl_tool(self):
        """
        If valid options and kubectl tool is given main should return True
        """
        return_value = ['microdc',
                        '--config', 'tests/good_config.yaml',
                        '--account', 'nonprod',
                        '--env', 'dev',
                        '--workdir', 'tests',
                        '--tool', 'kubectl',
                        'up']
        with patch('sys.argv', return_value):
            print(sys.argv)
            result = main()
        self.assertEquals(result, True)

    def test_main_with_terraform_tool(self):
        """
        If valid options and terraform tool is given main should return True
        """
        return_value = ['microdc',
                        '--config', 'tests/good_config.yaml',
                        '--account', 'nonprod',
                        '--env', 'dev',
                        '--stack', 'global',
                        '--workdir', 'tests',
                        '--tool', 'terraform',
                        'up']
        with patch('sys.argv', return_value):
            print(sys.argv)
            result = main()
        self.assertEquals(result, True)

    def test_main_with_no_options(self):
        """
        If no options are given then we expect a valid arguments object
        """
        with self.assertRaises(SystemExit) as result:
            main()

        self.assertEqual(result.exception.code, 2)
